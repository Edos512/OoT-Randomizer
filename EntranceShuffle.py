import random
import logging
from collections import OrderedDict
from Playthrough import Playthrough
from Rules import set_entrances_based_rules
from Entrance import Entrance
from State import State
from Item import ItemFactory


def get_entrance_pool(type):
    return [entrance_data for entrance_data in entrance_shuffle_table if entrance_data[0] == type]


def entrance_instances(world, entrance_pool):
    entrance_instances = []
    for type, forward_entrance, *return_entrance in entrance_pool:
        forward_entrance = set_shuffled_entrance(world, forward_entrance[0], forward_entrance[1], type)
        if return_entrance:
            return_entrance = return_entrance[0]
            return_entrance = set_shuffled_entrance(world, return_entrance[0], return_entrance[1], type)
            forward_entrance.bind_two_way(return_entrance)
        entrance_instances.append(forward_entrance)
    return entrance_instances


def set_shuffled_entrance(world, name, data, type):
    entrance = world.get_entrance(name)
    entrance.type = type
    entrance.data = data
    entrance.shuffled = True
    return entrance


def assume_pool_reachable(world, entrance_pool):
    assumed_pool = []
    for entrance in entrance_pool:
        assumed_forward = entrance.assume_reachable()
        if entrance.reverse != None:
            assumed_return = entrance.reverse.assume_reachable()
            if entrance.type in ['Dungeon', 'Interior', 'Grotto']:
                # Dungeon, Grotto and Simple Interior exits shouldn't be assumed to be able to give access to their parent region
                assumed_return.access_rule = lambda state: False
            assumed_forward.bind_two_way(assumed_return)
        assumed_pool.append(assumed_forward)
    return assumed_pool


