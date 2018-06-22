#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Quentin Ribac

import twitter # github.com/bear/twitter-python --- sudo pip install python-twitter

# api connection
api = twitter.Api(
    consumer_key = '-',
    consumer_secret = '-',
    access_token_key = '-',
    access_token_secret = '-',
    sleep_on_rate_limit = True
)

