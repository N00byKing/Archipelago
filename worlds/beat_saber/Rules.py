import typing
from ..generic.Rules import add_rule

def __add_song_rule(multiworld, player, node):
    add_rule(multiworld.get_location("Node " + f"{node}".zfill(2), player), lambda state: state.has("Song " + f"{node}".zfill(2), player))

def __add_node_dep_rule(multiworld, player, source, target):
    add_rule(multiworld.get_location("Node " + f"{target}".zfill(2), player), lambda state: state.can_reach("Node " + f"{source}".zfill(2), 'Location', player))

def __completion_condition(state, player, options, node_connections):
    for i in range(1, options.num_tracks):
        if i in node_connections[0]: continue
        if state.has("Song " + f"{i}".zfill(2), player): continue
        return False
    return True

def set_rules(multiworld, options, player, node_connections: typing.Dict[int, typing.Set[int]], node_layers: typing.Dict[int, typing.Set[int]]):
    # Enforce that for every connection there exists a dependency on previous track and local song item
    for node, targets in node_connections.items():
        # For each child node, access to parent node is required. If parent is root this is not needed
        for target in targets:
            __add_node_dep_rule(multiworld, player, node, target)
        # For every node but root, the track item is required
        if node == 0 or node in node_connections[0]: continue
        __add_song_rule(multiworld, player, node)
    # Winning condition: Beat campaing, so all songs currently.
    #TODO: Need to designate final node or smth
    multiworld.completion_condition[player] = lambda state: __completion_condition(state, player, options, node_connections)
