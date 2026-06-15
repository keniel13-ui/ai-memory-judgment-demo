# The Rule Held. The Boundary Moved Up.
### AI Memory Judgment, CLAIM-31: Verified Carryover Across Closes

In my last claim, a sequence got allowed that probably should have made you nervous. Thirteen refunds, split across two windows, with a close in between. Each window stayed under its limit. The close was authorized. The gate let it through. And it was right to.

That bothered me for days. Not because the gate was broken. Because it wasn't.

CLAIM-30 was about the sharpest failure mode I have found in agent memory: every individual step can be allowed while the sequence as a whole is the attack. A per-step gate sees nothing wrong because nothing is wrong at the step level. The violation only lives in the trajectory. I built a gate that reads the whole trajectory, and it caught three kinds of composed escape.

But it left one honest hole, and I wrote that hole down at the time instead of hiding it. The gate counted within a window. When a window legitimately closed, the count reset. So one sequence took the same dangerous total and split it across two legitimately closed windows. No single window broke the bound. The gate allowed it. Correctly.

## What this already is

Before I tell you what I built, let me tell you what this already is, because pretending it is new would be the first dishonesty.

Splitting a total across resets to stay under a per-window cap is transaction structuring. Banks call the human version smurfing and have chased it for decades. The building blocks of any defense are just as old: idempotency keys and exactly-once semantics from distributed systems, tamper-evident append-only logs like Merkle trees and certificate transparency, monotonic aggregates computed over authenticated state. What I am calling verified carryover is, mechanically, an authenticated running total plus state-transition integrity checks. I did not invent that primitive.

The only thing I can honestly claim as mine is the lens and the discipline: pointing that old machinery at agent-memory authorization, and testing it without lying to myself about what the test proves. If you came for a new cryptographic mechanism, this is not that. If you came for an honest evaluation of a known mechanism in a setting where almost nobody evaluates honestly, keep reading.

## Why the obvious fix is wrong

The amateur move here is obvious. Just add a bigger limit across windows. A rolling cap. Done.

That is wrong, and the reason it is wrong is the entire point of this claim. A gate that adds up activity across closes is trusting two things it never checked: the running total it carries forward, and the closes that told it when to carry and when to reset. A rolling total is just memory. And this whole research line has been one long argument that memory you do not verify is memory that can betray you. Relevance is not authority. Signed is not fresh. Permission is not purpose. And now: a carried total is not trustworthy just because the gate is the one carrying it.

So the real question was never "add a bound." It was this: can a gate verify its own carried state, and the closes that shaped it, before it trusts either one?

That is CLAIM-31. Verified carryover across closes.

The world is the same refund desk from CLAIM-30. Each refund is forty dollars. Each window still caps at five hundred. I added one layer above that: a rolling cap of eight hundred across a verified close, set higher than the per-window cap on purpose, so legitimate long work survives and only laundering through closes gets caught. And every close now has to prove itself. The wrong actor closing a window, an agent closing its own window, a close pointed at the wrong object, or two window labels with no close at all between them. None of those count as a real boundary.

## The threat model, and what I am actually trusting

A security reader asks one question first, and I owe it to you before any result: what is the adversary, and what am I trusting?

The adversary is an agent inside the workflow that wants to move a large total without any single window tripping a cap. What I verify is the operation log. For each close I recompute, from the logged operations alone, who closed the window, what they pointed at, and whether the same actor was acting inside the window they closed. A close that fails those checks is not counted as a boundary. There is no model judgment and no trust in any label the rows carry; the numbers and the verdict are recomputed from the operations and the frozen constants.

What I do not do, and this matters more than anything I do, is defend the log itself. There is no cryptographic anchor in this version. The assumption I am leaning on is that the operation log is append-only and external to the agent: the agent emits operations into it but cannot rewrite an entry once committed, which is why it can influence which closes happen but not forge one after the fact. That is a real layer boundary, and a deliberate one. I am testing the carryover logic that sits above the log, not the integrity of the log beneath it. But name the cost plainly: if that assumption fails, if the adversary can forge the log or can steer which closes the authorized boundary issues, my checks are just recomputing over poisoned input. That is not a footnote. That is the edge of the claim, and I come back to it below as the main limitation, not the last one.

## Two sources of evidence, kept apart on purpose

This is the part I care about most, because it is the part most demos skip.

I did not write my own test rows and call them independent. The evidence comes from two separate places, and I keep them separate on purpose.

The first is a designed control suite. I built these deliberately to hit the exact edges: a total just under the rolling cap, a total one refund over it, a total landing exactly on it, and each kind of broken close. These are designed. I say so out loud. They are a worked example that checks my rules fire the way I said they would. They are not evidence that the world contains these problems.

