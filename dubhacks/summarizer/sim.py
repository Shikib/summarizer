import math, string
import re
import numpy as np
from scipy.sparse import csc_matrix

pos_scores = [0.17, 0.23, 0.14, 0.08, 0.05, 0.04, 0.06, 0.04, 0.04, 0.15, 0]
epsilon = 1e-10

def page_rank(G, s = .85, maxerr = .001):
    """
    Computes the pagerank for each of the n states.
    Used in webpage ranking and text summarization using unweighted
    or weighted transitions respectively.
    Args
    ----------
    G: matrix representing state transitions
       Gij can be a boolean or non negative real number representing the
       transition weight from state i to j.
    Kwargs
    ----------
    s: probability of following a transition. 1-s probability of teleporting
       to another state. Defaults to 0.85
    maxerr: if the sum of pageranks between iterations is bellow this we will
            have converged. Defaults to 0.001
    """
    n = len(G[0])
    
    for i in range(0, len(G)):
        column = G[i]
        summ = sum(column)
        for j in range(0, len(G)):
            if not sum:
                column[j] /= summ              
        

    # transform G into markov matrix M
    M = csc_matrix(G,dtype=np.float)
    rsums = np.array(M.sum(1))[:,0]
    ri, ci = M.nonzero()
    M.data /= rsums[ri]

    # bool array of sink states
    sink = rsums==0

    # Compute pagerank r until we converge
    ro, r = np.zeros(n), np.ones(n)
    while np.sum(np.abs(r-ro)) > maxerr:
        ro = r.copy()
        # calculate each pagerank at a time
        for i in range(0,n):
            # inlinks of state i
            Ii = np.array(M[:,i].todense())[:,0]
            # account for sink states
            Si = sink / float(n)
            # account for teleportation to state i
            Ti = np.ones(n) / float(n)

            r[i] = ro.dot( Ii*s + Si*s + Ti*(1-s) )

    # return normalized pagerank
    return r/sum(r)



def import_idfs(filename):
    """
        Imports a dictionary of IDFs from a list of words sorted by inverse frequency.
    """
    ret = { }
    with open(filename) as f:
        i = 1
        for line in f.readlines():
            # Discard newline
            ret[line[:-1]] = i
            i += 1

    for key, value in ret.items():
        ret[key] = value / i

    return ret

idfs = import_idfs("dubhacks/summarizer/data-files/BingBodyDec13_Top100KWords.txt")

def tfs(words):
    """
        Returns a dictionary mapping words to their TF values.
    """
    ret = { }
    for word in words:
        if word in ret:
            ret[word] += 1
        else:
            ret[word] = 1

    return ret

def normalize(dd):
    """
        Normalizes all values of a dictionary.

        Modifies `dd`, returns nothing.
    """
    lo, hi = min(dd.values), max(dd.values)
    for key, value in dd.items():
        dd[key] = (value - lo) / (hi - lo)

def words(sentence):
    """
        Tokenizes a sentence.
        Returns a list of lowercase words containing no punctuation.
    """
    return "".join(e for e in sentence if e not in string.punctuation).lower().split()

def csim(tfidfs, a, b):
    """
        Cosine similarity of two lists of words `a` and `b`.
        
        Returns a float.
    """
    union = set()
    union.update(a)
    union.update(b)
    
    dot = 0
    alen = 0
    blen = 0
    for word in union:
        dot += tfidfs[word] * tfidfs[word] if (word in a and word in b) else 0
        alen += tfidfs[word] * tfidfs[word] if (word in a) else 0
        blen += tfidfs[word] * tfidfs[word] if (word in b) else 0

    norm = math.sqrt(alen) * math.sqrt(blen)

    return dot / norm if norm > 0 else 0

def centrality_scores(sentences):
    word_lists = [words(s) for s in sentences]
    freqs = tfs([i for l in word_lists for i in l]) # flatten word list
    tfidfs = { }

    for w in freqs.keys():
        tfidfs[w] = freqs[w] * (idfs[w] if w in idfs else 1)

    matrix = [[0 for i in range(len(word_lists))] for j in range(len(word_lists))]
    incidence = {}
    
   
    for i in range(0, len(sentences)):
        s1 = sentences[i]
        incidence[s1] = {}
        for j in range(0, len(sentences)):
            s2 = sentences[j]
            matrix[i][j] = csim(tfidfs, word_lists[i], word_lists[j])
            incidence[s1][s2] = csim(tfidfs, words(s1), words(s2))
           
    
    print(incidence)
    pagerank_scores = page_rank(matrix)

    scores = {}
    for i in range(0, len(sentences)):
        s = sentences[i]
        scores[s] = pagerank_scores[i]    
 
    return scores, incidence



