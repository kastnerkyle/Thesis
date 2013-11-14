#!/usr/bin/env python
import json
import dateutil.parser
import datetime
import twitter
import urllib2
from pandas.io import data


class Dataset(object):

    def __init__(self):
        """
        Abstract base class for datasets - required methods will go here
        """
        super(Dataset, self).__init__()
        self.data = None

    def to_one_hot(self):
        pass

    def to_dense(self):
        pass

    def to_sparse(self):
        pass

    def save(self, fpath):
        pass

    def load(self, fpath):
        pass


class TweetData(Dataset):

    def __init__(self, init_stream=True):
        super(TweetData, self).__init__()
        self.creds_ = None
        self.twitter_stream_ = None
        self.data = []
        if init_stream:
            self._init_stream()

    def get_creds(self, fpath='twitter_creds.txt'):
        """
        Read oAuth credentials from symlinked twitter_creds.txt file
        Expected file structure for twitter_creds.txt is:

        consumer_key:XXXX
        consumer_secret:XXXX
        token:XXXX
        token_secret:XXXX
        """

        creds = {}
        with open(fpath) as f:
            for line in f:
                k, v = line.strip().split(':')
                creds[k] = v
        return creds

    def _init_stream(self, fpath='twitter_creds.txt'):
        self.creds_ = self.get_creds(fpath)
        self.twitter_stream_ = twitter.TwitterStream(auth=twitter.OAuth(
            token=self.creds_['token'],
            token_secret=self.creds_['token_secret'],
            consumer_key=self.creds_['consumer_key'],
            consumer_secret=self.creds_['consumer_secret']))

    def get_tweet_from_json(self, json):
        return Tweet(json)

    def add_tweet_from_json(self, json):
        self.data.append(self.get_tweet_from_json(json))

    def get_next_tweet_from_stream(self, block=True, require_valid=True):
        if require_valid:
            valid = False
            while not valid:
                try:
                    t = Tweet(
                        self.twitter_stream_.statuses.sample(
                            block=block).next())
                    valid = t.valid
                except urllib2.HTTPError:
                    pass
        else:
            t = Tweet(
                self.twitter_stream_.statuses.sample(block=block).next())
        return t

    def add_next_tweet_from_stream(self, block=True, require_valid=True):
        self.data.append(
            self.get_next_tweet_from_stream(
                block=block, require_valid=require_valid))

    def get_all_text(self):
        return [t.text for t in self.data]


class Tweet(dict):

    def __init__(self, tweet_json):
        """
        Class to hold and represent tweets. Modified from from a post by
        Clayton Davis @ wakari.io
        """
        super(Tweet, self).__init__(self)
        self.valid = False
        if tweet_json and 'delete' not in tweet_json:
            # Clean this up pandas style
            self['timestamp'] = dateutil.parser.parse(
                tweet_json[u'created_at']).replace(tzinfo=None).isoformat()
            self.timestamp = self['timestamp']
            self['text'] = tweet_json['text']
            self.text = self['text']
            self['hashtags'] = [x['text']
                                for x in tweet_json['entities']['hashtags']]
            self.hashtags = self['hashtags']
            self['geo'] = tweet_json['geo'][
                'coordinates'] if tweet_json['geo'] else None
            self.geo = self['geo']
            self['id'] = tweet_json['id']
            self.id = self['id']
            self['screen_name'] = tweet_json['user']['screen_name']
            self.screen_name = self['screen_name']
            self['user_id'] = tweet_json['user']['id']
            self.user_id = self['user_id']
            self.valid = True

    def __str__(self):
        return json.dumps(self, indent=2, sort_keys=True)


class YahooData(Dataset):

    def __init__(self):
        super(YahooData, self).__init__()
        self.data = []

    def get_data(self, symbol="YHOO", start=datetime.datetime(2000, 1, 1)):
        return data.DataReader(
            symbol, "yahoo", start=datetime.datetime(2000, 1, 1))

    def add_data(self, symbol="YHOO", start=datetime.datetime(2000, 1, 1)):
        self.data.append(self.get_data(symbol=symbol, start=start))

    def get_all_from_col(self, col):
        return [x[col] for x in self.data]

    def get_all_adj_close(self, col="Adj Close"):
        return self.get_all_from_col(col)

if __name__ == "__main__":
    d = Dataset()
    t = TweetData()
    y = YahooData()
    t.add_next_tweet_from_stream()
    t.add_next_tweet_from_stream()
    print t.get_all_text()
    raise ValueError("Temp Stop")
    y.add_data("GOOG")
    y.add_data("XOM")
    r = y.get_all_adj_close()
    import matplotlib.pyplot as plt
    r[0].plot(color="steelblue")
    r[1].plot(color="darkred")
    plt.show()
