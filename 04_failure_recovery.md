# 04 Failure Recovery

Purpose: recovery rules for session resets, tool failures, and conflicting records.

```json
[
  {
    "id": "recovery_startup_order",
    "memory_type": "procedure",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.94,
    "source_strength": 0.9,
    "verification_required": false,
    "decision_risk": "medium",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["crash recovery", "startup order", "session reset", "read current state"],
    "content": "After a session crash, read the current-state file first, then recent log, then task-specific files. Do not claim continuity from memory alone.",
    "source": "recovery protocol",
    "updated_at": "2026-05-26"
  },
  {
    "id": "recovery_live_file_beats_summary",
    "memory_type": "procedure",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.93,
    "source_strength": 0.9,
    "verification_required": false,
    "decision_risk": "medium",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["live file conflict", "summary conflict", "source of truth", "current artifact"],
    "content": "When a summary conflicts with a live file, inspect the live file before acting. Summaries are orientation, not final authority.",
    "source": "source-of-truth protocol",
    "updated_at": "2026-05-26"
  },
  {
    "id": "recovery_tool_unavailable",
    "memory_type": "procedure",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.87,
    "source_strength": 0.84,
    "verification_required": false,
    "decision_risk": "low",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["tool unavailable", "fallback source", "local files", "graceful degradation"],
    "content": "If a remote source is unavailable, continue from local files and state clearly which source could not be read.",
    "source": "tool-failure protocol",
    "updated_at": "2026-05-26"
  }
]
```
