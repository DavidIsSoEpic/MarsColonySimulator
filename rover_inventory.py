import pygame
import time

class RoverInventory:
    def __init__(self, rover):
        self.rover = rover
        self.width = 400
        self.height = 320
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.mining = False
        self.mining_start_time = None
        self.mine_interval = 10  # seconds per resource
        self.error_message = ""
        self.current_resource = None
        self.rover.storage = getattr(self.rover, 'storage', 0)
        self.rover.resources_held = {}  # e.g., {"Iron": 3}

    def handle_event(self, event, resources):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                # Cancel left click movement if held
                self.rover.awaiting_move_confirmation = False
                return "close"

            # Mine button
            mine_rect = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
            if mine_rect.collidepoint(mx, my):
                if self.rover.storage >= 5:
                    self.error_message = "Rover Storage is Full"
                    return None

                # Toggle mining
                if self.mining:
                    self.mining = False
                    self.error_message = ""
                    self.rover.mining_active = False
                else:
                    if self.resource_under_rover(resources):
                        self.mining = True
                        self.mining_start_time = time.time()
                        self.error_message = ""
                        self.rover.mining_active = True
                    else:
                        self.error_message = "No Resources to Mine"
        return None

    def resource_under_rover(self, resources):
        rover_rect = pygame.Rect(self.rover.x - self.rover.size//2, self.rover.y - self.rover.size//2,
                                 self.rover.size, self.rover.size)
        for res in resources:
            for x, y in res.positions:
                res_rect = pygame.Rect(x*10, y*10, 10, 10)
                if rover_rect.colliderect(res_rect):
                    self.current_resource = res
                    return True
        self.current_resource = None
        return False

    def update(self, dt, resources):
        """Update rover inventory; handle mining logic based on time."""
        self.resource_under_rover(resources)

        # Stop mining if storage full
        if self.rover.storage >= 5:
            self.mining = False
            self.error_message = "Rover Storage is Full"
            self.rover.mining_active = False
            return

        # Handle mining
        if self.mining and self.current_resource:
            now = time.time()
            elapsed = now - self.mining_start_time
            if elapsed >= self.mine_interval:
                self.rover.storage = min(self.rover.storage + 1, 5)
                res_type = self.current_resource.type
                self.rover.resources_held[res_type] = self.rover.resources_held.get(res_type, 0) + 1
                self.mining_start_time = now  # reset timer

            # Stop mining if rover moved off resource
            if not self.resource_under_rover(resources):
                self.mining = False
                self.error_message = "No Resources to Mine"
                self.rover.mining_active = False

    def draw(self, screen, resources):
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font.render("Rover Inventory", True, (255, 255, 255))
        screen.blit(title_text, (self.x + (self.width - title_text.get_width()) // 2, self.y + 10))

        # X button
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Rover Info
        lines = [
            f"Rover Type: Standard",
            f"Rover Power: {int(self.rover.power)}%",
            f"Resource Under: {self.current_resource.type if self.current_resource else 'None'}",
            f"Rover Storage: {getattr(self.rover, 'storage', 0)}/5"
        ]
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (255, 255, 255))
            screen.blit(txt, (self.x + 20, self.y + 50 + i * 30))

        # Display mined resources
        y_offset = self.y + 50 + len(lines)*30
        for res_type, count in self.rover.resources_held.items():
            txt = self.font.render(f"{res_type}: {count}x", True, (200, 200, 255))
            screen.blit(txt, (self.x + 40, y_offset))
            y_offset += 30

        # Mine Button
        mine_rect = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
        pygame.draw.rect(screen, (0, 255, 0) if not self.mining else (255, 0, 0), mine_rect)

        # Countdown
        if self.mining and self.current_resource:
            elapsed = int(time.time() - self.mining_start_time)
            countdown = max(self.mine_interval - elapsed, 0)
            mine_text = f"Mine {countdown}"
        else:
            mine_text = "Mine"

        txt = self.font.render(mine_text, True, (255, 255, 255))
        screen.blit(txt, (mine_rect.x + (mine_rect.width - txt.get_width()) // 2,
                          mine_rect.y + (mine_rect.height - txt.get_height()) // 2))

        # Error message above Mine button
        if self.error_message:
            err_txt = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_txt, (self.x + (self.width - err_txt.get_width()) // 2,
                                  mine_rect.y - 35))
