from typing import Tuple, List
from . import spotify_oauth, youtube_oauth
import logging

logger = logging.getLogger(__name__)


def getRecommends(user_email: int) -> dict:
    # returns a dictionary of top tracks
    result = {'items': []}
    spotify_tracks = spotify_oauth.getTopTracks(user_email)
    spotify_artists = spotify_oauth.getFollowingArtists(user_email)
    top_tracks, top_artist, artist_names, top_genres = getSpotifyPrefIDs(spotify_tracks, spotify_artists["artists"])
    spotify_recs = spotify_oauth.getSpotifyRecs(user_email, top_tracks, top_artist, top_genres)
    spotify_result = parseSpotifyResult(spotify_recs)
    youtube_result = youtube_oauth.searchYoutube(user_email, artist_names, top_genres)
    result['items'] += youtube_result + spotify_result

    return result


def getSpotifyPrefIDs(tracks: dict, artists: dict) -> Tuple[List[str]]:
    """Parse the top tracks info and get its name """
    track_ids, artist_ids, artist_names, genres = [], [], [], []
    if not tracks.get('items', []):
        # use sample track ids
        track_ids = [
            "2pTkHM7SsdwJUPzcrkbqOv",
            "4HUpIaMKPS0zPxMDl8P5fv",
            "0hRRNHeSZv2x6pHCcXPAct",
            "0XhJIckMs6b1crNGl9RUAB",
            "5LMRKvWAfPRMGOKUEXGS8J"
        ]
    else:
        for album in tracks['items']:
            track_ids.append(album['id'])

    if not artists.get('items', []):
        # use sample artist ids and genres
        artist_ids = [
            '0UaZ2BhteWRHOjZo7lEDXj',
            '63XBtGSEZINSyXylZxEUbv',
            '6LuN9FCkKOj5PcnpouEgny',
            '3ycxRkcZ67ALN3GQJ57Vig',
            '0I2XqVXqHScXjHhk6AYYRe'
        ]
        artist_names = [
            'Drake',
            'Kendrick Lamar',
            'Cardi B',
            'Jay Chou',
            'H.E.R'
        ]
        genres = ["hip_hop", "blues", "dance", "disco", "indie"]
    else:
        for artist in artists['items']:
            artist_ids.append(artist['id'])
            artist_names.append(artist['name'])
            genres.append(artist['genres'][0])

    return track_ids, artist_ids, artist_names, genres


def parseSpotifyResult(result: dict) -> List:
    if not result["tracks"]:
        logger.error("Empty song recommendation from Spotify")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("*********************************************************************************")
        print("Error: Empty song recommendation from Spotify")
        return {}
    rec_tracks = []

    for track in result["tracks"]:
        track_info = {}
        track_info["title"] = track["album"]["name"]
        artist_list = []
        for person in track["album"]["artists"]:
            artist_list.append(person["name"])
        track_info["artists"] = artist_list
        track_info["url"] = track["album"]["external_urls"]
        rec_tracks.append(track_info)

    return rec_tracks
