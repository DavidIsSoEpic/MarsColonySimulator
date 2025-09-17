import pygame
import noise
import numpy as np
import random
from rover import Rover  # 🚙 import Rover class

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

# ---------------- Helper Functions ---------------- #
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def get_biome_color(value):
    if value < 0.35:
        return lerp_color((110, 40, 30), (180, 60, 40), value / 0.35)
    elif value < 0.55:
        return lerp_color((200, 90, 50), (230, 130, 70), (value - 0.35) / 0.2)
    elif value < 0.7:
        return lerp_color((210, 160, 120), (235, 190, 150), (value - 0.55) / 0.15)
    elif value < 0.85:
        return lerp_color((70, 60, 55), (130, 120, 115), (value - 0.7) / 0.15)
    else:
        return lerp_color((180, 180, 180), (230, 230, 230), (value - 0.85) / 0.15)

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
    return (noise_map - min_val) / (max_val - min_val + 1e-8)

def draw_terrain(noise_map):
    for y in range(ROWS):
        for x in range(COLS):
            color = get_biome_color(noise_map[y][x])
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

# ---------------- Main Loop ---------------- #
def main():
    noise_map = generate_noise_map()
    rover = Rover(WIDTH // 2, HEIGHT // 2)  # 🚙 initialize rover
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rover.set_target(event.pos)  # 🚙 set target

        draw_terrain(noise_map)
        rover.move(noise_map, TILE_SIZE, COLS, ROWS)  # 🚙 move rover
        rover.draw(screen)  # 🚙 draw rover

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()




# git init
# git add .
# git add main.py
# git commit -m (COMMENT)
# git push -u origin main