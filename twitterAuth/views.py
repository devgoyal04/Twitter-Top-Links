from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

import tweepy

CONSUMER_KEY = '6Uff1eSm3Filj2q26cFVSehfM'
CONSUMER_SECRET = '2khEE2qd6pMtdJen5obJgEuQzpb9hgFQM1qNaAAfjWcdjLljuu'
CALLBACK_URL = 'http://127.0.0.1:8000/callback'

def homeView(request):
    return render(request, 'home.html', {})

def oauth(request):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth_url = auth.get_authorization_url()
    response = HttpResponseRedirect(auth_url)

    request.session['request-token'] = auth.request_token
    return response

def callback(request):
    verifier = request.GET.get('oauth_verifier')
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    token = request.session.get('request-token')
    request.session.delete('request-token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    return HttpResponseRedirect(reverse('twitterAuth:home'))
