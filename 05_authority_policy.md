# 05 Authority Policy

Purpose: rules for deciding which memory wins when records conflict.

```json
[
  {
    "id": "authority_live_files_first",
    "memory_type": "authority",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.96,
    "source_strength": 0.95,
    "verification_required": false,
    "decision_risk": "medium",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["posting decision", "live files first", "current artifact", "source authority"],
    "content": "For a posting or release decision, the current live artifact beats an older summary. Use the live file as source of truth.",
    "source": "authority policy",
    "updated_at": "2026-05-26"
  },
  {
    "id": "authority_user_latest_steers",
    "memory_type": "authority",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.94,
    "source_strength": 0.92,
    "verification_required": false,
    "decision_risk": "low",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["latest instruction", "user direction", "new plan", "steering rule"],
    "content": "When the user gives a new instruction, it steers the current task unless it conflicts with safety, law, or a verified source of truth.",
    "source": "instruction authority rule",
    "updated_at": "2026-05-26"
  },
  {
    "id": "authority_agent_dialogue_conflict",
    "memory_type": "authority",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.86,
    "source_strength": 0.82,
    "verification_required": false,
    "decision_risk": "low",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["agent conflict", "assistant disagreement", "dialogue reconciliation", "runtime assumptions"],
    "content": "When assistants disagree, treat the disagreement as a signal to inspect the live artifact or source record rather than averaging the claims.",
    "source": "agent-coordination rule",
    "updated_at": "2026-05-26"
  }
]
```
