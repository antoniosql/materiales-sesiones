## Process lifecycle and cleanup

Clean up every process you start.

- Before starting a server, browser, watcher, emulator or test runner, check whether a suitable one is already running, and reuse it.
- Track each long-running process you start: its PID, port and how to stop it.
- Prefer commands that exit when they finish. Avoid watch mode and background processes unless the task needs them
- Never run broad kills like `pkill node`. Kill only processes you own, and ask before stopping any process you're unsure about.
- If the machine is slow, check process age, CPU, memory and parent processes, and clean up your own leftover processes before starting new ones.