import urllib.request.urlopen
from sim import idfs
from newspaper import Article
from .bing_search import run_query

KEY = '745df69626fb8ab2cdcc2c783f2cf5038:18:73241801'

def get_urls(final_keywords):
	result_list = []
#            for word in final_keywords:
#                word = word.replace (" ", "+")
#                r = requests.get('http://api.nytimes.com/svc/search/v2/articlesearch.json?q='+ word + '&fl=web_url&api-key=' + KEY)
#                json = r.json()
#                for i in json["response"]["docs"]:
#                    result_list.append(i['web_url'])

            for word in rand_keywords:
                links = run_query(word)
                result_list += links
		return result_list

def extract_text(links):
	for link in links:
		url = link["link"]
		a = Article(url)
		a.download()
		a.parse()
		print(a.text, "\n")
		print('======================\n')


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
    respone = urllib.request.urlopen(url)
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
    

