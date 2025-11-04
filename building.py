import pygame
import random

class Base:
    def __init__(self, x, y, size=4, color=(200, 200, 200), border_color=(0,0,0)):
        """
        x, y = center tile coordinates of the base
        size = number of tiles per side (square)
        color = interior color
        border_color = outline color
        """
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.border_color = border_color

    @staticmethod
    def spawn(noise_map, cols, rows, tile_size, size=4, max_attempts=1000):
        half = size // 2
        for _ in range(max_attempts):
            x = random.randint(half + 5, cols - half - 6)
            y = random.randint(half + 5, rows - half - 6)

            # Avoid UI area
            ui_block_width = 250
            ui_block_height = 200
            if (x - half) * tile_size < ui_block_width or (y - half) * tile_size < ui_block_height:
                continue

            safe = True
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    nx = x + dx
                    ny = y + dy
                    if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                        safe = False
                        break
                    if noise_map[ny][nx] >= 0.7:  # too steep/mountain
                        safe = False
                        break
                if not safe:
                    break

            if safe:
                return Base(x, y, size=size)

        # fallback
        return Base(cols // 2, rows // 2, size=size)

    def draw(self, screen, tile_size):
        half = self.size // 2
        rect = pygame.Rect(
            (self.x - half) * tile_size,
            (self.y - half) * tile_size,
            self.size * tile_size,
            self.size * tile_size
        )

        # Fill (base color)
        pygame.draw.rect(screen, (180, 180, 180), rect)

        # Black inner outline — same style as buildings
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    def is_clicked(self, mouse_pos, tile_size=10):
        mx, my = mouse_pos
        half = self.size // 2
        rect = pygame.Rect(
            (self.x - half) * tile_size,
            (self.y - half) * tile_size,
            self.size * tile_size,
            self.size * tile_size
        )
        return rect.collidepoint(mx, my)
