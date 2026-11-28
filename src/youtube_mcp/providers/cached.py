from youtube_mcp.cache.store import TTLStore


class CachingProvider:
    """Cache public metadata only. Search and account operations are delegated."""

    def __init__(self, inner, store=None, clock=None):
        self.inner = inner
        self.store = store if store is not None else TTLStore(clock)

    def _metadata(self, ids, method, id_attr):
        ids = list(dict.fromkeys(ids))
        cached = {key: self.store.get((method, key)) for key in ids}
        missing = [key for key, value in cached.items() if value is None]
        if missing:
            for item in getattr(self.inner, method)(missing):
                key = getattr(item, id_attr)
                cached[key] = item
                if getattr(item, "available", True):
                    self.store.put((method, key), item)
        return [cached[key] for key in ids if cached[key] is not None]

    def get_videos(self, ids):
        return self._metadata(ids, "get_videos", "video_id")

    def get_channels(self, ids):
        return self._metadata(ids, "get_channels", "channel_id")

    def _public(self, key, load):
        result = self.store.get(key)
        if result is None:
            result = load()
            self.store.put(key, result)
        return result

    def get_categories(self, region="US"):
        return dict(self._public(("categories", region),
                                 lambda: tuple(self.inner.get_categories(region).items())))

    def get_recent_uploads(self, channel_id, n=10):
        return list(self._public(("uploads", channel_id, n),
                                 lambda: tuple(self.inner.get_recent_uploads(channel_id, n))))

    def resolve_channel(self, ref):
        return self._public(("resolve", ref), lambda: self.inner.resolve_channel(ref))

    def search_videos(self, query, *, max_results=25, pages=1):
        return self.inner.search_videos(query, max_results=max_results, pages=pages)

    def search_channels(self, query, *, max_results=25):
        return self.inner.search_channels(query, max_results=max_results)

    def get_library(self):
        return self.inner.get_library()

    def account_fingerprint(self):
        return self.inner.account_fingerprint()

    def create_playlist(self, title, privacy="private"):
        return self.inner.create_playlist(title, privacy)

    def add_playlist_item(self, playlist_id, video_id):
        self.inner.add_playlist_item(playlist_id, video_id)

    def auth_status(self):
        return self.inner.auth_status()

    def ensure_write_scope(self):
        self.inner.ensure_write_scope()

    def sign_out(self):
        self.inner.sign_out()
