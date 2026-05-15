import pygame
import sys
import math

def run_tictactoe():

    print("Launching Tic Tac Toe Game...\n")

    # --- 1. Setup Constants (Aesthetic Colors) ---
    SQUARE_SIZE = 120 
    BOARD_ROWS = 3
    BOARD_COLS = 3
    WIDTH = BOARD_COLS * SQUARE_SIZE
    HEIGHT = BOARD_ROWS * SQUARE_SIZE
    BG_COLOR = (33, 47, 60)
    LINE_COLOR = (52, 73, 94)
    X_COLOR = (239, 71, 111)
    O_COLOR = (255, 203, 5)
    DIALOG_BG_COLOR = (20, 20, 20, 200)
    BUTTON_COLOR = (52, 73, 94)
    BUTTON_HOVER_COLOR = (44, 62, 80)
    TEXT_COLOR = (170, 170, 170)
    RESTART_COLOR = (46, 204, 113)
    EXIT_COLOR = (231, 76, 60)

    CIRCLE_RAD = 40
    CIRCLE_WIDTH = 12
    CROSS_WIDTH = 15

    # --- 2. Game Logic (Board State) ---
    board = [[' ' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    PLAYER = 'X'
    AI = 'O'
    game_over = False
    current_turn = PLAYER

    # --- 3. Pygame Functions ---
    pygame.init()
    FONT_TITLE = pygame.font.SysFont("sans-serif", 60, bold=True)
    FONT_BUTTON = pygame.font.SysFont("sans-serif", 30, bold=True)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tic Tac Toe AI')
    screen.fill(BG_COLOR)

    def reset_game():
        nonlocal board, game_over, current_turn
        board = [[' ' for _ in range(BOARD_COLS)] for _ in range(BOARD_COLS)] 
        game_over = False
        current_turn = PLAYER
        screen.fill(BG_COLOR)
        draw_lines()

    def draw_lines():
        for i in range(1, BOARD_ROWS):
            pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), 5)
            pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), 5)

    def draw_figures():
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                
                if board[row][col] == AI:
                    pygame.draw.circle(screen, O_COLOR, (center_x, center_y), CIRCLE_RAD, CIRCLE_WIDTH)
                elif board[row][col] == PLAYER:
                    offset = CIRCLE_RAD - 5
                    pygame.draw.line(screen, X_COLOR,
                                     (center_x - offset, center_y - offset),
                                     (center_x + offset, center_y + offset),
                                     CROSS_WIDTH)
                    pygame.draw.line(screen, X_COLOR,
                                     (center_x + offset, center_y - offset),
                                     (center_x - offset, center_y + offset),
                                     CROSS_WIDTH)

    def is_valid_square(row, col): 
        return board[row][col] == ' '

    def check_win(current_player):
        for row in range(BOARD_ROWS):
            if all(board[row][col] == current_player for col in range(BOARD_COLS)): return True
        for col in range(BOARD_COLS):
            if all(board[row][col] == current_player for row in range(BOARD_ROWS)): return True
        if all(board[i][i] == current_player for i in range(BOARD_ROWS)): return True
        if all(board[i][BOARD_COLS - 1 - i] == current_player for i in range(BOARD_ROWS)): return True
        return False

    def check_tie():
        return (
            not check_win(PLAYER) and 
            not check_win(AI) and 
            all(board[r][c] != ' ' for r in range(BOARD_ROWS) for c in range(BOARD_COLS))
        )

    def get_empty_squares():
        return [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] == ' ']

    # --- 4. Minimax Algorithm ---
    def evaluate(current_board):
        if check_win(AI): return 1
        elif check_win(PLAYER): return -1
        else: return 0

    def minimax(current_board, depth, is_maximizing, alpha, beta):
        score = evaluate(current_board)
        if score != 0 or check_tie(): return score
        
        if is_maximizing:
            max_eval = -math.inf
            for r, c in get_empty_squares():
                current_board[r][c] = AI
                eval = minimax(current_board, depth + 1, False, alpha, beta)
                current_board[r][c] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for r, c in get_empty_squares():
                current_board[r][c] = PLAYER
                eval = minimax(current_board, depth + 1, True, alpha, beta)
                current_board[r][c] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval

    def find_best_move():
        best_score = -math.inf
        best_move = None
        for r, c in get_empty_squares():
            board[r][c] = AI
            score = minimax(board, 0, False, -math.inf, math.inf)
            board[r][c] = ' '
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_move

    # --- 5. Game Over Dialog & Loop ---
    BUTTON_W, BUTTON_H = 140, 50
    GAP = 40
    RETRY_RECT_POS = pygame.Rect(WIDTH // 2 - BUTTON_W - GAP // 2, HEIGHT // 2, BUTTON_W, BUTTON_H)
    EXIT_RECT_POS = pygame.Rect(WIDTH // 2 + GAP // 2, HEIGHT // 2, BUTTON_W, BUTTON_H)

    def draw_game_over_dialog(winner):
        dialog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dialog_surface.fill(DIALOG_BG_COLOR)
        screen.blit(dialog_surface, (0, 0))

        if winner == PLAYER:
            msg = "Player X Wins!"
            msg_color = X_COLOR
        elif winner == AI:
            msg = "AI O Wins!"
            msg_color = O_COLOR
        else:
            msg = "Tie Game!"
            msg_color = LINE_COLOR
        
        label = FONT_TITLE.render(msg, 1, msg_color)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 3 - label.get_height() // 2))

        mouse_pos = pygame.mouse.get_pos()

        retry_text = FONT_BUTTON.render("RETRY", True, TEXT_COLOR)
        retry_color = RESTART_COLOR if RETRY_RECT_POS.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, retry_color, RETRY_RECT_POS, border_radius=10)
        screen.blit(retry_text, (RETRY_RECT_POS.centerx - retry_text.get_width() // 2, RETRY_RECT_POS.centery - retry_text.get_height() // 2))

        exit_text = FONT_BUTTON.render("EXIT", True, TEXT_COLOR)
        exit_color = EXIT_COLOR if EXIT_RECT_POS.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, exit_color, EXIT_RECT_POS, border_radius=10)
        screen.blit(exit_text, (EXIT_RECT_POS.centerx - exit_text.get_width() // 2, EXIT_RECT_POS.centery - exit_text.get_height() // 2))

    # --- Main Game Loop ---
    draw_lines()

    while True:
        if not game_over and current_turn == AI:
            pygame.time.wait(200)
            ai_move = find_best_move()
            if ai_move:
                r, c = ai_move
                board[r][c] = AI
                
                if check_win(AI) or check_tie():
                    game_over = True
                else:
                    current_turn = PLAYER
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if not game_over:
                if current_turn == PLAYER and event.type == pygame.MOUSEBUTTONDOWN:
                    pos_x, pos_y = event.pos
                    clicked_col = pos_x // SQUARE_SIZE
                    clicked_row = pos_y // SQUARE_SIZE

                    if 0 <= clicked_row < BOARD_ROWS and 0 <= clicked_col < BOARD_COLS and board[clicked_row][clicked_col] == ' ':
                        board[clicked_row][clicked_col] = PLAYER
                        
                        if check_win(PLAYER) or check_tie():
                            game_over = True
                        else:
                            current_turn = AI

            elif game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if RETRY_RECT_POS.collidepoint(event.pos):
                    reset_game()
                elif EXIT_RECT_POS.collidepoint(event.pos):
                    pygame.quit()
                    return

        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures()

        if game_over:
            winner = None
            if check_win(PLAYER): winner = PLAYER
            elif check_win(AI): winner = AI
            draw_game_over_dialog(winner)

        pygame.display.update()