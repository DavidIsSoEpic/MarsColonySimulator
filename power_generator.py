import pygame
import random

class PowerGenerator:
    def __init__(self, gx, gy, size=(4, 4)):
        self.gx = gx
        self.gy = gy
        self.size = size

        # Energy properties
        self.power = 25.0          # starts at 25%
        self.output_base = 2.4     # min Watts
        self.output_max = 5.0      # max Watts
        self.last_output = self.get_output()

        # Recharge rate for nearby units
        self.recharge_rate = 2.0   # % per second

    # -----------------------------
    # Drawing
    # -----------------------------
    def draw(self, screen, tile_size):
        rect = pygame.Rect(
            self.gx * tile_size,
            self.gy * tile_size,
            self.size[0] * tile_size,
            self.size[1] * tile_size
        )
        pygame.draw.rect(screen, (255, 255, 0), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    def is_clicked(self, pos, tile_size=10):
        rect = pygame.Rect(
            self.gx * tile_size,
            self.gy * tile_size,
            self.size[0] * tile_size,
            self.size[1] * tile_size
        )
        return rect.collidepoint(pos)

    # -----------------------------
    # Power management
    # -----------------------------
    def update_power(self, dt):
        """Increase internal power over time (solar recharge)."""
        self.power += dt / 3   # 1% every 3 seconds
        if self.power > 100:
            self.power = 100

    def get_output(self):
        """Return slightly flickering output for realism."""
        base_output = self.output_base + (self.power / 100) * (self.output_max - self.output_base)
        flicker = random.uniform(-0.05, 0.05)  # small flicker
        return round(max(self.output_base, min(self.output_max, base_output + flicker)), 1)

    # -----------------------------
    # Recharge nearby units
    # -----------------------------
    def recharge_units(self, units, dt, tile_size):
        """Recharge rovers/drones overlapping this generator."""
        gx_px = self.gx * tile_size
        gy_px = self.gy * tile_size
        width_px = self.size[0] * tile_size
        height_px = self.size[1] * tile_size
        generator_rect = pygame.Rect(gx_px, gy_px, width_px, height_px)

        for unit in units:
            unit_rect = pygame.Rect(unit.x - 10, unit.y - 10, 20, 20)
            if generator_rect.colliderect(unit_rect):
                if hasattr(unit, "power") and unit.power < unit.max_power:
                    unit.recharge(dt)
                    # Reduce generator charge proportionally
                    if self.power > 0:
                        self.power -= self.recharge_rate * dt * 0.5
                        if self.power < 0:
                            self.power = 0

# -----------------------------
# Inventory
# -----------------------------
class PowerGeneratorInventory:
    def __init__(self, generator, dashboard):
        self.generator = generator
        self.dashboard = dashboard
        self.width = 400
        self.height = 160
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.visible = False

    def update(self, dt):
        """Keep power updated regardless of visibility."""
        self.generator.update_power(dt)
        self.generator.last_output = self.generator.get_output()

        # Update dashboard to show percent, not flickering watts
        if self.dashboard:
            # sum of generator powers or display main generator percent
            self.dashboard.power = int(self.generator.power)

    def draw(self, screen):
        if not self.visible:
            return

        panel = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (20, 20, 20), panel)
        pygame.draw.rect(screen, (255, 255, 255), panel, 3)

        title_text = self.font.render("Solar Power Generator", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 20, self.y + 15))

        output_text = self.font.render(f"Power Output: {self.generator.last_output} W", True, (200, 255, 100))
        screen.blit(output_text, (self.x + 20, self.y + 60))

        charge_text = self.font.render(f"Stored Energy: {int(self.generator.power)}%", True, (180, 180, 255))
        screen.blit(charge_text, (self.x + 20, self.y + 95))
