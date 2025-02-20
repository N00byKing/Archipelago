import typing
from ..generic.Rules import add_rule

def __add_song_rule(multiworld, player, node):
    add_rule(multiworld.get_location("Node " + f"{node}".zfill(2), player), lambda state: state.has("Song " + f"{node}".zfill(2), player))

def __add_node_dep_rule(multiworld, player, source, target):
    add_rule(multiworld.get_location("Node " + f"{target}".zfill(2), player), lambda state: state.can_reach("Node " + f"{source}".zfill(2), 'Location', player))

def set_rules(multiworld, options, player, node_connections: typing.Dict[int, typing.Set[int]], node_layers: typing.Dict[int, typing.Set[int]]):
    # First, generate the campaign layout
    ## Step 1: Generate layers
    node_layers[0] = []
    cur_layer = 0
    cur_track = 0
    while options.num_tracks - cur_track > 0:
        # How many tracks to utilize for this layer,
        # at least 1 and up to min(remaining locations, 4)
        # TODO: Also generate gates at some point?
        count = multiworld.random.randint(1, min(options.num_tracks - cur_track, 4))
        node_layers[cur_layer] = list(range(cur_track,cur_track+count))
        cur_track += count
        cur_layer = max(node_layers.keys()) + 1
    ## Step 2: Generate connections
    nodes_occupied = []
    for cur_layer in range(len(node_layers)-1):
        exist_next_layer_conn = False
        for cur_node in node_layers[cur_layer]:
            node_connections[cur_node] = []
            if multiworld.random.randint(1,3) >= 2: # 2/3 chance of a connection
                target_node = multiworld.random.choice(node_layers[cur_layer+1])
                node_connections[cur_node].append(target_node)
                nodes_occupied.append(target_node)
                exist_next_layer_conn = True
        if not exist_next_layer_conn:
            # Unlucky, current layer has no connection to next. Choose one explicitly
            target_node = multiworld.random.choice(node_layers[cur_layer+1])
            node_connections[multiworld.random.choice(node_layers[cur_layer])] = [target_node]
            nodes_occupied.append(target_node)
    # Create empty connections for last layer
    for cur_node in node_layers[cur_layer+1]:
        node_connections[cur_node] = []
    # Multiple nodes cannot be unlocked at the start, so all without dependencies so far are assigned root as dependency
    for i in range(options.num_tracks):
        if i not in nodes_occupied and i != 0:
            node_connections[0].append(i)

    # Finally, actual rule generation
    # Enforce that for every connection there exists a dependency on previous track and local song item
    for node, targets in node_connections.items():
        # For each child node, access to parent node is required. If parent is root this is not needed
        for target in targets:
            __add_node_dep_rule(multiworld, player, node, target)
            print(f"{node} -> {target}")
        # For every node but root, the track item is required
        if node == 0: continue
        __add_song_rule(multiworld, player, node)
    # Winning condition: Beat campaing, so all songs currently.
    #TODO: Need to designate final node or smth
    multiworld.completion_condition[player] = lambda state: all(state.has("Song " + f"{node}".zfill(2), player) for node in range(1, options.num_tracks))
