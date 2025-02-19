import typing
import os, json
import zipfile
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

    campaign_name: str
    song_to_id: typing.Dict[int,int] = {}
    id_to_song: typing.Dict[int,int] = {}

    def create_regions(self):
        create_regions(self.multiworld, self.player)

    def set_rules(self):
        self.area_connections = {}
        self.area_cost_map = {}
        set_rules(self.multiworld, self.options, self.player, self.area_connections, self.area_cost_map)

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> Item:
        return BSItem(name, classification, item_table[name], self.player)

    def create_items(self):
        progtrinkets = [self.create_item("Song " + str(i+1).zfill(2), ItemClassification.progression) for i in range(self.options.num_tracks)]
        self.multiworld.itempool += progtrinkets

    def generate_basic(self):
        self.campaign_name = f"AP Campaign, Seed {self.multiworld.seed_name}"
        track_possibilities = [ 0x43A2E, 0x43A5D, 0x43A1F, 0x29715, 0x3c89, 0x4C6, 0x198F3 ]
        for i in range(self.options.num_tracks):
            track = self.multiworld.random.choice(track_possibilities)
            self.song_to_id[track] = i
            self.id_to_song[i] = track
        for i in range(self.options.num_tracks, 50):
            self.multiworld.get_location("Track " + f"{i}".zfill(2), self.player).place_locked_item(Item("Nothing", ItemClassification.filler, -1, self.player))

    def fill_slot_data(self):
        return {
            "DeathLink": self.options.death_link.value,
            "song_to_id": self.song_to_id,
            "campaign_name": self.campaign_name
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
        nodes = {}
        child_nodes = {
            0: [1, 2],
            1: [],
            2: []
        }
        for i in range(self.options.num_tracks):
            # Write meta info to info.json
            node_meta_info = {
                "childNotes": child_nodes[i],
                "x": 0,
                "y": i*100,
                "scale": 0.9,
                "letterPortion": f"Song{i}",
                "numberPortion": -1
            }
            info_json["mapPositions"].append(node_meta_info)

            # Write node info
            node_json = {
                "name": f"Song{i}",
                "songid": f'{self.id_to_song[i]:x}',
                "characteristic": "Standard",
                "difficulty": 4,
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
            nodes[i] = node_json

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
            bkgimg = load_data("map background.png")
            zf.writestr(f"{folder_prefix}/cover.png", coverimg)
            zf.writestr(f"{folder_prefix}/map background.png", bkgimg)
            for i in range(self.options.num_tracks):
                zf.writestr(f"{folder_prefix}/{i}.json", json.dumps(nodes[i]))
