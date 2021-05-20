import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def calcGeneProb(geneCount, motherGeneCount, fatherGeneCount):

    # person will get half of genes from each parent (according to their genes)
    probFromMother = motherGeneCount / 2
    probFromFather = fatherGeneCount / 2

    # calc mutation probability
    if geneCount == 0:
        # if person has no genes, he can only have the trait if he gets it from mutated parent genes
        notFromMother = (probFromMother * PROBS["mutation"] + (1 - probFromMother) * (1 - PROBS["mutation"]))
        notFromFather = (probFromFather * PROBS["mutation"] + (1 - probFromFather) * (1 - PROBS["mutation"]))
        return notFromMother * notFromFather

    if geneCount == 1:
        # probability of one "no gene" mutating into "trait" gene
        notFromMother = (probFromMother * PROBS["mutation"] + (1 - probFromMother) * (1 - PROBS["mutation"]))
        notFromFather = (probFromFather * PROBS["mutation"] + (1 - probFromFather) * (1 - PROBS["mutation"]))

        # probability of one "trait gene" mutating into "no trait gene"
        FromMother = (probFromMother * (1 - PROBS["mutation"]) + (1 - probFromMother) * PROBS["mutation"])
        FromFather = (probFromFather * (1 - PROBS["mutation"]) + (1 - probFromFather) * PROBS["mutation"])

        return notFromMother * FromFather + notFromFather * FromMother

    if geneCount == 2:
        # probability of "trait gene" mutating into "no trait gene"
        FromMother = (probFromMother * (1 - PROBS["mutation"]) + (1 - probFromMother) * PROBS["mutation"])
        FromFather = (probFromFather * (1 - PROBS["mutation"]) + (1 - probFromFather) * PROBS["mutation"])
        return FromFather * FromMother

    return 0

def joint_probability(people, one_gene, two_genes, have_trait):

    jointProb = 1
    for person in people:

        # count the genes for the person
        geneCount = 0
        if person in one_gene:
            geneCount = 1
        elif person in two_genes:
            geneCount = 2

        # check the trait
        hasTrait = False
        if person in have_trait:
            hasTrait = True

        if people[person]["mother"] is None: #if mother is None, father is also None - according to the specification
            probGene = PROBS["gene"][geneCount] # no parents details, so take the matching PROBS data
        else:
            # check parents data
            mother = people[person]["mother"]
            father = people[person]["father"]

            motherGeneCount = 0
            if mother in one_gene:
                motherGeneCount = 1
            elif mother in two_genes:
                motherGeneCount = 2

            fatherGeneCount = 0
            if father in one_gene:
                fatherGeneCount = 1
            elif father in two_genes:
                fatherGeneCount = 2

            # calc the probability, based on person genes + parents genes (and mutations)
            probGene = calcGeneProb(geneCount, motherGeneCount, fatherGeneCount)

        # get the trait probability (it has nothing to do with parents trait)
        probTrait = PROBS["trait"][geneCount][hasTrait]

        jointProb *= probGene * probTrait

    return jointProb

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        # count the genes for the person
        geneCount = 0
        if person in one_gene:
            geneCount = 1
        elif person in two_genes:
            geneCount = 2

        # check the trait
        hasTrait = False
        if person in have_trait:
            hasTrait = True

        # update the probabilities
        probabilities[person]["gene"][geneCount] += p
        probabilities[person]["trait"][hasTrait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        # normalize the "gene"
        geneSum = probabilities[person]["gene"][0] + probabilities[person]["gene"][1] + probabilities[person]["gene"][2]
        for i in range(3):
            probabilities[person]["gene"][i] /= geneSum

        # normalize the "trait"
        traitSum = probabilities[person]["trait"][True] + probabilities[person]["trait"][False]
        probabilities[person]["trait"][True] /= traitSum
        probabilities[person]["trait"][False] /= traitSum

if __name__ == "__main__":
    main()
