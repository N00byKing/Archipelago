import typing
import os
import json
from .Items import item_table, action_item_table, cannon_item_table, SM64Item
from .Locations import location_table, SM64Location
from .Options import sm64_options
from .Rules import set_rules
from .Regions import create_regions, sm64_level_to_entrances
from BaseClasses import Item, Tutorial, ItemClassification
from ..AutoWorld import World, WebWorld


class SM64Web(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up SM64EX for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["N00byKing"]
    )]


class SM64World(World):
    """ 
    The first Super Mario game to feature 3D gameplay, it features freedom of movement within a large open world based on polygons,
    combined with traditional Mario gameplay, visual style, and characters.
    """

    game: str = "Super Mario 64"
    topology_present = False

    web = SM64Web()

    item_name_to_id = item_table
    location_name_to_id = location_table

    data_version = 9
    required_client_version = (0, 3, 5)

    area_connections: typing.Dict[int, int]

    option_definitions = sm64_options

    number_of_stars: int
    move_rando_bitvec: int
    filler_count: int
    star_costs: typing.Dict[str, int]

    def generate_early(self):
        max_stars = 120
        if (not self.multiworld.EnableCoinStars[self.player].value):
            max_stars -= 15
        self.move_rando_bitvec = 0
        for action, itemid in action_item_table.items():
            # HACK: Disable randomization of double jump
            if action == 'Double Jump': continue
            if getattr(self.multiworld, f"MoveRandomizer{action.replace(' ','')}")[self.player].value:
                max_stars -= 1
                self.multiworld.itempool.append(self.create_item(action))
                self.move_rando_bitvec |= (1 << (itemid - action_item_table['Double Jump']))
        if (self.multiworld.ExclamationBoxes[self.player].value > 0):
            max_stars += 29
        self.number_of_stars = min(self.multiworld.AmountOfStars[self.player].value, max_stars)
        self.filler_count = max_stars - self.number_of_stars
        self.star_costs = {
            'FirstBowserDoorCost': round(self.multiworld.FirstBowserStarDoorCost[self.player].value * self.number_of_stars / 100),
            'BasementDoorCost': round(self.multiworld.BasementStarDoorCost[self.player].value * self.number_of_stars / 100),
            'SecondFloorDoorCost': round(self.multiworld.SecondFloorStarDoorCost[self.player].value * self.number_of_stars / 100),
            'MIPS1Cost': round(self.multiworld.MIPS1Cost[self.player].value * self.number_of_stars / 100),
            'MIPS2Cost': round(self.multiworld.MIPS2Cost[self.player].value * self.number_of_stars / 100),
            'StarsToFinish': round(self.multiworld.StarsToFinish[self.player].value * self.number_of_stars / 100)
        }
        # Nudge MIPS 1 to match vanilla on default percentage
        if self.number_of_stars == 120 and self.multiworld.MIPS1Cost[self.player].value == 12:
            self.star_costs['MIPS1Cost'] = 15
        self.topology_present = self.multiworld.AreaRandomizer[self.player].value

    def create_regions(self):
        create_regions(self.multiworld, self.player)

    def set_rules(self):
        self.area_connections = {}
        set_rules(self.multiworld, self.player, self.area_connections, self.star_costs, self.move_rando_bitvec)
        if self.topology_present:
            # Write area_connections to spoiler log
            for entrance, destination in self.area_connections.items():
                self.multiworld.spoiler.set_entrance(
                    sm64_level_to_entrances[entrance] + " Entrance",
                    sm64_level_to_entrances[destination],
                    'entrance', self.player)

    def create_item(self, name: str) -> Item:
        item_id = item_table[name]
        if name == "1Up Mushroom":
            classification = ItemClassification.filler
        elif name == "Power Star":
            classification = ItemClassification.progression_skip_balancing
        else:
            classification = ItemClassification.progression
        item = SM64Item(name, classification, item_id, self.player)

        return item

    def create_items(self):
        # 1Up Mushrooms
        preplaced_count = 29 if self.multiworld.ExclamationBoxes[self.player].value == 0 else 0
        self.multiworld.itempool += [self.create_item("1Up Mushroom") for i in range(0,self.filler_count - preplaced_count)]
        # Power Stars
        self.multiworld.itempool += [self.create_item("Power Star") for i in range(0,self.number_of_stars)]
        # Keys
        if (not self.multiworld.ProgressiveKeys[self.player].value):
            key1 = self.create_item("Basement Key")
            key2 = self.create_item("Second Floor Key")
            self.multiworld.itempool += [key1, key2]
        else:
            self.multiworld.itempool += [self.create_item("Progressive Key") for i in range(0,2)]
        # Caps
        self.multiworld.itempool += [self.create_item(cap_name) for cap_name in ["Wing Cap", "Metal Cap", "Vanish Cap"]]
        # Cannons
        if (self.multiworld.BuddyChecks[self.player].value):
            self.multiworld.itempool += [self.create_item(name) for name, id in cannon_item_table.items()]

    def generate_basic(self):
        if not (self.multiworld.BuddyChecks[self.player].value):
            self.multiworld.get_location("BoB: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock BoB"))
            self.multiworld.get_location("WF: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock WF"))
            self.multiworld.get_location("JRB: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock JRB"))
            self.multiworld.get_location("CCM: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock CCM"))
            self.multiworld.get_location("SSL: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock SSL"))
            self.multiworld.get_location("SL: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock SL"))
            self.multiworld.get_location("WDW: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock WDW"))
            self.multiworld.get_location("TTM: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock TTM"))
            self.multiworld.get_location("THI: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock THI"))
            self.multiworld.get_location("RR: Bob-omb Buddy", self.player).place_locked_item(self.create_item("Cannon Unlock RR"))

        if (self.multiworld.ExclamationBoxes[self.player].value == 0):
            self.multiworld.get_location("CCM: 1Up Block Near Snowman", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("CCM: 1Up Block Ice Pillar", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("CCM: 1Up Block Secret Slide", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("BBH: 1Up Block Top of Mansion", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("HMC: 1Up Block above Pit", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("HMC: 1Up Block Past Rolling Rocks", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("SSL: 1Up Block Outside Pyramid", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("SSL: 1Up Block Pyramid Left Path", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("SSL: 1Up Block Pyramid Back", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("SL: 1Up Block Near Moneybags", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("SL: 1Up Block inside Igloo", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("WDW: 1Up Block in Downtown", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("TTM: 1Up Block on Red Mushroom", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("THI: 1Up Block THI Small near Start", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("THI: 1Up Block THI Large near Start", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("THI: 1Up Block Windy Area", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("TTC: 1Up Block Midway Up", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("TTC: 1Up Block at the Top", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("RR: 1Up Block Top of Red Coin Maze", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("RR: 1Up Block Under Fly Guy", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("RR: 1Up Block On House in the Sky", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Bowser in the Dark World 1Up Block on Tower", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Bowser in the Dark World 1Up Block near Goombas", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Cavern of the Metal Cap 1Up Block", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Vanish Cap Under the Moat 1Up Block", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Bowser in the Fire Sea 1Up Block Swaying Stairs", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Bowser in the Fire Sea 1Up Block Near Poles", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Wing Mario Over the Rainbow 1Up Block", self.player).place_locked_item(self.create_item("1Up Mushroom"))
            self.multiworld.get_location("Bowser in the Sky 1Up Block", self.player).place_locked_item(self.create_item("1Up Mushroom"))

    def get_filler_item_name(self) -> str:
        return "1Up Mushroom"

    def fill_slot_data(self):
        return {
            "AreaRando": self.area_connections,
            "MoveRandoVec": self.move_rando_bitvec,
            "DeathLink": self.multiworld.death_link[self.player].value,
            "CompletionType" : self.multiworld.CompletionType[self.player].value,
            **self.star_costs
        }

    def generate_output(self, output_directory: str):
        if self.multiworld.players != 1:
            return
        data = {
            "slot_data": self.fill_slot_data(),
            "location_to_item": {self.location_name_to_id[i.name] : item_table[i.item.name] for i in self.multiworld.get_locations()},
            "data_package": {
                "data": {
                    "games": {
                        self.game: {
                            "item_name_to_id": self.item_name_to_id,
                            "location_name_to_id": self.location_name_to_id
                        }
                    }
                }
            }
        }
        filename = f"{self.multiworld.get_out_file_name_base(self.player)}.apsm64ex"
        with open(os.path.join(output_directory, filename), 'w') as f:
            json.dump(data, f)

    def modify_multidata(self, multidata):
        if self.topology_present:
            er_hint_data = {}
            for entrance, destination in self.area_connections.items():
                region = self.multiworld.get_region(sm64_level_to_entrances[destination], self.player)
                for location in region.locations:
                    er_hint_data[location.address] = sm64_level_to_entrances[entrance]
            multidata['er_hint_data'][self.player] = er_hint_data
