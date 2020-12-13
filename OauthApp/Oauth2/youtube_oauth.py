import google.oauth2.credentials
import google_auth_oauthlib.flow
import logging
from googleapiclient.discovery import build
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from decouple import config
from typing import List
from . import models

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
CLIENT_ID = config('YOUTUBE_CLIENT_ID')
CLIENT_SECRET = config('YOUTUBE_CLIENT_SECRET')


def getYoutubeAuthCode() -> HttpResponse:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'Oauth2/google_client_secret.json',
        scopes=SCOPES
    )
    flow.redirect_uri = 'http://localhost:8000/auth/youtube/callback'
    global state
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        include_granted_scope='true'
    )

    return redirect(auth_url)


def getYoutubeTokens(auth_code: str, user_id: int) -> None:
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'Oauth2/google_client_secret.json',
            scopes=SCOPES
        )
        flow.redirect_uri = 'http://localhost:8000/auth/youtube/callback'
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        models.YoutubeAuth.objects.create(
            user_id=user_id,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri
        )
    except Exception as e:
        raise Exception(e)


def searchYoutube(userid: int, artists: List[str], genres: List[str]) -> List:
    try:
        cur_user = models.YoutubeAuth.objects.get(user_id=userid)
    except ObjectDoesNotExist as e:
        logger.error("This user has not authorize our app access to YouTube.")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when search in YouTube: {e}")

    video_base_url = "https://www.youtube.com/watch?v="
    videos = []
    credentials = google.oauth2.credentials.Credentials(
        token=cur_user.access_token,
        refresh_token=cur_user.refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    yt_client = build('youtube', 'v3', credentials=credentials)

    for artist in artists:
        search_resp = yt_client.search().list(
            q=artist,
            type='video',
            maxResults=2,
            part='id,snippet'
        ).execute()
        for result in search_resp.get('items', []):
            videos.append({
                'title': result['snippet']['title'],
                'url': video_base_url + result['id']['videoId']
            })

    for genre in genres:
        search_resp = yt_client.search().list(
            q=genre,
            type='video',
            maxResults=2,
            part='id,snippet'
        ).execute()
        for result in search_resp.get('items', []):
            videos.append({
                'title': result['snippet']['title'],
                'url': video_base_url + result['id']['videoId']
            })

    return videos

