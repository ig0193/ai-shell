# ai-shell

Type natural language in your terminal, press `Ctrl+G`, and it transforms into a real shell command and runs.

## Setup

### 1. Install

```bash
cd ~/tools/ai-shell
pip install -e .
```

### 2. Configure your LLM

Set your API key as an environment variable (add to `~/.zshrc`):

```bash
# Pick ONE — whichever LLM provider you use
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
# or for Ollama (local, no key needed):
export AI_SHELL_MODEL="ollama/llama3"
```

To change the model, either set `AI_SHELL_MODEL` env var or run:

```bash
ai config
```

Then edit `~/.config/ai-shell/config.yaml`:

```yaml
model: gpt-4o-mini          # or claude-sonnet-4-20250514, ollama/llama3, gemini/gemini-pro, etc.
auto_execute_safe: true
```

See all supported providers: https://docs.litellm.ai/docs/providers

### 3. Enable the keybinding

Add this line to your `~/.zshrc`:

```bash
source ~/tools/ai-shell/ai-shell.zsh
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Usage

### With keybinding (recommended)

1. Type a natural language description on your command line
2. Press `Ctrl+G`
3. The line transforms into a shell command
   - **Safe commands** auto-execute immediately
   - **Dangerous commands** (rm -rf, sudo, etc.) pause for you to review — press Enter to confirm

### With `ai` command directly

```bash
ai "find all python files modified in the last 24 hours"
ai "compress the logs folder into a tar.gz"
ai "show disk usage sorted by size"
```

### Flags

- `--exec` / `-e` — execute the command immediately (standalone mode)
- `--dry` / `-d` — only show the command, never execute

### Examples

```
$ list files larger than 100mb        [Ctrl+G]
→ find . -size +100M -type f

$ count lines of code in src/         [Ctrl+G]
→ find src/ -name "*.py" | xargs wc -l

$ show my git log as a graph          [Ctrl+G]
→ git log --oneline --graph --all
```

## Supported LLM Providers

Via [litellm](https://docs.litellm.ai/docs/providers), ai-shell works with:

- OpenAI (gpt-4o, gpt-4o-mini, etc.)
- Anthropic (claude-sonnet-4-20250514, claude-haiku, etc.)
- Ollama (local models — llama3, mistral, codellama, etc.)
- Google Gemini
- AWS Bedrock
- Azure OpenAI
- And 100+ more

## Safety

Commands matching dangerous patterns (rm -rf, sudo rm, mkfs, dd, etc.) are flagged and **not auto-executed**. You always get a chance to review before running.

## How it Works

### Installation and `setup.py`

When you run `pip install -e .` during the setup, Python's package manager reads the `setup.py` file to understand how to install the project. 

The `setup.py` file does two critical things:
1. It lists the dependencies required by the script (like `litellm` and `rich`).
2. It defines an **entry point**: `"ai=ai_shell.cli:entry"`. This tells Python to create an executable command named `ai` on your system. Whenever you type `ai` in your terminal, it essentially runs the `entry()` function located in the `ai_shell/cli.py` file.

Running `pip install -e .` in "editable" mode (`-e`) generates an `ai_shell.egg-info/` directory. This directory maintains a live link between your Python environment and your source code folder, so any changes you make to the Python files take effect immediately without needing reinstallation.

### The Zsh Widget

The `ai-shell.zsh` script enables the seamless user experience. When you source this file in your `.zshrc`, it registers a custom Zsh widget and maps it to a keyboard shortcut.

Instead of having to type `ai "my command"`, you can simply type your request into the standard terminal prompt. When you press the shortcut, the Zsh script:
1. Captures the text you just typed (`$BUFFER`).
2. Shows a thinking indicator.
3. Passes your text to the underlying `ai` Python script behind the scenes.
4. Takes the resulting shell command and replaces your terminal prompt text with it, allowing you to execute it or edit it directly.
