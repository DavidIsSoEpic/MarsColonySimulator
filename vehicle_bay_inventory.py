import pygame
import time

class VehicleBayInventory:
    def __init__(self, vehicle_bay, dashboard):
        self.vehicle_bay = vehicle_bay
        self.dashboard = dashboard
        self.width = 600
        self.height = 450
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.error_message = ""
        self.build_queue = []  # Optional future feature

        # Define buttons as (rect, label, action)
        self.buttons = [
            (pygame.Rect(self.x + 20, self.y + 50, self.width - 40, 50), "Buy Rover (2 Metal)", "buy_rover"),
            (pygame.Rect(self.x + 20, self.y + 120, self.width - 40, 50), "Buy Drone (3 Metal)", "buy_drone"),
            (pygame.Rect(self.x + 20, self.y + 190, self.width - 40, 50), "Close", "close")
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Check buttons
            for rect, label, action in self.buttons:
                if rect.collidepoint(mx, my) and action:
                    return action

        return None

    def update(self):
        now = time.time()
        finished = [v for v in self.build_queue if v[1] <= now]
        for v in finished:
            self.build_queue = [q for q in self.build_queue if q[1] > now]

    def draw(self, screen):
        # Panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font.render("Vehicle Bay", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 20, self.y + 10))

        # X button
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Draw buttons
        for rect, label, action in self.buttons:
            pygame.draw.rect(screen, (50, 50, 50), rect)
            btn_text = self.font.render(label, True, (200, 200, 200))
            screen.blit(btn_text, (rect.x + 10, rect.y + 10))

        # Build queue display
        queue_y = self.y + 260
        queue_title = self.font.render("Build Queue:", True, (200, 200, 255))
        screen.blit(queue_title, (self.x + 20, queue_y))
        queue_y += 30
        for v in self.build_queue:
            name, finish_time, build_time = v
            remaining = max(finish_time - time.time(), 0)
            remaining_rounds = int(remaining)
            text = self.font.render(f"{name} - {remaining_rounds} Rounds left", True, (255, 255, 255))
            screen.blit(text, (self.x + 25, queue_y))
            queue_y += 30

        # Error message at bottom
        if self.error_message:
            err_text = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_text, (self.x + 20, self.y + self.height - 40))
