import pygame
import math

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOV = math.pi / 3  # Field of view
HALF_FOV = FOV / 2
NUM_RAYS = 120  # Number of rays to cast
MAX_DEPTH = 800  # Max distance to check for walls
SCALE = SCREEN_WIDTH // NUM_RAYS

# Player settings
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_angle = 0
player_pitch = 0  # Variable to track vertical look
player_speed = 3
mouse_sensitivity = 0.003  # Sensitivity for mouse movement

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Map (1 represents walls)
game_map = [
    "########",
    "#......#",
    "#......#",
    "#......#",
    "#......#",
    "########"
]

# Tile settings
TILE = 100  # Each tile size in the world


def cast_rays(screen, player_pos, player_angle, player_pitch):
    start_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        # Calculate ray angle and step
        ray_angle = start_angle + ray * FOV / NUM_RAYS
        x, y = player_pos
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # Check for wall collision
        for depth in range(MAX_DEPTH):
            target_x = x + depth * cos_a
            target_y = y + depth * sin_a

            col = int(target_x // TILE)
            row = int(target_y // TILE)

            if game_map[row][col] == '#':
                # Draw the wall strip
                depth *= math.cos(player_angle - ray_angle)  # Correct fish-eye effect
                wall_height = min(20000 / (depth + 0.0001), SCREEN_HEIGHT)
                color = 255 / (1 + depth * depth * 0.0001)

                # Adjust the wall's vertical position based on player pitch
                wall_column = pygame.Rect(
                    ray * SCALE,
                    SCREEN_HEIGHT // 2 - wall_height // 2 - player_pitch,  # Adjusting for pitch
                    SCALE,
                    wall_height
                )
                pygame.draw.rect(screen, (color, color, color), wall_column)
                break


def is_wall(x, y):
    """Check if the given (x, y) position is inside a wall."""
    col = int(x // TILE)
    row = int(y // TILE)
    if 0 <= col < len(game_map[0]) and 0 <= row < len(game_map):
        return game_map[row][col] == '#'
    return True  # Treat out-of-bounds as walls


def main():
    global player_pos, player_angle, player_pitch  # Declare global variables
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.event.set_grab(True)  # Lock the mouse to the window
    pygame.mouse.set_visible(False)  # Hide the mouse cursor

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle mouse movement
        mouse_movement = pygame.mouse.get_rel()
        player_angle += mouse_movement[0] * mouse_sensitivity
        player_pitch += mouse_movement[1] * mouse_sensitivity * 200  # Fixed direction for looking up/down

        # Clamp the pitch to prevent excessive up/down looking
        player_pitch = max(-SCREEN_HEIGHT // 2, min(SCREEN_HEIGHT // 2, player_pitch))

        # Player movement
        keys = pygame.key.get_pressed()
        dx = dy = 0

        # Calculate the player's movement vector
        if keys[pygame.K_w]:
            dx += player_speed * math.cos(player_angle)
            dy += player_speed * math.sin(player_angle)
        if keys[pygame.K_s]:
            dx -= player_speed * math.cos(player_angle)
            dy -= player_speed * math.sin(player_angle)
        if keys[pygame.K_a]:
            dx += player_speed * math.sin(player_angle)
            dy -= player_speed * math.cos(player_angle)
        if keys[pygame.K_d]:
            dx -= player_speed * math.sin(player_angle)
            dy += player_speed * math.cos(player_angle)

        # Check collision for the new position
        next_x = player_pos[0] + dx
        next_y = player_pos[1] + dy

        # Only update the player position if there is no collision
        if not is_wall(next_x, player_pos[1]):
            player_pos[0] = next_x
        if not is_wall(player_pos[0], next_y):
            player_pos[1] = next_y

        # Draw
        screen.fill(BLACK)
        cast_rays(screen, player_pos, player_angle, player_pitch)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
if __name__ == '__main__':
    main()
