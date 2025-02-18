import typing
import os, json
from .Items import item_table, BSItem
from .Locations import location_table, BSLocation
from .Options import BSOptions
from .Rules import set_rules
from .Regions import create_regions
from BaseClasses import Item, ItemClassification, Tutorial
from ..AutoWorld import World, WebWorld

client_version = 1


class BSWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Beat Saber for Multiworld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["N00byKing"]
    )]


class BSWorld(World):
    """ 
     bloks
    """ #Lifted from Store Page

    game: str = "Beat Saber"
    topology_present = False
    web = BSWeb()

    item_name_to_id = item_table
    location_name_to_id = location_table

    area_connections: typing.Dict[int, int]
    area_cost_map: typing.Dict[int,int]

    music_map: typing.Dict[int,int]

    options_dataclass = BSOptions

    def create_regions(self):
        create_regions(self.multiworld, self.player)

    def set_rules(self):
        self.area_connections = {}
        self.area_cost_map = {}
        set_rules(self.multiworld, self.options, self.player, self.area_connections, self.area_cost_map)

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> Item:
        return BSItem(name, classification, item_table[name], self.player)

    def create_items(self):
        progtrinkets = [self.create_item("Song " + str(i+1).zfill(2), ItemClassification.progression) for i in range(10)]
        self.multiworld.itempool += progtrinkets

    def generate_basic(self):
        pass

    def fill_slot_data(self):
        return {
            "DeathLink": self.options.death_link.value,
            "DeathLink_Amnesty": self.options.death_link_amnesty.value
        }
