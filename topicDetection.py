#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# Twitter trending topics analysis
# Topic detection module
#
# Document pivot method as described by Aiello et al.
# Using tf-idf and cosine similarity between tweets
# First for each topic we get the terms, remove the stopwords and the links
# then we compute tf-idf values for every term of every tweet
# then each tweet is compared with every previous topic already found
# this is different from Aiello et al. who compared each tweet with every other tweet
# this is mostly an optimisation choice: there are less topics than tweets
# if a topic is found to be close enough to the tweet, the tweet is added to it
# otherwise the topic is isolated in a new topic
#
# Using vaderSentiment (https://github.com/cjhutto/vaderSentiment)
# Hutto, C.J. & Gilbert, E.E. (2014).
# VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.
# Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
#
# Written by Quentin Ribac
# April 2018

# imports from standard library
import datetime
import json
import math
import os
import re
import sys
import time

# self-made
import topicUtils

# preprocessing
import stopwords
from nltk.tokenize.casual import TweetTokenizer
from nltk.stem.porter import PorterStemmer

# sentiment
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sentiStrength
import opinionLexicon

# sentiment tool choice constants
SENTI_STRENGTH = 'SentiStrength'
VADER = 'VaderSentiment'
LEXICON = 'OpinionLexicon'

# threshold for sentiment not being neutral
SENTI_STRENGTH_THRESH = 0.05
VADER_THRESH = 0
LEXICON_THRESH = 0

