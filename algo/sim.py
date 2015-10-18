import math, string

pos_scores = [0.17, 0.23, 0.14, 0.08, 0.05, 0.04, 0.06, 0.04, 0.04, 0.15, 0]
epsilon = 1e-10


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

idfs = import_idfs("../data/BingBodyDec13_Top100KWords.txt")

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

    #incidence = [[0 for i in range(len(word_lists))] for j in range(len(word_lists))]
    incidence = {}

    for s1 in sentences:
        incidence[s1] = {}
        for s2 in sentences:
            #incidence[i][j] = incidence[j][i] = csim(tfidfs, word_lists[i], word_lists[j])
            incidence[s1][s2] = csim(tfidfs, words(s1), words(s2))

    return incidence

print(centrality_scores(["the dog", "the cat", "the dog and the cat"]))


def title_score(sentence, title):
    return csim(words(sentence), (title))

def keyword_score(sentence, keywords):
    return sbfs(sentence, keywords) * dbfs(sentence, keywords)    


def sbfs(sentence, keywords):
    summ = 0.0
    for w in sentence.split():
        if w in keyword.keys():
             summ += keyword[w]
    
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
        if w in keyword.keys():
            keyword_count += 1
            if not last_index:
                summ += (last_score*keywords[w])/pow(i - last_index)
            last_score = keywords[w]
            last_index = i

    if not keyword_count:
      return 0
    
    if keyword_count == 1:
      return epsilon

    return summ/(keyword_count - 1) 
    
def length_score(sentence):
    return lenth(sentence)

def position_score(pos, sentence_count):
    normalize_pos = pos/sentence_count
    return pos_scores[math.floor(normalize_pos*10)]

def relevance_sentence_score(sentence, title, keywords, pos, sentence_count):
    return 0.25*title_score(sentence, title) + 0.4*keyword_score(sentence, keywords) + \
        0.1*length_score(sentence) + 0.25*position_score(pos, sentence_count)

def relevance_scores(sentences, title, keywords):
    scores = {}
    for i in range(0, len(sentences)):
        s = sentences[i]
        scores[s] = relevance_sentence_score(s, title, keywords, i, len(sentences))
    return scores

def sentences_scores(sentences, title, keywords):
    rscores = relevance_scores(sentences, title, keywords)
    cscores, sim_matrix = centrality_scores(sentences)
    scores = {}
    for s in sentences:
        scores[s] = math.sqrt(rscores[s]*cscores[s])
    return scores, sim_matrix

# find score of k-th best sentence
# looks at [start, end)
def quick_select(scores, k):
    pivot = sentences[0]
    left = []
    right = []
    for score in scores:
        if score < pivot:
            left.append(score)
        else:
            right.append(score)
    if k < len(left):
        return quick_select(left, k)
    elif k > len(left):
        return quick_select(right, k - len(left))
    else:
        return pivot

def select_best(scores, k):
    kth_best = quick_select(scores.values(), k)
    sentences = []
    for s in scores.keys():
        if scores[s] >= kth_best:
            sentences.append(s)

    return sentences
    
def maximal_similarity(s, summary_sentences, sim_matrix):
    maximal = 0.0
    for s2 in summary_sentneces:
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

    del sorted_sentences[max_sent]
    return max_sent
      
def summarize(sentences, title, keywords, summary_size):
    scores, sim_matrix = sentences_scores(sentences, title, keywords)
    sentences = select_best(sentences, summary_size*2)
   
    sorted_sentences = sorted(sentences, key=lambda s: scores[s], reverse=True) 
    
    sum_sentences = []
    for i in range(0, summary_size):
        sum_sentences.append(scores, sorted_sentences, summary_sentences, sim_matrix)

    return sum_sentences
    




