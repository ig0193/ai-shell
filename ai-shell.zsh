# ai-shell ZSH widget
# Source this file in your .zshrc:  source ~/tools/ai-shell/ai-shell.zsh
# Then use Ctrl+G to translate natural language to shell commands.

_ai_shell_transform() {
    # Don't do anything if the line is empty
    [[ -z "$BUFFER" ]] && return

    # Save the original query for display
    local query="$BUFFER"

    # Show a spinner while waiting for the LLM
    BUFFER="thinking: $query"
    zle -R  # force redraw to show the spinner

    # Call the AI tool — stdout = command, stderr = warnings/info
    local _ai_shell_bin="${AI_SHELL_BIN:-$HOME/tools/ai-shell/.venv/bin/ai}"
    local cmd
    cmd=$("$_ai_shell_bin" "$query" 2>/dev/tty)
    local exit_code=$?

    if [[ -z "$cmd" ]]; then
        BUFFER="$query"
        CURSOR=$#BUFFER
        zle -R
        return
    fi

    # Replace the buffer with the translated command
    BUFFER="$cmd"
    CURSOR=$#BUFFER

    if [[ $exit_code -eq 0 ]]; then
        # Safe command → auto-execute
        zle accept-line
    else
        # Dangerous or error → show command, let user review & press Enter
        zle -R
    fi
}

# Register the widget and bind to Ctrl+G
zle -N _ai_shell_transform
bindkey '^G' _ai_shell_transform
