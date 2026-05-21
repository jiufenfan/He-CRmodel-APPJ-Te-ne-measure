# Agent Issue Router

Purpose: minimal issue-work entrypoint for coding agents.

Use this file first when the user asks to solve, fix, implement, continue, review, or
work on a GitHub issue number or local `ISSUE-XXX`.

Detailed engineering context stays in `docs/devlog/ACTIVE_ISSUES.md`.
Dependency status stays in `docs/devlog/issue_dependencies.yaml`.

## Issue Routing Table

The `Human detail` link points to the start of the target issue section. When reading
`docs/devlog/ACTIVE_ISSUES.md`, stop at the next `## ISSUE-` header (or end of file).

| Issue | GitHub | Human detail | Primary rule |
| --- | --- | --- | --- |
| ISSUE-001 | #1 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:7) | `.agents/rules/model-agent.md`, `.agents/rules/solver-agent.md`, `.agents/rules/data-agent.md` |
| ISSUE-002 | #2 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:77) | `.agents/rules/data-agent.md`, `.agents/rules/test-agent.md` |
| ISSUE-003 | #3 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:128) | `.agents/rules/data-agent.md`, `.agents/rules/schema-agent.md`, `.agents/rules/test-agent.md` |
| ISSUE-004 | #4 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:319) | `.agents/rules/solver-agent.md`, `.agents/rules/harness-agent.md`, `.agents/rules/data-agent.md` |
| ISSUE-005 | #5 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:363) | `.agents/rules/data-agent.md`, `.agents/rules/test-agent.md` |
| ISSUE-006 | #6 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:185) | `.agents/rules/data-agent.md`, `.agents/rules/solver-agent.md`, `.agents/rules/model-agent.md` |
| ISSUE-007 | #7 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:216) | `.agents/rules/data-agent.md` |
| ISSUE-008 | #8 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:243) | `.agents/rules/data-agent.md`, `.agents/rules/schema-agent.md`, `.agents/rules/docs-agent.md` |
| ISSUE-009 | #9 | [ACTIVE_ISSUES.md](I:/spectrum-analysis/docs/devlog/ACTIVE_ISSUES.md:282) | `.agents/rules/solver-agent.md`, `.agents/rules/model-agent.md`, `.agents/rules/test-agent.md` |

## Start Protocol

Before implementation:

1. Identify the local issue ID and GitHub issue number.
2. Find the issue row in this routing table.
3. Read `docs/devlog/issue_dependencies.yaml` for current status, blockers, allowed blocked-issue scope, and model recommendation.
4. Read only the target issue section in `docs/devlog/ACTIVE_ISSUES.md` from its `## ISSUE-XXX` header until the next `## ISSUE-` header (or end of file). Do not read unrelated issue sections unless the target issue explicitly depends on them.
5. Summarize the issue and propose an implementation approach, then discuss it with the human and wait for explicit confirmation before proceeding further.
6. Read the relevant module rule from the routing row and any additional module rules required by touched files.
7. State the issue status, blockers, allowed scope, recommended model, and branch name before editing.
8. Use branch `codex/issue-XXX-short-name`; do not implement issue work directly on `main`.
9. Define allowed read files, allowed write files, and tests before editing.

If the issue is blocked, implement only the explicitly allowed blocked-scope work.

## Protected Files

Ordinary issue branches must not modify these unless the user explicitly requests a
rule/process update or the issue itself is governance work:

- `AGENTS.md`
- `.agents/ROUTER.md`
- `.agents/rules/`
- `docs/devlog/ISSUE_DEPENDENCY_GRAPH.md`
- `docs/devlog/AGENT_ISSUE_ROUTER.md`
- `docs/devlog/issue_dependencies.yaml`

Scientific data cannot be promoted from `data/raw_sources/` or `data/staged/` to
`data/canonical/` without explicit human review evidence.
