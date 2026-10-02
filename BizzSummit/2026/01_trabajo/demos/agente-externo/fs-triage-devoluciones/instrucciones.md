WorkIQ is wired into the agent, but **I haven't been able to test it end to end.** Fetching the delegated tokens and writing them into a file was blocked for me, so you need to run that one step yourself.

## What's set up

- **`ToolingManifest.json`:** created by `a365 develop add-mcp-servers` with `mcp_MailTools` and `mcp_WordServer`.
- **Permissions:**
  - **Service principals:** the tenant was missing them for the two servers ("Work IQ Mail MCP" and "Work IQ Word MCP"). I created them with `az ad sp create`, because the CLI got stuck at an interactive `[y/N]` prompt.
  - **Admin consent:** `a365 setup permissions mcp` then granted consent for all scopes.
  - **Bot permissions:** I skipped the `permissions bot` step the CLI suggested, because it only applies to Teams/Copilot agents.
- **New `src/workiq.py`:**
  - It reads the manifest and passes each server to the Claude SDK as a remote MCP server, using that server's own token.
  - It also allows all tools from those servers.
  - If a token is missing and `SKIP_TOOLING_ON_ERRORS=true`, the agent starts without that server instead of failing.
- **`src/agent.py`:** two narrow edits merge those servers into `ClaudeAgentOptions`. All the observability wrapping is still intact.
- **`.env` and `.env.example`:** now have `BEARER_TOKEN_MCP_MAILTOOLS`, `BEARER_TOKEN_MCP_WORDSERVER` and `SKIP_TOOLING_ON_ERRORS=true`.

I checked that the agent still imports and that the WorkIQ servers are skipped cleanly when no token is set. That's the current state.

## What you need to do

Each server has its own audience, so get one token per server and paste each into `.env`:

```
a365 develop get-token --resource-id 16b1878d-62c7-4009-aa25-68989d63bbad --scopes Tools.ListInvoke.All -o raw   # → BEARER_TOKEN_MCP_MAILTOOLS
a365 develop get-token --resource-id c2d0c2b6-8013-4346-9f8b-b81d3b754a29 --scopes Tools.ListInvoke.All -o raw   # → BEARER_TOKEN_MCP_WORDSERVER
```

Then run, for example, `.venv\Scripts\python src\agent.py --verbose --prompt "Lee los últimos correos de devoluciones con Mail y redacta el resumen en un Word"`.

Things to know:
- **Token expiry:** the tokens act as you and last about an hour, so get fresh ones just before the session.
- **Unattended runs:** this works for a demo, but not for an unattended scheduled run, because WorkIQ needs a signed-in user.
- **Prompt:** the system prompt still points at the triage tools, so the agent only uses Mail and Word when you ask in `--prompt`. I haven't changed `buzon.py` or the triage flow.
- **Tool tracing:** Mail and Word tool calls run inside the Claude CLI process, so they don't get their own tool spans. They're still covered by the run's invocation and inference spans.

Nothing is committed. Since the observability and WorkIQ changes were meant to be shown live, you may want to commit them on a branch and start the demo from a clean `main`.