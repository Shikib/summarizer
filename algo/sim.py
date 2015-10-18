import math

def import_idfs(filename):
    """
        Imports a dictionary of IDFs from a list of words sorted by inverse frequency.
    """
    ret = { }
    with open(filename) as f:
        i = 0
        for line in f.readlines():
            # Discard newline
            ret[line[:-1]] = i
            i += 1

    for key, value in ret.items():
        ret[key] = value / i

    return ret

idfs = import_idfs("data/BingBodyDec13_Top100KWords.txt")

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

    for key, value in ret.items():
        ret[key] = log(1 / value)

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
    return sentence.translate(string.maketrans("", ""), string.punctuation).lower().split()

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

    return dot / (math.sqrt(alen) * math.sqrt(blen))
        

def centralities(sentences):
    words = [words(s) for s in sentences]
    freqs = tfs(words)
    tfidfs = { }

    for w in words:
        tfidfs[w] = freqs[w] * idfs[w]

    for i in range(len()):
        for j in range(i + 1, len(words)):
            pass
            # TODO

pos_scores = [0.17, 0.23, 0.14, 0.08, 0.05, 0.04, 0.06, 0.04, 0.04, 0.15, 0]
epsilon = 1e-10


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
    words = sentence.split():
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
