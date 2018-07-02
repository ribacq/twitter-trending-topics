#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Quentin Ribac
# The goal of this script is to compute the number of tweets per news source in a json file of tweets.

# configuration
FILE = '../../tweets/newsEN-20180508/json/total.json'

# dependencies
import json
import sys
import matplotlib.pyplot as plt

# code
tweetsPerSource = {}
with open(FILE, 'r', encoding = 'utf-8') as f:
    for lIter, line in enumerate(f):
        # for every tweet
        print('\r', lIter, end = '', file = sys.stderr)
        tweet = json.loads(line)

        # get its author or the author of its retweeted status
        screen_name = '@'
        if 'retweeted_status' in tweet:
            screen_name += tweet['retweeted_status']['user']['screen_name']
        else:
            screen_name += tweet['user']['screen_name']

        # update dict
        if screen_name in tweetsPerSource:
            tweetsPerSource[screen_name] += 1
        else:
            tweetsPerSource[screen_name] = 1

print(file = sys.stderr)
tweetsPerSourceList = sorted(list(tweetsPerSource.items()), key = lambda c: c[1], reverse = True)

maxN = 30
x = [i for i in range(maxN)]
plt.bar(x, [100 * s[1] / 510000 for s in tweetsPerSourceList[:maxN]], color = 'r')
plt.xticks(x, [s[0] for s in tweetsPerSourceList[:maxN]], rotation = 90, fontsize = 'large')
plt.ylabel('Proportion of tweets (%)', fontsize = 'large')
plt.show()
