import csv
import itertools
import sys
from math import prod as product

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


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probsToMultiply = []
    childProb = 0
    
    """
        ONE GENE FUNCTIONALITY
        loop over people who have one bad gene
    """
    for person in one_gene:
        if people[person]["mother"] == None and people[person]["father"] == None:

            if person in have_trait:
                probsToMultiply.append(PROBS['gene'][1] * PROBS['trait'][1][True])
            else:
                probsToMultiply.append(PROBS['gene'][1] * PROBS['trait'][1][False])
            
        else:
            # get parents
            mom = people[person]["mother"]
            dad = people[person]['father']
            # calc prob of getting one bad gene from mom
            if mom in one_gene:
                momTemp = (.5 * (1 - PROBS["mutation"])) + (.5 * PROBS["mutation"])
            elif mom in two_genes:
                momTemp = 1 - PROBS["mutation"]
            else:
                momTemp = PROBS["mutation"]
            # calc prob of getting one bad gene from dad
            if dad in one_gene:
                dadTemp = (.5 * (1 - PROBS["mutation"])) + (.5 * PROBS["mutation"])
            elif dad in two_genes:
                dadTemp = 1 - PROBS["mutation"]
            else:
                dadTemp = PROBS["mutation"]
                
            # calc prob of getting one bad gene from mom OR dad (mom and not dad | dad and not mom)
            childProb = momTemp * (1 - dadTemp) + dadTemp * (1 - momTemp)
            # calc trait prob 
            if person in have_trait:
                childProb = childProb * PROBS['trait'][1][True]
            else: 
                childProb = childProb * PROBS['trait'][1][False]
            # append prob to multiply array
            probsToMultiply.append(childProb)


    for person in two_genes:
        
        if people[person]["mother"] == None and people[person]["father"] == None:
            if person in have_trait:
                probsToMultiply.append(PROBS['gene'][2] * PROBS['trait'][2][True])
            else:
                probsToMultiply.append(PROBS['gene'][2] * PROBS['trait'][2][False])
            
        else:
            mom = people[person]["mother"]
            dad = people[person]['father']   
            # since we have two genes we will be getting one bad gene from each parent 
            if mom in one_gene:
                momTemp = (.5 * (1 - PROBS["mutation"])) + (.5 * PROBS["mutation"])
            elif mom in two_genes:
                momTemp = 1 - PROBS["mutation"]
            else:
                momTemp = PROBS["mutation"]
                
            # calc prob of getting one bad gene from dad   
            if dad in one_gene:
                dadTemp = (.5 * (1 - PROBS["mutation"])) + (.5 * PROBS["mutation"])
            elif dad in two_genes:
                dadTemp = 1 - PROBS["mutation"]
            else:
                dadTemp = PROBS["mutation"]
            # we will need to multiply the prob of getting one bad gene from mom AND one bad gene from dad since we have two genes 
            childProb = momTemp * dadTemp
            # calc trait prob
            if person in have_trait:
                childProb = childProb * PROBS['trait'][2][True]
            else: 
                childProb = childProb * PROBS['trait'][2][False]
            # append prob to multiply array
            probsToMultiply.append(childProb)

        
    for person in people:
        if person not in one_gene and person not in two_genes:
            
            # no parents we just calc the prob of having no gene and trait or no gene no trait 
            if people[person]["mother"] == None and people[person]["father"] == None:
                if person in have_trait:
                    probsToMultiply.append(PROBS['gene'][0] * PROBS['trait'][0][True])
                else:
                    probsToMultiply.append(PROBS['gene'][0] * PROBS['trait'][0][False])
        
            else:
                # has parents but did inherit a bad gene from either parent
                mom = people[person]["mother"]
                dad = people[person]['father']
                
                # we will want to get the prob in each case where we do not pass down a x gene 
                if mom in one_gene:
                    momTemp = (.5 * (1 - PROBS["mutation"])) + (.5 * PROBS["mutation"])
                    pass
                elif mom in two_genes:
                    momTemp = PROBS["mutation"]
                else:
                    momTemp = 1 - PROBS["mutation"]
                    
                # calc prob of getting no bad genes from dad   
                if dad in one_gene:
                    # this will be the prob of o staying o and the prob of the 1 x gene mutating to a o gene
                    dadTemp = (.5 * (1 - PROBS["mutation"])) + (.5 * PROBS["mutation"])
                    pass
                elif dad in two_genes:
                    dadTemp = PROBS["mutation"]
                else:
                    dadTemp = 1 - PROBS["mutation"]
                    
                # we will want to get the prob of not mom and not dad and mult them together
                
                childProb = momTemp * dadTemp
                
                if person in have_trait:
                    childProb = childProb * PROBS['trait'][0][True]
                else:
                    childProb = childProb * PROBS['trait'][0][False]
                
                probsToMultiply.append(childProb)
    return product(probsToMultiply)
        
                    

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
            
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Each persons 1 gene 2 gene and 0 gene prob should sum to 1 and maintain the same proportions
    # Each persons trait prob should sum to 1 and maintain the same proportions
    # Loop over each person in probabilities and normalize each persons gene and trait probs
    for person in probabilities:
        # gene scaling 
        geneTotal = sum(probabilities[person]['gene'].values())
        sf = 1 / geneTotal
        for gene in probabilities[person]['gene']:
            probabilities[person]['gene'][gene] *= sf    
        # trait scaling
        traitTotal = sum(probabilities[person]['trait'].values())
        sf = 1 / traitTotal
        for trait in probabilities[person]['trait']:
            probabilities[person]['trait'][trait] *= sf
    


if __name__ == "__main__":
    main()
