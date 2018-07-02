# Twitter Trending Topic Detection and Analysis
This repository contains code used during my internship at the University of Plymouth (United Kingdom), done from April to June 2018, and associated with the article by Dr. Marco Palomino for the conference SOMET 2018 (http://secaba.ugr.es/SOMET2018/).

The files do several kinds of things:

* retrieve tweets (`stream.py`)
* group tweets in topics (`topicDetection.py`)
* analyze tweets to generate graphs (all `plot*.py`)

## How-to
### Retrieve tweets
Use `main.py` to retrieve tweets to `stdout`.

```bash
python3 main.py news
```

(more info in `python3 main.py --help`)

### Analyze tweets
Use a `plot*.py` file, set the configuration on top with your values, and use `python3 plotSomething.py`. If there is no error, this will generate both a plot and numerical values (in `stdout`).

## Used external software
**Python3**,
Programming language and its standard library,
https://docs.python.org/3/

**MongoDB** (unused),
database server,
https://docs.mongodb.com/manual/installation

**PyMongo** (unused),
MongoDB database client for Python,
https://api.mongodb.com/python/current/index.html

**NewsAPI**,
news headlines retrieval tool service,
https://newsapi.org

**Matplotlib**,
Python 2D plotting library,
https://matplotlib.org

**Twitter API**,
The documentation to the official Twitter API,
https://developer.twitter.com/en/docs

**python-twitter**,
Python wrapper for the Twitter API,
https://github.com/bear/twitter-python

**SentiStrength**,
Sentiment rating program,
http://sentistrength.wlv.ac.uk/

**VaderSentiment**,
Rule-based sentiment rating Python library,
https://github.com/cjhutto/vaderSentiment,
Citation:
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.

**Opinion Lexicon**,
Two lists of terms, positive and negative respectively,
http://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html,
Citation:
Minqing Hu and Bing Liu. "Mining and Summarizing Customer Reviews." Proceedings of the ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD-2004), Aug 22-25, 2004, Seattle, Washington, USA

**Node.js ‘stopwords’ package**,
A list of 661 stopwords which includes the SMART stopwords list,
https://github.com/huned/node-stopwords

**Natural Language ToolKit (NLTK) Tweet Tokenizer**,
A text tokenizer specifically made for tweets, in Python,
http://www.nltk.org/api/nltk.tokenize.html#module-nltk.tokenize.casual

**NLTK implementation of Porter Stemmer**,
A standard word stemming algorithm, in Python,
http://www.nltk.org/api/nltk.stem.html#module-nltk.stem.porter,
Citation:
Porter, M. “An algorithm for suffix stripping.” Program 14.3 (1980): 130-137.
