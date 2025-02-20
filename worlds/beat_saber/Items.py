from BaseClasses import Item

class BSItem(Item):
    game: str = "Beat Saber"

item_table = { "Song " + f"{i}".zfill(2) : i for i in range(1, 50) } # Must start at 1, Song0 is root node, always available
