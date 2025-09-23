import pygame
import math

class Rover:  
    def __init__(self, x, y, speed=1.5, size=10, color=(0, 255, 0)):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = speed
        self.size = size
        self.color = color

    def set_target(self, pos):
        self.target_x, self.target_y = pos

    def move(self, noise_map, tile_size, cols, rows, rock_threshold=0.7):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        if distance < self.speed:
            next_x, next_y = self.target_x, self.target_y
        else:
            next_x = self.x + self.speed * dx / distance
            next_y = self.y + self.speed * dy / distance

        tile_x = int(next_x / tile_size)
        tile_y = int(next_y / tile_size)
        if 0 <= tile_x < cols and 0 <= tile_y < rows:
            if noise_map[tile_y][tile_x] < rock_threshold:
                self.x, self.y = next_x, next_y

    def draw(self, screen):
        rover_rect = pygame.Rect(int(self.x)-self.size//2, int(self.y)-self.size//2,
                                 self.size, self.size)
        pygame.draw.rect(screen, self.color, rover_rect)
