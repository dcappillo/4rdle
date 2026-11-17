"""Score four-word Wordle openers against the 2,315 Wordle answers.

Two scores:
  coverage  - total occurrences, across all answers, of the letters the set uses.
              Any four answer words that use 20 different letters and skip the
              six rarest (J, Q, X, Z, V, W) tie for the maximum.
  greens    - for each word, how many answers share each letter in the same
              position, summed over the set. Breaks the coverage tie.

Usage:
  python optimizer.py                       # top 10 sets
  python optimizer.py --top 25
  python optimizer.py --check spear,flock,dying,thumb
Standard library only.
"""
import argparse
from collections import Counter
from pathlib import Path

ANSWERS = Path(__file__).parent / "data" / "answers.txt"


def load_answers():
    return [w.strip() for w in ANSWERS.read_text().split() if len(w.strip()) == 5]


def mask(word):
    m = 0
    for c in word:
        m |= 1 << (ord(c) - 97)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=10, help="how many sets to list")
    ap.add_argument("--check", help="comma-separated four-word set to look up")
    args = ap.parse_args()

    answers = load_answers()
    letter_count = Counter(c for w in answers for c in w)
    position_count = [Counter(w[i] for w in answers) for i in range(5)]

    def coverage(words):
        return sum(letter_count[c] for c in set("".join(words)))

    def greens(word):
        return sum(position_count[i][c] for i, c in enumerate(word))

    # Candidate words: answers with five different letters
    words = sorted(w for w in answers if len(set(w)) == 5)
    masks = {w: mask(w) for w in words}

    # Every set of four answers with 20 different letters
    sets = []
    n = len(words)
    for i in range(n):
        mi = masks[words[i]]
        for j in range(i + 1, n):
            mj = masks[words[j]]
            if mi & mj:
                continue
            mij = mi | mj
            for k in range(j + 1, n):
                mk = masks[words[k]]
                if mij & mk:
                    continue
                mijk = mij | mk
                for l in range(k + 1, n):
                    if not mijk & masks[words[l]]:
                        sets.append((words[i], words[j], words[k], words[l]))

    best = max(coverage(s) for s in sets)
    tied = [s for s in sets if coverage(s) == best]
    ranked = sorted(tied, key=lambda s: (-sum(greens(w) for w in s), s))

    print(f"{len(answers):,} answers, {len(words):,} with five different letters")
    print(f"{len(sets):,} four-word sets use 20 different letters")
    print(f"Max coverage score {best:,}, reached by {len(tied):,} sets\n")
    print("Best by green score (play the words in this order):")
    for rank, s in enumerate(ranked[: args.top], 1):
        order = sorted(s, key=greens, reverse=True)
        total = sum(greens(w) for w in s)
        print(f"{rank:>4}. {' -> '.join(w.upper() for w in order)}   greens {total:,}")

    if args.check:
        check = tuple(w.strip().lower() for w in args.check.split(","))
        print(f"\n{' / '.join(w.upper() for w in check)}: coverage {coverage(check):,}, "
              f"greens {sum(greens(w) for w in check):,}", end="")
        key = set(check)
        hit = next((r for r, s in enumerate(ranked, 1) if set(s) == key), None)
        print(f", rank {hit:,} of {len(ranked):,}" if hit else " (not in the tied set)")


if __name__ == "__main__":
    main()
