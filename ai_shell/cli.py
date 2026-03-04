import sys
from rich.console import Console

from .config import init_config, CONFIG_FILE
from .core import is_dangerous, run_command, translate

console = Console(stderr=True)


def entry():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        _print_help()
        sys.exit(0 if args else 1)

    if args[0] == "config":
        _config()
        sys.exit(0)

    _handle_query(args)


def _print_help():
    console.print("[bold]ai-shell[/] — Natural language to shell command translator\n")
    console.print("[yellow]Usage:[/]")
    console.print("  ai <natural language description>")
    console.print("  ai --exec <description>     translate & execute immediately")
    console.print("  ai --dry <description>      translate only, don't execute")
    console.print("  ai config                   manage configuration\n")
    console.print("[yellow]Examples:[/]")
    console.print('  ai "find all python files modified today"')
    console.print('  ai show disk usage sorted by size')
    console.print('  ai --exec "list open ports"')


def _config():
    result = init_config()
    if result:
        console.print(f"[green]Created config:[/] {result}")
    else:
        console.print(f"[blue]Config exists at:[/] {CONFIG_FILE}")
    console.print("\n[dim]Edit this file to change your model, API keys, etc.[/]")
    console.print("[dim]Supported models: gpt-4o-mini, claude-sonnet-4-20250514, ollama/llama3, gemini/gemini-pro, etc.[/]")
    console.print("[dim]See: https://docs.litellm.ai/docs/providers[/]")


def _handle_query(args: list[str]):
    execute = False
    dry_run = False
    query_parts = []

    for arg in args:
        if arg in ("--exec", "-e"):
            execute = True
        elif arg in ("--dry", "-d"):
            dry_run = True
        else:
            query_parts.append(arg)

    query = " ".join(query_parts)
    if not query:
        console.print("[red]No query provided.[/]")
        sys.exit(1)

    try:
        cmd = translate(query)
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "authentication" in err.lower():
            console.print("[red]No API key configured.[/]")
            console.print("[dim]Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.[/]")
            console.print("[dim]Or edit ~/.config/ai-shell/config.yaml[/]")
        else:
            console.print(f"[red]Error calling LLM:[/] {e}")
        sys.exit(2)

    dangerous = is_dangerous(cmd)

    if dangerous:
        console.print(f"[bold red]⚠ DANGEROUS:[/] {cmd}")
        print(cmd)
        sys.exit(1)

    print(cmd)

    from .config import load_config
    config = load_config()

    if dry_run:
        sys.exit(0)

    if execute:
        console.print(f"[dim]→ running:[/] {cmd}")
        exit_code = run_command(cmd)
        sys.exit(exit_code)

    # If it's safe but the user disabled auto-execute, exit with a non-zero code
    # so the ZSH widget puts it in the buffer but doesn't press Enter.
    if not config.get("auto_execute_safe", True):
        sys.exit(3)

    sys.exit(0)
