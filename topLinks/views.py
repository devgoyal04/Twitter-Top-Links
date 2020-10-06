from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import logout
from django.db.models import Count

from datetime import datetime

import requests
import tweepy
import tldextract

from .models import Author, Tweets

from config import CONSUMER_KEY, CONSUMER_SECRET

CALLBACK_URL = 'http://127.0.0.1:8000/callback'

#Landing page view
def indexView(request):
    if (checkKey(request)):
        return HttpResponseRedirect(reverse('topLinks:home'))
    else:
        return render(request, 'topLinks/index.html', {})

#Authorizing the user
def oauth(request):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth_url = auth.get_authorization_url()
    response = HttpResponseRedirect(auth_url)

    request.session['request_token'] = auth.request_token
    return response

#Handling the callback
def callback(request):
    verifier = request.GET.get('oauth_verifier')
    if verifier is None:
        return HttpResponseRedirect(reverse('topLinks:index'))

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    token = request.session.get('request_token')
    request.session.delete('request_token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get request token.')

    request.session['key'] = auth.access_token
    request.session['secret'] = auth.access_token_secret

    return HttpResponseRedirect(reverse('topLinks:home'))

#After the user logged in, the home page view
def homeView(request):
    if not checkKey(request):
        return HttpResponseRedirect(reverse('topLinks:index'))
        
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    key = request.session['key']
    secret = request.session['secret']
    auth.set_access_token(key, secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    request.session['username'] = api.me().screen_name
    request.session['name'] = api.me().name

    tweets = []
    Tweets.objects.all().delete()
    for status in tweepy.Cursor(api.home_timeline).items(150):
        urls = status.entities['urls']
        #finding link in a tweet and checking if it is not a retweet link
        if urls and urls[0]['display_url'][0:7] != 'twitter' and checkTweet(status):
            url = 'https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2FInterior%2Fstatus%2F' + status.id_str
            tweets.append(tweetTags(url))
            
            users = Author.objects.filter(username = status.user.screen_name)
            if len(users) == 0:
                Author(username = status.user.screen_name).save()

            #extracting domain from a link
            info = tldextract.extract(urls[0]['display_url'])
            tweet = Tweets(tweet_id = status.id, username = Author.objects.get(username = status.user.screen_name), domain = info.domain)
            tweet.save()

    top_sharers = getTopSharer()
    top_domains = getTopDomain()

    return render(request, 'topLinks/home.html', {
        'tweets': tweets,
        'top_sharers': top_sharers,
        'top_domains': top_domains
    })

#Logout the user
def unauth(request):
    if (checkKey(request)):
        request.session.clear()
        logout(request)
    return HttpResponseRedirect(reverse('topLinks:index'))

#check if users token are still in session or not 
def checkKey(request):
    try:
        access_key = request.session.get('key', None)
        if not access_key:
            return False

    except KeyError:
        return False

    return True

#get the twitter card from official twitter API
def tweetTags(url):
    tweetjson = requests.get(url).json()
    tweethtml = tweetjson['html']
    return tweethtml

#Check if tweet is within 7 days time
def checkTweet(tweet):
    days_old = (datetime.now() - tweet.created_at).days
    if days_old < 8:
        return True
    return False

#Query to find the User that shared maximum domains
def getTopSharer():
    query = Tweets.objects.values('username__username').annotate(total=Count('username__username')).order_by('-total')
    
    top_sharer = []
    count = 0
    for q in query:
        top_sharer.append(q)
        count += 1
        if count == 3:
            break
    return top_sharer
    
#Query to find the domain that is shared maximum times
def getTopDomain():
    query = Tweets.objects.values('domain').annotate(total=Count('domain')).order_by('-total')
    top_domain = []
    count = 0
    for q in query:
        top_domain.append(q)
        count += 1
        if count == 3:
            break
    return top_domain