entrance_shuffle_table = [
    ('Dungeon',  ('Outside Deku Tree -> Deku Tree Lobby',                    { 'index': 0x0000 }),
                 ('Deku Tree Lobby -> Outside Deku Tree',                    { 'index': 0x0209, 'blue_warp': 0x0457 })),
    ('Dungeon',  ('Dodongos Cavern Entryway -> Dodongos Cavern Beginning',   { 'index': 0x0004 }),
                 ('Dodongos Cavern Beginning -> Dodongos Cavern Entryway',   { 'index': 0x0242, 'blue_warp': 0x047A })),
    ('Dungeon',  ('Zoras Fountain -> Jabu Jabus Belly Beginning',            { 'index': 0x0028 }),
                 ('Jabu Jabus Belly Beginning -> Zoras Fountain',            { 'index': 0x0221, 'blue_warp': 0x010E })),
    ('Dungeon',  ('Sacred Forest Meadow -> Forest Temple Lobby',             { 'index': 0x0169 }),
                 ('Forest Temple Lobby -> Sacred Forest Meadow',             { 'index': 0x0215, 'blue_warp': 0x0608 })),
    ('Dungeon',  ('Death Mountain Crater Central -> Fire Temple Lower',      { 'index': 0x0165 }),
                 ('Fire Temple Lower -> Death Mountain Crater Central',      { 'index': 0x024A, 'blue_warp': 0x0564 })),
    ('Dungeon',  ('Lake Hylia -> Water Temple Lobby',                        { 'index': 0x0010 }),
                 ('Water Temple Lobby -> Lake Hylia',                        { 'index': 0x021D, 'blue_warp': 0x060C })),
    ('Dungeon',  ('Desert Colossus -> Spirit Temple Lobby',                  { 'index': 0x0082 }),
                 ('Spirit Temple Lobby -> Desert Colossus',                  { 'index': 0x01E1, 'blue_warp': 0x0610 })),
    ('Dungeon',  ('Shadow Temple Warp Region -> Shadow Temple Entryway',     { 'index': 0x0037 }),
                 ('Shadow Temple Entryway -> Shadow Temple Warp Region',     { 'index': 0x0205, 'blue_warp': 0x0580 })),
    ('Dungeon',  ('Kakariko Village -> Bottom of the Well',                  { 'index': 0x0098 }),
                 ('Bottom of the Well -> Kakariko Village',                  { 'index': 0x02A6 })),
    ('Dungeon',  ('Zoras Fountain -> Ice Cavern Beginning',                  { 'index': 0x0088 }),
                 ('Ice Cavern Beginning -> Zoras Fountain',                  { 'index': 0x03D4 })),
    ('Dungeon',  ('Gerudo Fortress -> Gerudo Training Grounds Lobby',        { 'index': 0x0008 }),
                 ('Gerudo Training Grounds Lobby -> Gerudo Fortress',        { 'index': 0x03A8 })),

    ('Interior', ('Kokiri Forest -> Mido House',                             { 'index': 0x0433 }),
                 ('Mido House -> Kokiri Forest',                             { 'index': 0x0443 })),
    ('Interior', ('Kokiri Forest -> Saria House',                            { 'index': 0x0437 }),
                 ('Saria House -> Kokiri Forest',                            { 'index': 0x0447 })),
    ('Interior', ('Kokiri Forest -> House of Twins',                         { 'index': 0x009C }),
                 ('House of Twins -> Kokiri Forest',                         { 'index': 0x033C })),
    ('Interior', ('Kokiri Forest -> Know It All House',                      { 'index': 0x00C9 }),
                 ('Know It All House -> Kokiri Forest',                      { 'index': 0x026A })),
    ('Interior', ('Kokiri Forest -> Kokiri Shop',                            { 'index': 0x00C1 }),
                 ('Kokiri Shop -> Kokiri Forest',                            { 'index': 0x0266 })),
    ('Interior', ('Lake Hylia -> Lake Hylia Lab',                            { 'index': 0x0043 }),
                 ('Lake Hylia Lab -> Lake Hylia',                            { 'index': 0x03CC })),
    ('Interior', ('Lake Hylia -> Fishing Hole',                              { 'index': 0x045F }),
                 ('Fishing Hole -> Lake Hylia',                              { 'index': 0x0309 })),
    ('Interior', ('Gerudo Valley Far Side -> Carpenter Tent',                { 'index': 0x03A0 }),
                 ('Carpenter Tent -> Gerudo Valley Far Side',                { 'index': 0x03D0 })),
    ('Interior', ('Castle Town Entrance -> Castle Town Rupee Room',          { 'index': 0x007E }),
                 ('Castle Town Rupee Room -> Castle Town Entrance',          { 'index': 0x026E })),
    ('Interior', ('Castle Town -> Castle Town Mask Shop',                    { 'index': 0x0530 }),
                 ('Castle Town Mask Shop -> Castle Town',                    { 'index': 0x01D1 })),
    ('Interior', ('Castle Town -> Castle Town Bombchu Bowling',              { 'index': 0x0507 }),
                 ('Castle Town Bombchu Bowling -> Castle Town',              { 'index': 0x03BC })),
    ('Interior', ('Castle Town -> Castle Town Potion Shop',                  { 'index': 0x0388 }),
                 ('Castle Town Potion Shop -> Castle Town',                  { 'index': 0x02A2 })),
    ('Interior', ('Castle Town -> Castle Town Treasure Chest Game',          { 'index': 0x0063 }),
                 ('Castle Town Treasure Chest Game -> Castle Town',          { 'index': 0x01D5 })),
    ('Interior', ('Castle Town -> Castle Town Bombchu Shop',                 { 'index': 0x0528 }),
                 ('Castle Town Bombchu Shop -> Castle Town',                 { 'index': 0x03C0 })),
    ('Interior', ('Castle Town -> Castle Town Man in Green House',           { 'index': 0x043B }),
                 ('Castle Town Man in Green House -> Castle Town',           { 'index': 0x0067 })),
    ('Interior', ('Kakariko Village -> Carpenter Boss House',                { 'index': 0x02FD }),
                 ('Carpenter Boss House -> Kakariko Village',                { 'index': 0x0349 })),
    ('Interior', ('Kakariko Village -> House of Skulltula',                  { 'index': 0x0550 }),
                 ('House of Skulltula -> Kakariko Village',                  { 'index': 0x04EE })),
    ('Interior', ('Kakariko Village -> Impas House',                         { 'index': 0x039C }),
                 ('Impas House -> Kakariko Village',                         { 'index': 0x0345 })),
    ('Interior', ('Kakariko Village -> Impas House Back',                    { 'index': 0x05C8 }),
                 ('Impas House Back -> Kakariko Village',                    { 'index': 0x05DC })),
    ('Interior', ('Kakariko Village -> Odd Medicine Building',               { 'index': 0x0072 }),
                 ('Odd Medicine Building -> Kakariko Village',               { 'index': 0x034D })),
    ('Interior', ('Graveyard -> Dampes House',                               { 'index': 0x030D }),
                 ('Dampes House -> Graveyard',                               { 'index': 0x0355 })),
    ('Interior', ('Goron City -> Goron Shop',                                { 'index': 0x037C }),
                 ('Goron Shop -> Goron City',                                { 'index': 0x03FC })),
    ('Interior', ('Zoras Domain -> Zora Shop',                               { 'index': 0x0380 }),
                 ('Zora Shop -> Zoras Domain',                               { 'index': 0x03C4 })),
    ('Interior', ('Lon Lon Ranch -> Talon House',                            { 'index': 0x004F }),
                 ('Talon House -> Lon Lon Ranch',                            { 'index': 0x0378 })),
    ('Interior', ('Lon Lon Ranch -> Ingo Barn',                              { 'index': 0x02F9 }),
                 ('Ingo Barn -> Lon Lon Ranch',                              { 'index': 0x042F })),
    ('Interior', ('Lon Lon Ranch -> Lon Lon Corner Tower',                   { 'index': 0x05D0 }),
                 ('Lon Lon Corner Tower -> Lon Lon Ranch',                   { 'index': 0x05D4 })),
    ('Interior', ('Castle Town -> Castle Town Bazaar',                       { 'index': 0x052C }),
                 ('Castle Town Bazaar -> Castle Town',                       { 'index': 0x03B8, 'dynamic_address': 0xBEFD74 })),
    ('Interior', ('Castle Town -> Castle Town Shooting Gallery',             { 'index': 0x016D }),
                 ('Castle Town Shooting Gallery -> Castle Town',             { 'index': 0x01CD, 'dynamic_address': 0xBEFD7C })),
    ('Interior', ('Kakariko Village -> Kakariko Bazaar',                     { 'index': 0x00B7 }),
                 ('Kakariko Bazaar -> Kakariko Village',                     { 'index': 0x0201, 'dynamic_address': 0xBEFD72 })),
    ('Interior', ('Kakariko Village -> Kakariko Shooting Gallery',           { 'index': 0x003B }),
                 ('Kakariko Shooting Gallery -> Kakariko Village',           { 'index': 0x0463, 'dynamic_address': 0xBEFD7A })),
    ('Interior', ('Desert Colossus -> Colossus Fairy',                       { 'index': 0x0588 }),
                 ('Colossus Fairy -> Desert Colossus',                       { 'index': 0x057C, 'dynamic_address': 0xBEFD82 })),
    ('Interior', ('Hyrule Castle Grounds -> Hyrule Castle Fairy',            { 'index': 0x0578 }),
                 ('Hyrule Castle Fairy -> Castle Grounds',                   { 'index': 0x0340, 'dynamic_address': 0xBEFD80 })),
    ('Interior', ('Ganons Castle Grounds -> Ganons Castle Fairy',            { 'index': 0x04C2 }),
                 ('Ganons Castle Fairy -> Castle Grounds',                   { 'index': 0x0340, 'dynamic_address': 0xBEFD6C })),
    ('Interior', ('Death Mountain Crater Lower -> Crater Fairy',             { 'index': 0x04BE }),
                 ('Crater Fairy -> Death Mountain Crater Lower',             { 'index': 0x0482, 'dynamic_address': 0xBEFD6A })),
    ('Interior', ('Death Mountain Summit -> Mountain Summit Fairy',          { 'index': 0x0315 }),
                 ('Mountain Summit Fairy -> Death Mountain Summit',          { 'index': 0x045B, 'dynamic_address': 0xBEFD68 })),
    ('Interior', ('Zoras Fountain -> Zoras Fountain Fairy',                  { 'index': 0x0371 }),
                 ('Zoras Fountain Fairy -> Zoras Fountain',                  { 'index': 0x0394, 'dynamic_address': 0xBEFD7E })),

    ('Grotto',   ('Desert Colossus -> Desert Colossus Grotto',               { 'scene': 0x5C, 'grotto_var': 0x00FD })),
    ('Grotto',   ('Lake Hylia -> Lake Hylia Grotto',                         { 'scene': 0x57, 'grotto_var': 0x00EF })),
    ('Grotto',   ('Zora River -> Zora River Storms Grotto',                  { 'scene': 0x54, 'grotto_var': 0x01EB })),
    ('Grotto',   ('Zora River -> Zora River Plateau Bombable Grotto',        { 'scene': 0x54, 'grotto_var': 0x10E6 })),
    ('Grotto',   ('Zora River -> Zora River Plateau Open Grotto',            { 'scene': 0x54, 'grotto_var': 0x0029 })),
    ('Grotto',   ('Death Mountain Crater Lower -> DMC Hammer Grotto',        { 'scene': 0x61, 'grotto_var': 0x00F9 })),
    ('Grotto',   ('Death Mountain Crater Upper -> Top of Crater Grotto',     { 'scene': 0x61, 'grotto_var': 0x007A })),
    ('Grotto',   ('Goron City -> Goron City Grotto',                         { 'scene': 0x62, 'grotto_var': 0x00FB })),
    ('Grotto',   ('Death Mountain -> Mountain Storms Grotto',                { 'scene': 0x60, 'grotto_var': 0x0157 })),
    ('Grotto',   ('Death Mountain -> Mountain Bombable Grotto',              { 'scene': 0x60, 'grotto_var': 0x00F8 })),
    ('Grotto',   ('Kakariko Village -> Kakariko Back Grotto',                { 'scene': 0x52, 'grotto_var': 0x0028 })),
    ('Grotto',   ('Kakariko Village -> Kakariko Bombable Grotto',            { 'scene': 0x52, 'grotto_var': 0x02E7 })),
    ('Grotto',   ('Hyrule Castle Grounds -> Castle Storms Grotto',           { 'scene': 0x5F, 'grotto_var': 0x01F6 })),
    ('Grotto',   ('Hyrule Field -> Field North Lon Lon Grotto',              { 'scene': 0x51, 'grotto_var': 0x02E1 })),
    ('Grotto',   ('Hyrule Field -> Field Kakariko Grotto',                   { 'scene': 0x51, 'grotto_var': 0x02E5 })),
    ('Grotto',   ('Hyrule Field -> Field Far West Castle Town Grotto',       { 'scene': 0x51, 'grotto_var': 0x10FF })),
    ('Grotto',   ('Hyrule Field -> Field West Castle Town Grotto',           { 'scene': 0x51, 'grotto_var': 0x0000 })),
    ('Grotto',   ('Hyrule Field -> Field Valley Grotto',                     { 'scene': 0x51, 'grotto_var': 0x02E4 })),
    ('Grotto',   ('Hyrule Field -> Field Near Lake Inside Fence Grotto',     { 'scene': 0x51, 'grotto_var': 0x02E6 })),
    ('Grotto',   ('Hyrule Field -> Field Near Lake Outside Fence Grotto',    { 'scene': 0x51, 'grotto_var': 0x0003 })),
    ('Grotto',   ('Hyrule Field -> Remote Southern Grotto',                  { 'scene': 0x51, 'grotto_var': 0x0022 })),
    ('Grotto',   ('Lon Lon Ranch -> Lon Lon Grotto',                         { 'scene': 0x63, 'grotto_var': 0x00FC })),
    ('Grotto',   ('Sacred Forest Meadow Entryway -> Front of Meadow Grotto', { 'scene': 0x56, 'grotto_var': 0x02ED })),
    ('Grotto',   ('Sacred Forest Meadow -> Meadow Storms Grotto',            { 'scene': 0x56, 'grotto_var': 0x01EE })),
    ('Grotto',   ('Sacred Forest Meadow -> Meadow Fairy Grotto',             { 'scene': 0x56, 'grotto_var': 0x10FF })),
    ('Grotto',   ('Lost Woods Beyond Mido -> Lost Woods Sales Grotto',       { 'scene': 0x5B, 'grotto_var': 0x00F5 })),
    ('Grotto',   ('Lost Woods -> Lost Woods Generic Grotto',                 { 'scene': 0x5B, 'grotto_var': 0x0014 })),
    ('Grotto',   ('Kokiri Forest -> Kokiri Forest Storms Grotto',            { 'scene': 0x55, 'grotto_var': 0x012C })),
    ('Grotto',   ('Zoras Domain -> Zoras Domain Storms Grotto',              { 'scene': 0x58, 'grotto_var': 0x11FF })),
    ('Grotto',   ('Gerudo Fortress -> Gerudo Fortress Storms Grotto',        { 'scene': 0x5D, 'grotto_var': 0x11FF })),
    ('Grotto',   ('Gerudo Valley Far Side -> Gerudo Valley Storms Grotto',   { 'scene': 0x5A, 'grotto_var': 0x01F0 })),
    ('Grotto',   ('Gerudo Valley -> Gerudo Valley Octorok Grotto',           { 'scene': 0x5A, 'grotto_var': 0x00F2 })),
    ('Grotto',   ('Lost Woods Beyond Mido -> Deku Theater',                  { 'scene': 0x5B, 'grotto_var': 0x00F3 })),
]


