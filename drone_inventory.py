import pygame
import time

class DroneInventory:
    def __init__(self, drone):
        self.drone = drone
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
        self.drone.storage = getattr(self.drone, 'storage', 0)
        self.drone.resources_held = {}  # e.g., {"Iron": 3}

    def handle_event(self, event, resources):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Mine button
            mine_rect = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
            if mine_rect.collidepoint(mx, my):
                if self.drone.storage >= 5:
                    self.error_message = "Drone Storage is Full"
                    return None

                if self.mining:
                    self.mining = False
                    self.error_message = ""
                    self.drone.mining_active = False
                else:
                    if self.resource_under_drone(resources):
                        self.mining = True
                        self.mining_start_time = time.time()
                        self.error_message = ""
                        self.drone.mining_active = True
                    else:
                        self.error_message = "No Resources to Mine"
        return None

    def resource_under_drone(self, resources):
        drone_rect = pygame.Rect(self.drone.x - self.drone.radius, self.drone.y - self.drone.radius,
                                 self.drone.radius*2, self.drone.radius*2)
        for res in resources:
            for x, y in res.positions:
                res_rect = pygame.Rect(x*10, y*10, 10, 10)
                if drone_rect.colliderect(res_rect):
                    self.current_resource = res
                    return True
        self.current_resource = None
        return False

    def update(self, resources):
        self.resource_under_drone(resources)

        if self.drone.storage >= 5:
            self.mining = False
            self.error_message = "Drone Storage is Full"
            self.drone.mining_active = False
            return

        if self.mining and self.current_resource:
            now = time.time()
            elapsed = now - self.mining_start_time
            if elapsed >= self.mine_interval:
                self.drone.storage = min(self.drone.storage + 1, 5)
                res_type = self.current_resource.type
                if res_type not in self.drone.resources_held:
                    self.drone.resources_held[res_type] = 0
                self.drone.resources_held[res_type] += 1
                self.mining_start_time = time.time()

            if not self.resource_under_drone(resources):
                self.mining = False
                self.error_message = "No Resources to Mine"
                self.drone.mining_active = False

    def draw(self, screen, resources):
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        title_text = self.font.render("Drone Inventory", True, (255, 255, 255))
        screen.blit(title_text, (self.x + (self.width - title_text.get_width()) // 2, self.y + 10))

        # X button
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Drone Info
        lines = [
            f"Drone Type: Standard",
            f"Drone Speed: {self.drone.speed}",
            f"Resource Under: {self.current_resource.type if self.current_resource else 'None'}",
            f"Drone Storage: {getattr(self.drone, 'storage', 0)}/5"
        ]
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (255, 255, 255))
            screen.blit(txt, (self.x + 20, self.y + 50 + i * 30))

        y_offset = self.y + 50 + len(lines)*30
        for res_type, count in self.drone.resources_held.items():
            txt = self.font.render(f"{res_type}: {count}x", True, (200, 200, 255))
            screen.blit(txt, (self.x + 40, y_offset))
            y_offset += 30

        mine_rect = pygame.Rect(self.x + 50, self.y + self.height - 70, self.width - 100, 50)
        pygame.draw.rect(screen, (0, 255, 0) if not self.mining else (255, 0, 0), mine_rect)

        if self.mining and self.current_resource:
            elapsed = int(time.time() - self.mining_start_time)
            countdown = max(self.mine_interval - elapsed, 0)
            mine_text = f"Mine {countdown}"
        else:
            mine_text = "Mine"

        txt = self.font.render(mine_text, True, (255, 255, 255))
        screen.blit(txt, (mine_rect.x + (mine_rect.width - txt.get_width()) // 2,
                          mine_rect.y + (mine_rect.height - txt.get_height()) // 2))

        if self.error_message:
            err_txt = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_txt, (self.x + (self.width - err_txt.get_width()) // 2,
                                  mine_rect.y - 35))
