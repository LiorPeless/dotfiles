
import pygame
import math
import socket
import pickle

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 800
SCALE = SCREEN_WIDTH // NUM_RAYS

# Player settings
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_angle = 0
player_pitch = 0
player_speed = 3
mouse_sensitivity = 0.003
key_rotation_speed = 0.05  # Speed of rotation using arrow keys

# Server connection settings
SERVER = '127.0.0.1'
PORT = 5555

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Map
game_map = [
    "########",
    "#......#",
    "#......#",
    "#......#",
    "#......#",
    "########"
]

TILE = 100

def normalize_angle(angle):
    """Normalizes an angle to be within the range of -π to π."""
    return (angle + math.pi) % (2 * math.pi) - math.pi

def get_sprite(viewer_angle, target_angle, sprites):
    """Select the appropriate sprite based on the viewer's and target's facing directions."""
    # Calculate the relative angle between the viewing direction and the target's facing direction
    relative_angle = normalize_angle(target_angle - viewer_angle)

    # Map relative angles to specific sprite directions
    if -math.pi / 4 <= relative_angle < math.pi / 4:
        # Target is facing away from the viewer
        return sprites['back'][0]
    elif math.pi / 4 <= relative_angle < 3 * math.pi / 4:
        # Target is facing left from the viewer's perspective
        return sprites['right'][0]
    elif -3 * math.pi / 4 <= relative_angle < -math.pi / 4:
        # Target is facing right from the viewer's perspective
        return sprites['left'][0]
    else:
        # Target is facing towards the viewer
        return sprites['front'][0]

