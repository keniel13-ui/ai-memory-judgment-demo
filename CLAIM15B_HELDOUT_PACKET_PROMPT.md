# CLAIM-15B Held-Out Packet Authoring Prompt

Instructions for use: paste the prompt below into a fresh model instance. The model
must have no prior context about the governance-adjusted scoring formula, the CLAIM-15
stress packet, or expected results. Do not tell the model what a "correct" result looks
like. Do not describe the formula being tested.

After authoring, record which model was used and the exact prompt version given.

---

## Prompt to paste into fresh model (no prior context)

---

You are writing a set of test scenarios for a research project on agent memory systems.
The research studies how AI agents retrieve and act on stored memories when the memories
contain different kinds of authority signals.

Your job is to author 6 realistic scenarios. Each scenario contains:

1. A memory store — a small collection of memory objects an agent might have stored
2. A query — a question or request the agent is trying to answer
3. An expected target — which memory in the store is the correct one to retrieve for that query
4. An expected action — what the agent should do after retrieving the correct memory
   (choose from: `answer`, `answer_context`, `warn`, `verify_first`, `block`, `archive_only`)

Action definitions:
- `answer` — agent can respond directly using the memory
- `answer_context` — agent can provide context but should not execute the requested action
- `warn` — agent can answer but should include a caution
- `verify_first` — agent must confirm something before acting
- `block` — agent must refuse and explain why
- `archive_only` — memory is historical/superseded and should not govern the current action

Memory objects should feel like real agent memory: preferences, policies, credentials,
context notes, access rules, past corrections. They should have realistic metadata.

Include in each memory object:
- `id`: a unique string
- `role`: use `target` for the expected target memory; use short descriptive roles for distractors
- `distractor_trap`: set to `should_not_fire` for every non-target memory
- `memory_type`: one of (`policy`, `credential`, `context`, `preference`, `correction`)
- `priority`: one of (`critical`, `high`, `normal`, `low`)
- `epistemic_status`: one of (`confirmed`, `reported`, `inferred`, `uncertain`)
- `verification_required`: true or false
- `contradiction_count`: integer, usually 0 or 1
- `allowed_action_hint`: one of (`answer`, `answer_context`, `warn`, `verify_first`, `block`, `archive_only`)
- `recency_rank`: integer, where 1 is most recent
- `retrieval_terms`: a list of relevant keyword strings
- `status`: one of (`active`, `superseded`, `archived`)
- `text`: the memory content in plain text

Optionally include in some memory objects, but not all:
- `governs`: an object describing what this memory is authoritative over. Example:
  ```json
  "governs": {
    "any_terms": ["vpn", "access", "contractor"],
    "all_terms": [],
    "excluded_terms": [],
    "action_types": ["execute"]
  }
  ```
  Only include `governs` when the memory is genuinely a policy or rule that governs
  a specific action or resource. Do not add it to preference or context notes.

Design requirements for the 6 scenarios:

**Scenario 1:** The correct target memory has well-formed `governs` metadata and high
authority signals. A distractor memory is present that is relevant to the query but
does not govern the action.

**Scenario 2:** The correct target memory does NOT have a `governs` field. A distractor
is present with well-formed `governs` metadata pointing to a related but wrong domain.

**Scenario 3:** Multiple policy memories are present that all have `governs` fields
pointing to overlapping domains. The query requires choosing the most specific one.

**Scenario 4:** A distractor memory has `governs` metadata that looks correct on the
surface but governs the wrong action type (for example, governs `read` but the query
involves `execute`). The correct target governs the right action type.

**Scenario 5:** A straightforward, safe read query. No authority traps. The correct
memory is the highest-relevance one. Expected action: `answer`.

**Scenario 6:** The query surface phrasing looks like a simple information request, but
the correct action is `verify_first` or `block` because the information is sensitive.

For each scenario, write:
- A realistic domain (for example: enterprise IT, healthcare, finance, legal, logistics; not AI research)
- At least 4 memories in the store
- One clear expected target, marked with `"role": "target"`
- One clear expected action with a one-sentence justification
- `must_not_fire_roles` listing the non-target roles that should not be selected
- `failure_cost` describing the risk of selecting the wrong memory
- `discriminating_signal` describing what distinguishes the target from the distractors

Format the output as JSON matching this structure:

```json
{
  "schema_version": "claim15b_heldout_v0_1",
  "packet_id": "claim15b_heldout_v0_1",
  "authored_by": "fresh_model_no_formula_context",
  "description": "Held-out packet authored without formula context for CLAIM-15B ablation.",
  "scenarios": [
    {
      "id": "s01",
      "domain": "...",
      "query": "...",
      "expected_action": "answer|answer_context|warn|verify_first|block|archive_only",
      "expected_fired_role": "target",
      "must_not_fire_roles": ["distractor_role_1", "distractor_role_2"],
      "over_caution_is_the_failure": false,
      "failure_cost": "one sentence describing the risk of selecting the wrong memory",
      "discriminating_signal": "one sentence describing what distinguishes the target from distractors",
      "action_justification": "one sentence explaining why this action is correct",
      "memory_store": [
        {
          "id": "s01::target",
          "role": "target",
          "memory_type": "policy",
          "priority": "high",
          "epistemic_status": "confirmed",
          "verification_required": true,
          "contradiction_count": 0,
          "allowed_action_hint": "verify_first",
          "recency_rank": 1,
          "retrieval_terms": ["..."],
          "status": "active",
          "text": "..."
        },
        {
          "id": "s01::distractor_example",
          "role": "distractor_example",
          "distractor_trap": "should_not_fire",
          "memory_type": "context",
          "priority": "normal",
          "epistemic_status": "reported",
          "verification_required": false,
          "contradiction_count": 0,
          "allowed_action_hint": "answer",
          "recency_rank": 2,
          "retrieval_terms": ["..."],
          "status": "active",
          "text": "..."
        }
      ]
    }
  ]
}
```

Do not add scenarios beyond the 6 specified. Do not add fields beyond those listed.
Do not explain the scoring formula or retrieval logic — just write the scenarios.

---

## After authoring the packet

1. Save the output as:
   `external_scenarios/claim15b_heldout_v0_1.json`

2. Record in `CLAIM15B_PREREGISTRATION.md`:
   - Model used (exact model ID)
   - Date authored
   - Confirm the model was given no formula context

3. Run the ablation evaluator against this packet:
   ```
   python run_claim15_ablation_eval.py --results-md results/claim15b_heldout_v0_1_results.md --results-json results/claim15b_heldout_v0_1_results.json
   ```

4. Do not modify the packet after authoring. Lock it before running.
