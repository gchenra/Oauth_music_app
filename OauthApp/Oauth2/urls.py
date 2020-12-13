from django.urls import path
from . import views

urlpatterns = [
    path('spotify', views.spotifyAuth, name='spotify_auth'),
    path('youtube', views.youtubeAuth, name='youtube_auth'),
    path('spotify/callback', views.spotifyCallback, name='spotify_callback'),
    path('youtube/callback', views.youtubeCallback, name='youtube_callback'),
    path('recs', views.getRecs, name='get_recommendations')
]