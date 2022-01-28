import tweepy
import requests
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

replied_tweets_file = open("D:/github/father-klingot/replied_tweets", "r+")
replied_tweets = [int(tweet_id) for tweet_id in replied_tweets_file.read().split()]
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
        else:
            tweet = reply_tweet
            tweet.data.text = ' '.join(tweet.text.split()[2:])
    
        if tweet.data.id not in replied_tweets:
            replied_tweets.append(tweet.data.id)
            if len(replied_tweets) > 20:
                replied_tweets.pop(0)
            replied_tweets_file.truncate(0)
            replied_tweets_file.write(' '.join([str(tweet) for tweet in replied_tweets]))
            if scramble:
                shuffle(languages)
                scrambled = tweet.data.text
                for language in languages[:9]:
                    try:
                        scrambled = translator.translate(scrambled, dest=language).text
                    except:
                        if scrambled != tweet.data.text:
                            client.create_tweet(text=scrambled[:279])
                            client.create_tweet(text=scrambled[:279], in_reply_to_tweet_id=tweet.data.id)
                            print("Replied.")
                        else:
                            client.create_tweet(text="there was an error generating my response :(", in_reply_to_tweet_id=tweet.data.id)
                            print("Translation error.")
                            break
                else:
                    scrambled = translator.translate(scrambled, dest="en").text
                    client.create_tweet(text=scrambled[:279])
                    client.create_tweet(text=scrambled[:279], in_reply_to_tweet_id=tweet.data.id)
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
                    notscrambled = f"... {notscrambled}"[:279]
                    client.create_tweet(text=notscrambled[:279])
                    client.create_tweet(text=notscrambled[:279], in_reply_to_tweet_id=tweet.data.id)
                    print("Replied.")
        else:
            print("No new tweets mentioning father.")
        sleep(60)
