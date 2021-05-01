import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from secrets import client_token, secret_token
import spotipy.util as util
import requests
import json
import .cache


def getTracksIDFromPlaylist(spotify, username_id, playlist_id):

    trackList = [] 
    flag = True
    #while(flag):
    results = spotify.user_playlist(username_id, playlist_id, fields='tracks,next,name')
    print(results)
    songs = results['tracks']
    items = songs['items']
    for track in items:
        id = track['track']
        trackList.append(id['id'])
        #if(len(trackList)%100 !=0 ):
        #    flag = False
    return trackList


# SONGS FROM PLAYLIST_A THAT ARE MISSING  ON PLAYLIST_B
def checkPlaylists(spotify, username_id_A, username_id_B, playlist_id_A, playlist_id_B):

    result_A = getTracksIDFromPlaylist(spotify, username_id_A,playlist_id_A)

    result_B = getTracksIDFromPlaylist(spotify, username_id_B,playlist_id_B)

    missing_on_B = list(set(result_A)-set(result_B))

    name_list = []

    for song_id in missing_on_B:

        results = spotify.track(song_id,None)
        track_name = results['name']
        track_link = results['external_urls']
        name_list.append(
            track_name + ' - ' + 
            track_link['spotify']
        )
    
    return name_list

def checkCommonSongs(spotify, username_id_A, username_id_B, playlist_id_A, playlist_id_B):

    result_A = getTracksFromIDPlaylist(spotify, username_id_A,playlist_id_A)

    result_B = getTracksFromIDPlaylist(spotify, username_id_B,playlist_id_B)

    name_list_A = []

    name_list_B = []

    for song_id in result_A:

        results = spotify.track(song_id,None)
        track_name = results['name']
        track_link = results['external_urls']
        name_list_A.append(
            (track_name,track_link['spotify'])
        )

    for song_id in result_B:

        results = spotify.track(song_id,None)
        track_name = results['name']
        track_link = results['external_urls']
        name_list_B.append(
            track_name + ' - ' + 
            track_link['spotify']
        )

    common_songs = set(name_list_A) - (set(name_list_A) - set(name_list_B))

    return common_songs


def checkCommonSongsHTML(client_token, secret_token, playlist_id_A, username_id_A, playlist_id_B, username_id_B):

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_token, client_secret=secret_token))

    missing_on_A = checkPlaylists(spotify, username_id_A,username_id_B,playlist_id_A, playlist_id_B)
    missing_on_B = checkPlaylists(spotify, username_id_B,username_id_A,playlist_id_B, playlist_id_A)
    common_songs = checkCommonSongs(spotify, username_id_B,username_id_A,playlist_id_B, playlist_id_A)

    text = """
        <!DOCTYPE html>\n
        <html>\n
        <header>\n
        <title>Missing songs from playlists</title>\n
        <meta charset="UTF-8"/>\n
        </header>\n
        <body>\n
        <h2>Songs from A that are not in B:</h2>\n
        <ul>\n
        """
    for item in missing_on_A:
        text.append("<li>"+item+"</li>\n")
    text.append("""
        </ul>\n
        <h2>Songs from B that are not in A:</h2>\n
        <ul>\n
        """)
    for item in missing_on_B:
       text.append("<li>"+item+"</li>\n")
    text.append("""
        </ul>\n
        <h2>Songs that are in both:</h2>\n
        <ul>\n
        """)
    for item in common_songs:
        text.append("<li>"+item+"</li>\n")
    text.append("""
        </ul>\n
        </body>\n
        </html>\n
        """)

    file = open("common_songs.html","w")
    file.write(text)
    file.close()

def dividePlaylists(client_token,secret_token,playlist_id,username_id,name_A,name_B,year):

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_token, client_secret=secret_token))
    #Browser Auth
    SCOPE = ('user-read-recently-played,user-library-read,user-read-currently-playing,playlist-read-private,playlist-modify-private'+
             ',playlist-modify-public,user-read-email,user-modify-playback-state,user-read-private,user-read-playback-state')
    sp_oauth = oauth2.SpotifyOAuth(client_token, secret_token,'http://localhost:8888/callback/',scope=SCOPE)
    code = sp_oauth.get_auth_response(open_browser=True)
    token = sp_oauth.get_access_token(code)
    refresh_token = token['refresh_token']
    sp = spotipy.Spotify(auth=token['access_token'])
    username = sp.current_user()['id']

    song_id_list = getTracksIDFromPlaylist(spotify,username_id,playlist_id)

    song_list_over  = []
    song_list_under = []

    #Sorting
    for song_id in song_id_list:
        result = spotify.track(song_id,None)
        release_date = result['album']['release_date']
        date = release_date.split("-")
        if(int(date[0])<year):
            song_list_under.append(song_id)
        else:
            song_list_over.append(song_id)

    #Creating playlists
    id_A = create_playlist(sp,code,token,username,name_A)
    id_B = create_playlist(sp,code,token,username,name_B)

    sp.playlist_add_items(id_A,song_list_under,0)
    sp.playlist_add_items(id_B,song_list_over,0)

def create_playlist(sp,code,token,username,playlist_name):
    cp = sp.user_playlist_create(username,playlist_name,True,False,'created by the best script out there')
    return cp["id"]
