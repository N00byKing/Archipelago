import typing
from dataclasses import dataclass
from Options import Option, DeathLink, Range, Toggle, PerGameCommonOptions

@dataclass
class BSOptions(PerGameCommonOptions):
    death_link: DeathLink
