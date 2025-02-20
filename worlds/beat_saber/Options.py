import typing
from dataclasses import dataclass
from Options import Option, DeathLink, Range, Toggle, PerGameCommonOptions

class NumTracks(Range):
    """Amount of Tracks to require"""
    display_name = "Number of Tracks"
    range_start = 3
    range_end = 50
    default = 3

#TODO: Option for starting map type (Onesaber, 360, etc)

@dataclass
class BSOptions(PerGameCommonOptions):
    num_tracks: NumTracks
    death_link: DeathLink
