import pygame
import noise
import numpy as np
import random

pygame.init()

# ---------------- Window setup ---------------- #
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")

# ---------------- Noise parameters ---------------- #
SCALE = 40.0        # Smaller = more varied features
OCTAVES = 8
PERSISTENCE = 0.5
LACUNARITY = 2.0

# Random offsets each run (avoid striping)
X_OFFSET = random.uniform(0, 10000)
Y_OFFSET = random.uniform(0, 10000)


# ---------------- Helper Functions ---------------- #
def lerp_color(c1, c2, t):
    """Linear interpolation between two colors"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def get_biome_color(value):
    """Map noise value (0–1) to Mars-like terrain colors"""
    if value < 0.3:  # Deep rust-red lowlands
        c1 = (110, 40, 30)
        c2 = (180, 60, 40)
        t = value / 0.3
        return lerp_color(c1, c2, t)
    elif value < 0.55:  # Orange dusty plains
        c1 = (200, 90, 50)
        c2 = (230, 130, 70)
        t = (value - 0.3) / 0.25
        return lerp_color(c1, c2, t)
    elif value < 0.7:  # Beige highlands
        c1 = (210, 160, 120)
        c2 = (235, 190, 150)
        t = (value - 0.55) / 0.15
        return lerp_color(c1, c2, t)
    elif value < 0.85:  # Rocky ridges (dark basalt/gray)
        c1 = (70, 60, 55)
        c2 = (130, 120, 115)
        t = (value - 0.7) / 0.15
        return lerp_color(c1, c2, t)
    else:  # Peaks (light gray / frost)
        c1 = (180, 180, 180)
        c2 = (230, 230, 230)
        t = (value - 0.85) / 0.15
        return lerp_color(c1, c2, t)


def generate_noise_map():
    """Generate 2D Perlin noise map, normalized to 0–1"""
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

    # Normalize full map to 0–1 range
    min_val = np.min(noise_map)
    max_val = np.max(noise_map)
    noise_map = (noise_map - min_val) / (max_val - min_val + 1e-8)

    return noise_map


def draw_terrain(noise_map):
    """Draw the terrain on screen based on noise map"""
    for y in range(ROWS):
        for x in range(COLS):
            color = get_biome_color(noise_map[y][x])
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)


# ---------------- Main Loop ---------------- #
def main():
    noise_map = generate_noise_map()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_terrain(noise_map)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
