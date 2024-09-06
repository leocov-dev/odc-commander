from pydantic import BaseModel


class Board(BaseModel):
    name: str
    fqbn: str = ""


class Release(BaseModel):
    version: str
    installed: bool = True
    boards: list[Board]
    compatible: bool


class Platform(BaseModel):
    id: str
    releases: dict[str, Release]
    installed_version: str
    latest_version: str


class Cores(BaseModel):
    platforms: list[Platform]
