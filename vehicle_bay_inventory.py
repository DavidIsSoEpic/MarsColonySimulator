import pygame
import time
from rover import Rover
from drone import Drone

class VehicleBayInventory:
    def __init__(self, vehicle_bay, dashboard, game_units):
        self.vehicle_bay = vehicle_bay
        self.dashboard = dashboard
        self.units = game_units  # list to append newly purchased units
        self.width = 600
        self.height = 450
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.error_message = ""
        self.build_queue = []

    def handle_event(self, event, units=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Buttons to spawn vehicles
            # Example: button rectangles
            rover_btn = pygame.Rect(self.x + 20, self.y + 50, self.width - 40, 50)
            drone_btn = pygame.Rect(self.x + 20, self.y + 120, self.width - 40, 50)

            if rover_btn.collidepoint(mx, my):
                # spawn rover inside vehicle bay
                spawn_x = self.vehicle_bay["gx"] * 10 + 20
                spawn_y = self.vehicle_bay["gy"] * 10 + 20
                new_rover = Rover(spawn_x, spawn_y)
                new_rover.storage = 0
                new_rover.mining_active = False
                new_rover.awaiting_move_confirmation = False
                units.append(new_rover)
                return "close"

            if drone_btn.collidepoint(mx, my):
                spawn_x = self.vehicle_bay["gx"] * 10 + 20
                spawn_y = self.vehicle_bay["gy"] * 10 + 20
                new_drone = Drone(spawn_x, spawn_y)
                units.append(new_drone)
                return "close"

        return None

    def update(self):
        now = time.time()
        finished = [v for v in self.build_queue if v[1] <= now]
        for v in finished:
            self.build_queue = [q for q in self.build_queue if q[1] > now]

    def draw(self, screen):
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        title_text = self.font.render("Vehicle Bay", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 20, self.y + 10))

        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Buttons
        rover_btn = pygame.Rect(self.x + 20, self.y + 50, self.width - 40, 50)
        drone_btn = pygame.Rect(self.x + 20, self.y + 120, self.width - 40, 50)

        pygame.draw.rect(screen, (50,50,50), rover_btn)
        pygame.draw.rect(screen, (50,50,50), drone_btn)

        rover_text = self.font.render("Purchase Rover", True, (200,200,200))
        drone_text = self.font.render("Purchase Drone", True, (200,200,200))
        screen.blit(rover_text, (rover_btn.x + 10, rover_btn.y + 10))
        screen.blit(drone_text, (drone_btn.x + 10, drone_btn.y + 10))

        # Error message
        if self.error_message:
            err_text = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_text, (self.x + 20, self.y + self.height - 40))