def title_score(sentence, title):
    word_lists = [words(s) for s in [sentence, title]]
    tfidfs = { }
    freqs = tfs([i for l in word_lists for i in l]) # flatten word list
    
    for w in freqs.keys():
        tfidfs[w] = freqs[w] * (idfs[w] if w in idfs else 1)

    print(csim(tfidfs, words(sentence), words(title)))
    return csim(tfidfs, words(sentence), words(title))
   

def keyword_score(sentence, keywords):
    return sbfs(sentence, keywords) * dbfs(sentence, keywords)    


def sbfs(sentence, keywords):
    if not sentence:
        return 0.0    

    summ = 0.0
    for w in sentence.split():
        if w in keywords.keys():
             summ += keywords[w]
    
    return summ/len(sentence)
    
# keyword scores normalized between 0 and 1
def dbfs(sentence, keywords):
    keyword_count = 0
    summ = 0.0
    last_score = 0.0
    last_index = 0
    words = sentence.split()
    for i in range(0, len(words)):
        w = words[i]
        if w in keywords.keys():
            keyword_count += 1
            # THIS WILL NEVER HAPPEN BUT DJANGO PLS
            if not last_index and i != last_index:
                summ += (last_score*keywords[w])/pow(i - last_index, 2)
            last_score = keywords[w]
            last_index = i

    if not keyword_count:
      return 0
    
    if keyword_count == 1:
      return epsilon

    return summ/(keyword_count - 1) 
    
def length_score(sentence):
    ideal = 20
    word_count = len(words(sentence))
    return abs(ideal - word_count)/ideal

def position_score(pos, sentence_count):
    normalize_pos = pos/sentence_count
    return pos_scores[math.floor(normalize_pos*10)]

def relevance_sentence_score(sentence, title, keywords, pos, sentence_count):
    score = 0.25*title_score(sentence, title) + 0.4*keyword_score(sentence, keywords) + \
        0.1*length_score(sentence) + 0.25*position_score(pos, sentence_count)
    if not len(keywords):
        return score / 0.6

def relevance_scores(sentences, title, keywords):
    scores = {}
    for i in range(0, len(sentences)):
        s = sentences[i]
        scores[s] = relevance_sentence_score(s, title, keywords, i, len(sentences))
    return scores

def scale(cscores, rscores):
    maxr = max(list(rscores.values()))
    maxc = max(list(cscores.values()))
    for key in cscores.keys():
        cscores[key] *= (maxr/maxc)
    return cscores
    

def sentences_scores(sentences, title, keywords):
    rscores = relevance_scores(sentences, title, keywords)
    cscores, sim_matrix = centrality_scores(sentences)
    csores = scale(cscores, rscores)

    scores = {}
    for s in sentences:
        scores[s] = math.sqrt(rscores[s]*cscores[s])
    return scores, sim_matrix

# find score of k-th best sentence
# looks at [start, end)
def quick_select(scores, k):
    pivot = scores[0]
    left = []
    right = []
    for score in scores:
        if score < pivot:
            left.append(score)
        elif score > pivot:
            right.append(score)

    if k < len(left):
        return quick_select(left, k)
    elif k > len(left):
        return quick_select(right, k - len(left) - 1)
    else:
        return pivot

def select_best(scores, k):
    kth_best = quick_select(list(scores.values()), k)
    sentences = []
    for s in scores.keys():
        if scores[s] >= kth_best:
            sentences.append(s)

    return sentences
    
def maximal_similarity(s, summary_sentences, sim_matrix):
    maximal = 0.0
    for s2 in summary_sentences:
        maximal = max(maximal, sim_matrix[s][s2])

    return maximal

def maximal_marginal_relevance(scores, sorted_sentences, summary_sentences, sim_matrix):   
    lambd = 0.6
    max_score = 0.0
    max_sent = None
    for s in sorted_sentences:
        score = lambd*scores[s] - (1-lambd)*maximal_similarity(s, summary_sentences, sim_matrix)
        if score > max_score:
            max_score = score
            max_sent = s

    if max_sent:
        sorted_sentences.remove(max_sent)

    return max_sent
      
def summarize(sentences, title, keywords, summary_size):
    if summary_size >= len(sentences):    
        return sentences

    print ("in summary!")
    print ("titles: ", title)
    print ("keywords", keywords)
    scores, sim_matrix = sentences_scores(sentences, title, keywords)
    print("scentences!")
   
    print("sorting")
    sorted_sentences = sorted(sentences, key=lambda s: scores[s], reverse=True)[0:2*summary_size]
    
    sum_sentences = []
    for i in range(0, summary_size):
        best_sent = maximal_marginal_relevance(scores, sorted_sentences, sum_sentences, sim_matrix)
        if best_sent:
            sum_sentences.append(best_sent)

    return sum_sentences
