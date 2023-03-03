import tweepy as tw
import config
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# Authentication for both API v1.1 and v.2
# (** These twitter API keys and secrets below are needed to be changed as your own credentials in the config.py file**)
# get Client object to use API v2 endpoints
client = tw.Client(bearer_token=config.bearer_token, return_type=requests.Response)
# get API object to use API v1.1 endpoints
auth = tw.OAuth1UserHandler(consumer_key=config.consumer_key,
                            consumer_secret=config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tw.API(auth)

# search recent tweets using query (API v.2 endpoints)
query = 'science -is:retweet lang:en'   # query can be modified by the rule of twitter API doc
response = client.search_recent_tweets(query=query, max_results=10, tweet_fields=['created_at', 'author_id'])

# get dataframe of the search results to manipulate data easily
response_json = response.json()
tweets_data = response_json['data']
df = pd.json_normalize(tweets_data)
# print(df)

# get user objects of the users by using information 'author_id' field
user_id = []
name = []
description = []
fav_cnt = []

for userid in df['author_id']:
    user = api.get_user(user_id=userid)
    name.append(user.screen_name)
    description.append(user.description)
    fav_cnt.append(user.favourites_count)
    user_id.append(userid)

# get a dataframe of user's information
list_of_tuples = list(zip(user_id, name, description, fav_cnt))
df_user = pd.DataFrame(list_of_tuples, columns=['User Id', 'Screen name', 'Description', 'favorite count'])
# print(df_user)

# get recent tweets of the users by loop (use API v1.1 endpoints)
# also add statistics information of retweet count and favorite count for each user
sum_ret = []
sum_fav = []
avg_ret = []
avg_fav = []
median_ret = []
median_fav = []
std_ret = []
std_fav = []
user = []
for userid in df['author_id']:
    # get user's recent 20 tweets
    public_tweets = api.user_timeline(user_id=userid)
    retweet_cnt = []
    favorite_cnt = []
    user.append(userid)
    for tweet in public_tweets:
        retweet_cnt.append(tweet.retweet_count)
        favorite_cnt.append(tweet.favorite_count)
    sum_ret.append(sum(retweet_cnt))
    sum_fav.append(sum(favorite_cnt))
    avg_ret.append(np.average(retweet_cnt))
    avg_fav.append(np.average(favorite_cnt))
    median_ret.append(np.median(retweet_cnt))
    median_fav.append(np.median(favorite_cnt))
    std_ret.append(np.std(retweet_cnt))
    std_fav.append(np.std(favorite_cnt))

# add columns of statistics to df_user
df_user['Total retweets'] = sum_ret
df_user['Total favorite'] = sum_fav
df_user['Average retweets'] = avg_ret
df_user['Average Favorites'] = avg_fav
df_user['Median retweets'] = median_ret
df_user['Median favorites'] = median_fav
df_user['stdev retweets'] = std_ret
df_user['stdev favorites'] = std_fav

# get the statistic dataframe
df_user_statistic = df_user[['Screen name', 'Description', 'Total retweets', 'Total favorite', 'Average retweets',
                             'Average Favorites', 'Median retweets', 'Median favorites',
                             'stdev retweets', 'stdev favorites']]
print(df_user_statistic)

# store dataframe as csv file into log folder
file_name = datetime.now().strftime('user_statistic_%H_%M_%d_%m_%Y.csv')
df_user_statistic.to_csv(f"log/{file_name}")