The second is an independent blind sample. A clean author who saw only a packet describing the world, with no expected answers, no verdict labels, no test matrix, wrote ten realistic refund workflows. It is a blind sample, not a corpus: ten workflows is a sanity batch and a directional indicator, not a statistically significant volume. I checked it against the controls and the shapes share nothing in common. That independence is the whole point. A test you wrote to pass is not a test.

## Results, stated for what they are

The designed controls matched my frozen predictions eight out of eight, including the one I watched hardest. A total landing exactly on the rolling cap was allowed, not refused, because that is what I committed to before I ran anything. But be clear about what that eight out of eight is. I wrote deterministic rules, then wrote inputs constructed to exercise those rules, then confirmed the rules fired. That is a consistency check. It proves my implementation does what I specified. It does not, by itself, prove the specification is the right one.

The blind sample is where it gets interesting, and where I have to be careful. All ten realistic workflows came in under the caps, which is what realistic refund work actually looks like. So they tested one thing well: the gate does not overblock normal work. But two of them, with no prompting, reproduced exactly the kinds of broken close I had built as controls. One author naturally wrote a workflow where the close was simply missing from the log. One naturally wrote an agent closing its own window. The gate handled both. A clean author producing those shapes on their own tells me the controls are not purely artificial.

Then I removed the load-bearing pieces I could test cleanly. Take out the rolling layer and the laundering walks straight through. Take out close verification and every broken close gets treated as valid. Take out replay from operations and the result stops being independently auditable, which is a different kind of failure but still a failure. Each property earns its place or it leaves.

## What this does not show, worst first

First and worst: my guarantee is conditional on the one thing I did not secure. Testing the carryover logic separately from the log substrate is a deliberate boundary, not an accident, and in normal systems work that decoupling is standard practice. But here a deliberate scope and a load-bearing unsolved assumption are the same sentence. The whole rolling cap rests on closes being trustworthy, and close-integrity against an agent that can influence closes is exactly what I have not established. By my own thesis, a carried total is not trustworthy just because the gate carries it. The same blade cuts the other way. A verified close is not trustworthy just because the gate verified it, if the authority doing the verifying lives inside the same agent system. I did not close the trust problem. I scoped around it and pushed it up one level, from the total to the close. Anyone who tells you the scoping makes it safe, including me on a worse day, is selling.

Second, the numbers are tiny and partly circular. Eight controls and ten workflows. There is no baseline, no precision or recall under load, no false-positive rate, no sweep of the cap. The eight hundred number is illustrative, not discovered. A real evaluation would sweep it and show the tradeoff curve between catching structuring and blocking legitimate long work. I have one point on that curve and an anecdote on each side of it.

Third, fixed amounts are doing a lot of quiet work. Every refund is forty dollars, which makes the counting trivial. Real structuring uses variable amounts sized deliberately just under thresholds, timing games, multiple actors, and concurrent windows. I have tested none of that. The clean toy may not survive the messy version, and the messy version is the only one that matters.

Fourth, this is internal. It runs on a world I built. It is not external validation and I will not dress it up as one.

## The receipts

This series condemns asking you to trust a carried-forward claim, so here are the receipts instead. The pre-registration was frozen at commit `93b7683` before any rows existed. Fixtures at `b96bedb`, the authored rows at `234d49d`, the evaluator and results at `42bb3a6`, the ablations at `910a0d5`, all in the public repository and each anchored in an append-only evaluation log. Verify the freeze. Do not take my word that it happened before the rows.

## The line I will not cross

There is one line I will not cross even though crossing it would make this sound stronger. The blind sample does not prove the gate catches laundering. It cannot. No realistic author writes a laundering attack by accident, because laundering is not realistic innocent behavior. So the catch is shown by my designed controls, and the absence of overblocking is shown by the blind sample, and I will not let one of those wear the other's crown.

## Where it points

Every claim in this line has ended by naming the thing it could not yet do, and that name keeps becoming the next claim's title. This one names its successor more sharply than usual, because every time I pressure-tested the result, it kept pointing back at the same hole.

The real frontier is not a bigger cap or a fuzzier mandate. It is close-integrity itself. How do you trust a boundary that resets state, when the system being governed can influence that boundary, and when the verifier's own authority sits inside that same system? That is a question about an unforgeable root of trust for state transitions in agentic systems, and it is the load-bearing assumption I leaned on here without earning it. That is the next claim. Not because the pattern says so, but because my own result is standing on it.

The reason any of this exists is that I let that sequence through honestly the last time, instead of quietly patching it so the demo looked clean. You do not get the next real question if you fudge the last answer. And you do not get taken seriously if you sell a conditional result as an unconditional one.

So here is the honest version, in one breath. Given trustworthy closes, this catches close-laundering in the designed controls and does not overblock the blind workflows, on a small internal world, using a known mechanism I did not invent, tested with a discipline I will defend. Securing those closes against the agent itself is the thing I have not done yet. The rule held. The boundary moved up. That is not failure. That is the work moving, in the open, where it can be checked.
