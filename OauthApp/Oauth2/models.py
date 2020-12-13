from django.db import models


class SpotifyAuth(models.Model):
    user_id = models.IntegerField(null=False)
    access_token = models.CharField(max_length=360, default="")
    refresh_token = models.CharField(max_length=360, default="")


class YoutubeAuth(models.Model):
    user_id = models.IntegerField(null=False)
    access_token = models.CharField(max_length=360, default="")
    refresh_token = models.CharField(max_length=360, default="")
    token_uri = models.CharField(max_length=526, default="")
