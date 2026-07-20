# Hermes QQBot Community Patch

A versioned patch for [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) that turns the official QQBot adapter into a safer community-operations channel.

This is not a standalone bot runtime. It deliberately reuses Hermes sessions, tools, memory, queueing, `NO_REPLY`, gateway lifecycle, and dashboard.

## Features

- Dispatch ordinary `GROUP_MESSAGE_CREATE` events, not only `@` mentions.
- One shared Agent session per QQ group with sender attribution.
- Strict group and owner OpenID allowlists.
- Fixed-target owner-DM-to-group and group-to-owner tools.
- Explicit group/C2C outbound routing, including home-channel shutdown notices.
- Optional HTTPS nickname resolution with TTL, negative caching, single-flight requests, and prompt-safe sanitization.
- Silent rejection for unauthorized groups and private chats.
- Dashboard form under **Channels > QQBot** for policies, OpenIDs, ordinary-message mode, nickname lookup, and Markdown.
- Focused regression tests for authorization, concurrency, queueing, deduplication, silence delivery, API routing, and dashboard config writes.

## Requirements

- A Git checkout of Hermes Agent.
- Python environment and Node dependencies required by Hermes itself.
- An official QQ Open Platform application with App ID and Client Secret.

## Install

```bash
git clone <this-repository-url>
python hermes-qqbot-community-patch/install.py /path/to/Hermes-Agent
```

The installer runs `git apply --check` first. If the current Hermes revision is incompatible, it stops without attempting conflict resolution.

For an inspection-only install without tests:

```bash
python install.py /path/to/Hermes-Agent --skip-tests
```

## Configure

1. Start the dashboard: `hermes dashboard`.
2. Open **Channels**.
3. Choose **QQBot > Configure**.
4. Enter the QQ App ID and Client Secret.
5. Set the private-chat OpenID, home-group OpenID, and sole owner OpenID.
6. Set both policies to `Allowlist`.
7. Enable ordinary group-message dispatch.
8. Optionally enable nickname lookup. This sends member OpenIDs and the App ID to the configured third-party HTTPS endpoint; it is disabled by default.
9. Save and restart the gateway.

Non-secret behavior settings are written to `config.yaml`. Credentials stay in `.env`.

See `config.example.yaml` for the equivalent manual configuration.

## Safety Model

- Unauthorized traffic is rejected before attachment processing, session creation, or model invocation.
- Owner authority is based only on the configured OpenID. A platform role, nickname, quoted message, or self-claim cannot grant authority.
- Cross-session tools have fixed destinations; the model cannot supply arbitrary target IDs.
- Group traffic uses queue mode so ordinary chatter does not interrupt active work.
- Nicknames are untrusted display data and are flattened, length-bounded, and stripped of attribution delimiters and bidirectional controls.
- A timed-out proactive send is reported as delivery-unknown and must not be automatically retried.

Prompt rules are not a complete security boundary. Keep dangerous Hermes toolsets disabled for untrusted community channels unless the operational use case requires them.

## Verify

```bash
scripts/run_tests.sh \
  tests/gateway/test_qqbot.py \
  tests/tools/test_qqbot_messaging_tool.py \
  tests/hermes_cli/test_web_server.py -q

cd web
npm run check
npm run build
```

## Upgrade

1. Remove the old patch with `python uninstall.py /path/to/Hermes-Agent`.
2. Update Hermes.
3. Pull the latest patch repository.
4. Run `install.py` again.

User configuration and credentials are never removed by the uninstaller.

## Project Direction

The long-term split is:

- Generic QQBot protocol, routing, shared-session, and dashboard support should be contributed upstream to Hermes Agent.
- Community-specific identity, prompts, feedback workflows, and knowledge-base behavior should live in a separate Hermes plugin.

## License

MIT. Hermes Agent retains its own license and copyright.
