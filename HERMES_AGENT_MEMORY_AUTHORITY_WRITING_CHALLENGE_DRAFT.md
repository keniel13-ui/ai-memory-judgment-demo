# Before I Would Trust an Agent's Memory, I Would Audit Its Authority

This is a submission for the [Hermes Agent Challenge](https://dev.to/challenges/hermes-agent-2026-05-15), under the **Write About Hermes Agent** prompt.

I've spent the last week testing AI memory failure modes in a public evaluation harness. That work changed how I read agent memory systems.

This is a writing submission, not a build submission. I did not build a Hermes Agent project for this challenge. I am writing from the perspective of someone testing how memory failures show up once agents can act.

So when I look at Hermes Agent, the question I care about is not only:

> Can the agent remember useful things?

The harder question is:

> When memory conflicts, which memory is allowed to govern the agent's action?

That distinction matters.

Hermes Agent is interesting because it is not just a chat interface. Its documentation describes an open-source agentic system with tool use, project context, persistent memory, skills, browser automation, checkpoints, delegation, scheduled tasks, and multiple memory providers.

That is exactly the kind of system where memory stops being a convenience feature and starts becoming part of the agent's operating boundary.

If an agent can run tools, edit files, browse, delegate work, schedule tasks, and remember across sessions, then memory is no longer just "context."

Memory becomes governance.

## The Memory Problem I Would Watch For

In a simple chatbot, bad memory is annoying.

In an agent, bad memory can become operational.

The failure mode is not only that the agent forgets something. Sometimes the more dangerous failure is that it remembers the wrong thing too confidently.

A memory can be:

- relevant but stale,
- relevant but low-authority,
- relevant but superseded,
- relevant but only context,
- relevant but not allowed to determine the action.

That is the distinction my own tests kept running into.

Retrieval systems are usually good at answering:

> What memory is closest to the user's request?

But safety often depends on a different question:

> What memory is allowed to decide what the agent should do?

Those are not the same objective.

## Why Hermes Makes This Worth Talking About

Hermes Agent has several memory and context surfaces that make this question practical rather than abstract.

The docs describe persistent memory through `MEMORY.md` and `USER.md`, project context through files like `AGENTS.md`, `.hermes.md`, `CLAUDE.md`, `SOUL.md`, and `.cursorrules`, and reusable procedures through skills.

The prompt assembly docs also describe `SOUL.md` as the identity layer loaded into the system prompt, while `MEMORY.md` and `USER.md` provide durable cross-session facts that are snapshotted into new sessions.

The tips docs add one detail that matters a lot: memory is a frozen snapshot during a session. Writes can happen on disk immediately, but those changes do not appear in the system prompt until the next session starts.

That is a reasonable engineering tradeoff. It protects prompt-cache stability and keeps memory bounded.

But it also creates a real audit question:

> If memory is frozen at session start, how does the operator reason about updates, corrections, and superseded facts during long-running work?

For ordinary preferences, that may not matter much.

For operational rules, credentials, approvals, safety constraints, or deployment procedures, it matters a lot.

## Memory Needs Roles, Not Just Text

The practical lesson from my own AI memory tests was simple:

> Relevance is not authority.

A memory can be a perfect semantic match and still be the wrong memory to obey.

For example:

- A stale Wi-Fi password is highly relevant to "what is the Wi-Fi password?"
- A loose old discussion about giving a contractor broad access is relevant to "what reach does this seat get?"
- A past note that a consultant might need donor data is relevant to "can I send the donor list?"

But none of those should necessarily govern the action.

The memory that should govern may be less conversationally obvious:

- "The current Wi-Fi credential lives with IT."
- "Payment-capable access must be checked against the current access matrix."
- "Donor data release requires verifiable named authorization."

This is where agent memory needs roles.

Not every remembered thing is the same kind of object.

Some memories are facts.
Some are preferences.
Some are procedures.
Some are policies.
Some are credentials.
Some are corrections.
Some are context.

If those all collapse into "text the agent remembers," the most relevant memory can win when the most authoritative memory should have governed.

In my own evaluation harness, adding an authority lane changed the result from 3/5 target memories selected to 5/5 on one adversarial packet. The same inputs that defeated the best lexical strategy were not fixed by making retrieval more semantic. They were fixed by separating authority from relevance before ordinary ranking got to decide.

In Hermes terms: `SOUL.md` carries role and identity. `MEMORY.md` and `USER.md` carry durable facts and preferences. Skills carry procedures. Project files like `AGENTS.md` and `.hermes.md` can become the policy layer, but only if the operator treats them that way.

## A Simple Authority Checklist For Hermes Users

If I were setting up Hermes Agent for serious work, I would not only ask what to put in memory.

I would ask what each memory is allowed to do.

Here is the checklist I would use.

### 1. Separate durable facts from operating rules

Facts belong in memory.

Operating rules need stronger treatment.

If a rule determines whether the agent may edit files, deploy, access credentials, send data, or take an external action, I would not leave it as ordinary prose mixed into general memory.

I would put it somewhere explicit, concise, and easy to audit: a project `AGENTS.md`, a `.hermes.md`, or a dedicated section in a context file.

### 2. Mark stale and superseded memories aggressively

The most dangerous old memory is not the obviously wrong one.

It is the one that still sounds useful.

Credentials, endpoints, deployment steps, access rules, and approval notes should carry clear status language:

```text
Superseded.
Do not use.
Current source is X.
Verify before acting.
```

That gives the agent a stronger signal than relevance alone.

### 3. Keep memory bounded and boring

Hermes documents bounded memory, and I think that is a strength.

Long memory files invite accidental policy drift. Shorter memory forces the operator to decide what actually deserves persistence.

The boring memory file is often the safer memory file.

### 4. Treat skills as procedures, not beliefs

Hermes' docs distinguish memory from skills: memory is for facts, skills are for procedures.

That distinction is important.

If a task has a repeatable workflow, it should probably be a skill or project instruction, not a vague remembered preference.

Procedures need steps, preconditions, and stop conditions.

Memory alone is not enough.

### 5. Audit what governs tool use

Once an agent can use tools, the key question becomes:

> What memory or instruction controls this action?

Before trusting an agent with a workflow, I would test examples like:

- stale credential vs current credential source,
- old deploy command vs current deploy procedure,
- read-only lookup vs write/execute action,
- low-trust user note vs project rule,
- previous approval vs current approval requirement.

The point is not to prove the agent is perfect.

The point is to find where relevant memories override authoritative ones.

## The Frozen Snapshot Detail Matters

One Hermes detail I would pay attention to is the frozen memory snapshot.

The docs say memory writes happen immediately, but the prompt snapshot does not update mid-session.

That means an agent could write a correction to memory during a session, while still operating from the old prompt context until a new session begins.

That is not necessarily a bug.

But operators should understand it.

For low-risk preferences, this is fine:

```text
Remember that I prefer terse answers.
```

For action-governing corrections, I would be more careful:

```text
The deploy target changed.
The old credential is revoked.
The approval rule changed.
The current source of truth moved.
```

For those, I would want either a session restart, an explicit context injection, or a workflow rule that says the agent must verify against the current file before acting.

The general principle:

> If a memory update changes what the agent is allowed to do, do not treat it like an ordinary preference update.

## What I Would Test Next

If I were evaluating Hermes memory for production-style use, I would build a small harness around authority conflicts.

Not a benchmark claiming general results.

Just a diagnostic.

Five scenarios would be enough to start:

1. A stale credential and an active credential policy.
2. A user preference that conflicts with a project rule.
3. A previous approval that is no longer valid.
4. A read-only question that shares vocabulary with a write/execute policy.
5. A broad remembered procedure that conflicts with a narrower current instruction.

For each one, I would track two separate metrics:

- Did the agent retrieve or cite the relevant memory?
- Did the correct memory govern the action?

Those are different scores.

That separation is the whole point.

## Why This Matters For Open Agents

The exciting thing about open agent systems is that people can inspect and shape them.

The risky thing is the same.

## My Takeaway

I would not evaluate an agent memory system only by asking whether it remembers.

I would ask whether it knows what its memories are allowed to do.

That is the difference between memory as convenience and memory as governance.

For Hermes Agent users, my practical advice is:

> Do not just write memories. Classify them.

Mark what is fact, what is preference, what is procedure, what is policy, what is stale, and what must be verified before action.

Because in an agentic system, the most relevant memory is not always the memory that should win.

Being on-topic is not the same as being authoritative.

And once an agent can act, that distinction becomes the whole game.

## Sources

- Hermes Agent Challenge: https://dev.to/challenges/hermes-agent-2026-05-15/
- Hermes Agent features overview: https://hermes-agent.nousresearch.com/docs/user-guide/features/overview/
- Hermes Agent prompt assembly docs: https://hermes-agent.nousresearch.com/docs/developer-guide/prompt-assembly
- Hermes Agent tips and best practices: https://hermes-agent.nousresearch.com/docs/guides/tips/
- Related public memory harness: https://github.com/keniel13-ui/ai-memory-judgment-demo

Tags: `hermesagentchallenge`, `ai`, `agents`, `machinelearning`
