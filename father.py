import tweepy
import requests
import re
from time import sleep
from googletrans import Translator as trans
from googletrans import LANGUAGES as lang
from random import shuffle
import keys

auth = tweepy.OAuthHandler(keys.api_key, keys.api_key_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=keys.bearer_token, 
consumer_key=keys.api_key, consumer_secret=keys.api_key_secret, 
access_token=keys.access_token, access_token_secret=keys.access_token_secret)
print("Connected.")

replied_tweets = [int(tweet_id) for tweet_id in open("D:/github/father-klingot/replied_tweets", "r+").read().split()]
print(replied_tweets)
translator = trans()
languages = list(lang)

while True:
    try:
        reply_tweets = [tweet for tweet in tweepy.Cursor(api.search_tweets, "@FatherKlingot").items(20)]
    except:
        print("No new tweets mentioning father.")
        sleep(60)
        continue

    for reply_tweet in reply_tweets:
        reply_id = reply_tweet.id
        scramble = notscramble = False
        if " scramble" in reply_tweet.text:
            scramble = True
        elif " notscramble" in reply_tweet.text:
            notscramble = True
        else:
            print("No new tweets mentioning father.")
            sleep(60)
            continue
    
        if reply_tweet._json["in_reply_to_status_id"]:
            tweet = client.get_tweet(id=reply_tweet._json["in_reply_to_status_id"])
            tweet.data.text = re.sub(r"@\w+[ |\n]", "", tweet.data.text)
        else:
            tweet = reply_tweet
            tweet.text.replace("unscramble ","")
            tweet.text.replace("scramble ","")
            tweet.text = re.sub(r"@\w+[ |\n]", "", tweet.text)
            tweet.data = lambda: None
            setattr(tweet.data, 'id', tweet.id)
            setattr(tweet.data, 'text', tweet.text)

        #if not(tweet.data):
        #    print("No new tweets mentioning father.")
        #    sleep(60)
        #    continue
        if tweet.data.id not in replied_tweets:
            replied_tweets.append(tweet.data.id)
            if len(replied_tweets) > 20:
                replied_tweets.pop(0)
            open("D:/github/father-klingot/replied_tweets", "r+").truncate(0)
            open("D:/github/father-klingot/replied_tweets", "r+").write(' '.join([str(tweet) for tweet in replied_tweets]))
            if scramble:
                shuffle(languages)
                scrambled = tweet.data.text
                for language in languages[:9]:
                    try:
                        scrambled = translator.translate(scrambled, dest=language).text
                    except:
                        if scrambled != tweet.data.text:
                            client.create_tweet(text=scrambled[:279])
                            client.create_tweet(text=scrambled[:279], in_reply_to_tweet_id=reply_id)
                            print("Replied.")
                        else:
                            client.create_tweet(text="there was an error generating my response :(", in_reply_to_tweet_id=reply_id)
                            print("Translation error.")
                            break
                else:
                    scrambled = translator.translate(scrambled, dest="en").text
                    scrambled_list = scrambled.split()
                    reply_tweet = str()
                    profile_tweet = None
                    for word in scrambled_list:
                        reply_tweet += " " + word
                        if len(reply_tweet) > 280:
                            reply_tweet = reply_tweet.replace(word, "")
                            reply_tweet = reply_tweet.replace(".", ". ")
                            if profile_tweet:
                                profile_tweet = client.create_tweet(text=reply_tweet, in_reply_to_tweet_id=int(profile_tweet.data["id"]))
                            else:
                                profile_tweet = client.create_tweet(text=reply_tweet)
                            reply = client.create_tweet(text=reply_tweet, in_reply_to_tweet_id=reply_id)
                            reply_id = int(reply.data["id"])
                            reply_tweet = word
                            break
                        else:
                            client.create_tweet(text=scrambled)
                            client.create_tweet(text=scrambled, in_reply_to_tweet_id=reply_id)
                    print("Replied.")
    
            elif notscramble:
                notscrambled = requests.post(
                "https://api.deepai.org/api/text-generator",
                data={
                    'text': tweet.data.text,
                },
                headers={'api-key': 'ebb6d07f-9985-460f-95f7-96d836b8a7c5'}
                )
                try:
                    notscrambled = notscrambled.json()['output']
                except:
                        print(notscrambled.json())
                else:
                    notscrambled = notscrambled.replace(tweet.data.text,"")
                    notscrambled_list = notscrambled.split()
                    reply_tweet = str()
                    profile_tweet = None
                    for word in notscrambled_list:
                        reply_tweet += " " + word
                        if len(reply_tweet) > 280:
                            reply_tweet = reply_tweet.replace(word, "")
                            reply_tweet = reply_tweet.replace(".", ". ")
                            if profile_tweet:
                                profile_tweet = client.create_tweet(text=reply_tweet, in_reply_to_tweet_id=int(profile_tweet.data["id"]))
                            else:
                                profile_tweet = client.create_tweet(text=reply_tweet)
                            reply = client.create_tweet(text=reply_tweet, in_reply_to_tweet_id=reply_id)
                            reply_id = int(reply.data["id"])
                            reply_tweet = word
                    print("Replied.")
        else:
            print("No new tweets mentioning father.")
        sleep(60)
