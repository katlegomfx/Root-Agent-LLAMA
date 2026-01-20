# RLM Remixed Workspace

This project provides a fully supported AI coding environment where an autonomous agent manages the lifecycle of code, from execution to improvement.

## Structure

```
/
├── main.py                 # The entry point. Run this!
├── core/                   # Core system components
│   ├── html_terminal.py    # Records terminal sessions to HTML
│   ├── context_agent.py    # The coding subagent
│   ├── improvements_manager.py # Tasks tracking
│   └── rlm_repl.py         # Persistent python shell
├── prompts/                # Directives for the AI Brain
└── improvements.json       # Auto-generated task list
```

## How to use

1.  **Start the environment**:
    ```bash
    python main.py
    ```

2.  **Enter a Goal**:
    The agent will ask for a goal. It will spin up a recorded terminal session and attempt to achieve it using the `html_terminal.py` tool and its coding subagent.

3.  **Auto-Improvement Loop**:
    After the goal is finished (or skipped), the system scans the codebase for TODOs or issues.
    *   It lists suggestions.
    *   It asks if you want to implement them.
    *   **Auto-Pilot**: If you don't respond in 5 minutes, it automatically says YES and attempts to write the code to fix the issue.

## Features

*   **HTML Terminal**: All command-line interactions are logged to `terminal_log.html` for easy review.
*   **Subagent Delegation**: Complex coding tasks are offloaded to a specialized subagent that can write files and analyze code.
*   **Timeouts Removed**: Optimized for varying machine speeds.
*   **Self-Healing**: The improvement manager finds what you left undone and offers to finish it.