class EntranceShuffleError(RuntimeError):
    pass


# Set entrances of all worlds, first initializing them to their default regions, then potentially shuffling part of them
def set_entrances(worlds):
    for world in worlds:
        world.initialize_entrances()

    if worlds[0].entrance_shuffle != 'off':
        shuffle_random_entrances(worlds)

    set_entrances_based_rules(worlds)


# Shuffles entrances that need to be shuffled in all worlds
def shuffle_random_entrances(worlds):

    # Store all locations reachable before shuffling to differentiate which locations were already unreachable from those we made unreachable
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    non_drop_locations = [location for world in worlds for location in world.get_locations() if location.type != 'Drop']
    max_playthrough.visit_locations(non_drop_locations)
    locations_to_ensure_reachable = [location for location in non_drop_locations if max_playthrough.visited(location)]

    # Shuffle all entrances within their own worlds
    for world in worlds:

        # Determine entrance pools based on settings
        entrance_pools = OrderedDict()

        if worlds[0].shuffle_dungeon_entrances:
            dungeon_entrance_pool = get_entrance_pool('Dungeon')
            # The fill algorithm will already make sure gohma is reachable, however it can end up putting
            # a forest escape via the hands of spirit on Deku leading to Deku on spirit in logic. This is
            # not really a closed forest anymore, so specifically remove Deku Tree from closed forest.
            if (not worlds[0].open_forest):
                dungeon_entrance_pool = list(filter(lambda entrance_data: entrance_data[1][0] != "Outside Deku Tree -> Deku Tree Lobby", dungeon_entrance_pool))
            entrance_pools['Dungeon'] = entrance_instances(world, dungeon_entrance_pool)

        if worlds[0].shuffle_interior_entrances:
            interior_entrance_pool = get_entrance_pool('Interior')
            entrance_pools['Interior'] = entrance_instances(world, interior_entrance_pool)

        if worlds[0].shuffle_grotto_entrances:
            grotto_entrance_pool = get_entrance_pool('Grotto')
            entrance_pools['Grotto'] = entrance_instances(world, grotto_entrance_pool)

        # Set the assumption that all entrances are reachable
        target_entrance_pools = {}
        for pool_type, entrance_pool in entrance_pools.items():
            target_entrance_pools[pool_type] = assume_pool_reachable(world, entrance_pool)

        # Shuffle all entrances among the pools to shuffle
        for pool_type, entrance_pool in entrance_pools.items():
            if pool_type in ['Dungeon']:
                # Those pools contain entrances leading to regions that might open access to completely new areas
                # Dungeons are among those because exiting Spirit Temple from the hands is in logic 
                # and could give access to Desert Colossus and potentially new areas from there
                shuffle_entrance_pool(worlds, entrance_pool, target_entrance_pools[pool_type], locations_to_ensure_reachable)
            else:
                # Other pools are only "internal", which means they are leaves in the world graph and can't open new access
                shuffle_entrance_pool(worlds, entrance_pool, target_entrance_pools[pool_type], locations_to_ensure_reachable, internal=True)

    # Multiple checks after shuffling entrances to make sure everything went fine
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)
    max_playthrough.visit_locations(locations_to_ensure_reachable)

    # Check that all shuffled entrances are properly connected to a region
    for world in worlds:
        for entrance in world.get_shuffled_entrances():
            if entrance.connected_region == None:
                logging.getLogger('').error('%s was shuffled but still isn\'t connected to any region [World %d]', entrance, world.id)

    # Log all locations unreachable due to shuffling entrances
    alr_compliant = True
    if not worlds[0].check_beatable_only:
        for location in locations_to_ensure_reachable:
            if not max_playthrough.visited(location):
                logging.getLogger('').error('Location now unreachable after shuffling entrances: %s [World %d]', location, location.world.id)
                alr_compliant = False

    # Check for game beatability in all worlds
    if not max_playthrough.can_beat_game(False):
        raise EntranceShuffleError('Cannot beat game!')

    # Throw an error if shuffling entrances broke the contract of ALR (All Locations Reachable)
    if not alr_compliant:
        raise EntranceShuffleError('ALR is enabled but not all locations are reachable!')

    # Validate the worlds one last time to ensure all special conditions are still valid
    valid_worlds, invalid_reason = validate_worlds(worlds, locations_to_ensure_reachable, complete_itempool)
    if not valid_worlds:
        raise EntranceShuffleError('Worlds are not valid after shuffling entrances because of %s', invalid_reason)


