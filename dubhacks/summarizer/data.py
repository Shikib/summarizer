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

def get_keywords(topic):
    plcontinue = None
    cont = True
    keywords = []

    try:
        while cont:
            r = requests.get("https://en.wikipedia.org/w/api.php?action=query&prop=links&format=json&titles=" + topic + \
                    "&pllimit=500&redirects" + (("&plcontinue=" + plcontinue) if plcontinue else ""))

            json = r.json()

            for link in next(iter(json["query"]["pages"].values()))["links"]:
                keywords.append(link["title"])

            cont = "continue" in json
            plcontinue = json["continue"]["plcontinue"] if "continue" in json else None

        return keywords
    except:
        return []

def best_keywords(keywords):
    rand_keywords = random.sample(keywords, min(10, len(keywords)))
    graph = {}
    print(keywords)
    for curr_node in rand_keywords:
        graph[curr_node] = []
        curr_keywords = get_keywords(curr_node)
        for curr_neighbor in curr_keywords:
            if curr_neighbor in rand_keywords:
                graph[curr_node].append(curr_neighbor)

    sorted_keys = sorted(graph, key=lambda x : len(graph[x]), reverse=True)
    final_keywords = list(islice(sorted_keys, 5))
    print(final_keywords)
    return final_keywords

def keyword_scores(topic, best_keywords):
    url = "http://en.wikipedia.org/wiki/" + topic    
    response = urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    keyword_scores = {}
    for word in best_keywords:
       tf = text.count(word)
       idf = idfs[word] if word in idfs else 1 
       keyword_scores[word] = tf*idf
    return keyword_scores


def get_topics(topic):
    keywords = get_keywords(topic)
    best_keywords = best_keywords(keywords)
    

