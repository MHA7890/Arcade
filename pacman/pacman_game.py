

import pygame
import sys
import heapq
import json
import os
import time
import random
import math

def run_pacman():
    Game().run()

# --- CONFIGURATION ---
TILE_SIZE = 24
FPS = 60

# --- SPEEDS ---
SPEED_PACMAN_NORMAL = 3
SPEED_PACMAN_POWER = 4 
SPEED_GHOST_NORMAL = 2
SPEED_GHOST_INSANE = 3
SPEED_GHOST_SCARED = 1

# Colors
BLACK = (0, 0, 0)
NAVY = (0, 0, 20)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
PINK = (255, 182, 193)
ORANGE = (255, 165, 0)
BLUE_SCARED = (50, 50, 255)
WALL_COLOR = (20, 20, 180)
NEON_GREEN = (57, 255, 20)
UI_BG = (10, 10, 30)

MAP_LAYOUT = [
    "1111111111111111111111111111",
    "1000000000000110000000000001",
    "1011110111110110111110111101",
    "1211110111110110111110111121",
    "1011110111110110111110111101",
    "1000000000000000000000000001",
    "1011110110111111110110111101",
    "1011110110111111110110111101",
    "1000000110000110000110000001",
    "1111110111110110111110111111",
    "0000000110000000000110000000",
    "1111110110111331110110111111",
    "1111110110118888110110111111",
    "1111110110118888110110111111",
    "0000000000111111110000000000",
    "1111110110111111110110111111",
    "1111110110000000000110111111",
    "1111110110111111110110111111",
    "1111110110111111110110111111",
    "1000000000000900000000000001",
    "1011110111110110111110111101",
    "1011110111110110111110111101",
    "1200110000000000000000110021",
    "1110110110111111110110110111",
    "1110110110111111110110110111",
    "1000000110000110000110000001",
    "1011111111110110111111111101",
    "1011111111110110111111111101",
    "1000000000000000000000000001",
    "1111111111111111111111111111"
]

ROWS = len(MAP_LAYOUT)
COLS = len(MAP_LAYOUT[0])
UI_WIDTH = 120
WIDTH = COLS * TILE_SIZE + (UI_WIDTH * 2)
HEIGHT = ROWS * TILE_SIZE

class AI:
    @staticmethod
    def get_neighbors(node, walls, current_dir=(0,0)):
        x, y = node
        neighbors = []
        possible_moves = []
        
        # Handle Tunnels 
        if x == 0: possible_moves.append(((COLS - 1, y), (-1, 0)))
        elif x == COLS - 1: possible_moves.append(((0, y), (1, 0)))

        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if (nx, ny) not in walls:
                    possible_moves.append(((nx, ny), (dx, dy)))
        
        # Filter for valid moves 
        valid_moves = []
        for next_node, next_dir in possible_moves:
            # Prevent reversing direction
            if current_dir != (0,0) and (next_dir[0], next_dir[1]) == (-current_dir[0], -current_dir[1]):
                continue
            valid_moves.append((next_node, next_dir))
            
        # If no non-reversing moves are found (dead end), allow the reverse move
        if not valid_moves and possible_moves:
            return possible_moves
            
        return valid_moves

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def random_move(start, current_dir, walls):
        neighbors = AI.get_neighbors(start, walls, current_dir)
        if not neighbors:
             back = AI.get_neighbors(start, walls, (0,0))
             return back[0][0] if back else start
        return random.choice(neighbors)[0]

    @staticmethod
    def greedy(start, target, current_dir, walls):
        neighbors = AI.get_neighbors(start, walls, current_dir)
        if not neighbors:
             back = AI.get_neighbors(start, walls, (0,0))
             return back[0][0] if back else start
        neighbors.sort(key=lambda n: AI.heuristic(n[0], target))
        return neighbors[0][0]

    @staticmethod
    def a_star(start, target, current_dir, walls):
        
        tx = max(0, min(COLS - 1, target[0]))
        ty = max(0, min(ROWS - 1, target[1]))
        target = (tx, ty)
        
        
        if target in walls: 
             return AI.greedy(start, target, current_dir, walls)

     
        frontier = [(0, start)] # (priority, node)
        came_from = {start: None}
        cost_so_far = {start: 0}
        
       
        limit = 0 
        
        # 3. Search Loop
        while frontier:
            _, current = heapq.heappop(frontier)
            limit += 1
            
            # Stop condition: Reached target or hit the safety limit
            if current == target or limit > 150: 
                break
                
            # Iterate through neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current[0] + dx, current[1] + dy
                
                # Check for validity: Must be within bounds and not a wall
                if 0 <= nx < COLS and 0 <= ny < ROWS and (nx, ny) not in walls:
                    new_cost = cost_so_far[current] + 1
                    
                    if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                        cost_so_far[(nx, ny)] = new_cost
                        priority = new_cost + AI.heuristic((nx, ny), target)
                        heapq.heappush(frontier, (priority, (nx, ny)))
                        came_from[(nx, ny)] = current
                        
        # 4. Path Reconstruction
        curr = target
        path = []
        
        # If target was unreachable, return the starting position
        if target not in came_from: return start
        
        # Backtrack from target to start
        while curr != start:
            path.append(curr)
            # Ensure path segment is valid
            if curr not in came_from: 
                break 
            curr = came_from[curr]
            if curr is None: 
                break
                
        path.reverse()
        
        
        if not path: return start
        
        first_step = path[0]
        dx = first_step[0] - start[0]
        dy = first_step[1] - start[1]
        
        
        if current_dir != (0,0) and (dx, dy) == (-current_dir[0], -current_dir[1]):
            
            return AI.greedy(start, target, current_dir, walls)
            
        return first_step

