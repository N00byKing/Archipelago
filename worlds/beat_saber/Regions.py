import typing
from BaseClasses import MultiWorld, Region, Entrance, Location
from .Locations import BSLocation, location_table

def create_regions(world: MultiWorld, player: int):
    regOvr = Region("Menu", player, world, "Menu")
    locOvr_names = location_table.keys()
    regOvr.locations += [BSLocation(player, loc_name, location_table[loc_name], regOvr) for loc_name in locOvr_names]
    world.regions.append(regOvr)
