#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Script using the opinion lexicon to rate texts
#
# Quentin Ribac
# May 2018

positive, negative = [], []
with open('opinionLexicon/POSITIVE-WORDS.TXT', 'r', encoding = 'utf-8') as posFile:
    for line in posFile:
        if line[0] != ';':
            positive.append(line.rstrip('\n').lower())

with open('opinionLexicon/NEGATIVE-WORDS.TXT', 'r', encoding = 'utf-8') as negFile:
    for line in negFile:
        if line[0] != ';':
            negative.append(line.rstrip('\n').lower())

def rate(texts):
    res = []
    for text in texts:
        words = [word.lower() for word in text.split()]
        res.append(len([1 for word in words if word in positive]) - len([1 for word in words if word in negative]))
    return res
