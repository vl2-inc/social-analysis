import json
from pymongo import MongoClient
from twython import Twython


config = json.load(open('config.json', 'r'))
APP_KEY = config['app_key']
APP_SECRET = config['app_secret']
ACCESS_TOKEN = config['access_token']
ACCESS_SECRET = config['access_secret']


def initialize_mongo():
    client = MongoClient()
    return client['lundero-twitter-poc']

def initialize_API():
    twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    return twitter

def demo():
    db = initialize_mongo()
    tweets_collection = db['tweets']
    twitter_api = initialize_API()
    # my_tweets = get_tweets(twitter_api, user='MartinVizcarraC')
    # for tweet in my_tweets:
    #     print(tweet)
    my_mentions = get_mentions(twitter_api, user='MartinVizcarraC')
    for tweet in my_mentions:
        print(tweet)

def get_tweets(twitter_api, user=None):
    my_tweets = twitter_api.get_user_timeline(screen_name=user, tweet_mode='extended')
    my_tweets_list = []
    for tweet in my_tweets:
        tweet_reduced_dict = {}
        tweet_reduced_dict['created_at'] = tweet['created_at']
        tweet_reduced_dict['id'] = tweet['id_str']
        tweet_reduced_dict['text'] = tweet['full_text']
        my_tweets_list.append(tweet_reduced_dict)
    return my_tweets_list


def get_mentions(twitter_api, user=None):
    my_mentions = twitter_api.get_mentions_timeline(screen_name=user, tweet_mode='extended')
    my_mentions_list = []
    for tweet in my_mentions:
        tweet_reduced_dict = {}
        tweet_reduced_dict['created_at'] = tweet['created_at']
        tweet_reduced_dict['id'] = tweet['id_str']
        tweet_reduced_dict['text'] = tweet['full_text']
        my_mentions_list.append(tweet_reduced_dict)
    return my_mentions_list

def match_tweets_and_replies(tweets, mentions):
    pass

def save_to_mongo(collection):
    pass

if __name__ == '__main__':
    demo()