def cast_rays(screen, player_pos, player_angle, player_pitch, players, sprites):
    """Cast rays to render the scene, including other players."""
    start_angle = player_angle - HALF_FOV
    objects_to_render = []  # To store walls and players to render in order of depth

    # Cast rays to find walls
    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * FOV / NUM_RAYS
        x, y = player_pos
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, MAX_DEPTH):
            target_x = x + depth * cos_a
            target_y = y + depth * sin_a

            col = int(target_x // TILE)
            row = int(target_y // TILE)

            if game_map[row][col] == '#':
                depth *= math.cos(player_angle - ray_angle)  # Correct fish-eye effect
                wall_height = min(20000 / (depth + 0.0001), SCREEN_HEIGHT)
                color = 255 / (1 + depth * depth * 0.0001)

                objects_to_render.append({
                    'depth': depth,
                    'color': (color, color, color),
                    'rect': pygame.Rect(ray * SCALE, SCREEN_HEIGHT // 2 - wall_height // 2 - player_pitch, SCALE, wall_height)
                })
                break

    # Draw other players
    for addr, data in players.items():
        if data['pos'] != player_pos:  # Don't draw yourself
            other_x, other_y = data['pos']
            other_angle = data['angle']  # Other player's facing angle
            dx = other_x - player_pos[0]
            dy = other_y - player_pos[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Calculate the angle between the player and the other player
            angle_to_player = math.atan2(dy, dx)
            angle_difference = normalize_angle(angle_to_player - player_angle)

            # Ensure the angle difference is within the field of view
            if -HALF_FOV < angle_difference < HALF_FOV:
                # Correct the fisheye effect
                distance *= math.cos(angle_difference)
                player_height = min(20000 / (distance + 0.0001), SCREEN_HEIGHT)
                scale_factor = 0.6  # Adjust this value as needed to get the correct size
                scaled_height = int(player_height * scale_factor)
                player_screen_x = SCREEN_WIDTH // 2 + (angle_difference * (SCREEN_WIDTH // FOV))

                # Select the correct sprite based on the relative angle between the viewer's and target's facing directions
                sprite_image = get_sprite(player_angle, other_angle, sprites)

                # Scale the sprite proportionally to its new height
                sprite_width = sprite_image.get_width()
                sprite_height = sprite_image.get_height()
                scaled_width = int(scaled_height * (sprite_width / sprite_height))
                scaled_sprite = pygame.transform.scale(sprite_image, (scaled_width, scaled_height))

                # Position the sprite so its bottom is at ground level
                sprite_rect = scaled_sprite.get_rect(center=(player_screen_x, SCREEN_HEIGHT // 2 - player_pitch))
                sprite_rect.bottom = SCREEN_HEIGHT // 2 + player_height // 2 - player_pitch  # Adjust to ground level

                # Add the sprite as a renderable object
                objects_to_render.append({
                    'depth': distance,
                    'sprite': scaled_sprite,
                    'rect': sprite_rect
                })

    # Sort objects to render by depth (draw farthest first)
    objects_to_render = sorted(objects_to_render, key=lambda obj: obj['depth'], reverse=True)

    # Render all objects
    for obj in objects_to_render:
        if 'color' in obj:
            # Render walls
            pygame.draw.rect(screen, obj['color'], obj['rect'])
        else:
            # Render sprites
            screen.blit(obj['sprite'], obj['rect'])

def is_wall(x, y):
    """Check if the given (x, y) position is inside a wall."""
    col = int(x // TILE)
    row = int(y // TILE)
    if 0 <= col < len(game_map[0]) and 0 <= row < len(game_map):
        return game_map[row][col] == '#'
    return True  # Treat out-of-bounds as walls

def main():
    global player_pos, player_angle, player_pitch
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    # Load the player sprites after initializing Pygame's display
    sprites = {
        'front': [pygame.image.load(f'assets/warlock/frame-{i:03}.png').convert_alpha() for i in range(1, 5)],  # Updated indices
        'right': [pygame.image.load(f'assets/warlock/frame-{i:03}.png').convert_alpha() for i in range(5, 9)],
        'left': [pygame.image.load(f'assets/warlock/frame-{i:03}.png').convert_alpha() for i in range(9, 13)],
        'back': [pygame.image.load(f'assets/warlock/frame-{i:03}.png').convert_alpha() for i in range(14, 17)]
    }

    # Connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_movement = pygame.mouse.get_rel()
        player_angle += mouse_movement[0] * mouse_sensitivity
        player_pitch += mouse_movement[1] * mouse_sensitivity * 200
        player_pitch = max(-SCREEN_HEIGHT // 2, min(SCREEN_HEIGHT // 2, player_pitch))

        # Normalize the player_angle to prevent it from growing infinitely
        player_angle = normalize_angle(player_angle)

        keys = pygame.key.get_pressed()
        dx = dy = 0

        # Handle movement
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

        # Handle looking around with arrow keys
        if keys[pygame.K_LEFT]:
            player_angle -= key_rotation_speed
        if keys[pygame.K_RIGHT]:
            player_angle += key_rotation_speed
        if keys[pygame.K_UP]:
            player_pitch -= key_rotation_speed * 200  # Adjust pitch speed to match mouse sensitivity
        if keys[pygame.K_DOWN]:
            player_pitch += key_rotation_speed * 200

        # Clamp the pitch to prevent looking too far up or down
        player_pitch = max(-SCREEN_HEIGHT // 2, min(SCREEN_HEIGHT // 2, player_pitch))

        # Normalize the player_angle to prevent it from growing infinitely
        player_angle = normalize_angle(player_angle)

        # Update player position with collision check
        next_x = player_pos[0] + dx
        next_y = player_pos[1] + dy

        if not is_wall(next_x, player_pos[1]):
            player_pos[0] = next_x
        if not is_wall(player_pos[0], next_y):
            player_pos[1] = next_y

        # Send player state to the server
        player_data = {'pos': player_pos, 'angle': player_angle}
        client.send(pickle.dumps(player_data))

        # Receive game state from the server
        data = client.recv(2048)
        players = pickle.loads(data)

        screen.fill(BLACK)
        cast_rays(screen, player_pos, player_angle, player_pitch, players, sprites)
        pygame.display.flip()
        clock.tick(60)

    client.close()
    pygame.quit()

if __name__ == '__main__':
    main()
