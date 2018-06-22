#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# Tweet retrieval script
#
# Written by Quentin Ribac
# April 2018

# dependencies
import datetime
import json
from newsSourcesENTT import english_sources_twitter
import sys
from twitterApiHandle import api

# English news
def news(screen_names = english_sources_twitter, date = datetime.date.today().isoformat()):
    tweetCount = 0
    print(file = sys.stderr)
    for screen_name in screen_names:
        for status in api.GetSearch(term = 'from:' + str(screen_name), until = date, count = 100) + api.GetSearch(term = 'from:' + str(screen_name), since = date, count = 100):
            tweet = json.loads(str(status))
            tweet['entities'] = {'urls': tweet['urls']}
            del tweet['urls']
            yield tweet
            tweetCount += 1
            print('\x1b[A\x1b[2K\r' + str(tweetCount), file = sys.stderr)

# live stream
def filter(track = [], follow = [], limit = 3000, englishOnly = True, keepRT = True):
    tweetCount = 0
    s = None
    if len(track) == 0 and len(follow) == 0:
        s = api.GetStreamSample()
    else:
        if englishOnly:
            s = api.GetStreamFilter(track = track, follow = follow, languages = ['en'])
        else:
            s = api.GetStreamFilter(track = track, follow = follow)
    
    print(file = sys.stderr)
    for message in s:
        # if we are done
        if limit > 0 and tweetCount >= limit:
            break

        # only keep tweets
        if 'text' not in message:
            continue

        # only keep tweets in English
        if englishOnly and message['lang'] != 'en':
            continue

        # filter out retweets
        if (not keepRT) and ('retweeted_status' in message):
            continue

        # kept tweet
        yield message
        tweetCount += 1
        print('\x1b[A\x1b[2K\r' + str(tweetCount), file = sys.stderr)

# read from file
def fromFile(fName, keepRT = True):
    with open(fName) as f:
        tweetCount = 0
        print(file = sys.stderr)
        for line in f:
            tweet = json.loads(line)

            if (not keepRT) and tweet['text'][:2] == 'RT':
                continue

            yield tweet
            tweetCount += 1
            print('\x1b[A\x1b[2K\r' + str(tweetCount), file = sys.stderr)

# get tweet IDs from a file
def fromIDsFile(fName, keepRT = True):
    with open(fName) as f:
        notFound = []
        tweetCount = 0
        print(file = sys.stderr)
        lines = [l for l in f]
        lines100 = [lines[100*i:100*i+100] for i in range(int(len(lines) / 100 + 1))]
        for i in range(len(lines100)):
            lines100[i] = [line.split('\t')[0] for line in lines100[i]]
        for tIter, tweetIDs in enumerate(lines100):
            try:
                tweets = [json.loads(str(s)) for s in api.GetStatuses(tweetIDs)]
                notFound += [tweetID for tweetID in tweetIDs if tweetID not in [tweet['id_str'] for tweet in tweets]]
                for tweet in tweets:
                    if (not keepRT) and tweet['text'][:2] == 'RT':
                        continue

                    yield tweet
                    tweetCount += 1
            except Exception as e:
                print(str(e) + '\n', file = sys.stderr)
                pass
            print('\x1b[A\x1b[2K\r' + str(tIter + 1) + '/' + str(len(lines100)) + ' ' + str(tweetCount) + ' kept', file = sys.stderr)
        print('\n'.join([json.dumps({'id_str': nf, 'id': int(nf)}) for nf in notFound]))
