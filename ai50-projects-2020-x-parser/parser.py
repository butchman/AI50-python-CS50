import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to" | "until"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S P S | VP
NP -> N | Det N | Det AP NP | NP PP
VP -> V | V NP | V NP PP | V PP | Adv VP | VP Adv
PP -> P NP
AP -> Adj | Adj AP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    wl2 = []
    # get the lower words
    wl1 = nltk.word_tokenize(sentence.lower())
    # Go through all the words
    for word in wl1:
        # check if word contains any alpha character
        if any(c.isalpha() for c in word):
            wl2.append(word)
    return wl2


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    NPChunkList = []
    for subtree in tree.subtrees():
        if subtree.label() == "NP":
            # check if this subtree has any subtree which is NP
            if not subTreeHasNP(subtree):
                NPChunkList.append(subtree)

    return NPChunkList

def subTreeHasNP(subTree):
    # check the sutrees of subtree we passed, but skip the subtree itself (since it was NP and that is why we got here...)
    for subtree in next(subTree.subtrees()):
        # if subtree is NP, we cant use the father subtree (which was also NP)
        if subtree.label() == "NP":
            return True
    # the subtree we're checking doesnt have any NP subtrees
    return False

if __name__ == "__main__":
    main()