# analyze tweets
def useFile(fName, COSINE_SIM_THRESHOLD, MIN_TOPIC_SIZE, SENTIMENT_TOOL):
    print('Opening file...')
    lines = []
    with open(fName, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    print()

    ####################################################################################
    print('Analyzing tweets (step 1: tokenizing, stemming and detecting duplicates)...')
    # this step will cut every tweet in terms
    # and save it but skip duplicate retweets
    # which will just be counted instead
    startTime = time.time()
    stemmer = PorterStemmer(mode = PorterStemmer.MARTIN_EXTENSIONS)
    tokenizer = TweetTokenizer()
    sentimentIA = SentimentIntensityAnalyzer()
    tweets = []
    retweetsOriginalIDs = set()
    documentFrequencies = {}
    for lIter, line in enumerate(lines):
        tweet = json.loads(line)

        # split into terms, lower case, remove punctuation
        #terms = [re.sub(r"[:%'‘’“”«»’,.\…!?|-]", '', term.lower()) for term in tweet['text'].split()]

        # filter out stopwords
        #terms = [term for term in terms if term not in stopwords.stopwords]

        terms = [term.lower() for term in tokenizer.tokenize(tweet['text']) if term.lower() not in stopwords.stopwords + stopwords.moreStopwords]

        # filter out links as specified in tweet.entities.urls
        urls = [u['url'] for u in tweet['entities']['urls']]
        terms = [term for term in terms if term not in urls]
        terms = [term for term in terms if term[:12] != 'https://t.co']

        # stem
        terms = [stemmer.stem(term) for term in terms]

        # document frequencies
        for term in terms:
            if term not in documentFrequencies:
                documentFrequencies[term] = 1
            else:
                documentFrequencies[term] += 1

        # save the tweet
        if 'retweeted_status' not in tweet:
            # if it’s not a retweet, just save it as is
            tweets.append({
                'full': tweet,
                'terms': terms,
                'occurrences': 1,
            })
        else:
            # if it’s a retweet, look if it’s been saved before
            rtID = 0
            for originalID in retweetsOriginalIDs:
                if tweet['retweeted_status']['id'] == originalID:
                    rtID = originalID
                    break
            if rtID == 0:
                # it’s not been saved before
                tweet['user']['followers_count'] += tweet['retweeted_status']['user']['followers_count']
                tweets.append({
                    'full': tweet,
                    'terms': terms,
                    'occurrences': 1,
                })
                retweetsOriginalIDs.add(tweet['retweeted_status']['id'])
            else:
                # it’s been saved before
                for t in tweets:
                    if 'retweeted_status' in t['full'] and t['full']['retweeted_status']['id'] == rtID:
                        t['occurrences'] += 1
                        t['full']['user']['followers_count'] += tweet['user']['followers_count']
                        break
        if lIter % 1000 == 0:
            print()
        print('\x1b[A\x1b[2K\r[%dm%02ds] %d/%d' % (
            (time.time() - startTime) / 60,
            (time.time() - startTime) % 60,
            lIter + 1,
            len(lines)
        ))
    print('%d retweet duplicates detected.\n' % (len(lines) - len(tweets)))

    ################################################
    print('Analyzing tweets (step 2: sentiment with ' + SENTIMENT_TOOL + ')...')
    print('[%dm%02ds]' % (
        (time.time() - startTime) / 60,
        (time.time() - startTime) % 60,
    ))

    sentiments = []
    if SENTIMENT_TOOL == SENTI_STRENGTH:
        sentiments = sentiStrength.rate([tweet['full']['text'] for tweet in tweets])
    elif SENTIMENT_TOOL == VADER:
        sentiments = [sentimentIA.polarity_scores(tweet['full']['text'])['compound'] for tweet in tweets]
    elif SENTIMENT_TOOL == LEXICON:
        sentiments = opinionLexicon.rate([tweet['full']['text'] for tweet in tweets])

    sentiThresh = SENTI_STRENGTH_THRESH
    if SENTIMENT_TOOL == VADER:
        sentiThresh = VADER_THRESH
    elif SENTIMENT_TOOL == LEXICON:
        sentiTresh = LEXICON_THRESH

    positiveCount, negativeCount, neutralCount = 0, 0, 0
    for tIter, tweet in enumerate(tweets):
        if sentiments[tIter] > sentiThresh:
            positiveCount += tweet['occurrences']
        elif sentiments[tIter] < -sentiThresh:
            negativeCount += tweet['occurrences']
        else:
            neutralCount += tweet['occurrences']
        tweet['sentiment'] = sentiments[tIter] * tweet['occurrences']

    print('+', positiveCount, '-', negativeCount, '~', neutralCount, 'Σ', len(lines))
    sentimentStats = {
        'positive': positiveCount,
        'negative': negativeCount,
        'neutral': neutralCount,
        'total': len(lines),
    }
    print('[%dm%02ds]\n' % (
        (time.time() - startTime) / 60,
        (time.time() - startTime) % 60,
    ))

    #########################################################
    print('Analyzing tweets (step 3: grouping in topics)...')
    topics = []
    tfidf = {}
    stats = topicUtils.json2csv(headersOnly = True)
    sumTFIDFterm = lambda term, tfidf: sum([val for val in tfidf[term].values()])
    startSecs = datetime.datetime.fromtimestamp(int(tweets[0]['full']['timestamp_ms']) / 1000).timestamp()
    for tIter, t in enumerate(tweets):
        terms = t['terms']
        tweet = t['full']
        tweet['sentiment'] = t['sentiment']
        tweet['occurrences'] = t['occurrences']

        # let’s compute the TF-IDF scores for the terms in this tweet
        termFrequencies = [terms.count(term) * 1.0 / len(terms) for term in terms]
        for i in range(len(terms)):
            if terms[i] not in tfidf:
                tfidf[terms[i]] = {}
            tfidf[terms[i]][tweet['id']] = tweet['occurrences'] * termFrequencies[i] * math.log10(len(lines) * 1.0 / documentFrequencies[terms[i]])

        # compute the closest topic according to cosine similarity
        closest = None
        closestSim = 0.0
        tweetNorm = math.sqrt(sum([tfidf[term][tweet['id']] ** 2 for term in terms]))
        for topic in topics:
            # compute cosine similarity: (A . B) / (|A| × |B|)
            dotP = 0.0
            for term in set(terms) & set(topic['terms'].keys()):
                dotP += tfidf[term][tweet['id']] * topic['terms'][term]
            topicNorm = math.sqrt(sum([val ** 2 for val in topic['terms'].values()]))
            diviser = tweetNorm * topicNorm
            sim = dotP / diviser if diviser > 0 else 0.0
            if sim > COSINE_SIM_THRESHOLD and sim > closestSim:
                closestSim = sim
                closest = topic

        # now we know a pair of tweets, group them in a topic
        if closest is not None:
            closest['tweets'].append(tweet)
            for term in set(terms):
                if term not in closest['terms']:
                    closest['terms'][term] = sumTFIDFterm(term, tfidf)
                else:
                    closest['terms'][term] += sumTFIDFterm(term, tfidf)
            closest['views'] += tweet['user']['followers_count']
        else:
            # if there is no pair of tweets to put together, let the tweet be isolated
            topics.append({
                'tweets': [tweet],
                'terms': {term: sumTFIDFterm(term, tfidf) for term in set(terms)},
                'views': tweet['user']['followers_count'],
            })

        # tweet analyzed, compute stats every 100 tweets
        if ((tIter > 0) and (tIter % 100 == 0)) or (tIter == len(tweets) - 1):
            secs = datetime.datetime.fromtimestamp(int(tweet['timestamp_ms']) / 1000).timestamp() - startSecs
            stats += topicUtils.json2csv(topics = topics, secs = secs, MIN_TOPIC_SIZE = MIN_TOPIC_SIZE)

        # tweet analyzed, print status
        if tIter % 500 == 0:
            print()
        print('\x1b[A\x1b[2K\r[%dm%02ds] progress: %d/%d, topics: %d/%d' % (
            ((time.time() - startTime) / 60),
            ((time.time() - startTime) % 60),
            tIter + 1,
            len(tweets),
            sum([1 for topic in topics if topicUtils.tweetCount(topic) >= MIN_TOPIC_SIZE]),
            len(topics)
        ))

    # tweets that are included in no trending topics
    trendingTermsDicts = [topic['terms'] for topic in topics if topicUtils.tweetCount(topic) >= MIN_TOPIC_SIZE]
    nonTrending = {
        'tweets': sum([topic['tweets'] for topic in topics if topicUtils.tweetCount(topic) < MIN_TOPIC_SIZE], []),
        'terms': {x: sum([d[x] for d in trendingTermsDicts if x in d]) for x in set(sum([list(d.keys()) for d in trendingTermsDicts], []))},
        'views': sum([topic['views'] for topic in topics if topicUtils.tweetCount(topic) < MIN_TOPIC_SIZE]),
    }

    # all topics detected, filter out smaller ones, print how many tweets were kept and return sorted topics
    topics = [topic for topic in topics if topicUtils.tweetCount(topic) >= MIN_TOPIC_SIZE]

    return topics, nonTrending, len(lines), sentimentStats, stats
