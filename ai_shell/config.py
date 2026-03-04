import os
import yaml
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "ai-shell"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "model": "gpt-4o-mini",
    "dangerous_patterns": [
        "rm -rf",
        "rm -r /",
        "mkfs",
        "dd if=",
        "> /dev/sd",
        "chmod -R 777 /",
        ":(){ :|:& };:",
        "mv /* ",
        "mv / ",
        "sudo rm",
        "sudo mkfs",
        "shutdown",
        "reboot",
        "init 0",
        "init 6",
    ],
    "auto_execute_safe": True,
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            user_config = yaml.safe_load(f) or {}
        config = {**DEFAULT_CONFIG, **user_config}
    else:
        config = DEFAULT_CONFIG.copy()

    for env_key, config_key in [
        ("AI_SHELL_MODEL", "model"),
        ("OPENAI_API_KEY", "openai_api_key"),
        ("ANTHROPIC_API_KEY", "anthropic_api_key"),
    ]:
        val = os.environ.get(env_key)
        if val:
            config[config_key] = val

    return config


def init_config():
    """Create default config file if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(
                {
                    "model": DEFAULT_CONFIG["model"],
                    "auto_execute_safe": True,
                },
                f,
                default_flow_style=False,
            )
        return CONFIG_FILE
    return None
