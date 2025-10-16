import pygame
import math

class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target = None
        self.speed = 100  # pixels per second
        self.storage = 0

        # Behavior attributes
        self.mining_active = False
        self.awaiting_move_confirmation = False

        # Visuals
        self.radius = 10
        self.color = (255, 255, 0)

        # --- Power (Battery) Attributes ---
        self.max_power = 100
        self.power = self.max_power
        self.power_depletion_time = 30   # seconds to fully drain while moving
        self.recharge_rate = 2           # % per second on generator

        # --- Move counters ---
        self.move_count = 0
        self.max_moves = 2

    # -----------------------------
    # Target and movement
    # -----------------------------
    def set_target(self, pos):
        self.target = pos

    def move(self, noise_map, tile_size, cols, rows, dt):
        if self.target and self.power > 0:
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            dist = math.hypot(dx, dy)
            if dist < 1:
                self.target = None
            else:
                step = self.speed * dt
                self.x += dx / dist * step
                self.y += dy / dist * step

                # Deplete power while moving
                depletion_rate = self.max_power / self.power_depletion_time
                self.power -= depletion_rate * dt
                if self.power < 0:
                    self.power = 0

    # -----------------------------
    # Recharge handling
    # -----------------------------
    def recharge(self, dt):
        """Recharges drone battery while on a generator."""
        if self.power < self.max_power:
            self.power += self.recharge_rate * dt
            if self.power > self.max_power:
                self.power = self.max_power

    # -----------------------------
    # Drawing
    # -----------------------------
    def draw(self, screen):
        # Drone body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Power bar
        bar_width = self.radius * 2
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 8

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (self.power / self.max_power))
        color = (50, 220, 50) if self.power > 30 else (220, 50, 50)
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))

    # -----------------------------
    # Click detection
    # -----------------------------
    def is_clicked(self, pos):
        mx, my = pos
        return (self.x - mx) ** 2 + (self.y - my) ** 2 <= self.radius ** 2
