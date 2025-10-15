import pygame

class PowerGenerator:
    def __init__(self, gx, gy, size=(4, 4)):
        """
        gx, gy: grid position (top-left corner of building)
        size: tuple (width, height) in tiles
        """
        self.gx = gx
        self.gy = gy
        self.size = size

        # Energy properties
        self.power = 25.0        # starts at 25%
        self.output_base = 2.4   # min Watts
        self.output_max = 3.0    # max Watts

        # For inventory display
        self.last_displayed_power = round(self.get_output(), 1)

    def draw(self, screen, tile_size):
        """
        Draws the generator on the map
        """
        rect = pygame.Rect(
            self.gx * tile_size,
            self.gy * tile_size,
            self.size[0] * tile_size,
            self.size[1] * tile_size
        )
        pygame.draw.rect(screen, (255, 255, 0), rect)  # yellow fill
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)  # white border

    def is_clicked(self, pos, tile_size=10):
        """
        Check if mouse click position (pixels) is inside this generator
        """
        rect = pygame.Rect(
            self.gx * tile_size,
            self.gy * tile_size,
            self.size[0] * tile_size,
            self.size[1] * tile_size
        )
        return rect.collidepoint(pos)

    def update_power(self, dt):
        """
        Gradually increases power over time (dt in seconds)
        1% every 3 seconds
        """
        self.power += (dt / 3)
        if self.power > 100:
            self.power = 100

    def get_output(self):
        """
        Returns the current output in Watts, scaled between base and max
        """
        output = self.output_base + (self.power / 100) * (self.output_max - self.output_base)
        return round(output, 1)  # rounded to 1 decimal for dashboard

# ------------------- Inventory for PowerGenerator -------------------

class PowerGeneratorInventory:
    def __init__(self, generator, dashboard):
        self.generator = generator
        self.dashboard = dashboard
        self.width = 200
        self.height = 100
        self.visible = False

    def update(self, dt):
        """
        Update the generator's power (even if inventory not visible)
        """
        self.generator.update_power(dt)
        self.generator.last_displayed_power = self.generator.get_output()

    def draw(self, screen):
        if not self.visible:
            return

        # Draw a simple inventory panel (matching other inventory style)
        rect = pygame.Rect(50, 50, self.width, self.height)
        pygame.draw.rect(screen, (50, 50, 50), rect)  # dark grey background
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)  # white border

        # Draw power info
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(f"Power Output: {self.generator.last_displayed_power} W", True, (255, 255, 255))
        screen.blit(text, (rect.x + 10, rect.y + 10))

        text2 = font.render(f"Charge: {int(self.generator.power)}%", True, (255, 255, 255))
        screen.blit(text2, (rect.x + 10, rect.y + 40))
