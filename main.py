import pygame
import noise
import numpy as np
import random
import math

pygame.init()

# ---------------- Window setup ---------------- #
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")

# ---------------- Noise parameters ---------------- #
SCALE = 40.0
OCTAVES = 8
PERSISTENCE = 0.5
LACUNARITY = 2.0

# Random offsets to avoid stripes
X_OFFSET = random.uniform(0, 10000)
Y_OFFSET = random.uniform(0, 10000)

# ---------------- Rover ---------------- #
rover_x, rover_y = WIDTH // 2, HEIGHT // 2
target_x, target_y = rover_x, rover_y
ROVER_SPEED = 1.5  # slower movement

# ---------------- Helper Functions ---------------- #
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def get_biome_color(value):
    if value < 0.35:
        c1 = (110, 40, 30)
        c2 = (180, 60, 40)
        t = value / 0.35
        return lerp_color(c1, c2, t)
    elif value < 0.55:
        c1 = (200, 90, 50)
        c2 = (230, 130, 70)
        t = (value - 0.35) / 0.2
        return lerp_color(c1, c2, t)
    elif value < 0.7:
        c1 = (210, 160, 120)
        c2 = (235, 190, 150)
        t = (value - 0.55) / 0.15
        return lerp_color(c1, c2, t)
    elif value < 0.85:
        c1 = (70, 60, 55)
        c2 = (130, 120, 115)
        t = (value - 0.7) / 0.15
        return lerp_color(c1, c2, t)
    else:
        c1 = (180, 180, 180)
        c2 = (230, 230, 230)
        t = (value - 0.85) / 0.15
        return lerp_color(c1, c2, t)

def generate_noise_map():
    noise_map = np.zeros((ROWS, COLS))
    for y in range(ROWS):
        for x in range(COLS):
            nx = (x + X_OFFSET) / SCALE
            ny = (y + Y_OFFSET) / SCALE
            noise_val = noise.pnoise2(nx, ny,
                                      octaves=OCTAVES,
                                      persistence=PERSISTENCE,
                                      lacunarity=LACUNARITY)
            noise_map[y][x] = noise_val

    min_val = np.min(noise_map)
    max_val = np.max(noise_map)
    noise_map = (noise_map - min_val) / (max_val - min_val + 1e-8)
    return noise_map

def draw_terrain(noise_map):
    for y in range(ROWS):
        for x in range(COLS):
            color = get_biome_color(noise_map[y][x])
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

def move_rover():
    global rover_x, rover_y
    dx = target_x - rover_x
    dy = target_y - rover_y
    distance = math.hypot(dx, dy)
    if distance < ROVER_SPEED:
        next_x, next_y = target_x, target_y
    else:
        next_x = rover_x + ROVER_SPEED * dx / distance
        next_y = rover_y + ROVER_SPEED * dy / distance

    # Convert next position to tile coordinates
    tile_x = int(next_x / TILE_SIZE)
    tile_y = int(next_y / TILE_SIZE)

    # Check boundaries and collision with rocks
    if 0 <= tile_x < COLS and 0 <= tile_y < ROWS:
        if noise_map[tile_y][tile_x] < 0.7:  # passable terrain
            rover_x, rover_y = next_x, next_y

def draw_rover():
    rover_rect = pygame.Rect(int(rover_x)-5, int(rover_y)-5, 10, 10)
    pygame.draw.rect(screen, (0, 255, 0), rover_rect)  # green rover

# ---------------- Main Loop ---------------- #
def main():
    global target_x, target_y, noise_map
    noise_map = generate_noise_map()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                target_x, target_y = event.pos  # click sets new rover target

        draw_terrain(noise_map)
        move_rover()
        draw_rover()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()



#git init
# git branch -M main
# git push -u origin main