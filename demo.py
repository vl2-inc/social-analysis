import sys
import json
import tweepy
from pymongo import MongoClient


config = json.load(open('config.json', 'r'))
APP_KEY = config['app_key']
APP_SECRET = config['app_secret']
ACCESS_TOKEN = config['access_token']
ACCESS_SECRET = config['access_secret']

def initialize_mongo():
    client = MongoClient()
    return client['lundero-twitter-poc']

def initialize_API():
    auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET) 
    twitter_api = tweepy.API(auth)
    return twitter_api

def demo(user, num_tweets, num_total_replies):
    db = initialize_mongo()
    tweets_collection = db['tweets']
    twitter_api = initialize_API()
    print('Getting tweets')
    tweets = get_tweets(twitter_api, user)
    print('...and getting replies')
    replies = get_replies(twitter_api, tweets, user, num_total_replies)
    print('Matching tweets and replies')
    matched_tweets = match_tweets_and_replies(tweets, replies)
    print('Saving to mongo')
    save_to_mongo(tweets_collection, user, matched_tweets)

def get_tweets(twitter_api, user=None, count=5):
    tweets = []
    for tweet in tweepy.Cursor(twitter_api.user_timeline, screen_name=user, tweet_mode='extended').items(count):
        formatted_tweet = _format_response(tweet)
        tweets.append(formatted_tweet)
    return tweets


def get_replies(twitter_api, tweets, user=None, result_type='mixed'):
    replies = []
    if len(tweets) > 0:
        earliest_tweet = min(tweets, key=lambda x: x['id'])
        earliest_tweet_id = earliest_tweet['id']
        query = 'to:' + user
        replies = []
        for tweet in tweepy.Cursor(twitter_api.search, q=query, since_id=earliest_tweet_id,
                                   result_type=result_type, tweet_mode='extended').items(200):
            formatted_tweet = _format_response(tweet)
            replies.append(formatted_tweet)
    return replies

def _format_response(tweet):
    formatted_tweet = {}
    formatted_tweet['created_at'] = tweet.created_at
    formatted_tweet['id'] = tweet.id_str
    formatted_tweet['user'] = tweet.user.screen_name
    formatted_tweet['user_id'] = tweet.user.id_str
    formatted_tweet['text'] = tweet.full_text
    formatted_tweet['in_reply_to_status_id'] = tweet.in_reply_to_status_id_str
    formatted_tweet['in_reply_to_user_id'] = tweet.in_reply_to_user_id_str
    return formatted_tweet

def match_tweets_and_replies(tweets, replies):
    matched_tweets_hash = {}
    for tweet in tweets:
        tweet['replies'] = []
        tweet_id = tweet['id']
        matched_tweets_hash[tweet_id] = tweet
    for reply in replies:
        in_reply_to = reply['in_reply_to_status_id']
        try:
            tweet_replied_to = matched_tweets_hash[in_reply_to]
            tweet_replied_to['replies'].append(reply)
        except KeyError:
            pass
    return list(matched_tweets_hash.values())

def save_to_mongo(collection, user, tweets):
    collection.insert_one({'user': f'{user}', 'tweets': tweets})

if __name__ == '__main__':
    user = sys.argv[1]
    num_tweets = sys.argv[2]
    num_total_replies = sys.argv[3]
    demo(user, num_tweets, num_total_replies)