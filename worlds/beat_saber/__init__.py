import typing
import os, json
import zipfile
from .Items import item_table, item_data_table, BSItem
from .Locations import location_table, BSLocation
from .CampainLayout import generate_campain_layout
from .Options import BSOptions
from .Rules import set_rules
from .Regions import create_regions
from BaseClasses import Item, ItemClassification, Tutorial
from ..AutoWorld import World, WebWorld

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

    node_layers: typing.Dict[int, typing.Set[int]]
    node_connections: typing.Dict[int, typing.Set[int]]

    songshuffle: list

    music_map: typing.Dict[int,int]

    options_dataclass = BSOptions

    campaign_name: str
    songident_to_node: typing.Dict[str,int] = {}
    node_to_songident: typing.Dict[int,str] = {}

    def create_regions(self):
        create_regions(self.multiworld, self.player)

    def set_rules(self):
        set_rules(self.multiworld, self.options, self.player, self.node_connections, self.node_layers)

    def create_item(self, name: str) -> Item:
        return BSItem(name, item_data_table[name].classification, item_data_table[name].code, self.player)

    def generate_early(self):
        self.node_connections = {}
        self.node_layers = {}
        generate_campain_layout(self.options, self.multiworld.random, self.node_connections, self.node_layers)

    def create_items(self):
        songUnlocks = []
        for i in range(1,self.options.num_tracks):
            if not i in list(self.node_connections[0]):
                songUnlocks.append(self.create_item("Song " + str(i).zfill(2)))
        #TODO: nice filler items
        filler = [Item("Nothing", ItemClassification.filler, -1, self.player) for i in range(self.options.num_tracks - len(songUnlocks))]
        self.multiworld.itempool += songUnlocks + filler

    def generate_basic(self):
        self.campaign_name = f"AP Campaign, Seed {self.multiworld.seed_name}"
        self.songshuffle = list(self.options.songs.keys())
        self.multiworld.random.shuffle(self.songshuffle)
        for i in range(self.options.num_tracks):
            self.songident_to_node[self.songshuffle[i]] = i
            self.node_to_songident[i] = self.songshuffle[i]
        for i in range(self.options.num_tracks, 50):
            self.multiworld.get_location("Node " + f"{i}".zfill(2), self.player).place_locked_item(Item("Nothing", ItemClassification.filler, -1, self.player))

    def fill_slot_data(self):
        return {
            "DeathLink": self.options.death_link.value,
            "node_to_songident": self.node_to_songident,
            "songident_to_node": self.songident_to_node,
            "campaign_name": self.campaign_name,
            "start_songs": [self.node_to_songident[0]] + [self.node_to_songident[i] for i in self.node_connections[0]]
        }

    def generate_output(self, output_directory: str):
        # Template for info.json
        info_json = {
            "name": self.campaign_name,
            "desc": "Generated on APWorld, version idk",
            "bigDesc": "TODO dump settings, other players maybe?",
            "allUnlocked": False,
            "mapPositions": [ ],
            "mapHeight": 1200,
            "backgroundAlpha": 0.9,
            "lightColor": {
                "r": 0.0,
                "g": 0.443137258,
                "b": 0.9843137
            }
        }

        # Nodes
        nodes_json = {}
        node_distance_horizontal = 60
        for layer in range(len(self.node_layers)):
            layer_width = len(self.node_layers[layer]) * node_distance_horizontal
            layer_start = -0.5 * layer_width # Center around 0, start from left, increment to right
            for i in range(len(self.node_layers[layer])):
                loc_id = self.node_layers[layer][i]
                # Write meta info to info.json
                locname = f"Track{loc_id}"
                node_meta_info = {
                    "childNodes": self.node_connections[loc_id],
                    "x":  layer_start + node_distance_horizontal * i,
                    "y": layer*80,
                    "scale": 0.9,
                    "letterPortion": locname,
                    "numberPortion": -1
                }
                info_json["mapPositions"].append(node_meta_info)

                # Write node info
                node_json = {
                    "name": locname,
                    "songid": self.options.songs[self.node_to_songident[loc_id]]["mapid"],
                    "characteristic": self.options.songs[self.node_to_songident[loc_id]]["characteristic"],
                    "difficulty": self.options.songs[self.node_to_songident[loc_id]]["difficulty"],
                    "modifiers": {
                        "fastNotes": False,
                        "songSpeed": 0,
                        "noBombs": False,
                        "disappearingArrows": False,
                        "strictAngles": False,
                        "noObstacles": False,
                        "batteryEnergy": False,
                        "failOnSaberClash": False,
                        "instaFail": False,
                        "noFail": False,
                        "noArrows": False,
                        "ghostNotes": False,
                        "energyType": 0,
                        "enabledObstacleType": 0,
                        "speedMul": 1.0
                    },
                    "requirements": [],
                    "externalModifiers": {},
                    "challengeInfo": None,
                    "unlockableItems": [],
                    "unlockMap": False
                }
                nodes_json[self.node_layers[layer][i]] = node_json
        # Write zipfile
        folder_prefix = f"AP_{self.multiworld.seed_name}"
        file_path = f"{self.multiworld.get_out_file_name_base(self.player)}.zip"
        with zipfile.ZipFile(file_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.writestr(f"{folder_prefix}/info.json", json.dumps(info_json))
            def load_data(name: str):
                import pkgutil
                data = pkgutil.get_data(__name__, "data/" + name)
                return data
            coverimg = load_data("cover.png")
            #bkgimg = load_data("map background.png")
            zf.writestr(f"{folder_prefix}/cover.png", coverimg)
            #zf.writestr(f"{folder_prefix}/map background.png", bkgimg)
            for i in range(self.options.num_tracks):
                zf.writestr(f"{folder_prefix}/{i}.json", json.dumps(nodes_json[i]))
