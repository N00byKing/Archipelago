from BaseClasses import Item

class BSItem(Item):
    game: str = "Beat Saber"

bs_id_offset = 140400
item_table = { "Song " + f"{i}".zfill(2) : bs_id_offset + i for i in range(1, 50) } # Must start at 1, Song0 is root node, always available
item_table["Nothing"] = bs_id_offset # Instead, use id 0 for "Nothing" filler TODO replace with cooler filler
