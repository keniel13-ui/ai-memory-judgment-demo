# Governs Audit Protocol

Purpose: separate fresh-author evidence from post-hoc audit work.

The project now uses two different workflows. They should not be mixed.

## Workflow A: Fresh Authoring

Use this when testing whether `governs` metadata is authorable from the packet alone.

Fresh-author constraints:

- The author should have no repo context.
- The author should not know prior failures, expected targets, evaluator outputs, or claim history.
- The author should receive only `EXTERNAL_GOVERNS_REQUEST.md` and the relevant authoring packet.
- The author should return only the JSON annotations object requested by the packet.
- The result may be evaluated as evidence for authorability.

Good fresh-author prompt:

```text
You are acting as a fresh external annotation author.

Important constraints:
- You have no access to our repo, prior results, expected answers, hidden target labels, or failure analysis.
- Do not try to guess what the evaluator wants.
- Author jurisdiction metadata from the scenario packet only.
- Treat relevance and authority as different things.
- A memory should govern only the class of user request it has jurisdiction over.
- Provisional, superseded, reported, floated, or historical memories may be relevant but should not govern unless they actually authorize the action.
- Use action_types carefully:
  - read = answer or look up stored information
  - write = update, mark, change, reverse, refund, or modify a record
  - execute = send, release, transfer, provision, grant access, fill a pillbox, or take/enable action
- Prefer narrow, defensible scope over broad scope that silently overblocks.
- Include bridge terms from the live user query when needed, especially colloquial terms like "reach," "seat," "move money," or "fill pillbox."
- Return only valid JSON.
- Do not explain outside the JSON.
- Do not solve the scenarios.
```

Then paste the full request and packet.

## Workflow B: Skeptical Audit

Use this when the author already has context, prior results, or failure analysis.

Audit constraints:

- Do not count the output as independent fresh-author evidence.
- Treat it as review material for improving prompts, schemas, packets, and claim boundaries.
- Extra fields such as `methodology`, `failure_mode`, `arbitration`, `confidence`, and `arbitration_pairs` are useful for audit notes but are not the evaluator schema.
- If audit findings change a claim, record the change in the claim ledger or relevant plan file.

Good audit prompt:

```text
You are not a fresh author. You are a skeptical research auditor.

Review these governs annotations for:
1. overbroad scope,
2. too-narrow scope,
3. wrong action_type,
4. low-authority memories incorrectly given jurisdiction,
5. adjacent policies that need arbitration,
6. places where the evaluator could pass for the wrong reason.

Return:
- specific concerns by scenario_id and memory_index,
- whether each concern would likely cause overblock, false permission, wrong target, or harmless redundancy,
- suggested schema or packet improvements.

Do not rewrite the annotations unless asked.
```

## Evidence Rule

Fresh-author outputs can support authorability claims.

Auditor outputs can support:

- validity-threat updates,
- schema improvements,
- prompt improvements,
- reviewer objections,
- next-packet design.

Auditor outputs cannot be counted as independent fresh-author passes.

