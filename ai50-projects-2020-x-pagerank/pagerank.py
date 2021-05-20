import os
import random
import re
import sys

DAMPING = 0.95
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    resDist = {}
    linksInPage = len(corpus[page]) # how many links are in the page

    if linksInPage > 0: #page has links to other pages
        for link in corpus: # for every page in the corpus
            resDist[link] = (1 - damping_factor) / len(corpus) # probability to select the page in random

        for link in corpus[page]: # and in the page itself
            resDist[link] += damping_factor / linksInPage # probability to use a link from the page itself
    else: # page has no links to other pages
        for link in corpus:
            resDist[link] = 1 / len(corpus) # unified distribution

    return resDist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    resDist = {}
    for page in corpus:
        resDist[page] = 0 # we might not calc distribution for each page in the corpus, so initialization is required

    # get the first random page
    randPage = random.choice(list(corpus.keys()))

    # create n X samples
    for i in range(1, n):
        currDist = transition_model(corpus, randPage, damping_factor)

        for page in resDist:
            resDist[page] = ((i - 1) * resDist[page] + currDist[page]) / i

        # get the next random page
        randPage = random.choices(list(resDist.keys()), list(resDist.values()), k=1)[0]

    return resDist

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # start ranking with def distribution values
    ranking = {}
    for i in corpus.keys():
        ranking[i] = 1 / len(corpus)

    runAgain = True
    while runAgain:
        runAgain = False
        for page in list(corpus.keys()):  # calc new ranking for each page
            prevRank = ranking[page]

            # calc SUM PR/NumLinks (sigma part of the function)
            pageRankSum = 0
            for otherPage in list(corpus.keys()):
                if len(corpus[otherPage]) == 0: # for pages with no external links
                    pageRankSum += ranking[otherPage] / len(corpus)

                if page in corpus[otherPage]: # if the otherpage points to the page we`re checking
                    pageRankSum += ranking[otherPage] / len(corpus[otherPage])

            # calc the new page rank using the formula
            ranking[page] = (1-damping_factor) / len(corpus)
            ranking[page] += pageRankSum * damping_factor

            # This process should repeat until no PageRank value changes by more than 0.001 between the current rank values and the new rank values.
            if abs(ranking[page] - prevRank) > 0.001:
                runAgain = True

    return ranking

if __name__ == "__main__":
    main()