# Shuffle all entrances within a provided pool
def shuffle_entrance_pool(worlds, entrance_pool, target_entrances, locations_to_ensure_reachable, internal=False):

    # Split entrances between those that have requirements (restrictive) and those that do not (soft). These are primarily age or time of day requirements.
    restrictive_entrances, soft_entrances = split_entrances_by_requirements(worlds, entrance_pool, target_entrances)

    # Shuffle restrictive entrances first while more regions are available in order to heavily reduce the chances of the placement failing.
    # check_valid=True ensures the world's structure stays valid according to settings
    shuffle_entrances(worlds, restrictive_entrances, target_entrances, locations_to_ensure_reachable, check_valid=True)

    # Shuffle the rest of the entrances
    if internal:
        # If we are shuffling an "internal" entrance pool, those entrances can be considered as completely versatile, 
        # So we don't have to check for validity while placing them
        shuffle_entrances(worlds, soft_entrances, target_entrances, check_valid=False)
    else:
        # Otherwise, we should still ensure the worlds stay valid when placing entrances
        shuffle_entrances(worlds, soft_entrances, target_entrances, locations_to_ensure_reachable, check_valid=True)


# Split entrances based on their requirements to figure out how each entrance should be handled when shuffling them
def split_entrances_by_requirements(worlds, entrances_to_split, assumed_entrances):

    # First, disconnect all root assumed entrances and save which regions they were originally connected to, so we can reconnect them later
    original_connected_regions = {}
    entrances_to_disconnect = assumed_entrances + [entrance.reverse for entrance in assumed_entrances 
                                                    if entrance.reverse and entrance.reverse not in assumed_entrances]
    for entrance in entrances_to_disconnect:
        if entrance.connected_region:
            original_connected_regions[entrance] = entrance.disconnect()

    # Generate the states with all assumed entrances disconnected
    # This ensures that no assumed entrances corresponding to those we are shuffling are required in order for an entrance to be reachable as one age/tod
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]
    max_playthrough = Playthrough.max_explore([world.state for world in worlds], complete_itempool)

    restrictive_entrances = []
    soft_entrances = []

    for entrance in entrances_to_split:
        # Here, we find entrances that may be unreachable under certain conditions
        if not max_playthrough.state_list[entrance.world.id].can_reach(entrance, age='both', tod='all'):
            restrictive_entrances.append(entrance)
            continue
        # If an entrance is reachable as both ages and all times of day with all the other entrances disconnected,
        # then it can always be made accessible in all situations by the Fill algorithm, no matter which combination of entrances we end up with.
        # Thus, those entrances aren't bound to any specific requirements and are very versatile during placement.
        soft_entrances.append(entrance)

    # Reconnect all disconnected entrances afterwards
    for entrance in entrances_to_disconnect:
        if entrance in original_connected_regions:
            entrance.connect(original_connected_regions[entrance])

    return restrictive_entrances, soft_entrances


