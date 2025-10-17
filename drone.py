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
        self.max_power = 100  # full battery now 100%
        self.power = self.max_power

        # Slower depletion → still slower than rover
        self.power_depletion_time = 45  # seconds to drain from 100% → 0%
        self.recharge_rate = 2          # % per second when on generator

        self.move_count = 0
        self.max_moves = 9999

        # Recharging rover
        self.recharging_rover = None

    # -----------------------------
    # Movement
    # -----------------------------
    def set_target(self, pos):
        if not self.recharging_rover:  # can't move while recharging a rover
            self.target = pos

    def move(self, noise_map, tile_size, cols, rows, dt):
        if self.target and self.power > 0 and not self.recharging_rover:
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
    # Recharge handling (generator)
    # -----------------------------
    def recharge(self, dt):
        self.power += self.recharge_rate * dt
        if self.power > self.max_power:
            self.power = self.max_power

    # -----------------------------
    # Transfer power to rover
    # -----------------------------
    def transfer_power_to_rover(self, rover, dt):
        """Transfer power from drone → rover."""
        if self.power > 0 and rover.power < rover.max_power:
            transfer_rate = 2 * dt  # 2% per second
            rover.power = min(rover.power + transfer_rate, rover.max_power)
            self.power -= transfer_rate
            if self.power < 0:
                self.power = 0

        # Stop if either battery is at limit
        if self.power <= 0 or rover.power >= rover.max_power:
            self.recharging_rover = None

    # -----------------------------
    # Drawing
    # -----------------------------
    def draw(self, screen):
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
