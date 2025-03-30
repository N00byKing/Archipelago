from typing import NamedTuple
from BaseClasses import Item, ItemClassification

class BSItem(Item):
    game: str = "Beat Saber"

class BSItemData(NamedTuple):
    code: int | None = None
    classification: ItemClassification = ItemClassification.progression

song_table = { "Song " + f"{i}".zfill(2) : BSItemData(i) for i in range(1, 50) } # Must start at 1, Song0 is root node, always available

filler_table = {
    "Nothing": BSItemData(0, ItemClassification.filler)
}

item_data_table = {
    **song_table,
    **filler_table
}

item_table = {name: data.code for name, data in item_data_table.items() if data.code is not None}