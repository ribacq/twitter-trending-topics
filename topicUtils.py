#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# Twitter trending topics analysis
# Topic utilities module
#
# Written by Quentin Ribac
# April 2018

import json
import sys

# utils
tweetCount = lambda topic: sum([tweet['occurrences'] for tweet in topic['tweets']])

# human readable summary of topics
def summary(topics, totalTweetCount, COSINE_SIM_THRESHOLD, MIN_TOPIC_SIZE):
    # sort topics by tweet count
    topics = sortByTweetCount(topics)

    # write summary to string
    tweetsKept = sum([tweetCount(topic) for topic in topics])
    ret = 'topics: ' + str(len(topics)) + ', tweets kept: ' + str(tweetsKept) + '/' + str(totalTweetCount) + ' (' + str(tweetsKept * 100 / totalTweetCount) + '%)\n'
    ret += 'θcs: ' + str(COSINE_SIM_THRESHOLD) + ', min size: ' + str(MIN_TOPIC_SIZE) + '\n'
    ret += '======\n'
    for i, topic in enumerate(topics):
        topic['terms'] = dict(sorted(topic['terms'].items(), key = lambda x: x[1], reverse = True)[:8])
        ret += 'Topic ' + str(i + 1) + ': ' + str(tweetCount(topic)) + ' tweets\n'
        ret += 'Terms: ' + ' '.join([term for (term, tfidf) in topic['terms'].items()]) + '\n'
        ret += 'Views: ' + str(topic['views']) + '\n'
        for tweet in sorted(topic['tweets'], key = lambda t: t['occurrences'], reverse = True):
            ret += '(' + str(tweet['occurrences']) + 'x)>>> ' + tweet['text'] + '\n'
        ret += '\n'
    ret += '======\n'
    ret += 'topics: ' + str(len(topics)) + ', tweets kept: ' + str(tweetsKept) + '/' + str(totalTweetCount) + ' (' + str(tweetsKept * 100 / totalTweetCount) + '%)\n'
    ret += 'θcs: ' + str(COSINE_SIM_THRESHOLD) + ', min size: ' + str(MIN_TOPIC_SIZE) + '\n'
    return ret

# topics sorting criteria
def sortByTFIDF(topics):
    return sorted(topics, key = lambda topic: sum(topic['terms'].values()), reverse = True)

def sortByViews(topics):
    return sorted(topics, key = lambda topic: topic['views'], reverse = True)

def sortByTweetCount(topics):
    return sorted(topics, key = tweetCount, reverse = True)

# print data CSV from json file
def json2csv(topics = [], secs = 0, headersOnly = False, MIN_TOPIC_SIZE = 5):
    # field helpers
    fieldHelpers = {
        'topicID': lambda topic: topics.index(topic),
        'secs': lambda topic: secs,
        'tweetCount': tweetCount,
        'singleTweetCount': lambda topic: len(topic['tweets']),
        'views': lambda topic: topic['views'],
        'avgViews': lambda topic: '%.2f' % (topic['views'] / tweetCount(topic)),
        'maxViews': lambda topic: max([t['user']['followers_count'] for t in topic['tweets']]),
        'tfidf': lambda topic: sum(topic['terms'].values()),
        'avgTfidf': lambda topic: '%.2f' % (sum(topic['terms'].values()) / tweetCount(topic)),
        'URLsCount': lambda topic: sum([len(t['entities']['urls']) for t in topic['tweets'] if 'urls' in t['entities']]),
        'avgURLsCount': lambda topic: '%.2f' % (sum([len(t['entities']['urls']) for t in topic['tweets'] if 'urls' in t['entities']]) / tweetCount(topic)),
        'avgMediaCount': lambda topic: '%.2f' % (
            sum(
                [
                    len(t['entities']['media'] if 'media' in t['entities'] else [])
                    + len(t['extended_entities']['media'] if 'extended_entities' in t and 'media' in t['extended_entities'] else [])
                    for t in topic['tweets']
                ]
            ) / tweetCount(topic)
        ),
        'retweets': lambda topic: sum([t['retweet_count'] * t['occurrences'] for t in topic['tweets']]),
        'avgRetweets': lambda topic: '%.2f' % (sum([t['retweet_count'] * t['occurrences'] for t in topic['tweets']]) / tweetCount(topic)),
        'favorites': lambda topic: sum([t['favorite_count'] * t['occurrences'] for t in topic['tweets']]),
        'avgFavorites': lambda topic: '%.2f' % (sum([t['favorite_count'] * t['occurrences'] for t in topic['tweets']]) / tweetCount(topic)),
        'sentiment': lambda topic: sum([t['sentiment'] for t in topic['tweets']]),
        'avgSentiment': lambda topic: '%.2f' % (sum([t['sentiment'] for t in topic['tweets']]) / tweetCount(topic)),
        'absSentiment': lambda topic: sum([abs(t['sentiment']) for t in topic['tweets']]),
        'minSentiment': lambda topic: min([t['sentiment'] / t['occurrences'] for t in topic['tweets']]),
        'maxSentiment': lambda topic: max([t['sentiment'] / t['occurrences'] for t in topic['tweets']]),
        'nsr': lambda topic: '%.2f' % (
            (
                sum([t['occurrences'] for t in topic['tweets'] if t['sentiment'] > 1 * t['occurrences']])
                - sum([t['occurrences'] for t in topic['tweets'] if t['sentiment'] < -1 * t['occurrences']])
            ) / tweetCount(topic)
        ),
        'positiveCount': lambda topic: sum([t['occurrences'] for t in topic['tweets'] if t['sentiment'] > 1]),
        'negativeCount': lambda topic: sum([t['occurrences'] for t in topic['tweets'] if t['sentiment'] < -1]),
        'neutralCount': lambda topic: sum([t['occurrences'] for t in topic['tweets'] if t['sentiment'] <= 1 and t['sentiment'] >= -1]),
    }

    # in case we only want the headers line
    if headersOnly:
        return '\t'.join(fieldHelpers.keys()) + '\n'

    # if we want the content
    ret = ''
    for topic in topics:
        if tweetCount(topic) >= MIN_TOPIC_SIZE:
            for i, fh in enumerate(fieldHelpers.values()):
                if i >= 1:
                    ret += '\t'
                ret += str(fh(topic))
            ret += '\n'
    return ret

if __name__ == '__main__':
    d = '../../tweets/newsEN-20180508'
    for i in range(41):
        topics = []
        with open('%s/json/filtered/filtered%02d.json' % (d, i), 'r', encoding = 'utf-8') as f:
            for line in f:
                topics.append(json.loads(line))
        with open('%s/topics/filtered/stats%02d.csv' % (d, i), 'w+', encoding = 'utf-8') as f:
            f.write(json2csv(headersOnly = True) + '\n')
            f.write(json2csv(topics = topics) + '\n')
