import pygame
import random

class PowerGeneratorInventory:
    def __init__(self, generator, dashboard):
        self.generator = generator
        self.dashboard = dashboard
        self.width = 600
        self.height = 400
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 22, bold=True)

        # Close button
        self.close_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)

        # Flicker setup
        self.current_output = self.generator.output_base
        self.fluctuation_timer = 0.0
        self.fluctuation_interval = 0.3  # seconds

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return "close"
        return None

    def update(self, dt):
        # Update generator charge %
        self.generator.update_power(dt)

        # Update flicker timer
        self.fluctuation_timer += dt
        if self.fluctuation_timer >= self.fluctuation_interval:
            self.fluctuation_timer = 0.0
            self.current_output = random.uniform(2.4, 5.0)

        # Always update dashboard to reflect % charge
        self.dashboard.power = int(self.generator.power)

    def draw(self, screen):
        # Panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (30, 30, 30), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font_title.render("Solar Power Generator", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 20, self.y + 10))

        # Close X button
        pygame.draw.rect(screen, (255, 0, 0), self.close_rect)
        x_text = self.font_title.render("X", True, (255, 255, 255))
        screen.blit(x_text, (
            self.close_rect.x + (self.close_rect.width - x_text.get_width()) // 2,
            self.close_rect.y + (self.close_rect.height - x_text.get_height()) // 2
        ))

        # Power output
        output_text = self.font_text.render(f"Power Output: {self.current_output:.2f} W", True, (200, 255, 100))
        screen.blit(output_text, (self.x + 20, self.y + 70))

        # Charge %
        charge_text = self.font_text.render(f"Charge: {self.generator.power:.0f}%", True, (180, 180, 255))
        screen.blit(charge_text, (self.x + 20, self.y + 120))

        # Energy bar
        bar_width = self.width - 40
        bar_height = 30
        bar_x = self.x + 20
        bar_y = self.y + 160
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (self.generator.power / 100))
        pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, fill_width, bar_height))
