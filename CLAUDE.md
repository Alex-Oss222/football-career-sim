# CLAUDE.md: football-career-sim

Claude Code is the runner for this simulation. Every rule in AGENTS.md applies to Claude exactly as written. Wherever AGENTS.md says "Codex", read "the agent running the task" (Claude Code in these sessions).

@AGENTS.md

## Claude Code specifics

- **Same rules, same gates.** Protagonist-blind resolution, no invented ratings or numbers, the no-hindsight playbook lock, atomic progression, any user-authorized migration procedure, `validate_repository.py` and `check_game_readiness.py` all apply unchanged. Changing the runner changes no football rule and no game result.
- **GitHub.** Commit on the designated working branch and open the normal pull request with the GitHub tools available in the session. Never push to `main` directly. Advance the private snapshot only from a merged `main` checkout.
- **Diff-size rules.** The Codex extraction limit does not bind Claude, but the storage rules stay: compact receipts for background games, no raw receipt data in Markdown, never commit `.sim_cache/`.
- **Cloud sessions are ephemeral.** `.sim_cache/` does not survive between cloud sessions. Rebuild the transient TeamInputs inside the same task that uses them, and never ask the user to supply them.
- **Private runtime.** Games still close only through the private Engine State service. Cloud sessions need `ENGINE_RUNTIME_URL` and `ENGINE_API_TOKEN` in the environment settings, and outbound network access to that host.
- **Token economy.** Read only the files a task names. Read the active playbook iterations by section rather than whole. Delegate large research sweeps, such as 32-club roster reconstruction, to subagents that return compact results.
