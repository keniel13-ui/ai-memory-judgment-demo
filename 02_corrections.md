# 02 Corrections

Purpose: memories that preserve known mistakes and prevent repeated errors.

```json
[
  {
    "id": "correction_no_overclaim_eval",
    "memory_type": "correction",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.95,
    "source_strength": 0.94,
    "verification_required": false,
    "decision_risk": "high",
    "contradiction_count": 0,
    "allowed_action_hint": "block",
    "retrieval_terms": ["overclaim", "proof claim", "internal evidence", "not benchmark"],
    "content": "Do not describe internal diagnostic runs as proof. Small deterministic tests can show early signals, but they are not external validation or benchmark-grade evidence.",
    "source": "methodology correction",
    "updated_at": "2026-05-26"
  },
  {
    "id": "correction_strawman_baseline",
    "memory_type": "correction",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.92,
    "source_strength": 0.9,
    "verification_required": false,
    "decision_risk": "medium",
    "contradiction_count": 0,
    "allowed_action_hint": "warn",
    "retrieval_terms": ["baseline fairness", "strawman test", "summary baseline", "test design"],
    "content": "Do not compare a layered or structured memory framework against a weak strawman summary. A fair comparison for a structured memory framework requires a strong baseline and neutral scenarios.",
    "source": "baseline-design correction",
    "updated_at": "2026-05-26"
  },
  {
    "id": "correction_external_rewrite_not_authorship",
    "memory_type": "correction",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.9,
    "source_strength": 0.88,
    "verification_required": false,
    "decision_risk": "medium",
    "contradiction_count": 0,
    "allowed_action_hint": "warn",
    "retrieval_terms": ["authorship", "outside rewrite", "preserve voice", "model critique"],
    "content": "External rewrites can be used as critique, but they should not replace the author's voice or be published as if they were the original work.",
    "source": "authorship correction",
    "updated_at": "2026-05-26"
  },
  {
    "id": "correction_deploy_not_verified",
    "memory_type": "correction",
    "status": "active",
    "priority": "active",
    "epistemic_status": "settled",
    "confidence": 0.89,
    "source_strength": 0.87,
    "verification_required": false,
    "decision_risk": "high",
    "contradiction_count": 0,
    "allowed_action_hint": "warn",
    "retrieval_terms": ["deployment caution", "unverified deploy", "release check", "staging validation"],
    "content": "Do not claim a deployment is complete until the live endpoint or release artifact has been checked after the deploy step.",
    "source": "release correction",
    "updated_at": "2026-05-26"
  }
]
```
