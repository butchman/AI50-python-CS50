from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(AKnight, AKnave), # Rule #1 : A could be a Knight or a Knave
    Not(And(AKnight, AKnave)), # Rule #2 : A cannot be a Knight And also a Knave
    Implication(AKnight, And(AKnight, AKnave)), # A is Knight = tells truth -> A is also a Knave
    Implication(AKnave,Not(And(AKnight,AKnave))) # A is a Knave = lies -> he's not a Knight and a Knave
)
# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnight, AKnave), # Rule #1 : A could be a Knight or a Knave
    Not(And(AKnight, AKnave)), # Rule #2 : A cannot be a Knight And also a Knave
    Or(BKnight, BKnave), # Rule #1 : B could be a Knight or a Knave
    Not(And(BKnight, BKnave)), # Rule #2 : B cannot be a Knight And also a Knave
    Implication(AKnight, And(AKnave, BKnave)), # A is Knight = tells truth -> A and B are Knaves
    Implication(AKnave,Not(And(AKnave, BKnave))) # A is Knave = lies -> A and B are not a Knight and a Knave
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave), # Rule #1 : A could be a Knight or a Knave
    Not(And(AKnight, AKnave)), # Rule #2 : A cannot be a Knight And also a Knave
    Or(BKnight, BKnave), # Rule #1 : B could be a Knight or a Knave
    Not(And(BKnight, BKnave)), # Rule #2 : B cannot be a Knight And also a Knave
    Implication(AKnight, Or(And(AKnight, BKnight),And(AKnave, BKnave))), # A is Knight = tells truth -> A and B are the same (both knights or both knaves)
    Implication(AKnave,Not(Or(And(AKnight, BKnight),And(AKnave, BKnave)))), # A is Knave, = lies -> A and B are NOT the same (not both knights and not both knaves)
    Implication(BKnight,Or(And(BKnight,AKnave),And(BKnave,AKnight))), # B is knight = truth -> A and B are different (one knight and one knave)
    Implication(BKnave,Not(Or(And(BKnight,AKnave),And(BKnave,AKnight)))) # B is knave = lies -> A and b are not different (not one knight and one nave)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave), # Rule #1 : A could be a Knight or a Knave
    Not(And(AKnight, AKnave)), # Rule #2 : A cannot be a Knight And also a Knave
    Or(BKnight, BKnave), # Rule #1 : B could be a Knight or a Knave
    Not(And(BKnight, BKnave)), # Rule #2 : B cannot be a Knight And also a Knave
    Or(CKnight, CKnave), # Rule #1 : C could be a Knight or a Knave
    Not(And(CKnight, CKnave)), # Rule #2 : C cannot be a Knight And also a Knave
    Implication(BKnight,Implication(AKnight,AKnave)), # B is knight = tells truth -> A said he's a knave. If A is knight, then A tells the truth -> A is knave
    Implication(BKnight,Implication(AKnave,AKnight)), # B is knight = tells truth -> A said he's a knave. If A is knave, then A lies -> A is knight
    # if B is a knave, we cant tell anything about what he lies (maybe he didn't talk about A at all...)
    Implication(BKnight,CKnave), # B is knight = tells truth -> C is knave
    Implication(BKnave,CKnight), # B is knave = lies -> C is Knight
    Implication(CKnight,AKnight), # C is Knight = tells truth -> A is Knight
    Implication(CKnave,AKnave), # C is knave = lies -> A is knave
)

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
