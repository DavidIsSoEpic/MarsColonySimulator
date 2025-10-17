import pygame

class HousingInventory:
    def __init__(self, building, dashboard=None):
        self.building = building
        self.dashboard = dashboard
        self.width = 400
        self.height = 200
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.error_message = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Upgrade button
            upgrade_rect = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
            if upgrade_rect.collidepoint(mx, my):
                self.error_message = "Upgrade feature not implemented yet"
        return None

    def update(self):
        # Nothing dynamic for now
        pass

    def draw(self, screen):
        # Panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font.render("Housing Inventory", True, (255, 255, 255))
        screen.blit(title_text, (self.x + (self.width - title_text.get_width()) // 2, self.y + 10))

        # X button
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Housing info
        housing_capacity = getattr(self.building, "capacity", 10)
        current_occupants = getattr(self.building, "occupants", 5)
        lines = [
            f"Housing Space: {current_occupants}/{housing_capacity}"
        ]
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (255, 255, 255))
            screen.blit(txt, (self.x + 20, self.y + 50 + i * 30))

        # Upgrade button
        upgrade_rect = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
        pygame.draw.rect(screen, (0, 255, 0), upgrade_rect)
        upgrade_text = self.font.render("Upgrade", True, (255, 255, 255))
        screen.blit(upgrade_text, (upgrade_rect.x + (upgrade_rect.width - upgrade_text.get_width()) // 2,
                                   upgrade_rect.y + (upgrade_rect.height - upgrade_text.get_height()) // 2))

        # Error message
        if self.error_message:
            err_txt = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_txt, (self.x + (self.width - err_txt.get_width()) // 2,
                                  upgrade_rect.y - 35))
