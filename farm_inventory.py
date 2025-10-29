import pygame
import math

class FarmInventory:
    def __init__(self, building, dashboard=None):
        self.building = building
        self.dashboard = dashboard
        self.width = 600
        self.height = 350
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.line_spacing = 24
        self.error_message = ""

        # --- Farm state ---
        self.is_growing = False
        self.level = 1
        self.food_gain = 5
        self.water_cost = 2

        # Buttons
        self.grow_button = None
        self.upgrade_button = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Close button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Grow button
            if self.grow_button and self.grow_button.collidepoint(mx, my):
                if not self.is_growing:
                    self.is_growing = True
                    self.error_message = "Growing..."
                else:
                    self.is_growing = False
                    self.error_message = "Stopped growing"

            # Upgrade button
            if self.upgrade_button and self.upgrade_button.collidepoint(mx, my):
                if self.dashboard and self.dashboard.metals >= 4 and self.dashboard.marsium >= 1:
                    self.dashboard.metals -= 4
                    self.dashboard.marsium -= 1
                    self.level += 1

                    # Boost stats
                    self.food_gain = math.ceil(self.food_gain * 1.25)
                    self.water_cost += 2
                    self.error_message = f"Farm upgraded to Level {self.level}!"
                else:
                    self.error_message = "Not enough resources to upgrade!"

        return None

    def update(self):
        # nothing per frame yet
        pass

    def apply_next_round(self):
        """Called each new round to apply farm production and costs."""
        if self.is_growing and self.dashboard:
            # Only produce if there’s enough water
            if self.dashboard.water >= self.water_cost:
                self.dashboard.water -= self.water_cost
                self.dashboard.food += self.food_gain
                self.error_message = f"+{self.food_gain} Food, -{self.water_cost} Water"
            else:
                self.error_message = "Not enough Water!"
                self.is_growing = False  # stop growing if can’t afford

    def draw(self, screen):
        # Panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (10, 10, 10), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font.render("Farm Inventory", True, (255, 255, 255))
        screen.blit(title_text, (self.x + (self.width - title_text.get_width()) // 2, self.y + 10))

        # X button
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Level and crop info
        col_x = self.x + 40
        col_y = self.y + 70

        lvl_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        screen.blit(lvl_text, (col_x, col_y))
        col_y += self.line_spacing

        name_text = self.font.render("Crop: Potatoes", True, (255, 255, 0))
        screen.blit(name_text, (col_x, col_y))
        col_y += self.line_spacing

        stat_text1 = self.font.render(f"Produces: +{self.food_gain} Food / Round", True, (200, 255, 200))
        stat_text2 = self.font.render(f"Uses: -{self.water_cost} Water / Round", True, (200, 200, 255))
        screen.blit(stat_text1, (col_x, col_y)); col_y += self.line_spacing
        screen.blit(stat_text2, (col_x, col_y)); col_y += self.line_spacing * 2

        # Grow button
        self.grow_button = pygame.Rect(col_x, col_y, self.width - 80, 45)
        pygame.draw.rect(screen, (0, 200, 0) if not self.is_growing else (200, 50, 50), self.grow_button)
        grow_text = "Grow" if not self.is_growing else "Growing..."
        g_text = self.font.render(grow_text, True, (255, 255, 255))
        screen.blit(g_text, (self.grow_button.x + (self.grow_button.width - g_text.get_width()) // 2,
                             self.grow_button.y + (self.grow_button.height - g_text.get_height()) // 2))
        col_y += 70

        # Upgrade button
        self.upgrade_button = pygame.Rect(col_x, col_y, self.width - 80, 45)
        pygame.draw.rect(screen, (0, 150, 255), self.upgrade_button)
        up_text = self.font.render("Upgrade (1 Marsium, 4 Metal)", True, (255, 255, 255))
        screen.blit(up_text, (self.upgrade_button.x + (self.upgrade_button.width - up_text.get_width()) // 2,
                              self.upgrade_button.y + (self.upgrade_button.height - up_text.get_height()) // 2))

        # Error message
        if self.error_message:
            err_txt = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_txt, (self.x + (self.width - err_txt.get_width()) // 2,
                                  self.upgrade_button.y + 60))
