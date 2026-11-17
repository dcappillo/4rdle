# 4rdle

Find every set of N Wordle words that never repeat a letter. Four words cover 20 letters; five words cover 25 and leave one behind.

It started as a question about my own Wordle opener (LIMPS, COWED, GRAVY, THUNK) and turned into a combinatorics problem: how many four-word sets with 20 different letters exist, and which one is actually best?

**Open index.html in any browser** (no install; runs entirely on your device)

## What it finds

Using the full Wordle word list (12,972 words: the 2,315 answers plus every valid guess):

| Search | Words with 5 different letters | Solutions |
|---|---|---|
| 4 words, 20 different letters | 8,322 | 25,456,119 |
| 5 words, 25 different letters | 8,322 | 11 |

## How it works

1. **Bitmasks.** Each word becomes a 26-bit integer, one bit per letter. Words with a repeated letter are dropped.
2. **Compatibility graph.** Two words can share a set only if their masks have no bits in common (`a & b == 0`). Each word's compatible neighbors are computed once.
3. **Clique search.** Recursively pick N mutually compatible words, OR-ing a running mask so every level prunes its candidates instantly.

Engineering that keeps 25 million results from crashing a browser tab:

- **Web Workers.** The search runs off the main thread, so the page stays responsive.
- **Turbo mode.** Splits the first-word choices across one worker per CPU core. Every worker still gets the full word list, so no cross-chunk combinations are missed.
- **Streaming.** Workers send results in batches of 500 instead of one giant payload.
- **Filter before you search.** Four-word mode counts every solution but only stores the ones matching your filter. Storing all 25 million was what crashed the tab.
- **Virtual scrolling.** Only the rows on screen exist in the page, whatever the result count.

## The opener question

`optimizer.py` scores four-word openers against the 2,315 Wordle answers.

**Coverage** counts how often the set's letters appear across all answers. It turns out to be a blunt instrument: any four answer words that skip the six rarest letters (J, Q, X, Z, V, W) hit the same maximum of **11,094**, and **1,247 sets** tie there. SPEAR, FLOCK, DYING, THUMB is one of them. My original LIMPS, COWED, GRAVY, THUNK scores 10,931 because it spends letters on V and W.

**Greens** breaks the tie: for each word, how many answers have the same letter in the same position. By that measure the best tied set is:

```
PRINT -> BALMY -> SHOCK -> FUDGE    greens 4,047
```

SPEAR, FLOCK, DYING, THUMB ranks 1,172 of the 1,247 (greens 2,985). Its letters are right; their positions mostly aren't (the Y in DYING and the B in THUMB sit where almost no answers put them). LIMPS, COWED, GRAVY, THUNK scores 3,228 greens, better than SPEAR's set, while losing on coverage. Which one you'd rather play depends on whether you want yellows or greens.

I play SPEAR/FLOCK/DYING/THUMB anyway. It speaks to me.

```
python optimizer.py                          # top 10 sets
python optimizer.py --top 25
python optimizer.py --check spear,flock,dying,thumb
```

Python 3.8+, standard library only. Takes about 30 seconds.

## Run it locally

Open `index.html` in any modern browser. That's it.

## Data

Word lists are the original Wordle answer and allowed-guess lists, as packaged in the [`wordle-wordlist`](https://www.npmjs.com/package/wordle-wordlist) npm package. Wordle is owned by The New York Times; this project isn't affiliated with it.
