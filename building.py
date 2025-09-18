import pygame
import random

class Base:
    def __init__(self, noise_map, cols, rows, mountain_threshold=0.7, radius=3, color=(200, 200, 200)):
        self.radius = radius
        self.color = color
        self.tile_size = None
        self.noise_map = noise_map
        self.cols = cols
        self.rows = rows
        self.mountain_threshold = mountain_threshold
        self.x, self.y = self.spawn_base()

    def spawn_base(self):
        DASHBOARD_WIDTH = 200
        DASHBOARD_HEIGHT = 150
        dashboard_cols = DASHBOARD_WIDTH // 10  # TILE_SIZE = 10
        dashboard_rows = DASHBOARD_HEIGHT // 10

        while True:
            x = random.randint(self.radius, self.cols - self.radius - 1)
            y = random.randint(self.radius, self.rows - self.radius - 1)

        # Avoid dashboard area
            if x < dashboard_cols and y < dashboard_rows:
                continue

            if self.noise_map[y][x] < self.mountain_threshold:
                safe = True
                for dy in range(-self.radius, self.radius + 1):
                    for dx in range(-self.radius, self.radius + 1):
                        if self.noise_map[y + dy][x + dx] >= self.mountain_threshold:
                            safe = False
                            break
                    if not safe:
                        break
                if safe:
                    return x, y


    def draw(self, screen, tile_size):
    # --- Draw outline (black border) ---
        for dy in range(-self.radius-1, self.radius+2):
            for dx in range(-self.radius-1, self.radius+2):
                if dx*dx + dy*dy <= (self.radius+1)*(self.radius+1):
                    rect = pygame.Rect((self.x+dx)*tile_size, (self.y+dy)*tile_size, tile_size, tile_size)
                    pygame.draw.rect(screen, (0, 0, 0), rect)

    # --- Draw base (light gray fill) ---
        for dy in range(-self.radius, self.radius+1):
            for dx in range(-self.radius, self.radius+1):
                if dx*dx + dy*dy <= self.radius*self.radius:
                    rect = pygame.Rect((self.x+dx)*tile_size, (self.y+dy)*tile_size, tile_size, tile_size)
                    pygame.draw.rect(screen, self.color, rect)

