# Playlist Converter API v1 🎛️
This application simply converts playlists from youtube to spotify and vice-versa.

> Note: there is no form of authentication so playlists aren't created nor stored they are jsut display in the response.

## Usage
You can read the api documentation [here](https://api-playlist-converter.damiisdandy.com/docs)
### Get Playlist Info
```bash
  curl -X 'POST' \
  'https://api-playlist-converter.damiisdandy.com/get-playlist' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "youtube-or-spotify-url-goes-here"
}'
```

### Generate Playlist
```bash
  curl -X 'POST' \
  'https://api-playlist-converter.damiisdandy.com/generate-playlist' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "playlist_url": "youtube-url-goes-here",
  "convert_to": "SPOTIFY"
}'
```

## Getting Started
```bash
  git clone https://github.com/damiisdandy/playlist-converter-api.git
  cd playlist-converter-api

  # activate virtual env (https://docs.pipenv.org/basics/#example-pipenv-workflow)
  pipenv shell --python 3.10

  # copy variables from `template.env` to `.env`
  cp template.env .env

  # setup redis locally or use remnote credentials (https://redis.io/docs/install/install-stack/docker/)
  # you can navigate to localhost:8001 to see the redis client
  docker run -d --name playlist-converter -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
  # (optional) you can also run redis cli 
  docker exec -it playlist-converter redis-cli

  # Install dependencies
  pipenv install

  # start application
  uvicorn app.main:app --reload

  # navigate to http://localhost:8000/docs to view API docs

```

## Running Tests
Unit tests are written with the python in-built `unittest`  package
```
python -m unittest app/utils/test.py
```
You can test the Spotify and Youtube Music Playlist URLs in `/tests.txt`

## Application Architecture
![Playlist Conversion API Application Architecture](/assets/application-flow.png)

## File Structure
```bash
app
│   ├── constants.py # global constants
│   ├── dependencies.py # app dependencies
│   ├── main.py # app root
│   ├── models
│   │   └── main.py # where models are declare we can see that converting to Spotify is ed
│   ├── services
│   │   ├── spotify.py # connect to spotify api
│   │   └── youtube.py # connect to youtbe api
│   └── utils
│       ├── parse_track.py # convert JSON to Track object
│       ├── parser.py # parse string and URLs
│       └── test.py # tests

```

## Design Doc

Note: So far I only plan on converting Spotify and Youtube Music playlists! (I am not trying to commercialize this)

### Main goals
1. Ability to fetch playlist from playlist URL
2. Ensure playlists on all platforms are re-modeled to be structured the same way.
3. Loop through  Playlist A and search for each corresponding song for Playlist B e.g. loop through YouTube music playlists and search for the same songs on Spotify.
    1. Implement the full ability of search that the API provides e.g Spotify API search can accept queries like this `artist:{artist} {q_track.title}` 
4. Cache already converted tracks, so we do not need to go through the expensive task of searching for each song all the time.
5. Return the search result / cached data.


### **Potential Performance issues and solutions**
#### Searching for each song in a playlist
To convert from one playlist to another, simply search for each song in Playlist A within Platform B, then rebuild or add up search results as Playlist B. 

The best Big O notation we can get here is `O(n)` since we have to loop through each song in the playlist. Searching for a song with the external API can be slow and since we'll end up searching for 1 to n amount of songs, we'll need to cache already searched results so we simply fetch the data from Redis instead of hitting the external API every time.

I will measure the time difference between a brand new request and the same request being run again, to see the time saved!



### More on Caching
For caching, we are using [Redis](https://redis.io/). I want to cache as many songs as I can but I have to consider te we can see that converting to Spotify is he amount of data stored since I am using this as a **CACHE. **I'll periodically clear cached songs based on the time used. a song after being cached should have a life span of 48 hours.

I will cache a song when it gets fetched either through "get from the playlist URL" or "direct search", this way I can simply cache both platforms simultaneously.

### How I plan to increase quality
because not all songs on platform A are on platform B and their information might not be equal either. we will face some inaccuracies within the search.  understanding that I am limited to the search quality of the platforms themselves and their search flexibility.

I have to include more information in the search in other to narrow down the songs. e.g. Including the artist's name, album, song duration, etc.

### Why I chose to cache the songs only
I cache songs, not playlists mainly because not every playlist is the same, but you can see the same song on multiple playlists. you might think well why not just cache it for the `/get-playlist`  request, it will make hitting the request again a lot quicker. Yes! **but **the issue comes from its unique identifier, if we simply use the playlist's `id` , then when the playlist is updated we won't send the updated version, so cache TTL (time to live) would need to be short (< 1min) I guess this is only good for someone who tries spamming. A way to solve this is to concatenate the `id` and `duration` but remember that we only get the playlist `id` from its URL and no other important information. 

### How do I measure quality/similarities?
To measure the similarity between each song converted, I simply compare the following properties:

1. Title (remove additional strings like (feat. XXXXX))
2. Album
3. Artist
4. Song Duration (should offset 2 secs max)
A perfectly matched song would score 4/4 (100%)

### Performace Reading
|          | no caching | half cached | fully cached |
|----------|------------|-------------|--------------|
| SP -> YT | 21.23s     | 5.59s       | 0.38s        |
| YT -> SP | 3.96s      | 2.48s       | 0.45s        |


SP: Spotify
<br/>
YT: Youtube Music

I've calculated the time it takes for each request ranging from no-caching to fully-cached, each test was done with a playlist with 20 songs. noticiably we can see that converting to Spotify is much faster! More likely due to the flexibility of spotify's search query and/or just being a faster API.

From the looks of it the performance from no caching to fully cached gave us a performance increase of **5486.84%** (x55) ⚡. 

> Disclaimer: these tests were run locally on a high-end system

### Final Note
I used this project to learn more about [Redis](https://redis.io/) and caching in general. There will always be room for improvement in the code. feel free to create a PR!