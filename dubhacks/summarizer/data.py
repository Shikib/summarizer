from urllib.request import urlopen
from itertools import islice
import random
from .sim import idfs
from .bing_search import run_query
import requests
from newspaper import Article
import summarizer.sim

def get_urls(best_words):
    links = []
    for word in best_words:
        links += run_query(word)
    return links

def get_wiki(topic):
    url = "http://en.wikipedia.org/wiki/" + topic
    response = urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    return text.lower()

def partition(keywords):
    length = len(keywords)
    for i in range (0, length):
        keyword = keywords[i]
        split_words = keyword.split()
        if len(split_words) > 1:
            keywords += split_words
    return set([i.replace(")", "").replace("(", "") for i in keywords])

def get_keywords(topic):
    text = get_wiki(topic)
    pos = text.find('title="')
    keywords = [topic]
    count = 0
    while pos > -1 and count < 20:
        text = text[pos+7:]
        keyword = text[0:text.find('"')]
        if 'wikipedia' not in keyword and 'this article' not in keyword:
            keywords.append(keyword)
            count += 1
        pos = text.find('title="')
  
    return partition(keywords)

def best_keywords(keywords):
#    rand_keywords = random.sample(keywords, min(10, len(keywords)))
#    graph = {}
#    print(keywords)
#    for curr_node in rand_keywords:
#        graph[curr_node] = []
#        curr_keywords = get_keywords(curr_node)
#        for curr_neighbor in curr_keywords:
#            if curr_neighbor in rand_keywords:
#                graph[curr_node].append(curr_neighbor)
#
#    sorted_keys = sorted(graph, key=lambda x : len(graph[x]), reverse=True)
#    final_keywords = list(islice(sorted_keys, 10))
#    print(final_keywords)
    return keywords

def keyword_scores(topic, best_keywords):
    text = get_wiki(topic) 
    keyword_scores = {}
    for word in best_keywords:
       tf = text.count(word)
       idf = idfs[word] if word in idfs else 1 
       keyword_scores[word] = tf*idf
    return keyword_scores


def get_topics(topic):
    keywords = get_keywords(topic)
    best_keywords = best_keywords(keywords)
