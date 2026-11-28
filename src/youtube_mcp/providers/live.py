"""Official YouTube Data API v3 adapter with per-request quota accounting."""
from contextvars import ContextVar
from datetime import datetime
from hashlib import sha256
import re
import shlex
from time import sleep
from urllib.parse import unquote, urlsplit

import httpx

from youtube_mcp.errors import (
    AuthRequiredError, ChannelRequiredError, ForbiddenError, NotFoundError,
    OverBudgetError, ProviderError, QuotaExceededError, RateLimitedError, ValidationError,
)
from youtube_mcp.models import (
    AuthStatus, Channel, Library, LikedVideo, PlaylistItem, Subscription, UserPlaylist,
    Video, parse_iso8601_duration,
)

API = "https://www.googleapis.com/youtube/v3/"
VIDEO_FIELDS = (
    "id,snippet(title,description,tags,channelId,channelTitle,categoryId,"
    "defaultAudioLanguage,defaultLanguage,publishedAt),contentDetails(duration),status/privacyStatus"
)
CHANNEL_FIELDS = (
    "id,snippet(title,description,customUrl),statistics(hiddenSubscriberCount,"
    "subscriberCount,videoCount),topicDetails(topicCategories),"
    "contentDetails(relatedPlaylists/uploads),brandingSettings(channel/keywords)"
)
ITEM_FIELDS = "snippet(publishedAt,resourceId/videoId)"
CHANNEL_ID = re.compile(r"UC[A-Za-z0-9_-]{22}")


