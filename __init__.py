from .io_utils.types import singleton

@singleton
class WoWVersionManager:

    def __init__(self):
        self.client_version = 0

    def set_client_version(self, version: int):
        self.client_version = version


class WoWVersions:
    CLASSIC = 0
    TBC = 1
    WOTLK = 2
    CATA = 3
    MOP = 4
    WOD = 5  # ?
    LEGION = 6
    BFA = 7
    NEW_CLASSIC = 8
