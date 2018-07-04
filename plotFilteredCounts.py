#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Quentin Ribac, May 2018

# configuration
# Those two files are lists (one number per line) of the numbers of filtered topics and news headlines, block per block of the collection.
# They must be of same length.
# The FILTERED_COUNTS_FILE would have been generated after having filtered the topics against the headlines, using news.py.
FILTERED_COUNTS_FILE = '../../tweets/newsEN-20180508/json/filteredCounts.csv'
HEADLINES_COUNTS_FILE = '../../tweets/newsEN-20180508/headlines/headlinesCounts.csv'

# imports
import matplotlib.pyplot as plt

# code
filteredCounts = []
with open(FILTERED_COUNTS_FILE, 'r', encoding = 'utf-8') as f:
    filteredCounts = [int(val) for val in f]

headlinesCount = []
with open(HEADLINES_COUNTS_FILE, 'r', encoding = 'utf-8') as f:
    headlinesCounts = [int(val) for val in f]

plt.plot([i for i in range(41)], headlinesCounts, 'r', label = 'News API')
plt.plot([i for i in range(41)], filteredCounts, 'b', label = 'Matching topics')
plt.legend(fontsize = 'xx-large')
plt.xlabel('British Summer Time (hours)', fontsize = 'x-large')
plt.ylabel('Number of headlines', fontsize = 'x-large')
plt.xticks([i-2 for i in range(45) if i%2], [str(int((12.5+0.5*(i-2))%24))+':00' for i in range(45) if i%2], rotation = -45, fontsize = 'large')
plt.yticks(fontsize = 'large')
plt.grid(True)
plt.show()

print('block', 'matching topics', 'news api', sep = '\t')
for i in range(len(filteredCounts)):
    print('%02d:%02d' % ((12.5+0.5*i)%24, (30+30*i)%60), filteredCounts[i], headlinesCounts[i], sep = '\t')