def _date(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def _number(value):
    return int(value) if value is not None else None


def _video(row):
    snippet = row["snippet"]
    language = snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage")
    return Video(
        video_id=row["id"], title=snippet["title"], channel_id=snippet["channelId"],
        description=snippet.get("description"), tags=tuple(snippet.get("tags", [])),
        channel_title=snippet.get("channelTitle"), category_id=snippet.get("categoryId"),
        duration_s=parse_iso8601_duration(row.get("contentDetails", {}).get("duration", "")),
        language=language.split("-")[0].lower() if language else None,
        published_at=_date(snippet.get("publishedAt")),
    )


def _channel(row):
    snippet = row["snippet"]
    stats = row.get("statistics", {})
    keywords = row.get("brandingSettings", {}).get("channel", {}).get("keywords", "")
    try:
        tokens = tuple(shlex.split(keywords))
    except ValueError:
        tokens = tuple(keywords.split())
    custom = snippet.get("customUrl", "")
    return Channel(
        channel_id=row["id"], title=snippet["title"], description=snippet.get("description"),
        handle=custom if custom.startswith("@") else None,
        topics=tuple(row.get("topicDetails", {}).get("topicCategories", [])),
        keywords=tokens, subscriber_count=None if stats.get("hiddenSubscriberCount")
        else _number(stats.get("subscriberCount")), video_count=_number(stats.get("videoCount")),
        uploads_playlist_id=row.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads"),
    )


def _error(status, reason):
    if reason in {"quotaExceeded", "dailyLimitExceeded", "dailyLimitExceededUnreg"}:
        return QuotaExceededError("Google reports that the daily YouTube quota is exhausted.")
    if status == 429 or reason in {"rateLimitExceeded", "userRateLimitExceeded"}:
        return RateLimitedError("Google is rate limiting requests.")
    if reason == "youtubeSignupRequired":
        return ChannelRequiredError("The authorised account has no YouTube channel.")
    if status == 401 or reason in {"invalid_grant", "authError", "insufficientPermissions"}:
        return AuthRequiredError("Google requires a valid YouTube grant.")
    if status == 404:
        return NotFoundError("The requested YouTube resource could not be found.")
    if status == 403:
        return ForbiddenError("The requested YouTube operation is forbidden.")
    return ProviderError("The YouTube API request failed.")


class LiveProvider:
    def __init__(self, quota, *, api_key=None, oauth=None, http=None, read_only=False, wait=sleep):
        self.quota = quota
        self.api_key = api_key
        self.oauth = oauth
        self.http = http or httpx.Client(timeout=15)
        self.read_only = read_only
        self.wait = wait
        self._write_binding = ContextVar("write_binding", default=None)

    def _oauth(self):
        if self.oauth is None:
            raise AuthRequiredError("Configure desktop OAuth for this operation.")
        return self.oauth

    def _request(self, op, *, params, auth=None, body=None, token=None):
        cost = self.quota.cost_of(op)
        _, action = op.split(".")
        if action != "list" and (self.read_only or op not in {"playlists.insert", "playlistItems.insert"}):
            raise ForbiddenError("This provider configuration prohibits the requested write.")
        self.quota.check(cost)
        headers = {}
        if auth:
            credential = token or self._oauth().token(write=auth == "write")
            headers["Authorization"] = f"Bearer {credential}"
        elif self.api_key:
            headers["X-Goog-Api-Key"] = self.api_key
        elif self.oauth:
            headers["Authorization"] = f"Bearer {self.oauth.token()}"
        else:
            raise AuthRequiredError("Configure an API key or authorise YouTube for public metadata.")
        try:
            return self._dispatch(op, params, headers, body, cost)
        except RateLimitedError as error:
            if action != "list":
                raise
            try:
                self.quota.check(cost)
            except OverBudgetError:
                raise error from None
            self.wait(0.5)
            return self._dispatch(op, params, headers, body, cost)

    def _dispatch(self, op, params, headers, body, cost):
        resource, action = op.split(".")
        day = self.quota.record(cost)
        try:
            response = self.http.request(
                "GET" if action == "list" else "POST", API + resource,
                params=params, headers=headers, json=body,
            )
        except httpx.HTTPError:
            raise ProviderError("Could not reach the YouTube API.") from None
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        if response.is_error:
            details = data.get("error")
            errors = details.get("errors", []) if isinstance(details, dict) else []
            reason = errors[0].get("reason") if errors and isinstance(errors[0], dict) else None
            error = _error(response.status_code, reason)
            if isinstance(error, QuotaExceededError):
                bucket = "search" if cost.search else "general"
                self.quota.mark_exhausted(bucket, day=day)
                error.message += f" Next reset at {self.quota.status().resets_at.isoformat()}."
                error.args = (error.message,)
            raise error
        if not data:
            raise ProviderError("YouTube returned an invalid response.")
        return data

    def _items(self, op, *, part, fields, auth=None, pages=None, **params):
        count = 0
        seen = set()
        while True:
            data = self._request(op, auth=auth, params={
                "part": part, "fields": f"nextPageToken,items({fields})", **params,
            })
            yield from data.get("items", [])
            count += 1
            page = data.get("nextPageToken")
            if not page or (pages is not None and count >= pages):
                return
            if page in seen:
                raise ProviderError("YouTube returned a repeated page token.")
            seen.add(page)
            params["pageToken"] = page

    def _metadata(self, ids, op, part, fields, mapper, *, auth=None):
        ids = list(dict.fromkeys(ids))
        if not ids:
            return []
        self.quota.check(self.quota.cost_of(op, calls=(len(ids) + 49) // 50))
        result = {}
        for start in range(0, len(ids), 50):
            rows = self._items(op, part=part, fields=fields, pages=1,
                               auth=auth, id=",".join(ids[start:start + 50]))
            for row in rows:
                if auth is None and row.get("status", {}).get("privacyStatus") == "private":
                    continue
                result[row["id"]] = mapper(row)
        return [result[key] for key in ids if key in result]

    def get_videos(self, ids):
        return self._metadata(ids, "videos.list", "snippet,contentDetails,status", VIDEO_FIELDS, _video)

    def get_channels(self, ids):
        return self._metadata(ids, "channels.list",
                              "snippet,statistics,topicDetails,contentDetails,brandingSettings",
                              CHANNEL_FIELDS, _channel)

    def _search(self, query, kind, max_results, pages):
        if type(max_results) is not int or not 1 <= max_results <= 50:
            raise ValidationError("Search page size must be between 1 and 50.")
        if type(pages) is not int or not 1 <= pages <= 2:
            raise ValidationError("Search permits at most two pages.")
        self.quota.check(self.quota.cost_of("search.list", calls=pages))
        key = f"{kind}Id"
        rows = self._items("search.list", part="snippet", fields=f"id/{key}", pages=pages,
                           q=query, type=kind, maxResults=max_results)
        return list(dict.fromkeys(row["id"][key] for row in rows if key in row.get("id", {})))

    def search_videos(self, query, *, max_results=25, pages=1):
        return self._search(query, "video", max_results, pages)

    def search_channels(self, query, *, max_results=25):
        return self._search(query, "channel", max_results, 1)

    def resolve_channel(self, ref):
        if "://" in ref:
            parsed = urlsplit(ref)
            if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in {
                "youtube.com", "www.youtube.com", "m.youtube.com",
            }:
                raise ValidationError("Use a YouTube channel URL.")
            path = unquote(parsed.path).strip("/").split("/")
            if len(path) == 2 and path[0] in {"user", "channel"}:
                ref = "user:" + path[1] if path[0] == "user" else path[1]
            elif len(path) == 1 and path[0].startswith("@"):
                ref = path[0]
            else:
                raise ValidationError("Use a channel ID, handle, or supported channel URL.")
        if CHANNEL_ID.fullmatch(ref):
            return ref
        if ref.startswith("@") and len(ref) > 1 and not any(ch.isspace() for ch in ref):
            selector = {"forHandle": ref}
        elif ref.startswith("user:") and re.fullmatch(r"[A-Za-z0-9_-]+", ref[5:]):
            selector = {"forUsername": ref[5:]}
        else:
            raise ValidationError("Use a channel ID or handle.")
        rows = list(self._items("channels.list", part="id", fields="id", pages=1, **selector))
        if len(rows) != 1:
            raise NotFoundError("The channel could not be uniquely resolved.")
        return rows[0]["id"]

    def get_recent_uploads(self, channel_id, n=10):
        if type(n) is not int or not 1 <= n <= 50:
            raise ValidationError("Recent upload count must be between 1 and 50.")
        self.quota.check(self.quota.cost_of("channels.list", calls=3))
        channels = self.get_channels([channel_id])
        if not channels:
            raise NotFoundError("The channel could not be found.")
        playlist_id = channels[0].uploads_playlist_id
        if not playlist_id:
            return []
        rows = self._items("playlistItems.list", part="snippet", fields=ITEM_FIELDS, pages=1,
                           playlistId=playlist_id, maxResults=n)
        return self.get_videos([row["snippet"]["resourceId"]["videoId"] for row in rows])

    def get_categories(self, region="US"):
        rows = self._items("videoCategories.list", part="snippet", fields="id,snippet/title",
                           pages=1, regionCode=region)
        return {row["id"]: row["snippet"]["title"] for row in rows}

    def _mine(self, *, write=False, token=None):
        data = self._request("channels.list", auth="write" if write else "read", token=token,
                             params={"part": "contentDetails", "mine": "true",
                                     "fields": "items(id,contentDetails/relatedPlaylists/likes)"})
        items = data.get("items", [])
        if len(items) != 1:
            raise ChannelRequiredError("Select an account with a single active YouTube channel.")
        return items[0]

    def account_fingerprint(self):
        return sha256(("youtube-channel:" + self._mine()["id"]).encode()).hexdigest()

    def _playlist_entries(self, playlist_id):
        rows = self._items("playlistItems.list", part="snippet", fields=ITEM_FIELDS, auth="read",
                           playlistId=playlist_id, maxResults=50)
        return [(row["snippet"]["resourceId"]["videoId"], _date(row["snippet"].get("publishedAt")))
                for row in rows]

    def get_library(self):
        self.quota.check(self.quota.cost_of("channels.list", calls=4))
        mine = self._mine()
        playlist = mine.get("contentDetails", {}).get("relatedPlaylists", {}).get("likes")
        likes = None
        if playlist:
            try:
                likes = self._playlist_entries(playlist)
            except (NotFoundError, ForbiddenError):
                pass
        if likes is None:
            rows = self._items("videos.list", part="id", fields="id", auth="read",
                               myRating="like", maxResults=50)
            likes = [(row["id"], None) for row in rows]
        subscriptions = tuple(
            Subscription(row["snippet"]["resourceId"]["channelId"], row["snippet"]["title"],
                         _date(row["snippet"].get("publishedAt")))
            for row in self._items("subscriptions.list", part="snippet", auth="read",
                                   fields="snippet(resourceId/channelId,title,publishedAt)",
                                   mine="true", maxResults=50)
        )
        playlists = tuple(
            UserPlaylist(row["id"], row["snippet"]["title"],
                         row.get("contentDetails", {}).get("itemCount"))
            for row in self._items("playlists.list", part="snippet,contentDetails", auth="read",
                                   fields="id,snippet/title,contentDetails/itemCount",
                                   mine="true", maxResults=50)
        )
        entries = [(p.playlist_id, key, added) for p in playlists
                   for key, added in self._playlist_entries(p.playlist_id)]
        ids = [key for key, _ in likes] + [key for _, key, _ in entries]
        metadata = self._metadata(ids, "videos.list", "snippet,contentDetails,status",
                                  VIDEO_FIELDS, _video, auth="read")
        videos = {video.video_id: video for video in metadata}

        def lookup(key):
            return videos.get(key) or Video(key, "Unavailable video", "", available=False)

        return Library(tuple(LikedVideo(lookup(key), date) for key, date in likes), subscriptions,
                       playlists, tuple(PlaylistItem(p, lookup(key), date) for p, key, date in entries))

    def ensure_write_scope(self):
        if self.read_only:
            raise ForbiddenError("This provider is configured for read-only access.")
        self.quota.check(self.quota.cost_of("channels.list", calls=2))
        oauth = self._oauth()
        self._write_binding.set(None)
        oauth.ensure_write_scope()
        read, write = oauth.token(), oauth.token(write=True)
        if self._mine(token=read)["id"] != self._mine(write=True, token=write)["id"]:
            raise AuthRequiredError("Choose the same YouTube channel for read and write consent.")
        self._write_binding.set((read, write))

    def _write_token(self):
        if self.read_only:
            raise ForbiddenError("This provider is configured for read-only access.")
        oauth = self._oauth()
        pair = (oauth.token(), oauth.token(write=True))
        if self._write_binding.get() != pair:
            raise AuthRequiredError("Verify the write grant for the current YouTube channel.")
        return pair[1]

    def create_playlist(self, title, privacy="private"):
        data = self._request("playlists.insert", auth="write", token=self._write_token(),
                             params={"part": "snippet,status", "fields": "id"},
                             body={"snippet": {"title": title}, "status": {"privacyStatus": privacy}})
        return data["id"]

    def add_playlist_item(self, playlist_id, video_id):
        self._request("playlistItems.insert", auth="write", token=self._write_token(),
                      params={"part": "snippet", "fields": "id"},
                      body={"snippet": {"playlistId": playlist_id,
                                        "resourceId": {"kind": "youtube#video", "videoId": video_id}}})

    def auth_status(self):
        return self.oauth.auth_status() if self.oauth else AuthStatus("needs_authorisation", ())

    def sign_out(self):
        self._write_binding.set(None)
        self._oauth().sign_out()
