from BaseClasses import Location

class BSLocation(Location):
    game: str = "Beat Saber"

bs_id_offset = 140400
location_table = { "Node " + f"{i}".zfill(2) : bs_id_offset + i for i in range(50) }