# Shuffle entrances by placing them instead of entrances in the provided target entrances list
# While shuffling entrances, if the check_valid parameter is true, the algorithm will ensure worlds are still valid based on settings
def shuffle_entrances(worlds, entrances, target_entrances, locations_to_ensure_reachable=None, retry_count=16, check_valid=True):

    # Retrieve all items in the itempool, all worlds included
    complete_itempool = [item for world in worlds for item in world.get_itempool_with_dungeon_items()]

    for _ in range(retry_count):
        success = True
        random.shuffle(entrances)
        rollbacks = []

        # Attempt to place all entrances in the pool, validating the states during every placement if necessary
        for entrance in entrances:
            if entrance.connected_region != None:
                continue
            random.shuffle(target_entrances)

            for target in target_entrances:
                # An entrance can't be connected to its reverse so we must always skip that case
                if target.connected_region == None or entrance == target.replaces.reverse:
                    continue

                change_connections(entrance, target)

                if check_valid:
                    valid_placement, fail_reason = validate_worlds(worlds, locations_to_ensure_reachable, complete_itempool)
                else:
                    valid_placement = True

                if valid_placement:
                    rollbacks.append((entrance, target))
                    break
                else:
                    # If the entrance can't be placed there, log a debug message and change the connections back to what they were previously
                    logging.getLogger('').debug('Failed to connect %s To %s (because of %s) [World %d]',
                                                entrance, entrance.connected_region, fail_reason, entrance.world.id)
                    restore_connections(entrance, target)

            if entrance.connected_region == None:
                success = False
                break

        # Check if all entrances were able to be placed, log connections and continue if that's the case, or rollback everything otherwise
        if success:
            for entrance, target in rollbacks:
                confirm_replacement(entrance, target)
            return
        else:
            for entrance, target in rollbacks:
                restore_connections(entrance, target)

        logging.getLogger('').debug('Entrance placement attempt failed [World %d]', entrances[0].world.id)

    raise EntranceShuffleError('Entrance placement attempt retry count exceeded [World %d]' % entrances[0].world.id)


