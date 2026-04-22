# AGENTS

## Primary agents
- Builder Agent: implements and tests core features.
- QA Agent: validates outputs and edge-case handling.
- Ops Agent: handles deployment, configuration, and runbooks.

## Operating rules
- Keep outputs deterministic by default.
- Enable provider/API modes via explicit config.
- Require human review for externally sent content.
