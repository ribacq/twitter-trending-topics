#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Quentin Ribac, May 2018
#
# Comparision of sentiment of tweets in trending topics and tweets not in trending topics, over time.

# configuration
inputDir = '../../tweets/newsEN-20180508/topics/parts30minUpdated'
field = 'retweets' # defined in topicUtils.py

# dependencies
import csv
import os
import matplotlib.pyplot as plt

# where to look for data
blockDirs = sorted(os.listdir(inputDir))


# for every block of 30 minutes
times = []
valuesTrending = []
barTrending = []
valuesNonTrending = []
barNonTrending = []
for i, d in enumerate(blockDirs):
    # save time string
    times.append(d[-5:].replace('h', ':'))

    # look at trending topics
    with open(inputDir + '/' + d + '/statsfiltered.csv', 'r', encoding = 'utf-8') as trendingFile:
        dreader = csv.DictReader(trendingFile, delimiter = '\t')
        topics = [{index: float(topic[index]) for index in topic} for topic in dreader]
        
        # if there are no topics, save a zero value
        if len(topics) == 0:
            valuesTrending.append(0)
            barTrending.append({'negative': 0, 'positive': 0, 'neutral': 0})
        else:
            # save the value per tweet
            valuesTrending.append(sum([topic[field] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]))
            # save the proportion of negative, positive and neutral tweets
            barTrending.append({
                'negative': sum([topic['negativeCount'] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]),
                'positive': sum([topic['positiveCount'] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]),
                'neutral': sum([topic['neutralCount'] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]),
            })

    # look at non trending topics
    with open(inputDir + '/' + d + '/statsnontrending.csv', 'r', encoding = 'utf-8') as nonTrendingFile:
        dreader = csv.DictReader(nonTrendingFile, delimiter = '\t')
        topics = [{index: float(topic[index]) for index in topic} for topic in dreader]

        # if there are no topics, save a zero value
        if len(topics) == 0:
            valuesTrending.append(0)
            barTrending.append({'negative': 0, 'positive': 0, 'neutral': 0})
        else:
            # save the value per tweet
            valuesNonTrending.append(sum([topic[field] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]))
            # save the proportion of negative, positive and neutral tweets
            barNonTrending.append({
                'negative': sum([topic['negativeCount'] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]),
                'positive': sum([topic['positiveCount'] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]),
                'neutral': sum([topic['neutralCount'] for topic in topics]) / sum([topic['tweetCount'] for topic in topics]),
            })

# CSV data
times = times[2:] + ['08:00', '08:30']
print('block\t' + field + 'Trending\t' + field + 'NonTrending')
for i in range(len(times)):
    print(times[i], valuesTrending[i], valuesNonTrending[i], sep = '\t')
#print(sum([valuesTrending[i] / valuesNonTrending[i] for i in range(len(times))]) / len(times))

# plot data
x = [12.5 + 0.5 * i for i in range(len(times))]
plt.plot(x, valuesTrending, 'r', label = 'Tweets in trending topics')
plt.plot(x, valuesNonTrending, 'b', label = 'Tweets not in trending topics')
plt.legend(fontsize = 'x-large')
plt.xlabel('British Summer Time (hours)', fontsize = 'x-large')
plt.ylabel('Number of retweets per tweet', fontsize = 'x-large')
plt.xticks([val for i, val in enumerate(x) if i % 2], [val for i, val in enumerate(times) if i % 2], rotation = -45, fontsize = 'large')
plt.yticks(fontsize = 'large')
plt.grid(True)
plt.show()
