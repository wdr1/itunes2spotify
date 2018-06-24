import sys
import pprint

import spotipy
import spotipy.util as util

spotifyObject = None
username = ""

iTunes2spotifyMapping = None


def getUserToken():
    global username

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Usage: %s username" % (sys.argv[0],)
        sys.exit()

    scope = 'user-library-read playlist-modify-private'
    token = util.prompt_for_user_token(username, scope)

    global spotifyObject
    if token:
        spotifyObject = spotipy.Spotify(auth=token)
    else:
        print "Can't get token for", username
        sys.exit()

    return token

def trackDict2SpotifySearchString(trackDict):
    s = ""
    for ituneKey, spotifyKey in iTunes2spotifyMapping.items():
        if spotifyKey in trackDict:
            s += spotifyKey + ':"' + trackDict[spotifyKey] + '" '
    return s


def findSpotifyURI(trackDict):
    # TODO: Some cachine here just in case it shits the bed mid-script
    searchString = trackDict2SpotifySearchString(trackDict)
    results = spotifyObject.search(q=searchString, type='track')
    return results['tracks']['items'][0]['uri']

def createPlaylist(playListName):
    playlistObject = spotifyObject.user_playlist_create(username, playListName, public=False)
    return playlistObject["id"]

def addSpotifyURIstoPlaylist(playlistID, songIDs):
    results = spotifyObject.user_playlist_add_tracks(username, playlistID, songIDs)
    pprint.pprint( results )