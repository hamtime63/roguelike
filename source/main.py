"""
Starting Template Simple

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template_simple
"""
import arcade
import pyglet.gl as gl

from game_map import GameMap
from constants import *
from entity import Entity
from recalculate_fov import recalculate_fov
from util import char_to_pixel
from fighter import Fighter
from util import get_blocking_sprites

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=False)

        arcade.set_background_color(arcade.color.BLACK)
        self.game_map = None
        self.player = None

        self.characters = None
        self.entities = None
        self.dungeon_sprites = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.up_left_pressed = False
        self.up_right_pressed = False
        self.down_left_pressed = False
        self.down_right_pressed = False

        self.game_state = PLAYER_TURN

        self.keyboard_frame_counter = 0

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # Set game state
        self.game_state = PLAYER_TURN

        # Create sprite lists
        self.characters = arcade.SpriteList()
        self.dungeon_sprites = arcade.SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=16
        )
        self.entities = arcade.SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=16
        )

        # Create player
        fighter_component = Fighter(hp=30, defense=2, power=5)
        self.player = Entity(x=0,
                             y=0,
                             char="@",
                             color=arcade.csscolor.WHITE,
                             fighter=fighter_component,
                             name="Player")
        self.characters.append(self.player)

        # --- Create map
        # Size of the map
        map_width = MAP_WIDTH
        map_height = MAP_HEIGHT

        # Some variables for the rooms in the map
        room_max_size = 10
        room_min_size = 6
        max_rooms = 30

        self.game_map = GameMap(map_width, map_height)
        self.game_map.make_map(
            max_rooms=max_rooms,
            room_min_size=room_min_size,
            room_max_size=room_max_size,
            map_width=map_width,
            map_height=map_height,
            player=self.player,
            entities=self.entities,
            max_monsters_per_room=3,
        )

        # Draw all the tiles in the game map
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                wall = self.game_map.tiles[x][y].block_sight
                sprite = Entity(x, y, WALL_CHAR, arcade.csscolor.BLACK)
                if wall:
                    sprite.name = "Wall"
                    sprite.block_sight = True
                    sprite.blocks = True
                    sprite.visible_color = colors["light_wall"]
                    sprite.not_visible_color = colors["dark_wall"]
                else:
                    sprite.name = "Ground"
                    sprite.block_sight = False
                    sprite.visible_color = colors["light_ground"]
                    sprite.not_visible_color = colors["dark_ground"]

                self.dungeon_sprites.append(sprite)

        # Set field of view
        recalculate_fov(
            self.player.x,
            self.player.y,
            FOV_RADIUS,
            [self.dungeon_sprites, self.entities],
        )

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()

        self.dungeon_sprites.draw(filter=gl.GL_NEAREST)
        self.entities.draw(filter=gl.GL_NEAREST)
        self.characters.draw(filter=gl.GL_NEAREST)


    def move_player(self, cx, cy):
        nx = self.player.x + cx
        ny = self.player.y + cy
        blocking_dungeon_sprites = get_blocking_sprites(nx, ny, self.dungeon_sprites)
        blocking_entity_sprites = get_blocking_sprites(nx, ny, self.entities)
        if not blocking_dungeon_sprites and not blocking_entity_sprites:
            self.player.x += cx
            self.player.y += cy
            recalculate_fov(
                self.player.x,
                self.player.y,
                FOV_RADIUS,
                [self.dungeon_sprites, self.entities],
            )
            return True
        elif blocking_entity_sprites:
            target = blocking_entity_sprites[0]
            attack_results = self.player.fighter.attack(target)
            print(attack_results)
            # print(f"You kick the {blocking_entity_sprites[0].name}.")
            return True

        return False

    def on_key_press(self, key: int, modifiers: int):
        """ Manage keyboard input """
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.NUM_8:
            self.up_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.DOWN or key == arcade.key.NUM_2:
            self.down_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.LEFT or key == arcade.key.NUM_4:
            self.left_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.RIGHT or key == arcade.key.NUM_6:
            self.right_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.RIGHT or key == arcade.key.NUM_6:
            self.right_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.NUM_7 or key == arcade.key.Q:
            self.up_left_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.NUM_9 or key == arcade.key.E:
            self.up_right_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.NUM_1 or key == arcade.key.Z:
            self.down_left_pressed = True
            self.keyboard_frame_counter = 0
        elif key == arcade.key.NUM_3 or key == arcade.key.C:
            self.down_right_pressed = True
            self.keyboard_frame_counter = 0

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.NUM_8:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.NUM_2:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.NUM_4:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.NUM_6:
            self.right_pressed = False
        elif key == arcade.key.NUM_7 or key == arcade.key.Q:
            self.up_left_pressed = False
        elif key == arcade.key.NUM_9 or key == arcade.key.E:
            self.up_right_pressed = False
        elif key == arcade.key.NUM_1 or key == arcade.key.Z:
            self.down_left_pressed = False
        elif key == arcade.key.NUM_3 or key == arcade.key.C:
            self.down_right_pressed = False

    def move_enemies(self):
        for entity in self.entities:
            if entity.ai:
                entity.ai.take_turn(target=self.player,
                                    fov_map=None,
                                    game_map=self.game_map,
                                    sprite_lists=[self.dungeon_sprites, self.entities])

    def on_update(self, dt):
        cx = 0
        cy = 0
        if self.keyboard_frame_counter % 10 == 0:

            if self.up_pressed or self.up_left_pressed or self.up_right_pressed:
                cy += 1
            if self.down_pressed or self.down_left_pressed or self.down_right_pressed:
                cy -= 1

            if self.left_pressed or self.down_left_pressed or self.up_left_pressed:
                cx -= 1
            if self.right_pressed or self.down_right_pressed or self.up_right_pressed:
                cx += 1

            if cx or cy:
                success = self.move_player(cx, cy)
                if success:
                    self.game_state = ENEMY_TURN

        self.keyboard_frame_counter += 1

        if self.game_state == ENEMY_TURN:
            self.move_enemies()
            self.game_state = PLAYER_TURN


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
