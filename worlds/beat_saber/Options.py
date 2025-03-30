import typing
from dataclasses import dataclass
from Options import Option, DeathLink, Range, OptionDict, PerGameCommonOptions
from schema import Schema, And, Or, Use, Optional, SchemaError

class NumTracks(Range):
    """Amount of Tracks to require"""
    display_name = "Number of Tracks"
    range_start = 5 # Require 5 at minimum to ensure > 1 layer
    range_end = 50
    default = 5

#TODO: Items for starting map type (Onesaber, etc)
default_songs = {
    "[Extra Sensory II] Xtrullor - Ego Death": {
        "mapid": "43A2E",
        "difficulty": 4,
        "characteristic": "Standard"
    },
    "[Extra Sensory II] RXLZQ - Through The Screen": {
        "mapid": "43A5D",
        "difficulty": 4,
        "characteristic": "Standard"
    },
    "[Extra Sensory II] Simplifi - you": {
        "mapid": "43A1F",
        "difficulty": 2,
        "characteristic": "Standard"
    },
    "[RANKED] DJ Genki - Introduction": {
        "mapid": "29715",
        "difficulty": 4,
        "characteristic": "Standard"
    },
    "99.9 // Mob Choir feat. Sajou no Hana": {
        "mapid": "3C89",
        "difficulty": 4,
        "characteristic": "Standard"
    },
    "Muse - Uprising": {
        "mapid": "4C6",
        "difficulty": 3,
        "characteristic": "Standard"
    },
    "Spider Dance - Toby Fox (Undertale modchart)": {
        "mapid": "198F3",
        "difficulty": 4,
        "characteristic": "Standard"
    },
    "RIOT - Overkill": {
        "mapid": "1F90",
        "difficulty": 4,
        "characteristic": "Standard"
    },
    "Avicii - The Nights": {
        "mapid": "16ABF",
        "difficulty": 4,
        "characteristic": "Standard"
    },
}
class Songs(OptionDict):
    """Songs that may occur in the custom campaign generated. Need to specify a name, the mapid from beatsaver (in the url, /maps/<id>), and the characteristic (most likely "Standard")"""
    display_name = "Songs"
    default = default_songs
    schema = Schema({
        str: {
            "mapid": str,
            "difficulty": And(Use(int), lambda n: 1 <= 4),
            "characteristic": And(Use(str), lambda s: s in ("Standard", "OneSaber")),
        }
    })


@dataclass
class BSOptions(PerGameCommonOptions):
    num_tracks: NumTracks
    death_link: DeathLink
    songs: Songs
