import pygame
import sys
import time

def run_pingpong():
    print("Launching Ping Pong Game...\n")

    # Initialize pygame
    pygame.init()

    # Window dimensions
    WIDTH, HEIGHT = 800, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ping Pong AI")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    # Paddle dimensions
    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 10

    # Ball dimensions
    BALL_RADIUS = 10

    # Paddle positions
    user_x = WIDTH // 2 - PADDLE_WIDTH // 2
    user_y = HEIGHT - 40
    user_speed = 7

    ai_x = WIDTH // 2 - PADDLE_WIDTH // 2
    ai_y = 30
    ai_speed = 5

    # Ball position
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_speed_x = 5
    ball_speed_y = 5

    # Scores
    user_score = 0
    ai_score = 0
    WIN_SCORE = 5
    font = pygame.font.SysFont("Arial", 30)

    # Countdown before start
    def countdown():
        for i in range(3, 0, -1):
            win.fill(BLACK)
            text = font.render(f"Starting in {i}", True, WHITE)
            win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            time.sleep(1)

    countdown()

    # Main loop
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(60)
        win.fill(BLACK)

        # Draw paddles
        pygame.draw.rect(win, BLUE, (user_x, user_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(win, RED, (ai_x, ai_y, PADDLE_WIDTH, PADDLE_HEIGHT))

        # Draw ball
        pygame.draw.circle(win, WHITE, (ball_x, ball_y), BALL_RADIUS)

        # Draw scores
        user_text = font.render(f"User: {user_score}", True, WHITE)
        ai_text = font.render(f"AI: {ai_score}", True, WHITE)
        win.blit(user_text, (10, HEIGHT - 40))
        win.blit(ai_text, (10, 10))

        pygame.display.update()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # User movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and user_x > 0:
            user_x -= user_speed
        if keys[pygame.K_RIGHT] and user_x < WIDTH - PADDLE_WIDTH:
            user_x += user_speed

        # AI movement (simple tracking)
        if ai_x + PADDLE_WIDTH/2 < ball_x:
            ai_x += ai_speed
        elif ai_x + PADDLE_WIDTH/2 > ball_x:
            ai_x -= ai_speed
        ai_x = max(0, min(WIDTH - PADDLE_WIDTH, ai_x))

        # Move ball
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Wall collision
        if ball_x - BALL_RADIUS <= 0 or ball_x + BALL_RADIUS >= WIDTH:
            ball_speed_x *= -1

        # Paddle collision
        if (user_y <= ball_y + BALL_RADIUS <= user_y + PADDLE_HEIGHT) and (user_x <= ball_x <= user_x + PADDLE_WIDTH):
            ball_speed_y *= -1
        if (ai_y <= ball_y - BALL_RADIUS <= ai_y + PADDLE_HEIGHT) and (ai_x <= ball_x <= ai_x + PADDLE_WIDTH):
            ball_speed_y *= -1

        # Score
        if ball_y < 0:
            user_score += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            countdown()
        if ball_y > HEIGHT:
            ai_score += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            countdown()

        # Win/Lose
        if user_score == WIN_SCORE:
            win.fill(BLACK)
            text = font.render("You Win!", True, WHITE)
            win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            time.sleep(3)
            break
        if ai_score == WIN_SCORE:
            win.fill(BLACK)
            text = font.render("AI Wins!", True, WHITE)
            win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            time.sleep(3)
            break

    pygame.quit()
