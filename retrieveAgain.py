#!/usr/bin/python3
# -*- encoding: utf-8 -*-
#
# Quentin Ribac

from twitterApiHandle import api
from pymongo import MongoClient
import json

client = MongoClient()
db = client.twitterDB

with open('ids.txt', 'r', encoding = 'utf-8') as f:
    tweet100IDs = []
    for i, line in enumerate(f):
        if i > 0 and (i % 100 == 0 or i == 99):
            db.tweetsSecondRetrieval.insert_many([json.loads(str(status)) for status in api.GetStatuses(tweet100IDs)])
            print(i)
            tweet100IDs = [line[1:-2]]
        else:
            tweet100IDs.append(line[1:-2])
