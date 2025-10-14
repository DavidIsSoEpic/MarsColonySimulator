import pygame
import math

class Rover:  
    def __init__(self, x, y, speed=1.5, size=20, color=(0, 255, 0)):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = speed
        self.size = size
        self.color = color
        self.storage = 0

        # --- Power attributes ---
        self.max_power = 100              # Maximum power %
        self.power = self.max_power       # Current power %
        self.power_depletion_time = 30    # seconds to fully deplete power
        self.awaiting_move_confirmation = False
        self.mining_active = False
        self.target = None

    def set_target(self, pos):
        self.target_x, self.target_y = pos
        self.target = pos

    def move(self, noise_map, tile_size, cols, rows, dt, rock_threshold=0.7):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        # Only move if target exists, distance > 0, and has power
        if distance > 0 and self.power > 0:
            if distance < self.speed:
                next_x, next_y = self.target_x, self.target_y
            else:
                next_x = self.x + self.speed * dx / distance
                next_y = self.y + self.speed * dy / distance

            tile_x = int(next_x / tile_size)
            tile_y = int(next_y / tile_size)

            if 0 <= tile_x < cols and 0 <= tile_y < rows:
                if noise_map[tile_y][tile_x] < rock_threshold:
                    moved_distance = math.hypot(next_x - self.x, next_y - self.y)
                    self.x, self.y = next_x, next_y

                    # Deplete power only if actually moved
                    if moved_distance > 0:
                        # Power depletes over 30 seconds of continuous movement
                        power_depletion_rate = self.max_power / self.power_depletion_time  # per second
                        self.power -= power_depletion_rate * dt
                        if self.power < 0:
                            self.power = 0


    def draw(self, screen):
        rect = pygame.Rect(int(self.x - self.size//2), int(self.y - self.size//2),
                           self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

    def is_clicked(self, pos):
        rect = pygame.Rect(int(self.x - self.size//2), int(self.y - self.size//2),
                           self.size, self.size)
        return rect.collidepoint(pos)
