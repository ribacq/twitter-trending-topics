#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Quentin Ribac

import twitter # github.com/bear/twitter-python --- sudo pip install python-twitter

# api connection
api = twitter.Api(
    consumer_key = 'ChvsprEQxdVWatFJA6cgDXHfy',
    consumer_secret = '1GKMb3S2wMWmGT84tdrFHpirvnJHydDbs0w7tCH8QOrtNTlJTU',
    access_token_key = '965594046176616448-Nr0Dh8FYVxIzgukU97OBh3vM9BaklIg',
    access_token_secret = 'oFfETSfBdi2d89OnrroeBbXzKhTLCKmSo8YJHWJGVeIFY',
    sleep_on_rate_limit = True
)

