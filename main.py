#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# Twitter trending topics analysis
# Main program
#
# Written by Quentin Ribac
# April 2018

import json
from newsSourcesENTT import english_sources_twitter
import os
import stream
import sys
import topicUtils
import topicDetection

def usage():
    print('Twitter trending topics detection and analysis')
    print('==============================================')
    print('')
    print('Usage:')
    print('    ' + sys.argv[0] + ' [-l <number>] -r <choice>')
    print('    ' + sys.argv[0] + ' [-t <number>] [-s <number>] -a <tweets file> <output directory>')
    print('')
    print('--help, -h')
    print('    Display this help message')
    print('')
    print('--retrieve, -r [filter <term1 term2 ...> | news [date]]')
    print('    Get tweets from Twitter to STDOUT.')
    print('    ‘filter <terms>’ streams a live sample 10,000 tweets, filtered by given terms, if any')
    print('    ‘news’ streams a live sample of tweets from UK news sources’')
    print('    ‘idsfile <fname>’ will retrieve tweets whose IDs are specified in given file, one per line')
    print('    Default: get a sample of the whole of Twitter without filters')
    print('')
    print('--limit, -l <number>')
    print('    Indicate the number of tweets you want to retrieve with ‘filter’. Default: 10,000')
    print('')
    print('--analyze, -a <tweets file> <output directory>')
    print('    Given a tweets file, this will generate, in the output directory:')
    print('    topics.json, containing all topics')
    print('    summary.txt, containing a more human-readable summary of topics')
    print('    stats.csv,   containing tweetCount, views and tfidf for each topic (TAB seperated values)')
    print('')
    print('--threshold, -t <number>')
    print('    Set the cosine similarity threshold between tweet and topics.')
    print('    Values can range from 0.1 to 0.9. Default: 0.3')
    print('')
    print('--size, -s <number>')
    print('    Set the minimum number of tweets in a topic.')
    print('    Default: 5')

COSINE_SIM_THRESHOLD = 0.3
MIN_TOPIC_SIZE = 5
RETRIEVAL_LIMIT = 10000

if __name__ == '__main__':
    # react to cli arguments
    args = sys.argv[1:]

    # parameters arguments
    while len(args) >= 1 and args[0] in ('-t', '--threshold') + ('-s', '--size') + ('-l', '--limit'):
        if len(args) < 2:
            print('No value given.', file = sys.stderr)
            args = []
            break
        if args[0] in ('-t', '--threshold'):
            try:
                givenThresh = float(args[1])
                if givenThresh < 0.1 or givenThresh > 0.9:
                    print('Invalid threshold value given: outside range', file = sys.stderr)
                else:
                    COSINE_SIM_THRESHOLD = givenThresh
            except ValueError:
                print('Invalid threshold value given: not a number', file = sys.stderr)
                continue
            finally:
                args = args[2:]
        elif args[0] in ('-s', '--size'):
            try:
                MIN_TOPIC_SIZE = int(args[1])
            except ValueError:
                print('Invalid size value given: not a number', file = sys.stderr)
            finally:
                args = args[2:]
        elif args[0] in ('-l', '--limit'):
            try:
                RETRIEVAL_LIMIT = int(args[1])
            except ValueError:
                print('Invalid retrival limit value given: not a number', file = sys.stderr)
            finally:
                args = args[2:]

    # no argument given: exit
    if len(args) == 0:
        print('Nothing to do. Try -h or --help option.')
        sys.exit(0)

    # main action arguments
    if args[0] in ('-h', '--help'):
        # help
        usage()
        sys.exit(0)
    elif args[0] in ('-r', '--retrieve'):
        # -r / --retrieve: get tweets in json format to STDOUT
        args = args[1:]
        s = None
        if len(args) > 0 and args[0] == 'filter':
            s = stream.filter(track = args[1:], limit = RETRIEVAL_LIMIT)
        elif len(args) > 0 and args[0] == 'news':
            s = stream.filter(follow = list(english_sources_twitter.values()), limit = RETRIEVAL_LIMIT)
        elif len(args) > 1 and args[0] == 'idsfile':
            s = stream.fromIDsFile(args[1])
        else:
            s = stream.filter()

        for tweet in s:
            print(json.dumps(tweet))
        sys.exit(0)
    elif args[0] in ('-a', '--analyze'):
        # -a / --analyze: generate in output directory topics.json, summary.txt and stats.csv
        # exit if too few arguments
        if len(args) < 3:
            print('Too few arguments given. Exiting.', file = sys.stderr)
            sys.exit(1)
        
        # check existence of tweets file and output directory
        tweetsFile = args[1]
        outputDir = args[2] if args[2][-1] != '/' else args[2][:-1]
        if not os.path.isfile(tweetsFile):
            print('Incorrect input file. Exiting.', file = sys.stderr)
            sys.exit(1)
        if not os.path.isdir(outputDir):
            print('Creating output directory...')
            os.makedirs(outputDir)

        # generate topics
        print('Similarity threshold:', COSINE_SIM_THRESHOLD)
        print('Minimum topic size:', MIN_TOPIC_SIZE)
        topics, nonTrending, tweetCount, sentimentStats, stats = topicDetection.useFile(args[1], COSINE_SIM_THRESHOLD, MIN_TOPIC_SIZE, topicDetection.VADER)
        print('non trending tweets:', topicUtils.tweetCount(nonTrending))
        print()

        # write outputDir/sentimentStats.json
        print('Writing sentimentStats.json...', end = ' ')
        with open(outputDir + '/sentimentStats.json', 'w+', encoding = 'utf-8') as ssf:
            ssf.write(json.dumps(sentimentStats) + '\n')
        print('done.')

        # write ouputDir/topics.json
        print('Writing topics.json...', end = ' ')
        with open(outputDir + '/topics.json', 'w+', encoding = 'utf-8') as tf:
            for topic in topics:
                tf.write(json.dumps(topic) + '\n')
        print('done.')

        # write outputDir/summary.txt
        print('Writing summary.txt...', end = ' ')
        with open(outputDir + '/summary.txt', 'w+', encoding = 'utf-8') as sf:
            sf.write(topicUtils.summary(topics, tweetCount, COSINE_SIM_THRESHOLD, MIN_TOPIC_SIZE))
        print('done.')

        # write outputDir/stats.csv
        print('Writing stats.csv...', end = ' ')
        with open(outputDir + '/statstime.csv', 'w+', encoding = 'utf-8') as cf:
            cf.write(stats)
        with open(outputDir + '/stats.csv', 'w+', encoding = 'utf-8') as cf:
            stats = topicUtils.json2csv(headersOnly = True)
            stats += topicUtils.json2csv(topics)
            cf.write(stats)
        with open(outputDir + '/statsnontrending.csv', 'w+', encoding = 'utf-8') as cf:
            stats = topicUtils.json2csv(headersOnly = True)
            stats += topicUtils.json2csv([nonTrending])
            cf.write(stats)
        print('done.')
        sys.exit(0)
    else:
        print('Argument not recognized. Exiting.', file = sys.stderr)
        sys.exit(1)
