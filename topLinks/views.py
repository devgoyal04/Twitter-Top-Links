from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import logout

from datetime import datetime

import requests
import tweepy
import tldextract

CONSUMER_KEY = '6Uff1eSm3Filj2q26cFVSehfM'
CONSUMER_SECRET = '2khEE2qd6pMtdJen5obJgEuQzpb9hgFQM1qNaAAfjWcdjLljuu'
CALLBACK_URL = 'http://127.0.0.1:8000/callback'

def indexView(request):
    if (checkKey(request)):
        return HttpResponseRedirect(reverse('topLinks:home'))
    else:
        return render(request, 'topLinks/index.html', {})

def oauth(request):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth_url = auth.get_authorization_url()
    response = HttpResponseRedirect(auth_url)

    request.session['request_token'] = auth.request_token
    return response

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
    for status in tweepy.Cursor(api.home_timeline).items(100):
        urls = status.entities['urls']
        if urls and urls[0]['display_url'][0:7] != 'twitter' and checkTweet(status):
            url = 'https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2FInterior%2Fstatus%2F' + status.id_str
            tweets.append(tweetTags(url))
            info = tldextract.extract(urls[0]['display_url'])
            print(info.domain)

    return render(request, 'topLinks/home.html', {'tweets': tweets})

def unauth(request):
    if (checkKey(request)):
        request.session.clear()
        logout(request)
    return HttpResponseRedirect(reverse('topLinks:index'))

def checkKey(request):
    try:
        access_key = request.session.get('key', None)
        if not access_key:
            return False

    except KeyError:
        return False

    return True

def tweetTags(url):
    tweetjson = requests.get(url).json()
    tweethtml = tweetjson['html']
    return tweethtml

def checkTweet(tweet):
    days_old = (datetime.now() - tweet.created_at).days
    if days_old < 8:
        return True
    return False