# Validate the provided worlds' structures, returning whether or not the states are still correct based on some setting-dependent criterias
# It also returns the reason for failing so we can use it in debug logs
def validate_worlds(worlds, locations_to_ensure_reachable, itempool):

    max_playthrough = Playthrough.max_explore([world.state for world in worlds], itempool)

    # If ALR is enabled, ensure all locations we want to keep reachable are indeed still reachable, otherwise just continue if the game is still beatable
    if not (worlds[0].check_beatable_only and max_playthrough.can_beat_game(False)):
        max_playthrough.visit_locations(locations_to_ensure_reachable)
        for location in locations_to_ensure_reachable:
            if not max_playthrough.visited(location):
                return (False, location.name)

    return (True, None)


# Change connections between an entrance and a target assumed entrance, in order to test the connections afterwards if necessary
def change_connections(entrance, target_entrance):
    entrance.connect(target_entrance.disconnect())
    entrance.replaces = target_entrance.replaces
    if entrance.reverse:
        target_entrance.replaces.reverse.connect(entrance.reverse.assumed.disconnect())
        target_entrance.replaces.reverse.replaces = entrance.reverse.assumed.replaces


# Restore connections between an entrance and a target assumed entrance
def restore_connections(entrance, target_entrance):
    target_entrance.connect(entrance.disconnect())
    entrance.replaces = None
    if entrance.reverse:
        entrance.reverse.assumed.connect(target_entrance.replaces.reverse.disconnect())
        target_entrance.replaces.reverse.replaces = None


# Confirm the replacement of a target entrance by a new entrance, logging the new connections and completely deleting the target entrances
def confirm_replacement(entrance, target_entrance):
    delete_target_entrance(target_entrance)
    logging.getLogger('').debug('Connected %s To %s [World %d]', entrance, entrance.connected_region, entrance.world.id)
    if entrance.reverse:
        replaced_reverse = target_entrance.replaces.reverse
        delete_target_entrance(entrance.reverse.assumed)
        logging.getLogger('').debug('Connected %s To %s [World %d]', replaced_reverse, replaced_reverse.connected_region, replaced_reverse.world.id)


# Delete an assumed target entrance, by disconnecting it if needed and removing it from its parent region
def delete_target_entrance(target_entrance):
    if target_entrance.connected_region != None:
        target_entrance.disconnect()
    if target_entrance.parent_region != None:
        target_entrance.parent_region.exits.remove(target_entrance)
        target_entrance.parent_region = None
