import pygame
import numpy as np
import noise
import random

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
    """Linearly interpolate between two colors."""
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

def generate_noise_map(rows, cols):
    """Generate a normalized 2D noise map."""
    noise_map = np.zeros((rows, cols))
    for y in range(rows):
        for x in range(cols):
            nx = (x + X_OFFSET) / SCALE
            ny = (y + Y_OFFSET) / SCALE
            noise_val = noise.pnoise2(nx, ny,
                                      octaves=OCTAVES,
                                      persistence=PERSISTENCE,
                                      lacunarity=LACUNARITY)
            noise_map[y][x] = noise_val

    # Normalize to 0-1
    min_val = np.min(noise_map)
    max_val = np.max(noise_map)
    return (noise_map - min_val) / (max_val - min_val + 1e-8)

def draw_terrain(screen, noise_map, tile_size):
    """Draw the terrain on the screen."""
    rows, cols = noise_map.shape
    for y in range(rows):
        for x in range(cols):
            color = get_biome_color(noise_map[y][x])
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            pygame.draw.rect(screen, color, rect)
