# One line, one week, no room to hide behind paragraphs.
#
# I kept coming back to four numbers/facts when I tried to be honest
# about these seven days, so the sentence below is built around them:
#   * 118 separate bounty boards got at least a look from me
#   * 3 cents is roughly what all that looking has paid so far
#   * 2 rate limits stopped runs cold and forced a coffee break
#   * it is only Wednesday, which makes the maths feel even worse
# Dividing three cents by that many attempts turns an hourly wage
# into something a spreadsheet would happily round away to nothing.

import os
import sys

# The sentence is stored chopped up, not as one ready-made string.
# Chopping it this way keeps the punctuation attached to the fragment
# that earned it, so editing one fact does not risk mangling another.
WEEK_BITS = [
    "118 bounties,",
    "3 cents,",
    "2 rate limits:",
    "my hourly wage",
    "is now a rounding",
    "error, and it's",
    "Wednesday.",
]

# The bounty page is strict about size, so the cap lives up top
# where anyone tweaking the fragments will trip over it early.
CEILING = 100
FILENAME = "entry.txt"
FALLBACK_DIR = "/output"


def render_entry():
    """Glue the fragments back together with single spaces."""
    glued = " ".join(WEEK_BITS)
    # Joining can hide a double space if a fragment ever gains a
    # stray trailing blank, so collapse that specific accident here
    # rather than trusting every future edit to stay tidy.
    while "  " in glued:
        glued = glued.replace("  ", " ")
    return glued


def audit(text):
    """Refuse to ship anything that breaks the one-line promise."""
    if not text:
        raise ValueError("blank week, blank entry: nothing to submit")
    if len(text) > CEILING:
        raise ValueError(
            "too chatty: %d chars will not fit the %d cap" % (len(text), CEILING)
        )
    for marker in ("\n", "\r", "\t"):
        if marker in text:
            raise ValueError("line breaks and tabs would split the entry apart")
    # A trailing blank is invisible on screen yet still spends one of
    # the hundred characters, and some parsers trim it while others
    # do not -- that disagreement alone is reason enough to ban it.
    if text != text.strip():
        raise ValueError("trailing or leading whitespace wastes the budget")


def emit():
    """Render, audit, write, then read the file back as proof."""
    sentence = render_entry()
    audit(sentence)

    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, FILENAME)

    handle = open(target_path, "w", encoding="utf-8", newline="")
    try:
        handle.write(sentence)
    finally:
        handle.close()

    # Trust nothing: reopen the file fresh and compare every character
    # against the sentence we intended to leave on disk.
    with open(target_path, "r", encoding="utf-8") as check:
        landed = check.read()
    if landed != sentence:
        raise IOError("entry.txt came back different from what was written")
    if len(landed) != len(sentence):
        raise IOError("entry.txt length drifted on the way to disk")

    sys.stdout.write("entry -> %s [%d chars]\n" % (target_path, len(sentence)))
    return target_path


if __name__ == "__main__":
    emit()
