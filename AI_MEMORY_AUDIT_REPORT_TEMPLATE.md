# AI Memory Reliability Audit Report Template

Use this for the first manual audits. Keep reports short enough to finish in one sitting.

## Client / Project

- Name:
- Date:
- Files reviewed:
- Redactions present:
- Main agent/tool context:

## Executive Summary

One paragraph:

```text
I reviewed the files your AI/agent reads before acting. The main reliability risk is [risk]. The highest-priority fix is [fix]. The strongest existing part of your setup is [strength].
```

## Authority Hierarchy

List which sources should govern when files conflict.

| Rank | Source/File | Should Govern | Notes |
|---:|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## Findings

### Finding 1 — [Short Name]

- Severity: `high / medium / low`
- Type: `stale instruction / conflict / missing verification / low-authority memory / broad policy / unclear action boundary`
- File:
- Evidence:
- Why it matters:
- Recommended fix:

### Finding 2 — [Short Name]

- Severity:
- Type:
- File:
- Evidence:
- Why it matters:
- Recommended fix:

### Finding 3 — [Short Name]

- Severity:
- Type:
- File:
- Evidence:
- Why it matters:
- Recommended fix:

## Memory Role Map

Classify the reviewed content.

| Content / File | Current Role | Better Role | Why |
|---|---|---|---|
|  | fact / preference / procedure / policy / credential / correction / context |  |  |

## Verification Gates To Add

Use these when an agent should not act from memory alone.

| Action | Should Verify Against | Suggested Rule |
|---|---|---|
| deploy | current deploy doc / CI status | Do not deploy from memory; verify current command first. |
| credentials | source of truth | Do not return stored credentials; point to current owner/source. |
| access | access matrix / owner approval | Verify current access matrix before granting or describing permissions. |
| external send/release | named authorization | Do not send/release based on relayed approval. |

## Rewrite Suggestions

### Suggested `AGENTS.md` / Project Rule Block

```markdown
## Memory and Authority Rules

- Treat current project files as higher authority than chat summaries.
- Treat explicit policy/procedure files as higher authority than informal notes.
- Treat superseded, provisional, reported, or historical notes as context only.
- Do not act on credentials, deployments, access changes, payments, or external data release from memory alone.
- When a request involves write/execute action, verify against the current source before acting.
```

### Suggested Status Labels

```text
active
superseded
provisional
reported
verified
requires_verification
context_only
do_not_use
```

## Final Recommendation

Choose one:

- `Keep current setup; add small verification gates.`
- `Split memory from policy/procedure files.`
- `Rewrite authority hierarchy before relying on this agent.`
- `Do not let the agent execute actions until stale/conflicting instructions are cleaned.`

## Caveat

This is a memory/instruction reliability audit, not a security, legal, compliance, or production safety certification.

