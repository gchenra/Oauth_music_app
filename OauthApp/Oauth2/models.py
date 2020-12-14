from django.db import models


class SpotifyAuth(models.Model):
    user_email = models.CharField(max_length=360, null=False, unique=True, default="null@email.com")
    access_token = models.CharField(max_length=360, null=False, default="")
    refresh_token = models.CharField(max_length=360, null=False, default="")


class YoutubeAuth(models.Model):
    user_email = models.CharField(max_length=360, null=False, unique=True, default="null@email.com")
    access_token = models.CharField(max_length=360, null=False, default="")
    refresh_token = models.CharField(max_length=360, null=False, default="")
    token_uri = models.CharField(max_length=526, null=False, default="")
