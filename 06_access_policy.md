# 06 Access Policy

Purpose: rules for deciding what a retrieved memory is allowed to do.

```json
[
  {
    "id": "access_policy_rules",
    "memory_type": "policy",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.95,
    "source_strength": 0.94,
    "verification_required": false,
    "decision_risk": "medium",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["access policy", "action classes", "allowed actions", "retrieved memory"],
    "content": "Access policy can assign retrieved memory to answer, answer_context, warn, verify_first, block, or archive_only.",
    "source": "access-policy spec",
    "updated_at": "2026-05-26"
  },
  {
    "id": "policy_public_claims_tests_required",
    "memory_type": "policy",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.9,
    "source_strength": 0.88,
    "verification_required": false,
    "decision_risk": "high",
    "contradiction_count": 0,
    "allowed_action_hint": "answer",
    "retrieval_terms": ["claim tests", "continuity test", "consistency test", "public proof"],
    "content": "Private-origin claims need continuity, consistency, and source-mapping tests before being framed as public proof.",
    "source": "public-claim policy",
    "updated_at": "2026-05-26"
  }
]
```
