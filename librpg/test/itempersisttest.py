# Imports

import librpg
from librpg.map import MapModel
from librpg.mapobject import ScenarioMapObject
from librpg.util import Position
from librpg.party import Character, Party
from librpg.world import MicroWorld
from librpg.item import OrdinaryInventory
from librpg.dialog import MessageDialog
from librpg.collection.context import CommandContext
from librpg.collection.menu import ItemMenu
from librpg.collection.theme import ClassicMenuTheme
from librpg.path import charset_path, tileset_path

from pygame.locals import K_i, K_p, K_a, K_b, K_c, K_d
import os

import itembase


SAVE_FILE = "itempersisttest_save"


# Map objects

class LogPile(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 2)

    def activate(self, party_avatar, direction):
        added = party_avatar.party.inventory.add_item_by_id('log')
        if added:
            MessageDialog("Got a Log.").sync_open()
        else:
            MessageDialog("Inventory full of Logs.").sync_open()


class Tree(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 23)

    def activate(self, party_avatar, direction):
        added = party_avatar.party.inventory.add_item_by_id('leaf')
        if added:
            msg = "Got a Leaf."
        else:
            msg = "Inventory full of Leaves."
        MessageDialog(msg).sync_open()


class PandoraBarrel(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 4)

    def activate(self, party_avatar, direction):
        for id in itembase.item_factory.classes.keys():
            party_avatar.party.inventory.add_item_by_id(id)
        MessageDialog('Found a lot of stuff inside the barrel.').sync_open()


class SavePoint(ScenarioMapObject):

    def __init__(self, map):
        ScenarioMapObject.__init__(self, map, 0, 1)

    def activate(self, party_avatar, direction):
        MessageDialog('You game will be saved to %s.' % SAVE_FILE,
                      block_movement=True).sync_open()
        self.map.save_world(SAVE_FILE)
        MessageDialog('Game saved.', block_movement=True).sync_open()


# Map

class PersistTestMap(MapModel):

    def __init__(self):
        MapModel.__init__(self, 'itempersisttest.map',
                          (tileset_path('city_lower.png'),
                           tileset_path('city_lower.bnd')),
                          [(tileset_path('world_upper.png'),
                            tileset_path('world_upper.bnd'))])

    def initialize(self, local_state, global_state):
        self.add_object(LogPile(self), Position(4, 5))
        self.add_object(Tree(self), Position(6, 5))
        self.add_object(PandoraBarrel(self), Position(5, 6))
        self.add_object(SavePoint(self), Position(5, 2))

        self.inventory_context = InventoryContext(self)
        self.add_context(self.inventory_context)


# Party

class TestParty(Party):

    def __init__(self, reserve):
        Party.__init__(self, reserve)
        self.inventory = OrdinaryInventory(itembase.item_factory)

    def custom_save(self):
        return self.inventory.save_state()

    def custom_load(self, party_state=None):
        self.inventory.load_state(party_state)
        print 'Loaded', self.inventory.get_items_with_amounts()


# Char and party factories

def char_factory(name):
    CHAR_IMAGES = {'Andy': (charset_path('naked_man.png'), 0),
                   'Brenda': ('test_chars.png', 1),
                   'Charles': ('test_chars.png', 0),
                   'Dylan': ('test_chars.png', 2)}
    image_and_index = CHAR_IMAGES[name]
    return Character(name, image_and_index[0], image_and_index[1])


def party_factory(reserve):
    return TestParty(reserve)


# Inventory context

class InventoryContext(CommandContext):

    def __init__(self, map):
        CommandContext.__init__(self,
                                {K_i: self.open_inventory,
                                 K_p: self.open_party,
                                 K_a: (self.switch_char, 'Andy'),
                                 K_b: (self.switch_char, 'Brenda'),
                                 K_c: (self.switch_char, 'Charles'),
                                 K_d: (self.switch_char, 'Dylan')},
                                map.controller)
        self.map = map
        self.reserve = map.world.reserve
        self.party = map.party
        self.inv = map.party.inventory
        self.item_menu = None

    def open_inventory(self):
        self.item_menu = MyItemMenu(self.inv, self.party)
        self.item_menu.sync_open()
        return True

    def open_party(self):
        msg = 'Party:' + str(self.party)
        MessageDialog(msg).sync_open()
        msg = 'Reserve:' + str(self.reserve.get_names())
        MessageDialog(msg).sync_open()
        return True

    def switch_char(self, char):
        if char in self.party.chars:
            if (len(self.party.chars) > 1
                and self.party.remove_char(char)):
                    msg = 'Removed %s.' % char
            else:
                msg = 'Cannot remove %s.' % char
        else:
            if self.party.add_char(char):
                msg = 'Added %s.' % char
            else:
                msg = 'Could not add %s.' % char
        MessageDialog(msg).sync_open()
        return True


class MyItemMenu(ItemMenu):

    def __init__(self, inv, party):
        ItemMenu.__init__(self, inv, party,
                          librpg.config.graphics_config.screen_width - 40,
                          librpg.config.graphics_config.screen_height - 40,
                          x=20, y=20)
        #self.config_action_dialog(bg=(0, 28, 0, 60))


# Main

def main():
    librpg.init('Item Persist Test')
    librpg.config.graphics_config.config(tile_size=32,
                                         object_height=32,
                                         object_width=32,
                                         scale=2,
                                         screen_width=480,
                                         screen_height=320)
    librpg.config.menu_config.config(theme=ClassicMenuTheme())

    world = MicroWorld(PersistTestMap(), char_factory, party_factory)
    if SAVE_FILE in os.listdir('.'):
        world.load_state(SAVE_FILE)
    else:
        world.initial_state(Position(4, 3),
                             chars=['Andy', 'Brenda', 'Charles', 'Dylan'],
                             party_capacity=3,
                             party=['Andy'])
    world.gameloop()
    exit()

if __name__ == '__main__':
    main()
