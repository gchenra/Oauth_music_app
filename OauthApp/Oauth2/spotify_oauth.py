import logging
import requests
import base64
from decouple import config
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from . import models

logger = logging.getLogger(__name__)
CLIENT_ID = config('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SCOPE = 'user-top-read user-follow-read '
REDIRECT_URI = 'http://localhost:8000/auth/spotify/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'


def getSpotifyAuthCode() -> HttpResponse:
    request_params = urlencode({
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code'
    })
    request_url = f'{AUTH_URL}/?{request_params}'

    return redirect(request_url)


def getSpotifyTokens(auth_code: str, userid: int) -> None:
    """
    :param auth_code:
    :return: None
    obtain access_token and refresh_token and store it in database
    """
    request_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    resp = requests.post(TOKEN_URL, data=request_params)
    # check status code
    if resp.status_code/100 != 2:
        logger.error('receiving non 2XX response when requesting Oauth token')
        raise Exception('receiving non 2XX response when requesting Oauth token')

    # get access token and refresh token
    # store them in database
    json_resp = resp.json()
    access_token = json_resp.get('access_token', "")
    refresh_token = json_resp.get('refresh_token', "")
    if access_token and refresh_token:
        models.SpotifyAuth.objects.create(
            user_id=userid,
            access_token=access_token,
            refresh_token=refresh_token
        )
    else:
        logger.error("response when requesting spotify tokens is not right")
        raise Exception("response when requesting spotify tokens is not right")


def getNewTokens(userid: int) -> str:
    """Return the new access token"""
    # make request to the api/token with refresh code ...
    cur_tokens = models.SpotifyAuth.objects.get(user_id=userid)
    request_params = {
        'grant_type': 'refresh_token',
        'refresh_token': cur_tokens.refresh_token
    }
    client_info = CLIENT_ID+':'+CLIENT_SECRET
    resp = requests.post(
        TOKEN_URL,
        headers={
            'Authorization': f"Basic {base64.b64encode(client_info.encode('ascii')).decode('ascii')}"
        },
        data=request_params
    )
    json_resp = resp.json()
    print(json_resp)
    access_token = json_resp.get('access_token', "")
    if access_token:
        cur_tokens.access_token = access_token
        cur_tokens.save()
    else:
        logger.error("response when refresh spotify tokens is not right")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("response when refresh spotify tokens is not right")

    return access_token


def getTopTracks(userid: int) -> dict:
    try:
        user_tokens = models.SpotifyAuth.objects.get(user_id=userid)
    except ObjectDoesNotExist as e:
        logger.error("This user has not authorize our app access to spotify")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when getting spotify top tracks: {e}")

    track_url = "https://api.spotify.com/v1/me/top/tracks"
    request_param = {
        'limit': 5,
    }
    resp = requests.get(
        track_url,
        headers={
            'Authorization': f'Bearer {user_tokens.access_token}'
        },
        params=request_param
    )

    if resp.status_code == 401:
        new_access_token = getNewTokens(userid)
        resp = requests.get(
            track_url,
            headers={
                'Authorization': f'Bearer {new_access_token}'
            },
            params=request_param
        )
    if resp.status_code / 100 == 4:
        logger.error(f"Error when requesting spotify top tracks: {resp.text}")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when requesting spotify top tracks: {resp.text}")

    return resp.json()


def getFollowingArtists(userid: int) -> dict:
    try:
        user_tokens = models.SpotifyAuth.objects.get(user_id=userid)
    except ObjectDoesNotExist as e:
        logger.error("This user has not authorize our app access to spotify")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when getting spotify top artists: {e}")

    track_url = "https://api.spotify.com/v1/me/following"
    request_param = {
        'type': 'artist',
        'limit': 5,
    }
    resp = requests.get(
        track_url,
        headers={
            'Authorization': f'Bearer {user_tokens.access_token}'
        },
        params=request_param
    )

    if resp.status_code == 401:
        new_access_token = getNewTokens(userid)
        resp = requests.get(
            track_url,
            headers={
                'Authorization': f'Bearer {new_access_token}'
            },
            params=request_param
        )
    if resp.status_code / 100 == 4:
        logger.error(f"Error when requesting spotify top tracks: {resp.text}")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when requesting spotify top tracks: {resp.text}")

    return resp.json()


def getPlaylist(userid: int) -> dict:
    try:
        user_tokens = models.SpotifyAuth.objects.get(user_id=userid)
    except ObjectDoesNotExist as e:
        logger.error("This user has not authorize our app access to spotify")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when getting spotify top artists: {e}")


def getSpotifyRecs(userid, track_seeds, artist_seeds, genre_seeds):
    try:
        user_tokens = models.SpotifyAuth.objects.get(user_id=userid)
    except ObjectDoesNotExist as e:
        logger.error("This user has not authorize our app access to spotify")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when getting spotify top artists: {e}")

    rec_url = "https://api.spotify.com/v1/recommendations"
    request_params = {
        'limit': 10,
        'seed_artists': artist_seeds,
        'seed_genres': genre_seeds,
        'seed_tracks': track_seeds
    }
    resp = requests.get(
        rec_url,
        headers={
            'Authorization': f'Bearer {user_tokens.access_token}'
        },
        params=request_params
    )

    if resp.status_code == 401:
        new_access_token = getNewTokens(userid)
        resp = requests.get(
            rec_url,
            headers={
                'Authorization': f'Bearer {new_access_token}'
            },
            params=request_params
        )
    if resp.status_code / 100 == 4:
        logger.error(f"Error when requesting spotify top tracks: {resp.text}")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print(f"Error when requesting spotify top tracks: {resp.text}")

    return resp.json()
