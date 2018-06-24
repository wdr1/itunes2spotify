import sys
import pprint
import spotipy
import spotipy.util as util

scope = 'user-library-read playlist-modify-private'
spotifyObject = None
username = ""
iTunes2spotifyMapping = {"Name": "track", "Artist": "artist", "Album": "album"}

def getUserToken():
    global username
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Usage: %s username" % (sys.argv[0],)
        sys.exit()

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
    searchString = trackDict2SpotifySearchString(trackDict)
    results = spotifyObject.search(q=searchString, type='track')
    return results['tracks']['items'][0]['uri']

def createPlaylist(playListName):
    spotifyObject.user_playlist_create(username, playListName, public=False)

def addSpotifyURItoPlaylist(spotifyURI, playlistName):
    Null


def main():
    token = getUserToken();
    testDict = {'album': 'Live In London', 'track': 'Dance Me To The End Of Love', 'artist': 'Leonard Cohen'}
    pprint.pprint( findSpotifyURI(testDict) )
    createPlaylist("Test1")

if __name__ == "__main__":
    main()
