import pygame
import noise
import numpy as np
import random
from terrain import get_biome_color  

class Menu:
    def __init__(self, width, height, tile_size=10, num_stars=200):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.cols = width // tile_size
        self.rows = height // tile_size

        # fonts
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_button = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_slider = pygame.font.SysFont("Arial", 28, bold=True)

        # Main menu buttons
        self.start_button = pygame.Rect(width // 2 - 100, height // 2 - 70, 200, 50)
        self.settings_button = pygame.Rect(width // 2 - 100, height // 2 + 0, 200, 50)
        self.quit_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)

        # Settings menu buttons
        self.back_button = pygame.Rect(width // 2 - 100, height - 100, 200, 50)
        self.audio_slider_rect = pygame.Rect(width // 2 - 150, height // 2 - 60, 300, 40)
        self.resolution_button = pygame.Rect(width // 2 - 100, height // 2 + 0, 200, 50)
        self.difficulty_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)

        self.audio_value = 100  
        self.resolutions = ["1280x720", "1920x1080"]
        self.res_index = 0
        self.difficulties = ["Easy", "Normal", "Hard"]
        self.diff_index = 1

        self.dragging_audio = False

        self.radius_x = self.cols // 1.6
        self.radius_y = self.rows // 4
        self.cx = self.cols // 2
        self.cy = self.rows

        self.noise_map = self.generate_noise_map()

        # Stars
        self.num_stars = num_stars
        self.stars = self.generate_stars()

    def generate_stars(self):
        stars = []
        for _ in range(self.num_stars):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
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
            # Ensure color is valid
            if not color or len(color) != 3:
                color = (255, 255, 255)
            screen.fill(color, rect=pygame.Rect(x, y, 2, 2))

        # Draw Mars half-sphere / terrain
        for y in range(self.rows):
            for x in range(self.cols):
                val = self.noise_map[y][x]
                if val is None or val < 0:
                    continue
                color = get_biome_color(val)

                # Fallback if biome function returns invalid
                if not color or len(color) != 3:
                    color = (100, 100, 100)  # grey for unknown

                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(screen, color, rect)

    def draw_main_menu(self, screen):
        screen.fill((0, 0, 0))
        self.draw_background(screen)

        # Title
        title_text = self.font_title.render("Mars Colony Simulator", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 100))

        # Buttons
        pygame.draw.rect(screen, (200, 50, 50), self.start_button)
        pygame.draw.rect(screen, (50, 150, 50), self.settings_button)
        pygame.draw.rect(screen, (50, 50, 200), self.quit_button)

        start_text = self.font_button.render("Start Game", True, (255, 255, 255))
        settings_text = self.font_button.render("Settings", True, (255, 255, 255))
        quit_text = self.font_button.render("Quit", True, (255, 255, 255))

        screen.blit(start_text, (self.start_button.centerx - start_text.get_width() // 2,
                                 self.start_button.centery - start_text.get_height() // 2))
        screen.blit(settings_text, (self.settings_button.centerx - settings_text.get_width() // 2,
                                    self.settings_button.centery - settings_text.get_height() // 2))
        screen.blit(quit_text, (self.quit_button.centerx - quit_text.get_width() // 2,
                                self.quit_button.centery - quit_text.get_height() // 2))

    def draw_settings_menu(self, screen):
        screen.fill((0, 0, 0))
        self.draw_background(screen)

        # Settings Title
        title_text = self.font_title.render("Settings", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 100))

        # Audio slider
        pygame.draw.rect(screen, (200, 50, 50), self.audio_slider_rect)
        handle_x = self.audio_slider_rect.x + int(self.audio_value / 100 * self.audio_slider_rect.width)
        pygame.draw.rect(screen, (255, 255, 255), (handle_x - 8, self.audio_slider_rect.y, 16, self.audio_slider_rect.height))

        audio_text = self.font_slider.render(f"Game Audio: {self.audio_value}%", True, (255, 255, 255))
        screen.blit(audio_text, (self.audio_slider_rect.centerx - audio_text.get_width() // 2,
                                 self.audio_slider_rect.y - 30))

        # Resolution button
        pygame.draw.rect(screen, (50, 150, 50), self.resolution_button)
        res_text = self.font_button.render(self.resolutions[self.res_index], True, (255, 255, 255))
        screen.blit(res_text, (self.resolution_button.centerx - res_text.get_width() // 2,
                               self.resolution_button.centery - res_text.get_height() // 2))

        # Difficulty button
        pygame.draw.rect(screen, (50, 50, 200), self.difficulty_button)
        diff_text = self.font_button.render(self.difficulties[self.diff_index], True, (255, 255, 255))
        screen.blit(diff_text, (self.difficulty_button.centerx - diff_text.get_width() // 2,
                                self.difficulty_button.centery - diff_text.get_height() // 2))

        # Back button
        pygame.draw.rect(screen, (150, 50, 200), self.back_button)
        back_text = self.font_button.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (self.back_button.centerx - back_text.get_width() // 2,
                                self.back_button.centery - back_text.get_height() // 2))

    def handle_events(self, event, in_settings=False, mouse_pos=None, mouse_held=False):
        if in_settings:
            if event and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Start dragging only if clicked inside slider
                if self.audio_slider_rect.collidepoint(event.pos):
                    self.dragging_audio = True
                else:
                    self.dragging_audio = False
                if self.back_button.collidepoint(event.pos):
                    return "back"
                elif self.resolution_button.collidepoint(event.pos):
                    self.res_index = (self.res_index + 1) % len(self.resolutions)
                elif self.difficulty_button.collidepoint(event.pos):
                    self.diff_index = (self.diff_index + 1) % len(self.difficulties)

            if mouse_held and self.dragging_audio:
                rel_x = mouse_pos[0] - self.audio_slider_rect.x
                self.audio_value = max(0, min(100, int((rel_x / self.audio_slider_rect.width) * 100)))

        else:
            if event and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button.collidepoint(event.pos):
                    return "start"
                elif self.settings_button.collidepoint(event.pos):
                    return "settings"
                elif self.quit_button.collidepoint(event.pos):
                    return "quit"

        return None
