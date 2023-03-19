import logging
import os
from collections import defaultdict
import itertools
import random

# TODO Update constraints
# If we knew that there was an A somewhere, but no other A
# If we find the position, we can move this "allowed" A into the "fixed" category


def is_good_candidate(
    word,
    fixed_letters: dict,
    allowed_letters: list,
    forbidden_letters: list,
    frequencies: dict,  # TODO Add frequency
):
    # Example of edge case : we could have a 'P' in 1st position,
    # another 'P' in `allowed_letters`,
    # and yet another 'P' in `forbidden_letters`,
    # that would rule out the word 'PUPPY'
    # Other case : We tried "TEPEE" and we got Green Green Grey Yellow Grey
    # We can rule out "TENET", because we know that the 4th letter is not an E
    # So we need to remember the position of allowed letters

    # Check frequencies
    for l in set(word):
        # I'm using a set since we don't need to count the letters twice
        if word.count(l) not in frequencies[l]:
            return False
    # Check fixed letters
    if any(word[i] != l for i, l in fixed_letters.items()):
        return False
    # Discard the fixed letters, we already checked them
    trimmed = {i: l for i, l in enumerate(word) if i not in fixed_letters}
    # Check that the other allowed letters are present, but not in the position that we already tried
    for pos, letter in allowed_letters:
        if trimmed[pos] == letter or letter not in trimmed.values():
            return False

    # If we computed the frequencies right, we only have to check that the forbidden
    # letters are not in the specified places
    return all(trimmed[i] != l for i, l in forbidden_letters)


def filter_candidates(
    corpus: list,
    fixed_letters: dict,
    allowed_letters: list,
    forbidden_letters: list,
    frequencies: dict,
):
    """Return a smaller corpus of all the words that fit the given constraints"""
    return [
        w
        for w in corpus
        if is_good_candidate(
            w, fixed_letters, allowed_letters, forbidden_letters, frequencies
        )
    ]


def split_words_by_size(filepath):
    with open(filepath, "r") as fp:
        data = fp.read()
    logging.debug(f"Read {len(data.splitlines())} lines.")
    size_range = range(3, 6)
    split_data = defaultdict(set)
    for word in data.splitlines():
        if len(word) in size_range:
            split_data[len(word)].add(word)
    for n in size_range:
        start, ext = os.path.splitext(filepath)
        with open(f"{start}_{n}{ext}", "w") as file_out:
            file_out.write("\n".join(split_data[n]))


def biggest_corpus(guess, corpus):
    # TODO add fixed_letters, allowed_letters, forbidden_letters:
    word_size = len(guess)
    best_corpus = None
    best_fixed, best_allowed, best_forbidden = None, None, None
    set_indices = list(itertools.product(range(3), repeat=word_size))
    for comb in set_indices:
        # constraints contains [fixed_letters, allowed_letters and forbidden_letters]
        constraints = [dict() for _ in range(3)]
        for i, letter in enumerate(guess):
            constraints[comb[i]][i] = letter
        fixed = constraints[0]
        allowed = list(constraints[1].items())
        forbidden = list(constraints[2].items())
        frequencies = defaultdict(lambda: range(0, len(guess)))
        for letter in set(guess):
            f_min = list(fixed.values()).count(letter)
            f_min += [l for (_, l) in allowed].count(letter)
            if letter in [l for (_, l) in forbidden]:
                f_max = f_min
            else:
                f_max = 5
            frequencies[letter] = range(f_min, f_max + 1)
        filtered_corpus = filter_candidates(
            corpus, fixed, allowed, forbidden, frequencies
        )
        if (
            not best_corpus
            or len(filtered_corpus) > len(best_corpus)
            or (
                len(filtered_corpus) == (len(best_corpus))
                and (len(best_fixed) > len(fixed))
            )
        ):
            best_corpus = filtered_corpus
            best_fixed = fixed
            best_allowed = allowed
            best_forbidden = forbidden
    return best_corpus, best_fixed, best_allowed, best_forbidden


