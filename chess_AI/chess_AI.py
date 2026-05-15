import pygame
import chess
import math
import time
import threading
import sys

def run_chess():
    print("Starting Chess...")

# --- CONFIGURATION & VISUALS ---
WIDTH, HEIGHT = 900, 700
BOARD_SIZE = 700
SQUARE_SIZE = BOARD_SIZE // 8
PANEL_WIDTH = WIDTH - BOARD_SIZE
FPS = 60

# Colors
LIGHT_SQUARE = (240, 217, 181) 
DARK_SQUARE = (181, 136, 99)   
HIGHLIGHT = (205, 210, 106)    
LAST_MOVE = (170, 162, 58)     

BG_COLOR = (40, 40, 40)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER = (70, 70, 70)
BUTTON_BORDER = (100, 100, 100)
WHITE_PIECE_COL = (255, 255, 255)
BLACK_PIECE_COL = (10, 10, 10)

# --- AI SETTINGS ---
AI_DEPTH = 3 

# --- PIECE-SQUARE TABLES ---
pawntable = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
knighttable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]
bishoptable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
rooktable = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
]
queentable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]
kingtable = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]

# --- OPTIMIZED AI ENGINE ---

def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    piece_values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
    
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece: continue
        
        value = piece_values.get(piece.piece_type, 0)
        
        if piece.color == chess.WHITE:
            idx = chess.square_mirror(square)
            if piece.piece_type == chess.PAWN: value += pawntable[idx]
            elif piece.piece_type == chess.KNIGHT: value += knighttable[idx]
            elif piece.piece_type == chess.BISHOP: value += bishoptable[idx]
            elif piece.piece_type == chess.ROOK: value += rooktable[idx]
            elif piece.piece_type == chess.QUEEN: value += queentable[idx]
            elif piece.piece_type == chess.KING: value += kingtable[idx]
            score += value
        else:
            idx = square
            if piece.piece_type == chess.PAWN: value += pawntable[idx]
            elif piece.piece_type == chess.KNIGHT: value += knighttable[idx]
            elif piece.piece_type == chess.BISHOP: value += bishoptable[idx]
            elif piece.piece_type == chess.ROOK: value += rooktable[idx]
            elif piece.piece_type == chess.QUEEN: value += queentable[idx]
            elif piece.piece_type == chess.KING: value += kingtable[idx]
            score -= value
            
    return score

def quiescence(board, alpha, beta, maximizing_player):
    stand_pat = evaluate_board(board)
    
    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat

    moves = [m for m in board.legal_moves if board.is_capture(m)]
    # MVV-LVA Sort
    moves.sort(key=lambda m: 1 if board.is_en_passant(m) else (board.piece_at(m.to_square).piece_type if board.piece_at(m.to_square) else 0), reverse=True)

    if maximizing_player:
        for move in moves:
            board.push(move)
            score = quiescence(board, alpha, beta, False)
            board.pop()
            if score >= beta: return beta
            if score > alpha: alpha = score
        return alpha
    else:
        for move in moves:
            board.push(move)
            score = quiescence(board, alpha, beta, True)
            board.pop()
            if score <= alpha: return alpha
            if score < beta: beta = score
        return beta

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return quiescence(board, alpha, beta, maximizing_player)
    
    if board.is_game_over():
        return evaluate_board(board)

    moves = list(board.legal_moves)
    
    def move_order(m):
        score = 0
        if board.is_capture(m): score += 10
        if board.gives_check(m): score += 5
        return score
    
    moves.sort(key=move_order, reverse=True)

    if maximizing_player:
        max_eval = -math.inf
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

def get_best_move(board, depth):
    best_move = None
    alpha = -math.inf
    beta = math.inf
    
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: (board.is_capture(m), board.gives_check(m)), reverse=True)
    
    maximize = board.turn == chess.WHITE
    best_val = -math.inf if maximize else math.inf
    
    for move in moves:
        board.push(move)
        val = minimax(board, depth - 1, alpha, beta, not maximize)
        board.pop()
        
        if maximize:
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, val)
        else:
            if val < best_val:
                best_val = val
                best_move = move
            beta = min(beta, val)
            
    return best_move

# --- GRAPHICS & GAMEPLAY ---

