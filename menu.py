import pygame
import noise
import numpy as np
import random
from terrain import get_biome_color  # reuse your terrain biomes

class Menu:
    def __init__(self, width, height, tile_size=10, num_stars=200):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.cols = width // tile_size
        self.rows = height // tile_size

        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_button = pygame.font.SysFont("Arial", 36, bold=True)

        # Buttons with more space for settings
        self.start_button = pygame.Rect(width // 2 - 100, height // 2 - 70, 200, 50)
        self.settings_button = pygame.Rect(width // 2 - 100, height // 2 + 0, 200, 50)
        self.quit_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)

        # Half-sphere parameters
        self.radius_x = self.cols // 1.6  # horizontal radius
        self.radius_y = self.rows // 4    # vertical radius
        self.cx = self.cols // 2          # center X in tile coords
        self.cy = self.rows               # bottom of screen in tile coords

        # Generate noise map for Mars half-sphere
        self.noise_map = self.generate_noise_map()

        # Generate stars
        self.num_stars = num_stars
        self.stars = self.generate_stars()

    def generate_stars(self):
        stars = []
        for _ in range(self.num_stars):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)  # allow stars all the way to bottom
            color = random.choice([(255, 255, 255), (255, 255, 200), (200, 200, 255)])
            stars.append((x, y, color))
        return stars


    def generate_noise_map(self):
        noise_map = np.zeros((self.rows, self.cols))
        scale = 10.0
        octaves = 4
        persistence = 0.5
        lacunarity = 2.0
        x_offset = random.uniform(0, 1000)
        y_offset = random.uniform(0, 1000)

        for y in range(self.rows):
            for x in range(self.cols):
                dx = x - self.cx
                dy = (y - self.cy) * 0.65
                if (dx*dx)/(self.radius_x*self.radius_x) + (dy*dy)/(self.radius_y*self.radius_y) > 1:
                    noise_map[y][x] = -1
                    continue

                nx = (x + x_offset) / scale
                ny = (y + y_offset) / scale
                val = noise.pnoise2(nx, ny, octaves=octaves,
                                    persistence=persistence,
                                    lacunarity=lacunarity,
                                    repeatx=1024, repeaty=1024, base=0)
                noise_map[y][x] = (val + 0.5)
        return noise_map

    def draw_background(self, screen):
    # Draw stars
        for x, y, color in self.stars:
            screen.fill(color, rect=pygame.Rect(x, y, 2, 2))

    # Draw Mars half-sphere on top
        for y in range(self.rows):
            for x in range(self.cols):
                val = self.noise_map[y][x]
                if val < 0:
                    continue
                color = get_biome_color(val)
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                self.tile_size, self.tile_size)
                pygame.draw.rect(screen, color, rect)


    def draw(self, screen):
        # Black sky
        screen.fill((0, 0, 0))
        # Pixelated Mars half-sphere + stars
        self.draw_background(screen)

        # Title
        title_text = self.font_title.render("Mars Colony Simulator", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 100))

        # Start button
        pygame.draw.rect(screen, (200, 50, 50), self.start_button)
        start_text = self.font_button.render("Start Game", True, (255, 255, 255))
        screen.blit(start_text, (self.start_button.centerx - start_text.get_width() // 2,
                                 self.start_button.centery - start_text.get_height() // 2))

        # Settings button
        pygame.draw.rect(screen, (50, 150, 50), self.settings_button)
        settings_text = self.font_button.render("Settings", True, (255, 255, 255))
        screen.blit(settings_text, (self.settings_button.centerx - settings_text.get_width() // 2,
                                    self.settings_button.centery - settings_text.get_height() // 2))

        # Quit button
        pygame.draw.rect(screen, (50, 50, 200), self.quit_button)
        quit_text = self.font_button.render("Quit", True, (255, 255, 255))
        screen.blit(quit_text, (self.quit_button.centerx - quit_text.get_width() // 2,
                                self.quit_button.centery - quit_text.get_height() // 2))

    def handle_events(self, event):
        """Returns 'start', 'settings', or 'quit' if buttons are pressed"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.collidepoint(event.pos):
                return "start"
            elif self.settings_button.collidepoint(event.pos):
                return "settings"
            elif self.quit_button.collidepoint(event.pos):
                return "quit"
        return None
