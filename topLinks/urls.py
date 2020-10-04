from django.urls import path

from .views import oauth, indexView, callback, homeView

app_name = 'topLinks'

urlpatterns = [
    path('', indexView, name = 'index'),
    path('auth/', oauth, name = 'oauth'),
    path('callback/', callback, name = 'callback'),
    path('home/', homeView, name = 'home'),
]
