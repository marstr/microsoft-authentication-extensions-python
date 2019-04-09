class MSALCacheStorage:
    def read_data(self):
        # type: () -> str
        """Read and unprotected cache data."""
        # TODO: Fetch cache data from protected backend.
        pass

    def write_data(self, data):
        # type: (str) -> None
        """Protect and write cache data to file."""
        # TODO: Persist cache data to protected backend.
        pass
