from datetime import datetime

from . import format, get
from .tweet import Tweet
from .user import User
from .storage import write

import logging as logme

follows_list = []
tweets_list = []
users_list = []

author_list = {''}
author_list.pop()

# used by Pandas
_follows_object = {}


def _formatDateTime(datetimestamp):
    try:
        return int(datetime.strptime(datetimestamp, "%Y-%m-%d %H:%M:%S").timestamp())
    except ValueError:
        return int(datetime.strptime(datetimestamp, "%Y-%m-%d").timestamp())


def _clean_follow_list():
    logme.debug(__name__ + ':clean_follow_list')
    global _follows_object
    _follows_object = {}


def clean_lists():
    logme.debug(__name__ + ':clean_lists')
    global follows_list
    global tweets_list
    global users_list
    follows_list = []
    tweets_list = []
    users_list = []


def datecheck(datetimestamp, config):
    logme.debug(__name__ + ':datecheck')
    if config.Since:
        logme.debug(__name__ + ':datecheck:SinceTrue')

        d = _formatDateTime(datetimestamp)
        s = _formatDateTime(config.Since)

        if d < s:
            return False
    if config.Until:
        logme.debug(__name__ + ':datecheck:UntilTrue')

        d = _formatDateTime(datetimestamp)
        s = _formatDateTime(config.Until)

        if d > s:
            return False
    logme.debug(__name__ + ':datecheck:dateRangeFalse')
    return True


# TODO In this method we need to delete the quoted tweets, because twitter also sends the quoted tweets in the
#  `tweets` list along with the other tweets
def is_tweet(tw):
    try:
        tw["data-item-id"]
        logme.debug(__name__ + ':is_tweet:True')
        return True
    except:
        logme.critical(__name__ + ':is_tweet:False')
        return False


def _output(obj, output, config, **extra):
    logme.debug(__name__ + ':_output')
    if config.Lowercase:
        if isinstance(obj, str):
            logme.debug(__name__ + ':_output:Lowercase:username')
            obj = obj.lower()
        elif obj.__class__.__name__ == "user":
            logme.debug(__name__ + ':_output:Lowercase:user')
            pass
        elif obj.__class__.__name__ == "tweet":
            logme.debug(__name__ + ':_output:Lowercase:tweet')
            obj.username = obj.username.lower()
            author_list.update({obj.username})
            for dct in obj.mentions:
                for key, val in dct.items():
                    dct[key] = val.lower()
            for i in range(len(obj.hashtags)):
                obj.hashtags[i] = obj.hashtags[i].lower()
            for i in range(len(obj.cashtags)):
                obj.cashtags[i] = obj.cashtags[i].lower()
        else:
            logme.info('_output:Lowercase:hiddenTweetFound')
            print("[x] Hidden tweet found, account suspended due to violation of TOS")
            return
    if config.Output != None:
        write.Text(output, config.Output)
        logme.debug(__name__ + ':_output:Text')
    if not config.Hide_output:
        try:
            print(output.replace('\n', ' '))
        except UnicodeEncodeError:
            logme.critical(__name__ + ':_output:UnicodeEncodeError')
            print("unicode error [x] output._output")


async def checkData(tweet, config):
    logme.debug(__name__ + ':checkData')
    tweet = Tweet(tweet, config)
    if not tweet.datestamp:
        logme.critical(__name__ + ':checkData:hiddenTweetFound')
        print("[x] Hidden tweet found, account suspended due to violation of TOS")
        return
    if datecheck(tweet.datestamp + " " + tweet.timestamp, config):
        output = format.Tweet(config, tweet)
        #if config.Store_object:
        #    logme.debug(__name__ + ':checkData:Store_object')
        #    if hasattr(config.Store_object_tweets_list, 'append'):
        #        config.Store_object_tweets_list.append(tweet)
        #    else:
        #        tweets_list.append(tweet)
        _output(tweet, output, config)
    # else:
    #     logme.critical(__name__+':checkData:copyrightedTweet')


async def Tweets(tweets, config):
    logme.debug(__name__ + ':Tweets')
    if config.TwitterSearch:
        logme.debug(__name__ + ':Tweets:TwitterSearch')
        await checkData(tweets, config)
    else:
        logme.debug(__name__ + ':Tweets:else')
        if int(tweets["data-user-id"]) == config.User_id:
            await checkData(tweets, config)


async def Users(u, config):
    logme.debug(__name__ + ':User')
    global users_list

    user = User(u)
    output = format.User(config.Format, user)

    #if config.Store_object:
    #    logme.debug(__name__ + ':User:Store_object')
    #    if hasattr(config.Store_object_follow_list, 'append'):
    #        config.Store_object_follow_list.append(user)
    #    elif hasattr(config.Store_object_users_list, 'append'):
    #        config.Store_object_users_list.append(user)
    #    else:
    #        users_list.append(user)  # twint.user.user

    _output(user, output, config)


async def Username(username, config):
    logme.debug(__name__ + ':Username')
    global _follows_object
    global follows_list

    #if config.Store_object:
    #    if hasattr(config.Store_object_follow_list, 'append'):
    #        config.Store_object_follow_list.append(username)
    #    else:
    #        follows_list.append(username)  # twint.user.user

    _output(username, username, config)
