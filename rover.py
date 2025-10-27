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
        self.max_storage = 5  # Max resource units rover can hold

        # --- Power (Battery) Attributes ---
        self.max_power = 100              # Max battery (%)
        self.power = self.max_power       # Current battery (%)
        self.power_depletion_time = 30    # Seconds to fully drain while moving
        self.recharge_rate = 2            # % per second when on generator

        # --- Movement / Mining ---
        self.awaiting_move_confirmation = False
        self.mining_active = False
        self.target = None
        self.current_resource = None      # Resource rover is currently mining
        self.resources_held = {}          # Dictionary {"Iron": 3, "Copper": 2}

        # --- Move counters ---
        self.move_count = 0
        self.max_moves = 2

    # -----------------------------
    # Target and movement
    # -----------------------------
    def set_target(self, pos):
        self.target_x, self.target_y = pos
        self.target = pos

    def move(self, noise_map, tile_size, cols, rows, dt, rock_threshold=0.7):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        # Move only if there’s power and distance
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

                    # Deplete power when moving
                    if moved_distance > 0:
                        depletion_rate = self.max_power / self.power_depletion_time
                        self.power -= depletion_rate * dt
                        if self.power < 0:
                            self.power = 0

    # -----------------------------
    # Recharge handling
    # -----------------------------
    def recharge(self, dt):
        """Recharges rover battery while on a generator or via drone."""
        if self.power < self.max_power:
            self.power += self.recharge_rate * dt
            if self.power > self.max_power:
                self.power = self.max_power

    # -----------------------------
    # Drawing
    # -----------------------------
    def draw(self, screen):
        # Rover body
        rect = pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2),
                           self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

        # Power bar background
        bar_width = self.size
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size // 2 - 8

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # Power bar fill
        fill_width = int(bar_width * (self.power / self.max_power))
        color = (50, 220, 50) if self.power > 30 else (220, 50, 50)
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))

    # -----------------------------
    # Click detection
    # -----------------------------
    def is_clicked(self, pos):
        rect = pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2),
                           self.size, self.size)
        return rect.collidepoint(pos)
