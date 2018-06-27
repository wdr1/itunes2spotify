import sys
import pprint
import shelve
import time

import random

import spotipy
import spotipy.util as util

spotifyObject = None
username = ""
iTunes2spotifyMapping = None

uriCache = None
uriFilename = ".uricache"

maxSongsPerAddTracksCall = 20
jankyRateLimitingWaitTime = 500 # milliseconds
jankyRateLimitingLastRequestTime = None

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

# Check if we already have the URI.  When we don't retreive, cache, while
# rate-limiting so Spotify doesn't get cranky
def tracks2SpotifyURIs( tracks ):
    global uriCache, uriFilename
    if uriCache is None:
        uriCache = shelve.open(uriFilename)

    results = []
    for t in tracks:
        searchString = trackDict2SpotifySearchString(t)
        if searchString in uriCache:
            results.append(uriCache[searchString])
        else:
            jankyRateLimiting()
            songURI = findSpotifyURI(t)
            results.append(songURI)
            uriCache[ searchString ] = songURI
    uriCache.close()
    return results

# Make sure we don't hammer Spotify
def jankyRateLimiting():
    global jankyRateLimitingLastRequestTime
    now = int(round(time.time() * 1000))

    if jankyRateLimitingLastRequestTime is None:
        jankyRateLimitingLastRequestTime = now
        return

    timeSince = now - jankyRateLimitingLastRequestTime
    jankyRateLimitingLastRequestTime = now

    if timeSince < jankyRateLimitingWaitTime:
        waitTime = (jankyRateLimitingWaitTime - timeSince)/1000.0
        print "Waiting %1.2f" % waitTime
        time.sleep( waitTime )


def findSpotifyURI(trackDict):
    searchString = trackDict2SpotifySearchString(trackDict)
    results = spotifyObject.search(q=searchString, type='track')
    # TODO: If the song isn't found
    return results['tracks']['items'][0]['uri']

def createPlaylist(playlistName):
    playlistName += " " + str(int(time.time()))
    print "Created playlist '%s'" % playlistName
    playlistObject = spotifyObject.user_playlist_create(username, playlistName, public=False)
    return playlistObject["id"]

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def addSpotifyURIstoPlaylist(playlistId, songUris):
    for group in chunker(songUris, maxSongsPerAddTracksCall):
            jankyRateLimiting()
            results = spotifyObject.user_playlist_add_tracks(username, playlistId, group)

def addTracksToPlaylist(playlistName, tracks):
    getUserToken()
    songUris = tracks2SpotifyURIs(tracks)
    playlistId = createPlaylist(playlistName)

    addSpotifyURIstoPlaylist(playlistId, songUris)
