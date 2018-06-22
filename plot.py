#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Convert a csv into a series of scatter plot images
#
# Quentin Ribac
# May 2018

import csv
import random
import sys
import matplotlib.pyplot as plt

def csv2plot(fName, topicIDs, xField, yField, xLabel = 'x', yLabel = 'y', title = '', removeConstant = False, noPlot = False):
    """
    csv2plot draws a scatter plot from given csv data.
    
    Parameters:
    fName: str, name of a file containing csv data about trending topics
    topicIDs: list of int; empty list or None means all topics are used
    xField and yField:
        can be a str that will be used as field name, which can be followed by % (with no space before it)
        or a function which must take as argument a topic dictionary and return a number
        example str: 'tweetCount', 'views%'
        example function: lambda topic: topic['views'] / topic['tweetCount']
    xLabel: a str used as x axis label
    yLabel: a str used as y axis label
    removeConstant: if True, topics for which either xField or yField has constant values will be removed
    noPlot: if True, do not show plot, just return the values
    """

    values = []
    with open(fName, 'r', encoding = 'utf-8') as f:
        dreader = csv.DictReader(f, delimiter = '\t')
        values = [val for val in dreader]

    # do we have several topics?
    severalTopics = topicIDs is not None and len(topicIDs) > 0
    if severalTopics:
        values = [val for val in values if val['topicID'] in topicIDs]

    # make xField and yField lambda functions if they aren’t
    xIsPct = False
    if type(xField) is str:
        xIsPct = xField[-1] == '%'
        xFieldStr = xField
        xLabel = xFieldStr
        xFieldStr = xField.rstrip('%')
        xField = lambda t: t[xFieldStr]
    if not callable(xField):
        print('csv2plot: error, xField is neither a field name nor a function', file = sys.stderr)
        return

    yIsPct = False
    if type(yField) is str:
        yIsPct = yField[-1] == '%'
        yFieldStr = yField
        yLabel = yFieldStr
        yFieldStr = yField.rstrip('%')
        yField = lambda t: t[yFieldStr]
    if not callable(yField):
        print('csv2plot: error, yField is neither a field name nor a function', file = sys.stderr)
        return
    
    # get data to plot
    if not severalTopics:
        topicIDs = set([val['topicID'] for val in values])

    xData = [[xField(val) for val in values if val['topicID'] == topicID] for topicID in topicIDs]
    if xIsPct:
        xSum = sum([sum(xd) for xd in xData])
        xData = [[100 * xi / xSum for xi in xd] for xd in xData]

    yData = [[yField(val) for val in values if val['topicID'] == topicID] for topicID in topicIDs]
    if yIsPct:
        ySum = sum([sum(yd) for yd in yData])
        yData = [[100 * yi / ySum for yi in yd] for yd in yData]

    # remove topics for which either xData or yData is constant
    if removeConstant:
        removedIDs = [i for i in range(len(xData)) if len(set(xData[i])) <= 1 or len(set(yData[i])) <= 1]
        xData = [xData[i] for i in range(len(xData)) if i not in removedIDs]
        yData = [yData[i] for i in range(len(yData)) if i not in removedIDs]

    # plot 1: given x and y data and/or save image to file
    if not noPlot:
        fig1 = plt.figure(1)
        for i in range(len(xData)):
            plt.plot(xData[i], yData[i], '-o')
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        plt.grid(True)
        if len(title) > 0:
            plt.title(title)
        else:
            plt.title(yLabel + ' / ' + xLabel)
        plt.show()
        #fig.savefig('img.png') # or img.png

    return xData, yData

if __name__ == '__main__':
    x, y = 'avgFavorites', 'tweetCount'
    res = csv2plot('../plopres/statstime.csv', [], x, y, removeConstant = False)
