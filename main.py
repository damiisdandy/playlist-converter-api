from fastapi import FastAPI, HTTPException
from ytmusicapi import YTMusic
from models.index import GetPlaylist, Playlist
from utils.index import get_playlist_source

ytmusic = YTMusic()
app = FastAPI()


@app.post("/get-playlist", response_model=Playlist)
async def get_playlist(data: GetPlaylist):
    playlist = {}
    playlist_data = get_playlist_source(data.url)
    if playlist_data is None:
        raise HTTPException(status_code=400, detail="playlist url is invalid")
    if playlist_data.get("source") == 'YOUTUBE':
        try:
            gotten_playlist = ytmusic.get_playlist(
                playlist_data.get("playlist_id"))
            tracks = []
            for track in gotten_playlist.get("tracks"):
                artists = ""
                for artist in track.get("artists"):
                    if track.get("artists")[-1].get("name") != artist.get("name"):
                        artists += (artist.get("name") + ", ")
                    else:
                        artists += artist.get("name")
                tracks.append({
                    "title": track.get("title"),
                    "artists": artists,
                    "duration": track.get("duration"),
                    "thumbnail": track.get("thumbnails")[0].get("url"),
                    "album": track.get("album").get("name") if track.get("album") is not None else "",
                    "isExplicit": track.get("isExplicit"),
                    "searchKey": track.get("title") + " " + track.get("album").get("name") if track.get("album") is not None else ""
                })
            playlist = {
                "id": gotten_playlist.get('id'),
                "title":  gotten_playlist.get('title'),
                "description":  gotten_playlist.get('description'),
                "thumbnail": gotten_playlist.get('thumbnails')[0].get("url"),
                "author":  gotten_playlist.get('author').get("name"),
                "year":  gotten_playlist.get('year'),
                "duration":  gotten_playlist.get('duration'),
                "trackCount":  gotten_playlist.get('trackCount'),
                "tracks": tracks
            }
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"problem getting playlist - {e}")
    return playlist
