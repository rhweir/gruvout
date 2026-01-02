"""
A simple breakout clone built in Python.
"""

import pygame

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 48)

# --- Sound Initialisation
pygame.mixer.init()
hit_sound = pygame.mixer.Sound("hit.wav")
bounce_sound = pygame.mixer.Sound("bounce.wav")
start_sound = pygame.mixer.Sound("start.wav")
loss_sound = pygame.mixer.Sound("loss.wav")
# Optional: Set volume (0.0 to 1.0)
hit_sound.set_volume(0.5)
bounce_sound.set_volume(0.2)
loss_sound.set_volume(0.2)

# --- Define Global Placeholders for the Linter ---
paddle = pygame.Rect(0, 0, 0, 0)
ball = pygame.Rect(0, 0, 0, 0)
ball_speed_x = 0
ball_speed_y = 0
ball_active = False
bricks = []
lives = 0
game_over = False
message = ""
score = 0
shake_timer = 0
high_score = 0
combo_multiplier = 1

# Gruvbox Dark Palette
BG = (40, 40, 40)
WHITE = (235, 219, 178)
UI_GREY = (102, 92, 84)

RED = (204, 36, 29)
ORANGE = (214, 93, 14)
YELLOW = (215, 153, 33)
GREEN = (152, 151, 26)
BLUE = (69, 133, 136)
PURPLE = (177, 98, 134)
AQUA = (0, 255, 255)
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

COLOR_POINTS = {RED: 50, ORANGE: 40, YELLOW: 30, GREEN: 20, BLUE: 10}

running = True

# --- Game State Function ---


def reset_game():
    """Sets or resets all game variables to their starting state"""
    global paddle, ball, ball_speed_x, ball_speed_y, ball_active
    global bricks, lives, game_over, message, score, shake_timer, combo_multiplier

    start_sound.play()
    # Reset Objects
    paddle = pygame.Rect(350, 560, 100, 20)
    ball = pygame.Rect(390, 540, 20, 20)

    # Reset Physics
    ball_speed_x = 4
    ball_speed_y = -4  # Start by moving UP
    ball_active = False

    # Reset Stats
    lives = 3
    game_over = False
    message = "Game Over"
    score = 0
    shake_timer = 0
    combo_multiplier = 1

    # Rebuild the brick wall
    bricks = []
    for row in range(5):
        row_color = BRICK_COLORS[row]  # Select color based on row index
        for col in range(10):
            brick_rect = pygame.Rect(col * 80, row * 30 + 60, 78, 28)
            # Store as a list: [the_rect, the_color]
            bricks.append([brick_rect, row_color])


# Initialise the game for the first time
reset_game()

# --- Main Game Loop ---
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                ball_active = True

            if event.key == pygame.K_r:
                reset_game()

    # 2. Input and Movement Logic
    if not game_over:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and paddle.x > 0:
            paddle.x -= 10
        if keys[pygame.K_RIGHT] and paddle.x < 700:
            paddle.x += 10

        if ball_active:
            ball.x += ball_speed_x
            ball.y += ball_speed_y
        else:
            ball.centerx = paddle.centerx
            ball.bottom = paddle.top

        # 3. Collision Logic
        if ball.x >= 780 or ball.x <= 0:
            ball_speed_x *= -1
            bounce_sound.play()
        if ball.y <= 50:
            ball_speed_y = min(ball_speed_y * -1.05, 12)

            if ball_speed_x > 0:
                ball_speed_x = min(ball_speed_x * 1.05, 12)
            else:
                ball_speed_x = max(ball_speed_x * 1.05, -10)

            bounce_sound.play()

            ball_speed_x *= 1.05
            ball_speed_y *= 1.05

        if ball.y >= 600:
            ball_active = False
            ball_speed_y = -4
            lives -= 1
            if lives == 0:
                game_over = True
                loss_sound.play()

        if ball.colliderect(paddle):
            bounce_sound.play()
            combo_multiplier = 1
            ball_speed_y = max(ball_speed_y * -1.05, -12)

            if ball_speed_x > 0:
                ball_speed_x = min(ball_speed_x * 1.05, 10)
            else:
                ball_speed_x = max(ball_speed_x * 1.05, -10)

            relative_intersect_x = (paddle.centerx - ball.centerx) / (paddle.width / 2)

            ball_speed_x = -relative_intersect_x * 7
            ball_speed_y = -abs(ball_speed_y) * 1.05

            ball_speed_y = max(ball_speed_y, -12)

            ball.bottom = paddle.top

        for item in bricks[:]:
            brick_rect, color = item
            if ball.colliderect(brick_rect):
                ball_speed_y *= -1
                hit_sound.play()

                base_points = COLOR_POINTS.get(color, 10)
                score += base_points * combo_multiplier
                combo_multiplier += 1

                bricks.remove(item)

                if score > high_score:
                    high_score = score
                shake_timer = 10

                shake_timer = 10
                if len(bricks) == 0:
                    game_over = True
                    message = "You Win!"
                break

    # 4. Rendering
    render_offset = [0, 0]
    if shake_timer > 0:
        import random

        render_offset = [random.randint(-4, 4), random.randint(-4, 4)]
        shake_timer -= 1

    screen.fill(BG)

    # --- UI Header Row ---
    # Draw a thin seperator line
    pygame.draw.line(screen, UI_GREY, (0, 50), (800, 50), 2)

    pygame.draw.rect(screen, UI_GREY, paddle.move(render_offset), border_radius=5)
    pygame.draw.ellipse(screen, WHITE, ball.move(render_offset))

    for brick_rect, color in bricks:
        pygame.draw.rect(screen, color, brick_rect.move(render_offset), border_radius=2)

    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (20, 15))

    high_text = font.render(f"High Score: {high_score}", True, WHITE)
    high_rect = high_text.get_rect(center=(400, 30))
    screen.blit(high_text, high_rect)

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (650, 15))

    if combo_multiplier > 3:
        neon_cyan = (0, 255, 255)
        outline_color = (20, 20, 20)
        pos_x, pos_y = 630, 70

        if combo_multiplier > 5:
            display_font = big_font
            combo_str = f"x{combo_multiplier} MEGA!!!"
        else:
            display_font = font
            combo_str = f"x{combo_multiplier} Combo!"

        text_surf = display_font.render(combo_str, True, neon_cyan)
        text_rect = text_surf.get_rect(topright=(780, 70))
        outline_surf = display_font.render(combo_str, True, outline_color)

        for dx, dy in [(-1, -1), (0, -1), (1, 1), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            outline_surf = display_font.render(combo_str, True, outline_color)
            screen.blit(outline_surf, (text_rect.x + dx, text_rect.y + dy))

        screen.blit(text_surf, text_rect)

    if game_over:
        # loss_sound.play()
        msg_surface = font.render(f"{message}! Press 'R' to Restart", True, WHITE)
        msg_rect = msg_surface.get_rect(center=(400, 300))
        screen.blit(msg_surface, msg_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
