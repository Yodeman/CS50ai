import os
import random
import re
import sys
import math

DAMPING = 0.85
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
    pages_to_visit = corpus[page]
    if len(pages_to_visit)==0:
        initial_prob = (1-damping_factor)/len(corpus.keys())
        probab = ((damping_factor/len(corpus.keys()))+initial_prob)
        return {k:probab for k in corpus.keys()}
    else:
        initial_prob = (1-damping_factor)/(1+len(pages_to_visit))
        probab = damping_factor/len(pages_to_visit)
        d = {k:probab+initial_prob for k in pages_to_visit}
        d.update({page:initial_prob})
        return d


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = random.choice(list(corpus.keys()))
    pages = {k:0 for k in corpus.keys()}
    m = n
    while m:
        pages[page] += 1
        distribution = transition_model(corpus, page, damping_factor)
        #if len(set(probab.values()))==1:
        #    page = random.choice(list(probab.keys()))
        #elif len(set(probab.values()))==2:
        #    pages_to_visit = list(probab.keys()).remove(page)
        #    page = random.choice(pages_to_visit)
        variables,scores = zip(*distribution.items())
        page = random.choices(population=variables, weights=scores, k=1)[0]
        m -= 1
    return {k:v/n for k,v in pages.items()}

#def recur_iterative_algo(page_rank, new_rank, corpus, damping_factor):
#    rank = page_rank
#    for page in page_rank:
#        total = 0.0
#        for possible_page in corpus:
#            if page in corpus[possible_page]:
#                total += page_rank[possible_page]/len(corpus[possible_page])
#            elif not corpus[possible_page]:
#                total += page_rank[possible_page]/len(corpus)
#        new_rank[page] = ((1-damping_factor)/len(page_rank) + (damping_factor*total))
#    for page in page_rank:
#        if not math.isclose(new_rank[page], page_rank[page], abs_tol=0.001):
#            rank = recur_iterative_algo(new_rank, {}, corpus, damping_factor)
#    return rank

def iterative_algo(page_rank, new_rank, corpus, damping_factor):
    repeat = True
    while repeat:
        for page in page_rank:
            total = 0.0
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    total += page_rank[possible_page]/len(corpus[possible_page])
                elif not corpus[possible_page]:
                    total += page_rank[possible_page]/len(corpus)
            new_rank[page] = ((1-damping_factor)/len(page_rank) + (damping_factor*total))
        repeat = False
        for page in page_rank:
            if not math.isclose(new_rank[page], page_rank[page], abs_tol=0.001):
                repeat = True
                page_rank[page] = new_rank[page]
    return page_rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #from time import perf_counter
    page_rank = {k:1/len(corpus.keys()) for k in corpus.keys()}
    #start = perf_counter()
    #new_rank = recur_iterative_algo(page_rank, {}, corpus, damping_factor)
    #print(new_rank)
    #print("recur completed in: %0.4f" %(perf_counter()-start))
    #return new_rank
    #start = perf_counter()
    new_rank = iterative_algo(page_rank, {}, corpus, damping_factor)
    return new_rank

if __name__ == "__main__":
    main()
