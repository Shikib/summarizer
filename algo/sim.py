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

    for key, value in ret:
        ret[key] = log(1 / value)

    return ret

def idfs(words):
    """
        Returns a dictionary mapping words to their IDF values.
    """
    # TODO
    ret = { }
    for word in words:
        ret[word] = 1

    return ret

def normalize(dd):
    """
        Normalizes all values of a dictionary.

        Modifies `dd`, returns nothing.
    """
    lo, hi = min(dd.values), max(dd.values)
    for key, value in dd:
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
    
    for word in union:
        # TODO
        pass

def centralities(sentences):
    words = [words(s) for s in sentences]
    freqs = tfs(words)
    ifreqs = idfs(words)
    tfidfs = {}

    for w in words:
        tfidfs[w] = freqs[w] * ifreqs[w]

    for i in range(len()):
        for j in range(i + 1, len(words)):
            pass
            # TODO
