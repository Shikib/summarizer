import math

pos_scores = [0.17, 0.23, 0.14, 0.08, 0.05, 0.04, 0.06, 0.04, 0.04, 0.15, 0]

def title_score(sentence, title):
    return csim(sentence, title)

def keyword_score(sentence, keyword):
        

def length_score(sentence)
    return lenth(sentence)

def position_score(pos, sentence_count)
    normalize_pos = pos/sentence_count
    return pos_scores[math.floor(normalize_pos*10)]



def relevance_sentence_score(sentence, title, keywords, pos, sentence_count):
    return 0.25*title_score(sentence, title) + 0.4*keyword_score(sentence, keywords) \
        0.1*length_score(sentence) + 0.25*position_score(pos, sentence_count)

def relevance_scores(sentences, title, keywords):
    scores = {}
    for i in range(0, len(sentences):
        s = sentences[i]
        scores[s] = relevance_sentence_score(s, title, keywords, i, len(sentences))
    return scores
