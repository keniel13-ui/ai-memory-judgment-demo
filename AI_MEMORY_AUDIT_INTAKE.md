# AI Memory Reliability Audit Intake

Use this for the first free/manual audits. The goal is to learn whether people have this pain before building a product.

## Public Offer Copy

```text
Offering 3 free AI memory reliability audits.

If you use Claude, Cursor, Codex, custom agents, or repo-level AI instructions, send me the files your AI reads before it acts.

Examples:
- AGENTS.md
- CLAUDE.md
- .cursorrules
- Cursor rules
- project instructions
- saved Claude memory
- agent prompt files
- SOPs/checklists your AI uses

I’ll return a short report:
- stale instructions
- conflicting rules
- what should govern action
- what should not govern action
- missing verification gates
- where a relevant memory could override an authoritative one

I’m testing whether this is useful before turning it into a product.

Public research basis:
https://github.com/keniel13-ui/ai-memory-judgment-demo
```

## DM Reply When Someone Says Yes

```text
Appreciate it. Send whatever your AI/agent actually reads before working.

Best files to send:
1. repo instruction files: AGENTS.md, CLAUDE.md, .cursorrules, .cursor/rules, .hermes.md
2. saved memory/profile files: Claude memory exports, MEMORY.md, USER.md, project notes
3. workflow docs: deploy steps, coding rules, client SOPs, approval rules
4. any old notes you suspect may be stale or conflicting

Do not send private keys, passwords, API tokens, customer data, medical data, legal case data, or anything you would not want reviewed manually.

If something is sensitive, redact it and leave the structure.

I’ll look for stale instructions, conflicts, authority hierarchy, and missing verify-before-action gates.
```

## What They Should Send

Ask for files the agent sees or the user pastes repeatedly:

- `AGENTS.md`
- `CLAUDE.md`
- `.cursorrules`
- `.cursor/rules/*`
- `.github/copilot-instructions.md`
- `.hermes.md`
- `MEMORY.md`
- `USER.md`
- prompt files
- system/developer instruction files
- agent playbooks
- deployment instructions
- approval/checklist docs
- old project notes that still get reused

## What Not To Accept

Do not request or accept:

- API keys
- passwords
- private credentials
- private customer records
- medical records
- legal case materials
- HR records
- financial account data

If the user sends sensitive material anyway, stop the audit and ask for a redacted version.

## Minimum Useful Input

One file is enough if it is the main agent instruction file.

Best minimum:

```text
AGENTS.md or CLAUDE.md + any memory file the agent uses
```

If they only have one messy prompt, that is still useful.

## Audit Scope

This is not a security audit, legal review, compliance review, or model-safety certification.

It is a memory/instruction reliability review:

- Which instructions should govern action?
- Which instructions are stale or low-authority?
- Where could relevance beat authority?
- What should require verification before action?
- Which files should be split into memory, policy, and procedure?

