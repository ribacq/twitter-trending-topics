#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# The purpose of this script is to check if topics overlap between two consecutive 30-minutes blocks of a tweet collection.
#
# Quentin Ribac
# May 2018

# configuration
COLLECTION_DIR = '../../tweets/newsEN-20180508' # a collection directory
Y_FIELD = 'sentiment' # a field defined in topicUtils.py

# imports
import csv
import json
import os
import sys

import stopwords

import matplotlib.pyplot as plt

# comparison function
def useFiles(fName1, fName2):
    """
    Parameters:
    fName1 and fName2: uri of files to compare

    Output:
    A list of couples of topic IDs from (fName1, fName2) that correspond to the same topic.
    """

    topics1 = []
    topics2 = []
    with open(fName1, 'r', encoding = 'utf-8') as tf1, open(fName2, 'r', encoding = 'utf-8') as tf2:
        topics1 = [json.loads(line) for line in tf1.readlines()]
        topics2 = [json.loads(line) for line in tf2.readlines()]

    if len(topics1) == 0 or len(topics2) == 0:
        print('Error: no topics found.', file = sys.stderr)
        return None

    overlap = []
    for i1, t1 in enumerate(topics1):
        for i2, t2 in enumerate(topics2):
            terms1 = set(t1['terms'].keys())
            terms2 = set(t2['terms'].keys())
            if 'used' not in t2 and len(terms1 & terms2) == min(len(terms1), len(terms2)):
                # if the intersection between the two sets of terms is as big as the smaller of the two,
                # then one topic is included in the other.
                # we can consider this an overlap, save this and skip to the next topic
                overlap.append((i1, i2))
                t2['used'] = True
                break

    return len(topics1), overlap

# using the above function
if __name__ == '__main__':
    inputDir = COLLECTION_DIR
    inputJsonFiles = [inputDir + '/json/filtered/' + d for d in sorted(os.listdir(inputDir + '/json/filtered'))]
    inputTopicsDirs = [inputDir + '/topics/parts30minWithFiltered/' + d for d in sorted(os.listdir(inputDir + '/topics/parts30minWithFiltered'))]
    originalTopicsCount = 0
    overlaps = []
    for i in range(len(inputJsonFiles) - 1):
        tc, overlap = useFiles(inputJsonFiles[i], inputJsonFiles[i+1])
        originalTopicsCount += tc
        overlaps.append(overlap)

    # construct topics which are lists of dictionaries
    # each dictionary indicates the IDs of a topic in the successive files
    topics = []
    for oIter, overlap in enumerate(overlaps):
        for idA, idB in overlap:
            for topic in topics:
                if oIter in topic and topic[oIter] == idA:
                    topic[oIter + 1] = idB
                    break
            else:
                topics.append({
                    oIter: idA,
                    oIter + 1: idB,
                })

    # get the topics’ values
    topicIDs = []
    data = []
    for i in range(len(inputTopicsDirs)):
        with open(inputTopicsDirs[i] + '/statsfiltered.csv', 'r', encoding = 'utf-8') as f:
            dreader = csv.DictReader(f, delimiter = '\t')
            csvValues = [topic for topic in dreader]
            topicIDs.append([float(topic['topicID']) for topic in csvValues])
            data.append([float(topic[Y_FIELD]) for topic in csvValues])

    # filter topics to only keep the longest ones
    #topics = sorted(topics, key = lambda t: sum([data[blockID][topicIDs[blockID].index(float(t[blockID]))] for blockID in t]), reverse = True)[:5]
    topics = sorted(topics, key = lambda t: len(t), reverse = True)[:5]

    # now plot the results
    for topic in topics:
        xData = [blockID for blockID in topic]
        yData = [data[blockID][topicIDs[blockID].index(float(topic[blockID]))] for blockID in topic]
        terms = []
        txt = ''
        with open(inputJsonFiles[xData[0]], 'r', encoding = 'utf-8') as jsonF:
            lines = [line for line in jsonF]
            terms = list(json.loads(lines[topic[xData[0]]])['terms'])
            terms = [term for term in terms if term[0] != '@']
            for sw in stopwords.stopwords + stopwords.moreStopwords + ['thi']:
                if sw in [t.lower() for t in terms]:
                    terms.pop([t.lower() for t in terms].index(sw))
            terms = [term.replace('\'', '') for term in terms]
            tweetsText = ['(' + str(tweet['occurrences']) + 'x)>>> ' + tweet['text'] for tweet in json.loads(lines[topic[xData[0]]])['tweets'][:3]]
            print('\n' + ', '.join(terms))
            print('\n'.join(tweetsText))
        plt.plot(xData, yData, '-o', label = ', '.join(terms[:3]))
    plt.grid(True)
    plt.xlabel('British Summer Time (hours)', fontsize = 'large')
    plt.ylabel(Y_FIELD.capitalize(), fontsize = 'large')
    plt.xticks([i for i in range(41) if i%2], [str(int((11.5 + 0.5 * i) % 24))+':00' for i in range(41) if i%2], rotation = -45, fontsize = 'large')
    plt.yticks(fontsize = 'large')
    plt.legend(fontsize = 'x-large')
    plt.show()
