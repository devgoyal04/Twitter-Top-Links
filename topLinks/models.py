from django.db import models

class Author(models.Model):
    username = models.CharField(max_length=50)

    def __str__(self):
        return self.username
class Tweets(models.Model):
    tweet_id = models.CharField(max_length = 20)
    username = models.ForeignKey(Author, on_delete=models.CASCADE)
    domain = models.CharField(max_length = 50)

    def __str__(self):
        return self.domain