class Entity:
    def __init__(self, x, y, speed, color):
        self.grid_x, self.grid_y = x, y
        self.pixel_x, self.pixel_y = x * TILE_SIZE, y * TILE_SIZE
        self.speed = speed
        self.color = color
        self.dir = (0, 0)
        self.next_dir = (0, 0)
    
    def draw(self, screen, sprites, key, offset_x):
        img = sprites.get(key)
        draw_x = offset_x + self.pixel_x
        draw_y = self.pixel_y
        if img: screen.blit(img, (draw_x, draw_y))
        else: pygame.draw.circle(screen, self.color, (int(draw_x + 12), int(draw_y + 12)), 10)

    def can_move(self, dx, dy, walls, is_player=False):
        nx, ny = self.grid_x + dx, self.grid_y + dy
        if (nx < 0 or nx >= COLS): return True
        if (nx, ny) in walls: return False
        if is_player:
            cell = MAP_LAYOUT[ny][nx]
            if cell == '8' or cell == '3': return False
        return True

    def move_int(self, walls, is_player=False):
        
        distance_to_move = self.speed
        
        while distance_to_move > 0:
            
            dist_to_edge = 0
            if self.dir == (1, 0):   dist_to_edge = TILE_SIZE - (self.pixel_x % TILE_SIZE)
            elif self.dir == (-1, 0): dist_to_edge = self.pixel_x % TILE_SIZE
            elif self.dir == (0, 1):  dist_to_edge = TILE_SIZE - (self.pixel_y % TILE_SIZE)
            elif self.dir == (0, -1): dist_to_edge = self.pixel_y % TILE_SIZE
            
            if dist_to_edge == 0: dist_to_edge = TILE_SIZE 
            
            
            step = min(distance_to_move, dist_to_edge)
            
            
            self.pixel_x += self.dir[0] * step
            self.pixel_y += self.dir[1] * step
            distance_to_move -= step
            
            
            if self.pixel_x % TILE_SIZE == 0 and self.pixel_y % TILE_SIZE == 0:
                self.grid_x = int(self.pixel_x // TILE_SIZE)
                self.grid_y = int(self.pixel_y // TILE_SIZE)
                
                
                if self.grid_x < 0: self.pixel_x = (COLS - 1) * TILE_SIZE; self.grid_x = COLS - 1
                elif self.grid_x >= COLS: self.pixel_x = 0; self.grid_x = 0
                
                
                if self.next_dir != (0, 0) and self.can_move(self.next_dir[0], self.next_dir[1], walls, is_player):
                    self.dir = self.next_dir
                    self.next_dir = (0, 0)
                
               
                if not self.can_move(self.dir[0], self.dir[1], walls, is_player):
                    self.dir = (0, 0)
                    distance_to_move = 0 
            
            
            if self.dir == (0, 0): break

class Pacman(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, SPEED_PACMAN_NORMAL, YELLOW)
    def set_dir(self, dx, dy): self.next_dir = (dx, dy)
    def update_speed(self, is_powered):
        self.speed = SPEED_PACMAN_POWER if is_powered else SPEED_PACMAN_NORMAL

class Ghost(Entity):
    def __init__(self, x, y, name, color, algo, release_delay, mode_name):
        super().__init__(x, y, SPEED_GHOST_NORMAL, color)
        self.name = name
        self.algo = algo
        self.in_house = True
        self.release_time = time.time() + release_delay
        self.mode_name = mode_name
        self.on_tile_center = True 
    
    def update_ai(self, player, walls, is_scared):
        
        if is_scared: self.speed = SPEED_GHOST_SCARED
        elif self.mode_name == "Insane": self.speed = SPEED_GHOST_INSANE
        else: self.speed = SPEED_GHOST_NORMAL

       
        if self.in_house:
            if time.time() > self.release_time:
                
                if self.grid_y > 11:
                    self.pixel_y -= self.speed
                    self.grid_y = int(self.pixel_y // TILE_SIZE)
                    return
                
                else: 
                    self.in_house = False
                    self.pixel_y = 11 * TILE_SIZE
                    self.pixel_x = 13 * TILE_SIZE
                    self.grid_y = 11; self.grid_x = 13
                    self.dir = (random.choice([-1, 1]), 0) 
            return 

        
       
        if self.pixel_x % TILE_SIZE == 0 and self.pixel_y % TILE_SIZE == 0:
            
           
            curr = (self.grid_x, self.grid_y)
            target = (player.grid_x, player.grid_y)
            
           
            if self.algo == "Ambush" and not is_scared:
                target = (target[0] + player.dir[0]*4, target[1] + player.dir[1]*4)

            next_pos = curr
            if is_scared or self.algo == "Random": next_pos = AI.random_move(curr, self.dir, walls)
            elif self.algo == "Greedy": next_pos = AI.greedy(curr, target, self.dir, walls)
            elif self.algo == "A*" or self.algo == "Ambush": next_pos = AI.a_star(curr, target, self.dir, walls)
            
           
            dx = next_pos[0] - self.grid_x
            dy = next_pos[1] - self.grid_y
            
            
            if abs(dx) > 1: dx = -1 if self.grid_x == 0 else 1
            if abs(dy) > 1: dy = 0 

            
            self.dir = (dx, dy)
            
        
        self.move_int(walls) 
        
    def respawn(self):
        self.grid_x, self.grid_y = 14, 14 
        self.pixel_x, self.pixel_y = 14 * TILE_SIZE, 14 * TILE_SIZE
        self.dir = (0, -1) 
        self.in_house = True
        self.release_time = time.time() + 3

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pacman Arcade Ultimate")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_xl = pygame.font.SysFont("Impact", 60)
        self.font_lg = pygame.font.SysFont("Impact", 30)
        self.load_assets()
        self.load_leaderboard()
        self.state = "MENU"
        self.new_high = False

    def load_assets(self):
        self.sprites = {}
        files = {
            'pacman': ('pacman.png', YELLOW),
            'red': ('ghost_red.png', RED),
            'cyan': ('ghost_cyan.png', CYAN),
            'pink': ('ghost_pink.png', PINK),
            'orange': ('ghost_orange.png', ORANGE),
            'scared': ('ghost_scared.png', BLUE_SCARED)
        }
        for key, (fname, col) in files.items():
            if os.path.exists(fname):
                img = pygame.image.load(fname).convert_alpha()
                self.sprites[key] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            else: self.sprites[key] = None

    def load_leaderboard(self):
        if not os.path.exists("leaderboard.json"):
            self.leaderboard = {"Easy": 0, "Medium": 0, "Hard": 0, "Insane": 0}
            with open("leaderboard.json", "w") as f: json.dump(self.leaderboard, f)
        else:
            with open("leaderboard.json", "r") as f: self.leaderboard = json.load(f)

    def save_score(self):
        self.new_high = False
        if self.score > self.leaderboard[self.mode]:
            self.leaderboard[self.mode] = self.score
            self.new_high = True
            with open("leaderboard.json", "w") as f: json.dump(self.leaderboard, f)

    def reset_game(self, mode):
        self.mode = mode
        self.walls = set(); self.pellets = set(); self.powerups = set()
        self.ghosts = []; ghost_starts = []
        for y, row in enumerate(MAP_LAYOUT):
            for x, char in enumerate(row):
                if char == "1": self.walls.add((x, y))
                elif char == "0": self.pellets.add((x, y))
                elif char == "2": self.powerups.add((x, y))
                elif char == "9": self.player = Pacman(x, y)
                elif char == "8": ghost_starts.append((x,y))

        algo_map = {"Easy": "Random", "Medium": "Greedy", "Hard": "A*", "Insane": "Ambush"}
        algo = algo_map[mode]
        identities = [("red", RED), ("cyan", CYAN), ("pink", PINK), ("orange", ORANGE)]
        delays = [0, 4, 8, 12]
        for i, (name, col) in enumerate(identities):
            pos = ghost_starts[i] if i < len(ghost_starts) else (14, 13)
            self.ghosts.append(Ghost(pos[0], pos[1], name, col, algo, delays[i], mode))
        self.score = 0; self.power_timer = 0; self.state = "PLAYING"

    def run(self):
        while True:
            if self.state == "MENU": self.menu_loop()
            elif self.state == "PLAYING": self.game_loop()
            elif self.state in ["WIN", "LOSE"]: self.end_loop()

    def draw_ui(self):
        pygame.draw.rect(self.screen, UI_BG, (0, 0, UI_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, WHITE, (UI_WIDTH, 0), (UI_WIDTH, HEIGHT), 2)
        lbl_hi = self.font.render("HIGH", True, YELLOW)
        val_hi = self.font.render(str(self.leaderboard[self.mode]), True, WHITE)
        self.screen.blit(lbl_hi, (10, 50)); self.screen.blit(val_hi, (10, 80))

        rx = WIDTH - UI_WIDTH
        pygame.draw.rect(self.screen, UI_BG, (rx, 0, UI_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, WHITE, (rx, 0), (rx, HEIGHT), 2)
        lbl_sc = self.font.render("SCORE", True, CYAN)
        val_sc = self.font.render(str(self.score), True, WHITE)
        self.screen.blit(lbl_sc, (rx+10, 50)); self.screen.blit(val_sc, (rx+10, 80))
        if self.power_timer > 0:
            pwr = self.font.render("POWER!", True, RED)
            self.screen.blit(pwr, (rx+10, 200))

    def menu_loop(self):
        sel = 0
        modes = ["Easy", "Medium", "Hard", "Insane"]
        while self.state == "MENU":
            self.screen.fill(NAVY)
            t = self.font_xl.render("PAC-MAN AI", True, YELLOW)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 100))
            for i, m in enumerate(modes):
                col = NEON_GREEN if i == sel else WHITE
                txt = self.font_lg.render(f"> {m} <" if i == sel else m, True, col)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 300 + i*50))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: sel = (sel - 1) % 4
                    if event.key == pygame.K_DOWN: sel = (sel + 1) % 4
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.reset_game(modes[sel])
            self.clock.tick(60)

    def game_loop(self):
        while self.state == "PLAYING":
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: self.player.set_dir(-1, 0)
                    if event.key == pygame.K_RIGHT: self.player.set_dir(1, 0)
                    if event.key == pygame.K_UP: self.player.set_dir(0, -1)
                    if event.key == pygame.K_DOWN: self.player.set_dir(0, 1)
                    if event.key == pygame.K_ESCAPE: self.state = "MENU"

            is_scared = self.power_timer > 0
            if is_scared: self.power_timer -= 1
            
            self.player.update_speed(is_scared)
            self.player.move_int(self.walls, is_player=True)
            
            px, py = self.player.grid_x, self.player.grid_y
            if (px, py) in self.pellets:
                self.pellets.remove((px, py)); self.score += 10
            if (px, py) in self.powerups:
                self.powerups.remove((px, py)); self.power_timer = 600; self.score += 50
            if not self.pellets and not self.powerups: self.state = "WIN"

            for g in self.ghosts:
                g.update_ai(self.player, self.walls, is_scared)
                dist = math.hypot(g.pixel_x - self.player.pixel_x, g.pixel_y - self.player.pixel_y)
                if dist < TILE_SIZE * 0.8:
                    if is_scared: g.respawn(); self.score += 200
                    else: self.state = "LOSE"

            self.screen.fill(BLACK)
            self.draw_ui()
            off = UI_WIDTH
            for y in range(ROWS):
                for x in range(COLS):
                    dx, dy = off + x*TILE_SIZE, y*TILE_SIZE
                    if (x, y) in self.walls:
                        pygame.draw.rect(self.screen, WALL_COLOR, (dx, dy, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(self.screen, BLACK, (dx+4, dy+4, TILE_SIZE-8, TILE_SIZE-8))
                    elif (x, y) in self.pellets: pygame.draw.circle(self.screen, (255, 200, 200), (dx+12, dy+12), 3)
                    elif (x, y) in self.powerups: pygame.draw.circle(self.screen, WHITE, (dx+12, dy+12), 8)
                    elif MAP_LAYOUT[y][x] == '3': pygame.draw.line(self.screen, PINK, (dx, dy+12), (dx+TILE_SIZE, dy+12), 2)
            
            self.player.draw(self.screen, self.sprites, 'pacman', off)
            for g in self.ghosts:
                key = 'scared' if is_scared else g.name
                g.draw(self.screen, self.sprites, key, off)
            pygame.display.flip()

    def end_loop(self):
        if self.state in ["WIN", "LOSE"]: self.save_score()
        while self.state in ["WIN", "LOSE"]:
            self.screen.fill(BLACK)
            msg = "VICTORY!" if self.state == "WIN" else "GAME OVER"
            col = NEON_GREEN if self.state == "WIN" else RED
            t = self.font_xl.render(msg, True, col)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 100))
            sc = self.font_lg.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(sc, (WIDTH//2 - sc.get_width()//2, HEIGHT//2))
            if self.new_high:
                h = self.font_lg.render("NEW HIGH SCORE!", True, YELLOW)
                self.screen.blit(h, (WIDTH//2 - h.get_width()//2, HEIGHT//2 + 50))
            info = self.font.render("Press SPACE for Menu", True, WHITE)
            self.screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 100))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = "MENU"