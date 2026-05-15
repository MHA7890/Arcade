import arcade
import arcade.gui
import os

# --- Game Imports ---
from chess_AI.chess_AI import run_chess
from pacman.pacman_game import run_pacman
from pingpong.pingpong_game import run_pingpong
from tit_tac_toe.tictactoe_game import run_tictactoe

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ARCADE MANIA"
SLIDE_DURATION = 3.0  # Seconds per image

# --- Visual Theme Constants ---
COLOR_BG_DARK = (10, 10, 25)
COLOR_NEON_BLUE = (0, 255, 255)
COLOR_NEON_YELLOW = (255, 255, 0)
COLOR_NEON_PINK = (255, 0, 128)

class MainMenu(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = COLOR_BG_DARK

        # --- Slideshow Setup ---
        self.time_counter = 0.0
        self.current_image_index = 0
        
        # List of your image files
        self.image_files = ["image_0.png", "image_8.png", "image_7.png", "image_6.png"]
        self.textures = []

        # Load all textures upfront
        for img_path in self.image_files:
            if os.path.exists(img_path):
                self.textures.append(arcade.load_texture(img_path))
            else:
                print(f"WARNING: Could not find {img_path}")

        # --- FIX: Create a SpriteList to hold the background ---
        self.bg_sprite_list = arcade.SpriteList()

        # Create the background sprite
        self.bg_sprite = arcade.Sprite()
        if self.textures:
            self.bg_sprite.texture = self.textures[0]
            # Scale to fit screen
            self.bg_sprite.width = SCREEN_WIDTH
            self.bg_sprite.height = SCREEN_HEIGHT
            self.bg_sprite.center_x = SCREEN_WIDTH // 2
            self.bg_sprite.center_y = SCREEN_HEIGHT // 2
            
            # Add sprite to the list
            self.bg_sprite_list.append(self.bg_sprite)

        # --- UI Manager Setup ---
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # --- Define Button Styles ---
        self.button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=16,
                font_name=("Courier New", "Arial"),
                font_color=COLOR_NEON_BLUE,
                bg=(10, 10, 25, 200), # Semi-transparent background
                border=COLOR_NEON_BLUE,
                border_width=2,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=17, 
                font_name=("Courier New", "Arial"),
                font_color=arcade.color.BLACK,
                bg=COLOR_NEON_YELLOW,
                border=COLOR_NEON_YELLOW,
                border_width=2,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=16,
                font_name=("Courier New", "Arial"),
                font_color=arcade.color.WHITE,
                bg=COLOR_NEON_PINK, 
                border=COLOR_NEON_PINK,
                border_width=2,
            ),
        }

        # --- Main Layout ---
        self.main_v_box = arcade.gui.UIBoxLayout(space_between=15)

        # --- Title ---
        title_label = arcade.gui.UILabel(
            text="ARCADE MANIA",
            font_size=48,
            font_name=("Impact", "Arial"), 
            text_color=COLOR_NEON_YELLOW,
            align="center"
        )
        self.main_v_box.add(title_label)
        self.main_v_box.add(arcade.gui.UISpace(height=30))

        # --- Create Buttons ---
        self.create_neon_button("CHESS", self.launch_chess)
        self.create_neon_button("TIC TAC TOE", self.launch_tictactoe)
        self.create_neon_button("PING PONG", self.launch_pingpong)
        self.create_neon_button("PACMAN", self.launch_pacman)

        # --- Exit Button ---
        self.main_v_box.add(arcade.gui.UISpace(height=20))
        exit_button = arcade.gui.UIFlatButton(text="EXIT SYSTEM", width=250, style=self.button_style)
        self.main_v_box.add(exit_button)
        
        @exit_button.event("on_click")
        def on_click_exit(event):
            self.quit_game()

        # --- Anchor Layout ---
        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=self.main_v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor_layout)

    def create_neon_button(self, text, action_function):
        """Helper for creating buttons"""
        button = arcade.gui.UIFlatButton(text=text, width=250, height=50, style=self.button_style)
        self.main_v_box.add(button)
        @button.event("on_click")
        def on_click(event):
            action_function()

    def on_update(self, delta_time):
        """Slideshow Logic"""
        if not self.textures:
            return

        self.time_counter += delta_time
        
        # Check if it is time to switch slide
        if self.time_counter > SLIDE_DURATION:
            self.time_counter = 0
            # Advance index
            self.current_image_index = (self.current_image_index + 1) % len(self.textures)
            
            # Update the sprite texture
            self.bg_sprite.texture = self.textures[self.current_image_index]
            
            # Re-apply dimensions because changing texture might reset size
            self.bg_sprite.width = SCREEN_WIDTH
            self.bg_sprite.height = SCREEN_HEIGHT

    def on_draw(self):
        """Render the screen."""
        self.clear()
        
        # 1. Draw Background Slideshow
        if self.textures:
            self.bg_sprite_list.draw()
        
        # 2. Draw Dimming Layer
        arcade.draw_polygon_filled(
            [(0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)],
            (0, 0, 0, 150) # Black with transparency
        )
        
        # 3. Draw UI
        self.manager.draw()

    # --- Launcher Functions ---
    def launch_chess(self): self._safe_launch(run_chess, "Chess")
    def launch_pacman(self): self._safe_launch(run_pacman, "Pacman")
    def launch_pingpong(self): self._safe_launch(run_pingpong, "Ping Pong")
    def launch_tictactoe(self): self._safe_launch(run_tictactoe, "Tic Tac Toe")

    def _safe_launch(self, game_func, name):
        print(f"Booting {name}...")
        self.set_visible(False)
        try:
            game_func()
        except SystemExit:
            print(f"{name} exited normally.")
        except Exception as e:
            print(f"Error in {name}: {e}")
        self.set_visible(True)

    def quit_game(self):
        arcade.exit()

if __name__ == "__main__":
    window = MainMenu()
    arcade.run()