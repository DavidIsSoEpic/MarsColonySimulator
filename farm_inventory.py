import pygame

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

        # Farm options with stats
        self.farm_options = [
            {
                "name": "Grow Potatoes:",
                "stats": ["Generates 5 Food per Round", "Costs 2 Water per round"]
            },
            {
                "name": "Grow Carrots:",
                "stats": ["Generates 10 Food per Round", "Costs 5 Water per round"]
            },
            {
                "name": "Grow Tomatoes:",
                "stats": ["Generates 20 Food per Round", "Costs 10 Water per round"]
            },
        ]

        # Keep track of buttons for event handling
        self.grow_buttons = []
        self.upgrade_button = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Grow buttons
            for i, rect in enumerate(self.grow_buttons):
                if rect.collidepoint(mx, my):
                    self.error_message = f"{self.farm_options[i]['name']} Grow feature not implemented yet"

            # Upgrade button
            if self.upgrade_button and self.upgrade_button.collidepoint(mx, my):
                self.error_message = "Upgrade feature not implemented yet"

        return None

    def update(self):
        pass

    def wrap_text(self, text, max_width):
        """Split text into lines that fit max_width"""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, screen):
        # Panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
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

        # Draw farm options in columns
        num_options = len(self.farm_options)
        column_width = self.width // num_options
        self.grow_buttons = []
        for i, option in enumerate(self.farm_options):
            col_x = self.x + i * column_width + 10
            col_y = self.y + 60

            # Option name
            name_lines = self.wrap_text(option["name"], column_width - 20)
            for line in name_lines:
                txt = self.font.render(line, True, (255, 255, 255))
                screen.blit(txt, (col_x, col_y))
                col_y += self.line_spacing

            # Option stats
            for stat in option["stats"]:
                stat_lines = self.wrap_text(stat, column_width - 20)
                for line in stat_lines:
                    txt = self.font.render(line, True, (200, 255, 200))
                    screen.blit(txt, (col_x, col_y))
                    col_y += self.line_spacing

            # Grow button under this column
            grow_rect = pygame.Rect(col_x, col_y + 5, column_width - 20, 40)
            pygame.draw.rect(screen, (0, 200, 0), grow_rect)
            grow_text = self.font.render("Grow", True, (255, 255, 255))
            screen.blit(grow_text, (grow_rect.x + (grow_rect.width - grow_text.get_width()) // 2,
                                    grow_rect.y + (grow_rect.height - grow_text.get_height()) // 2))
            self.grow_buttons.append(grow_rect)

        # Upgrade button at the bottom of panel
        self.upgrade_button = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
        pygame.draw.rect(screen, (0, 150, 255), self.upgrade_button)
        upgrade_text = self.font.render("Upgrade", True, (255, 255, 255))
        screen.blit(upgrade_text, (self.upgrade_button.x + (self.upgrade_button.width - upgrade_text.get_width()) // 2,
                                   self.upgrade_button.y + (self.upgrade_button.height - upgrade_text.get_height()) // 2))

        # Error message
        if self.error_message:
            err_txt = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_txt, (self.x + (self.width - err_txt.get_width()) // 2,
                                  self.upgrade_button.y - 35))
