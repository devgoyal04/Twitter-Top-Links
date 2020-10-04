from django.urls import path

from .views import oauth, homeView, callback

app_name = 'twitterAuth'

urlpatterns = [
    path('', homeView, name = 'home'),
    path('auth/', oauth, name = 'oauth'),
    path('callback/', callback, name = 'callback'),
]