def all_tests():
    # Tests :
    freqs = defaultdict(lambda: range(0, 6))
    # Two fixed letters:
    assert is_good_candidate("tenet", {0: "t", 1: "e"}, [], [], freqs)
    # One allowed letter, not in the word
    assert not is_good_candidate("tenet", {0: "z"}, [], [], freqs)
    # One allowed letter, in the word
    assert is_good_candidate("tenet", {}, [(0, "e")], [], freqs)
    # One allowed letter, in the word but in the wrong place
    # The test should fail because "TENET" cannot have a yellow E in the second position
    assert not is_good_candidate("tenet", {}, [(1, "e")], [], freqs)
    # One fixed letter, that is not repeated
    assert is_good_candidate("tenet", {2: "n"}, [], [(0, "n")], freqs)
    # One forbidden letter, that is in the word
    assert not is_good_candidate("tenet", {}, [], [], {**freqs, "n": range(1)})
    # One fixed E, another E somewhere else, but no other E
    assert is_good_candidate(
        "tenet", {1: "e"}, [(0, "e")], [(4, "e")], {**freqs, "e": range(2, 3)}
    )
    # One fixed E, and the word should not contain another E
    assert not is_good_candidate(
        "tenet", {1: "e"}, [], [(4, "e")], {**freqs, "e": range(1, 2)}
    )  # Tests :
    freqs = defaultdict(lambda: range(0, 6))
    # Two fixed letters:
    assert is_good_candidate("tenet", {0: "t", 1: "e"}, [], [], freqs)
    # One allowed letter, not in the word
    assert not is_good_candidate("tenet", {0: "z"}, [], [], freqs)
    # One allowed letter, in the word
    assert is_good_candidate("tenet", {}, [(0, "e")], [], freqs)
    # One allowed letter, in the word but in the wrong place
    # The test should fail because "TENET" cannot have a yellow E in the second position
    assert not is_good_candidate("tenet", {}, [(1, "e")], [], freqs)
    # One fixed letter, that is not repeated
    assert is_good_candidate("tenet", {2: "n"}, [], [(0, "n")], freqs)
    # One forbidden letter, that is in the word
    assert not is_good_candidate("tenet", {}, [], [], {**freqs, "n": range(1)})
    # One fixed E, another E somewhere else, but no other E
    assert is_good_candidate(
        "tenet", {1: "e"}, [(0, "e")], [(4, "e")], {**freqs, "e": range(2, 3)}
    )
    # One fixed E, and the word should not contain another E
    assert not is_good_candidate(
        "tenet", {1: "e"}, [], [(4, "e")], {**freqs, "e": range(1, 2)}
    )
    # Testing the filtering of corpus
    smol_corpus = ["bled", "sled", "fled"]
    # Checking all words have an L as their 2nd letter
    assert filter_candidates(smol_corpus, {1: "l"}, [], [], freqs) == smol_corpus
    # Checking no words have an L as their 3rd letter
    assert filter_candidates(smol_corpus, {2: "l"}, [], [], freqs) == []
    # Checking only one word starts with a B
    assert filter_candidates(smol_corpus, {0: "b"}, [], [], freqs) == ["bled"]
    # Checking that no word has a B elsewhere
    assert filter_candidates(smol_corpus, dict(), [(0, "b")], [], freqs) == []
    # Checking no words contain a Z
    assert (
        filter_candidates(
            smol_corpus, dict(), [(0, "z")], [], {**freqs, "z": range(1, 6)}
        )
        == []
    )
    # Checking two of the three words do not contain a B as their 2nd letter
    assert filter_candidates(
        smol_corpus, dict(), [], [(1, "b")], {**freqs, "b": range(0, 1)}
    ) == ["sled", "fled"]
    # Checking no word fit the "no E" constraint
    assert (
        filter_candidates(
            smol_corpus, dict(), [], [(1, "e")], {**freqs, "e": range(0, 1)}
        )
        == []
    )


def auto_play(n_letters=3):
    words = []
    with open(f"data/words_en_{n_letters}.txt", "r") as f_in:
        words = f_in.read().splitlines()
    print(f"[Computer] I'm starting with {len(words)} possible words, good luck")
    guess = "TRACE"
    while len(words) > 1:
        print(f"[Player  ] I'm playing: {guess}")
        candidates, fix, allow, forbid = biggest_corpus(guess, words)
        char_green = "🟩"
        char_grey = "⬛"
        char_yellow = "🟨"
        print("[Computer] Result: ", end="")
        for i in range(n_letters):
            if i in fix.keys():
                print(char_green, end="")
            elif i in [x for x, _ in allow]:
                print(char_yellow, end="")
            else:
                print(char_grey, end="")
        print("")
        if len(words) > 1:
            print(f"[Computer] I still have {len(candidates)} choices left.")
        words = candidates
        guess = random.choice(words)
    print("[Computer] Well played...")


def load_corpus(filepath):
    if not os.path.isabs(filepath):
        root = os.path.split(__file__)[0]
        filepath = os.path.join(root, filepath)
    with open(filepath, "r") as fp:
        return fp.read().splitlines()


def play_round(guess, words):
    candidates, fix, allow, forbid = biggest_corpus(guess, words)
    char_green = "🟩"
    char_grey = "⬛"
    char_yellow = "🟨"
    display = ""
    for i in range(len(guess)):
        if i in fix.keys():
            display += char_green
        elif i in [x for x, _ in allow]:
            display += char_yellow
        else:
            display += char_grey
    return display, candidates


def play():
    n_letters = 5
    words = load_corpus(f"data/words_en_{n_letters}.txt")
    print(f"[Computer] I'm starting with {len(words)} possible words, good luck")
    while len(words) > 1:
        guess = input("Your guess: ")
        print(f"[Player  ] I'm playing: {guess}")
        display, words = play_round(guess, words)
        print(f"[Computer] {display}")
        if len(words) > 1:
            print(f"[Computer] I still have {len(words)} choices left.")
    print("[Computer] Well played...")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    all_tests()
    # auto_play(n_letters=5)
    play()

# Good examples : EERIE, TEPEE
# If the word is "EERIE", and we tried "TEPEE", we know that there are 3 'E'
# If we tried "EERIE" and we got Allowed Allowed Forbidden Forbidden Forbidden,
# We know that there are only 2 'E'
# The frequency for an unkown letter is 0-5
# The lower bound is the max number of green+yellow squares we got in a single guess
# The exact frequency is the number of green+yellow squares the moment we got a grey square.
# Therefore, until we get a grey square, we don't know the upper limit of a letter frequency
