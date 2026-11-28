"""Deterministic provider backed by synthetic JSON or an injected dataset."""
import json

from youtube_mcp.auth.oauth import READ_SCOPE, WRITE_SCOPE
from youtube_mcp.errors import AuthRequiredError, NotFoundError, ValidationError
from youtube_mcp.models import AuthStatus, Channel, Library, LikedVideo, PlaylistItem
from youtube_mcp.models import Subscription, UserPlaylist, Video
from youtube_mcp.providers.live import _date


class FixtureProvider:
    def __init__(self, data=None, *, errors=None, authorised=True):
        self.data = data or {}
        self.errors = errors or {}
        self.calls = []
        self.authorised = authorised
        self.writable = False
        self.created = {}
        self.videos = {}
        for row in self.data.get("videos", []):
            video = Video(**{**row, "tags": tuple(row.get("tags", [])),
                             "published_at": _date(row.get("published_at"))})
            self.videos[video.video_id] = video
        self.channels = {}
        for row in self.data.get("channels", []):
            channel = Channel(**{**row, "topics": tuple(row.get("topics", [])),
                                 "keywords": tuple(row.get("keywords", []))})
            self.channels[channel.channel_id] = channel

    @classmethod
    def from_json(cls, path, **kwargs):
        with open(path, encoding="utf-8") as stream:
            return cls(json.load(stream), **kwargs)

    def _call(self, method, *args):
        self.calls.append((method, *args))
        if method in self.errors:
            error = self.errors[method]
            raise error() if callable(error) else error

    def _auth(self, *, write=False):
        if not self.authorised or (write and not self.writable):
            raise AuthRequiredError("The fixture account requires authorisation.")

    def get_videos(self, ids):
        self._call("get_videos", tuple(ids))
        return [self.videos[key] for key in dict.fromkeys(ids) if key in self.videos]

    def get_channels(self, ids):
        self._call("get_channels", tuple(ids))
        return [self.channels[key] for key in dict.fromkeys(ids) if key in self.channels]

    def _search(self, method, query, max_results, pages, values, key):
        if not 1 <= max_results <= 50 or not 1 <= pages <= 2:
            raise ValidationError("Invalid fixture search page size or count.")
        self._call(method, query, max_results, pages)
        matches = self.data.get(method, {}).get(query)
        if matches is None:
            matches = [getattr(value, key) for value in values
                       if query.casefold() in value.title.casefold()]
        return list(dict.fromkeys(matches))[:max_results * pages]

    def search_videos(self, query, *, max_results=25, pages=1):
        return self._search("search_videos", query, max_results, pages,
                            self.videos.values(), "video_id")

    def search_channels(self, query, *, max_results=25):
        return self._search("search_channels", query, max_results, 1,
                            self.channels.values(), "channel_id")

    def resolve_channel(self, ref):
        self._call("resolve_channel", ref)
        if ref in self.channels:
            return ref
        for channel in self.channels.values():
            if channel.handle and channel.handle.casefold() == ref.rstrip("/").split("/")[-1].casefold():
                return channel.channel_id
        last_segment = ref.rstrip("/").split("/")[-1]
        if last_segment in self.channels:
            return last_segment
        raise NotFoundError("The fixture channel could not be found.")

    def get_recent_uploads(self, channel_id, n=10):
        self._call("get_recent_uploads", channel_id, n)
        if channel_id not in self.channels:
            raise NotFoundError("The fixture channel could not be found.")
        return [video for video in self.videos.values() if video.channel_id == channel_id][:n]

    def get_categories(self, region="US"):
        self._call("get_categories", region)
        return dict(self.data.get("categories", {}).get(region, {}))

    def get_library(self):
        self._call("get_library")
        self._auth()
        library = self.data.get("library", {})
        return Library(
            tuple(LikedVideo(self.videos[row["video_id"]], _date(row.get("added_at")))
                  for row in library.get("liked", [])),
            tuple(Subscription(**{**row, "subscribed_at": _date(row.get("subscribed_at"))})
                  for row in library.get("subscriptions", [])),
            tuple(UserPlaylist(**row) for row in library.get("playlists", [])),
            tuple(PlaylistItem(row["playlist_id"], self.videos[row["video_id"]],
                               _date(row.get("added_at"))) for row in library.get("playlist_items", [])),
        )

    def account_fingerprint(self):
        self._call("account_fingerprint")
        self._auth()
        return self.data.get("owner", "synthetic-fixture-owner")

    def create_playlist(self, title, privacy="private"):
        self._call("create_playlist", title, privacy)
        self._auth(write=True)
        key = f"PLfixture{len(self.created) + 1}"
        self.created[key] = []
        return key

    def add_playlist_item(self, playlist_id, video_id):
        self._call("add_playlist_item", playlist_id, video_id)
        self._auth(write=True)
        if playlist_id not in self.created or video_id not in self.videos:
            raise NotFoundError("The fixture playlist or video could not be found.")
        self.created[playlist_id].append(video_id)

    def auth_status(self):
        self._call("auth_status")
        if not self.authorised:
            return AuthStatus("needs_authorisation", ())
        return AuthStatus("ok", (READ_SCOPE, WRITE_SCOPE) if self.writable else (READ_SCOPE,))

    def ensure_write_scope(self):
        self._call("ensure_write_scope")
        self._auth()
        self.writable = True

    def sign_out(self):
        self._call("sign_out")
        self.authorised = self.writable = False
