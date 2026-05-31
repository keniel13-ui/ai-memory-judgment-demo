# Article 09 Skeptical Audit Prompt

Use this before posting `ARTICLE_09_AUTHORITY_ARBITRATION_DEV_READY.md`.

First audit pass completed: the title was narrowed, metric definitions were added, and the held-out-packet / one-embedding-model / non-independent-fresh-model caveats were added. Use this prompt again only if a final cold review is needed.

This is an audit pass, not a fresh-author evidence pass.

```text
You are a skeptical technical reviewer. Audit the article below for credibility before publication.

Focus on:
1. overclaims,
2. unsupported causal claims,
3. places where "fresh-authored" may sound stronger than it is,
4. places where "fixed" or "resolved" should be narrowed to "in this packet",
5. missing validity threats,
6. confusing explanation of target-selected vs action-correct,
7. whether the tables support the narrative,
8. whether a credible ML/retrieval researcher would object to the framing.

Return:
- must-fix issues,
- should-fix issues,
- optional wording improvements,
- one paragraph assessing whether the post is credible enough to publish.

Do not rewrite the whole article unless asked.
```
