import pygame
import random

class Base:
    def __init__(self, x, y, radius=3, color=(200, 200, 200)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    @staticmethod
    def spawn(noise_map, cols, rows, tile_size, radius=3, max_attempts=1000):
        """Find a safe spawn location for the base (not on or near mountains, not behind UI)."""
        for _ in range(max_attempts):
            x = random.randint(radius + 5, cols - radius - 6)
            y = random.randint(radius + 5, rows - radius - 6)

            if x * tile_size < 250 and y * tile_size < 200:
                continue

            safe = True
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx*dx + dy*dy <= radius*radius:
                        nx = x + dx
                        ny = y + dy
                        if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                            safe = False
                            break
                        if noise_map[ny][nx] >= 0.7: 
                            safe = False
                            break
                if not safe:
                    break

            if safe:
                return Base(x, y, radius=radius)

        return Base(cols // 2, rows // 2, radius=radius)

    def draw(self, screen, tile_size):
        for dy in range(-self.radius-1, self.radius+2):
            for dx in range(-self.radius-1, self.radius+2):
                if dx*dx + dy*dy <= (self.radius+1)*(self.radius+1):
                    rect = pygame.Rect(
                        (self.x+dx) * tile_size,
                        (self.y+dy) * tile_size,
                        tile_size,
                        tile_size
                    )
                    pygame.draw.rect(screen, (0, 0, 0), rect)

        for dy in range(-self.radius, self.radius+1):
            for dx in range(-self.radius, self.radius+1):
                if dx*dx + dy*dy <= self.radius*self.radius:
                    rect = pygame.Rect(
                        (self.x+dx) * tile_size,
                        (self.y+dy) * tile_size,
                        tile_size,
                        tile_size
                    )
                    pygame.draw.rect(screen, self.color, rect)
