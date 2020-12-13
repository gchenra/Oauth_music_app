from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from . import spotify_oauth
from . import youtube_oauth
from . import recommend_gen
import logging
from . import models

logger = logging.getLogger(__name__)
cur_spotify_user = 0
cur_youtube_user = 0


def spotifyAuth(request: HttpRequest) -> HttpResponse:
    # check oauth tokens in DB
    global cur_spotify_user
    cur_spotify_user = request.GET.get('userid', default=None)
    try:
        if cur_spotify_user:
            models.SpotifyAuth.objects.get(user_id=cur_spotify_user)
            return HttpResponse("You've already authorized us access to Spotify")
        else:
            return HttpResponse("No user identity specified in the request", status=400)
    except ObjectDoesNotExist:
        pass

    # if not go get the auth code
    return spotify_oauth.getSpotifyAuthCode()


def spotifyCallback(request: HttpRequest) -> HttpResponse:
    auth_code = request.GET.get('code', default=None)
    if not auth_code:
        error = request.GET.get('error')
        logger.error(f'User did not accept spotify authorization: {error}')
        print(f'User did not accept spotify authorization: {error}')
        return HttpResponse("User refuse to authorize access to Spotify", status=403)
    try:
        spotify_oauth.getSpotifyTokens(auth_code, cur_spotify_user)
    except Exception as e:
        logger.error(f"Error when requesting for Spotify access token: {e}")
        return HttpResponse("Error when requesting for Spotify access token", status=500)

    return HttpResponse("Spotify Oauth2 succeeded!!!")


def youtubeAuth(request:HttpRequest) -> HttpResponse:
    global cur_youtube_user
    cur_youtube_user = request.GET.get('userid', default=None)
    try:
        if cur_youtube_user:
            models.YoutubeAuth.objects.get(user_id=cur_youtube_user)
            return HttpResponse("You've already authorized us access to YouTube")
        else:
            return HttpResponse("No user identity specified in the request", status=400)
    except ObjectDoesNotExist:
        pass

    return youtube_oauth.getYoutubeAuthCode()


def youtubeCallback(request: HttpRequest) -> HttpResponse:
    auth_code = request.GET.get('code', default=None)
    if not auth_code:
        error = request.GET.get('error')
        logger.error(f'User did not accept YouTube authorization: {error}')
        print(f'User did not accept YouTube authorization: {error}')
        return HttpResponse("User refuse to authorize access to YouTube", status=403)
    try:
        youtube_oauth.getYoutubeTokens(auth_code, cur_youtube_user)
    except Exception as e:
        logger.error(f"Error when requesting YouTube Oauth tokens: {e}")
        return HttpResponse("Error when requesting YouTube Oauth tokens", status=500)

    return HttpResponse("YouTube oauth succeeded!!!")


def getRecs(request: HttpRequest) -> HttpResponse:
    cur_user = request.GET.get('userid', default=None)
    if not cur_user:
        return HttpResponse("No user identity specified in the request", status=400)
    data = recommend_gen.getRecommends(cur_user)

    return JsonResponse(data)

