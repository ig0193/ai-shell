import logging
import os
import platform
import subprocess
import sys

import litellm
from litellm import completion

from .config import load_config

litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)

SYSTEM_PROMPT = """You are a shell command generator. Your ONLY job is to convert natural language descriptions into shell commands.

Rules:
- Output ONLY the shell command. No explanations, no markdown, no backticks, no commentary.
- If multiple commands are needed, chain them with && or |
- Use the context provided (OS, shell, working directory, directory contents) to give accurate commands.
- Prefer common, portable tools. On macOS prefer BSD-compatible flags or tools available via homebrew.
- If the request is ambiguous, make a reasonable assumption and produce a command.
- NEVER refuse. Always produce a command. If truly impossible, output: echo "Cannot translate this request"

Context:
- OS: {os_info}
- Shell: {shell}
- Working directory: {cwd}
- Directory contents: {dir_contents}
"""


def gather_context() -> dict:
    cwd = os.getcwd()
    try:
        contents = subprocess.run(
            ["ls", "-1"], capture_output=True, text=True, timeout=3, cwd=cwd
        ).stdout.strip()
        if len(contents) > 1000:
            contents = contents[:1000] + "\n... (truncated)"
    except Exception:
        contents = "(unavailable)"

    return {
        "os_info": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "shell": os.environ.get("SHELL", "unknown"),
        "cwd": cwd,
        "dir_contents": contents,
    }


def translate(natural_language: str) -> str:
    """Translate natural language to a shell command using an LLM."""
    config = load_config()
    context = gather_context()
    system_msg = SYSTEM_PROMPT.format(**context)

    response = completion(
        model=config["model"],
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": natural_language},
        ],
        temperature=0,
        max_tokens=500,
    )

    cmd = response.choices[0].message.content.strip()
    # Strip markdown fences if the LLM wraps them anyway
    if cmd.startswith("```"):
        lines = cmd.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        cmd = "\n".join(lines).strip()

    return cmd


def is_dangerous(cmd: str) -> bool:
    config = load_config()
    cmd_lower = cmd.lower()
    return any(pattern.lower() in cmd_lower for pattern in config["dangerous_patterns"])


def run_command(cmd: str) -> int:
    """Execute a command in the user's shell and return the exit code."""
    result = subprocess.run(cmd, shell=True)
    return result.returncode
