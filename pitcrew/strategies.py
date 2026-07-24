"""Seed strategies (32 of them; a race uses the first n_bays). Each bay gets a different one so the swarm explores
genuinely different optimisations instead of writing the same patch thirty times.

Mock mode ignores these (its patches are pre-written). Fireworks mode puts each
one in the prompt as the angle that bay should try. A couple are deliberately
weak, so the leaderboard has a believable tail instead of thirty identical wins.
"""

STRATEGIES = [
    "replace the linear membership scan with a hash set built once",
    "precompute the index as a set before the loop, then O(1) lookups",
    "use str.join instead of repeated string concatenation for the label",
    "sort the result exactly once instead of repeatedly",
    "combine the set lookup and single sort into one pass",
    "hoist every loop-invariant computation out of the hot loop",
    "build the id set once and join tags in a comprehension",
    "avoid rebuilding intermediate lists; iterate lazily where possible",
    "use a dict/set for membership and a single sort key",
    "minimise per-row dict copying while keeping every field",
    "short-circuit rows that cannot match before doing any work",
    "replace the inner comprehension with a precomputed lookup structure",
    "use ''.join for labels and remove the redundant sort passes",
    "cache the index lookup and sort once with a stable key",
    "reduce allocations in the hot path without changing behaviour",
    "profile the three costs and fix the dominant one first",
    "convert the membership test to set containment",
    "eliminate the triple sort, keep a single reverse sort",
    "use comprehensions to cut interpreter overhead in the loop",
    "batch the tag join and avoid quadratic concatenation",
    "index the lookup, join the tags, sort once, touch nothing else",
    "prefer built-in sort over manual repeated sorting",
    "remove work that produces the same result every iteration",
    "set membership plus a single pass to build the output",
    "keep it simple: one set, one join, one sort",
    "optimise for the common case where most rows do not match",
    "avoid list comprehension inside the loop condition",
    "precompute, then filter, then label, then sort once",
    "cut the algorithmic complexity from O(n*m) to O(n)",
    "the smallest correct change that removes the biggest cost",
]


def for_bay(bay: int) -> str:
    return STRATEGIES[(bay - 1) % len(STRATEGIES)]
