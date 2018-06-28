#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script simply plot the data from a CSV containing three columns: block, recall and precision.
#
# Quentin Ribac

# configuration
FILE = 'recprec.csv'

# imports
import csv
import matplotlib.pyplot as plt

# code
def plot(fName = FILE):
    values = []
    with open(fName, 'r', encoding = 'utf-8') as f:
        dreader = csv.DictReader(f, delimiter = '\t')
        values = [val for val in dreader]

    plt.plot([i for i in range(len(values))], [100 * float(val['recall']) for val in values], 'b', label = 'Recall')
    plt.plot([i for i in range(len(values))], [100 * float(val['precision']) for val in values], 'r', label = 'Precision')
    plt.legend(fontsize = 'x-large')
    plt.xticks([i for i in range(len(values)) if i%2], [values[i]['block'] for i in range(len(values)) if i%2], rotation = -45, fontsize = 'large')
    plt.yticks(fontsize = 'large')
    plt.xlabel('Block time', fontsize = 'x-large')
    plt.ylabel('Percentage (%)', fontsize = 'x-large')
    plt.grid(True)
    plt.show()

    print('block\tprecision\trecall')
    for i in range(len(values)):
        print(values[i]['block'], values[i]['precision'], values[i]['recall'], sep = '\t')

if __name__ == '__main__':
    plot()
