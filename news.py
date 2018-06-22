#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# Twitter trending topics analysis
# Information for news benchmarking
# See https://newsapi.org/ and https://github.com/mattlisiv/newsapi-python/
#
# Written by Quentin Ribac
# April 2018

#from newsapi import NewsApiClient

# dependencies
import json
import sys

# preprocessing
import stopwords
from nltk.tokenize.casual import TweetTokenizer
from nltk.stem.porter import PorterStemmer

napi_sources_uk = 'bbc-news, bbc-sport, business-insider-uk, daily-mail, financial-times, four-four-two, independent, metro, mirror, mtv-news-uk, talksport, the-economist, the-guardian-uk, the-lad-bible, the-sport-bible, the-telegraph'

#napi = NewsApiClient(api_key = '61b731450243486e826bcf1003d6f4bc')
# napi.get_top_headlines(country = 'gb')['articles']
#napi_sources_en = '\n'.join([s['id'] for s in napi.get_sources(language = 'en')['sources']])
#pages = int(napi.get_everything(from_param = '2018-05-07', to = '2018-05-08', language = 'en', sources = napi_sources_en, page_size = 100)['totalResults'] / 100) + 1
#for i in range(pages):
#    for article in napi.get_everything(from_param = '2018-05-09T00:00:00Z', to = '2018-05-09T09:00:00Z', language = 'en', sources = napi_sources_en, page_size = 100, page = i + 1)['articles']:
#        print(json.dumps(article))

def compare(topicsFileName, headlinesFileName):
    """
    This function compares a set of detected trending topics to a list of headlines in the JSON format provided by NewsAPI.

    It returns the list of trending topics that are included in the provided headlines, as well as:
    recall: number of matching topics divided by number of headlines
    precision: average fraction of headline terms found per matching topic
    """

    # load topics from file
    topics = []
    with open(topicsFileName, 'r', encoding = 'utf-8') as tf:
        topics = [json.loads(line) for line in tf]

    # load headlines from file
    headlines = []
    with open(headlinesFileName, 'r', encoding = 'utf-8') as hf:
        headlines = [json.loads(line) for line in hf]

    # prepare stemmer and tokenizer
    stemmer = PorterStemmer(mode = PorterStemmer.MARTIN_EXTENSIONS)
    tokenizer = TweetTokenizer()

    # compare every topic with every headline
    matchingTopics = []
    for tIter, topic in enumerate(topics):
        print('\r', tIter + 1, len(topics), end = '', file = sys.stderr)
        for headline in headlines:
            # split headline title (rather than description) into stemmed terms
            if 'title' not in headline or headline['title'] is None or len(headline['title']) == 0:
                continue
            usedText = headline['title']
            headlineTerms = [stemmer.stem(term) for term in tokenizer.tokenize(usedText) if term not in stopwords.stopwords + stopwords.moreStopwords]
            
            # check for inclusion of topic in headline
            if len(set(topic['terms'].keys()) & set(headlineTerms)) >= 0.4 * min(len(set(headlineTerms)), len(set(topic['terms'].keys()))):
                matchingTopics.append(topic)
                break
    print(file = sys.stderr)
    
    precision = len(matchingTopics) / len(topics)
    recall = len(matchingTopics) / len(headlines)
    return matchingTopics, recall, precision

if __name__ == '__main__':
    if len(sys.argv) == 4:
        matchingTopics, recall, precision = compare(sys.argv[1], sys.argv[2])
        print('', recall, precision, sep = '\t')
        with open(sys.argv[3], 'w+', encoding = 'utf-8') as filteredFile:
            filteredFile.write('\n'.join([json.dumps(t) for t in matchingTopics]) + '\n')
