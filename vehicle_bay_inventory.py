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
        self.build_queue = []
        self.rover_cost = 5
        self.drone_cost = 10

    def handle_event(self, event):
        """Returns one of: 'buy_rover', 'buy_drone', 'close', or None"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button (close)
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Buttons
            rover_btn = pygame.Rect(self.x + 20, self.y + 60, self.width - 40, 50)
            drone_btn = pygame.Rect(self.x + 20, self.y + 130, self.width - 40, 50)

            if rover_btn.collidepoint(mx, my):
                return "buy_rover"

            if drone_btn.collidepoint(mx, my):
                return "buy_drone"

        return None

    def update(self):
        now = time.time()
        finished = [v for v in self.build_queue if v[1] <= now]
        for v in finished:
            self.build_queue = [q for q in self.build_queue if q[1] > now]

    def draw(self, screen):
        # Panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (20, 20, 20), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font.render("Vehicle Bay", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 20, self.y + 10))

        # Close button (X)
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (
            x_rect.x + (x_rect.width - x_text.get_width()) // 2,
            x_rect.y + (x_rect.height - x_text.get_height()) // 2
        ))

        # Rover Button
        rover_btn = pygame.Rect(self.x + 20, self.y + 60, self.width - 40, 50)
        pygame.draw.rect(screen, (60, 60, 60), rover_btn)
        rover_text = self.font.render(f"Purchase Rover - {self.rover_cost} Metal", True, (200, 200, 200))
        screen.blit(rover_text, (rover_btn.x + 15, rover_btn.y + 12))

        # Drone Button
        drone_btn = pygame.Rect(self.x + 20, self.y + 130, self.width - 40, 50)
        pygame.draw.rect(screen, (60, 60, 60), drone_btn)
        drone_text = self.font.render(f"Purchase Drone - {self.drone_cost} Metal", True, (200, 200, 200))
        screen.blit(drone_text, (drone_btn.x + 15, drone_btn.y + 12))

        # Current metals display
        metals_text = self.font.render(f"Available Metal: {getattr(self.dashboard, 'metals', 0)}", True, (180, 180, 255))
        screen.blit(metals_text, (self.x + 20, self.y + 210))

        # Error message (if used)
        if self.error_message:
            err_text = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_text, (self.x + 20, self.y + self.height - 40))
