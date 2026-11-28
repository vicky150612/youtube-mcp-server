import json
import os
import stat
from pathlib import Path
from tempfile import NamedTemporaryFile

from youtube_mcp.errors import ProviderError


class KeyringTokenStore:
    def __init__(self, client_id: str):
        import keyring

        self.backend = keyring.get_keyring()
        if self.backend.__class__.__module__ == "keyring.backends.chainer":
            native = [backend for backend in self.backend.backends
                      if backend.__class__.__module__.split(".")[-1]
                      in {"Windows", "macOS", "SecretService", "kwallet"}]
            self.backend = native[0] if native else None
        if self.backend is None or self.backend.__class__.__module__ not in {
            "keyring.backends.Windows", "keyring.backends.macOS",
            "keyring.backends.SecretService", "keyring.backends.kwallet",
        }:
            raise ProviderError("No supported OS credential store is available.")
        self.service = f"youtube-mcp:{client_id}"

    def load(self, slot):
        return self.backend.get_password(self.service, slot)

    def save(self, slot, token):
        self.backend.set_password(self.service, slot, token)

    def delete(self, slot):
        if self.load(slot) is not None:
            self.backend.delete_password(self.service, slot)


class ProtectedFileTokenStore:
    """Explicit fallback for POSIX user-only directories and files."""

    def __init__(self, directory: Path):
        if os.name != "posix":
            raise ProviderError("Use the native OS credential store on this platform.")
        self.directory = directory
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ProviderError("The credential directory must be owned and accessible only by you.")

    def _path(self, slot):
        if slot not in {"read", "write"}:
            raise ValueError("Unknown credential slot.")
        return self.directory / f"{slot}.json"

    def load(self, slot):
        try:
            fd = os.open(self._path(slot), os.O_RDONLY | os.O_NOFOLLOW)
        except FileNotFoundError:
            return None
        with os.fdopen(fd, encoding="utf-8") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ProviderError("The credential file must be owned and accessible only by you.")
            return json.load(stream)["refresh_token"]

    def save(self, slot, token):
        path = self._path(slot)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.directory,
                                delete=False) as stream:
            temporary = Path(stream.name)
            try:
                json.dump({"refresh_token": token}, stream)
                stream.flush()
                os.fsync(stream.fileno())
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)

    def delete(self, slot):
        self._path(slot).unlink(missing_ok=True)
