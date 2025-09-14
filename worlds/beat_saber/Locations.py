from BaseClasses import Location

class BSLocation(Location):
    game: str = "Beat Saber"

location_table = { "Node " + f"{i}".zfill(2) : i for i in range(50) }
