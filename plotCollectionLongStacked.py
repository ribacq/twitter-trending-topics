#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script will serve to draw a stacked plot of number of positive, negative and neutral tweets in every block of 30 minutes.
#
# Quentin Ribac
# May 2018

# configuration
FILE = '../../tweets/newsEN-20180508/topics/sentimentStats.json'

# imports
import datetime
import matplotlib.pyplot as plt
import json

# opening data file
blockStats = []
with open(FILE, 'r', encoding = 'utf-8') as f:
    for line in f:
        blockStats.append(json.loads(line))

# calculating plot coordinates
x = [12.5 + 0.5 * i for i in range(len(blockStats))]

def pct(blockStats):
    positive = [100 * block['positive'] / block['total'] for block in blockStats]
    negative = [100 * block['negative'] / block['total'] for block in blockStats]
    neutral = [100 * block['neutral'] / block['total'] for block in blockStats]
    return positive, negative, neutral

def val(blockStats):
    positive = [block['positive'] for block in blockStats]
    negative = [block['negative'] for block in blockStats]
    neutral = [block['neutral'] for block in blockStats]
    return positive, negative, neutral

def acc(blockStats):
    positive, negative, neutral = [blockStats[0]['positive']], [blockStats[0]['negative']], [blockStats[0]['neutral']]
    for block in blockStats[1:]:
        positive.append(positive[-1] + block['positive'])
        negative.append(negative[-1] + block['negative'])
        neutral.append(neutral[-1] + block['neutral'])
    return positive, negative, neutral

positive, negative, neutral = acc(blockStats)

# setup and display plot
# the stack plot
plt.stackplot(x, neutral, negative, positive, colors = ('#ffc107', '#f44336', '#4caf50'))

# axis labels
plt.xlabel('British Summer Time (hours)', fontsize = 'x-large')
plt.ylabel('Number of tweets', fontsize = 'x-large')

# time labels
hoursStr = ['%02d:%02d' % (x[i] % 24, (x[i] - int(x[i])) * 60) for i in range(len(x)) if x[i] != int(x[i])]
plt.xticks([t for t in x if t != int(t)], hoursStr, rotation = -45, fontsize = 'large')
plt.yticks([0, 1e5, 2e5, 3e5, 4e5, 5e5], ['0', '100,000', '200,000', '300,000', '400,000', '500,000'], fontsize = 'large')

# legend
plt.legend(('Neutral', 'Negative', 'Positive'), loc = 'upper left', bbox_to_anchor=(0.66, 0.33), fontsize = 'x-large')

# display
plt.grid(True)
plt.show()

# print data in CSV format
print('time\tpositive\tnegative\tneutral')
for i in range(len(blockStats)):
    print(['%02d:%02d' % (x[i] % 24, (x[i] - int(x[i])) * 60) for i in range(len(x))][i], positive[i], negative[i], neutral[i], sep = '\t')