class ChessGame:
    def __init__(self, time_limit_minutes):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess AI")
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        
        self.font_ui = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_pieces = pygame.font.SysFont("Segoe UI Symbol", 80) 

        self.time_limit = time_limit_minutes * 60
        self.white_time = self.time_limit
        self.black_time = self.time_limit
        self.last_update = time.time()
        self.game_over = False
        self.winner = None

        self.selected_square = None
        self.valid_moves = []
        self.ai_thinking = False
        self.ai_move_result = None

    def get_piece_symbol(self, piece):
        if piece.color == chess.WHITE:
            return "♔♕♖♗♘♙"["KQRBNP".index(piece.symbol())]
        else:
            return "♚♛♜♝♞♟"["kqrbnp".index(piece.symbol())]

    def draw_text_centered(self, text, font, color, center_x, center_y):
        rend = font.render(text, True, color)
        rect = rend.get_rect(center=(center_x, center_y))
        self.screen.blit(rend, rect)

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
                sq_idx = chess.square(c, 7-r)
                
                if self.board.move_stack:
                    last_move = self.board.peek()
                    if sq_idx == last_move.from_square or sq_idx == last_move.to_square:
                        color = LAST_MOVE
                
                if self.selected_square == sq_idx:
                    color = HIGHLIGHT

                pygame.draw.rect(self.screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                if sq_idx in [m.to_square for m in self.valid_moves]:
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(s, (0, 0, 0, 50), (SQUARE_SIZE//2, SQUARE_SIZE//2), 12)
                    self.screen.blit(s, (c*SQUARE_SIZE, r*SQUARE_SIZE))

                piece = self.board.piece_at(sq_idx)
                if piece:
                    symbol = self.get_piece_symbol(piece)
                    center_x = c * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = r * SQUARE_SIZE + SQUARE_SIZE // 2
                    
                    if piece.color == chess.WHITE:
                        offset = 2
                        for dx, dy in [(-offset,-offset), (-offset,offset), (offset,-offset), (offset,offset)]:
                            rend_outline = self.font_pieces.render(symbol, True, (0,0,0))
                            rect_out = rend_outline.get_rect(center=(center_x+dx, center_y+dy))
                            self.screen.blit(rend_outline, rect_out)
                        rend = self.font_pieces.render(symbol, True, WHITE_PIECE_COL)
                    else:
                        rend = self.font_pieces.render(symbol, True, BLACK_PIECE_COL)
                    
                    rect = rend.get_rect(center=(center_x, center_y))
                    self.screen.blit(rend, rect)

    def draw_ui(self):
        pygame.draw.rect(self.screen, BG_COLOR, (BOARD_SIZE, 0, PANEL_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, (60,60,60), (BOARD_SIZE, 0), (BOARD_SIZE, HEIGHT), 3)

        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        if not self.game_over and self.board.outcome() is None:
            if self.board.turn == chess.WHITE:
                self.white_time -= dt
            else:
                self.black_time -= dt

        if self.white_time <= 0: self.end_game("Time's Up! Black Wins")
        if self.black_time <= 0: self.end_game("Time's Up! White Wins")

        def fmt_time(t):
            m, s = divmod(max(0, int(t)), 60)
            return f"{m:02}:{s:02}"

        # Black Timer
        pygame.draw.rect(self.screen, (60, 60, 60), (BOARD_SIZE + 20, 50, PANEL_WIDTH - 40, 80), border_radius=15)
        self.draw_text_centered("AI (Black)", self.font_ui, (180,180,180), BOARD_SIZE + PANEL_WIDTH//2, 75)
        self.draw_text_centered(fmt_time(self.black_time), self.font_big, TEXT_COLOR, BOARD_SIZE + PANEL_WIDTH//2, 110)

        # White Timer
        pygame.draw.rect(self.screen, (200, 200, 200), (BOARD_SIZE + 20, HEIGHT - 130, PANEL_WIDTH - 40, 80), border_radius=15)
        self.draw_text_centered("YOU (White)", self.font_ui, (50,50,50), BOARD_SIZE + PANEL_WIDTH//2, HEIGHT - 105)
        self.draw_text_centered(fmt_time(self.white_time), self.font_big, (0,0,0), BOARD_SIZE + PANEL_WIDTH//2, HEIGHT - 70)

        status_text = "Your Turn"
        status_color = (100, 255, 100)
        
        if self.game_over:
            status_text = "GAME OVER"
            status_color = (255, 80, 80)
        elif self.ai_thinking:
            status_text = "AI Thinking..."
            status_color = (255, 200, 80)
        elif self.board.is_check():
             status_text = "CHECK!"
             status_color = (255, 100, 100)

        self.draw_text_centered(status_text, self.font_big, status_color, BOARD_SIZE + PANEL_WIDTH//2, HEIGHT // 2)
        if self.winner:
            self.draw_text_centered(self.winner, self.font_ui, (200,200,200), BOARD_SIZE + PANEL_WIDTH//2, HEIGHT // 2 + 40)

    def end_game(self, reason):
        self.game_over = True
        self.winner = reason

    def ai_turn(self):
        # COPY BOARD FOR THREAD SAFETY
        board_copy = self.board.copy()
        best_move = get_best_move(board_copy, AI_DEPTH)
        self.ai_move_result = best_move
        self.ai_thinking = False

    def run(self):
        running = True
        while running:
            if self.board.turn == chess.BLACK and not self.game_over and not self.ai_thinking:
                if not self.ai_move_result:
                    self.ai_thinking = True
                    threading.Thread(target=self.ai_turn, daemon=True).start()
                else:
                    self.board.push(self.ai_move_result)
                    self.ai_move_result = None
                    if self.board.is_game_over():
                        self.end_game(self.board.result())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.board.turn == chess.WHITE:
                    x, y = pygame.mouse.get_pos()
                    if x < BOARD_SIZE:
                        c, r = x // SQUARE_SIZE, y // SQUARE_SIZE
                        sq = chess.square(c, 7-r)
                        
                        if self.selected_square is None:
                            piece = self.board.piece_at(sq)
                            if piece and piece.color == chess.WHITE:
                                self.selected_square = sq
                                self.valid_moves = [m for m in self.board.legal_moves if m.from_square == sq]
                        else:
                            move = chess.Move(self.selected_square, sq)
                            if move not in self.board.legal_moves:
                                move = chess.Move(self.selected_square, sq, promotion=chess.QUEEN)
                            
                            if move in self.board.legal_moves:
                                self.board.push(move)
                                self.selected_square = None
                                self.valid_moves = []
                                if self.board.is_game_over():
                                    self.end_game(self.board.result())
                            else:
                                piece = self.board.piece_at(sq)
                                if piece and piece.color == chess.WHITE:
                                    self.selected_square = sq
                                    self.valid_moves = [m for m in self.board.legal_moves if m.from_square == sq]
                                else:
                                    self.selected_square = None
                                    self.valid_moves = []

            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.display.quit()  # Only closes the chess window, keeps Pygame alive


# --- MODERN MENU ---
def modern_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI - Main Menu")
    
    font_title = pygame.font.SysFont("Verdana", 60, bold=True)
    font_sub = pygame.font.SysFont("Verdana", 24)
    font_btn = pygame.font.SysFont("Verdana", 20, bold=True)
    
    
    time_options = [
        ("Bullet (3 min)", 3),
        ("Blitz (5 min)", 5),
        ("Rapid (10 min)", 10),
        ("Classic (30 min)", 30),
        ("Marathon (60 min)", 60)
    ]
    
    buttons = []
    center_x = WIDTH // 2
    start_y = 230
    for i, (label, val) in enumerate(time_options):
        rect = pygame.Rect(0, 0, 300, 50)
        rect.center = (center_x, start_y + i * 70)
        buttons.append({"rect": rect, "label": label, "val": val, "hover": False})

    clock = pygame.time.Clock()
    bg_offset = 0
    running = True
    selected_time = None
    
    while running:
        screen.fill(BG_COLOR)
        bg_offset = (bg_offset + 0.5) % 100
        for r in range(-1, 9):
            for c in range(-1, 10):
                col = (45, 45, 45) if (r+c)%2==0 else (50, 50, 50)
                pygame.draw.rect(screen, col, (c*100 + bg_offset, r*100 + bg_offset, 100, 100))
        
        panel_rect = pygame.Rect(0, 0, 500, 600)
        panel_rect.center = (center_x, HEIGHT // 2)
        s = pygame.Surface((500, 600), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 180), (0,0,500,600), border_radius=20)
        screen.blit(s, panel_rect.topleft)

        title_surf = font_title.render("CHESS AI", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(center_x, 130))
        screen.blit(title_surf, title_rect)
        
        sub_surf = font_sub.render("Select Time Control", True, (200, 200, 200))
        screen.blit(sub_surf, sub_surf.get_rect(center=(center_x, 180)))

        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn["hover"] = btn["rect"].collidepoint(mouse_pos)
            color = BUTTON_HOVER if btn["hover"] else BUTTON_COLOR
            pygame.draw.rect(screen, color, btn["rect"], border_radius=10)
            pygame.draw.rect(screen, BUTTON_BORDER, btn["rect"], 2, border_radius=10)
            txt_surf = font_btn.render(btn["label"], True, (255, 255, 255) if btn["hover"] else (200, 200, 200))
            screen.blit(txt_surf, txt_surf.get_rect(center=btn["rect"].center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn["rect"].collidepoint(event.pos):
                        selected_time = btn["val"]
                        running = False
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    return selected_time
def run_chess():
    pygame.init()  # Initialize Pygame
    t_limit = modern_menu()
    if t_limit:
        game = ChessGame(t_limit)
        game.run()