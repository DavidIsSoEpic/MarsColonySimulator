import pygame
import time

class RoverInventory:
    def __init__(self, rover, building_manager=None, dashboard=None, units_list=None):
        self.rover = rover
        self.building_manager = building_manager
        self.dashboard = dashboard
        self.units_list = units_list

        # Window layout
        self.width = 400
        self.height = 400
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        # State
        self.mining = False
        self.mining_start_time = None
        self.mine_interval = 10
        self.error_message = ""
        self.current_resource = None

        # Rover stats
        self.rover.storage = getattr(self.rover, "storage", 0)
        self.rover.storage_capacity = 5
        self.rover.resources_held = getattr(self.rover, "resources_held", {})

        # Move limiter
        self.rover.move_count = getattr(self.rover, 'move_count', 0)
        self.rover.max_moves = 2  # Limit moves per round

    # -----------------------------
    # Handle clicks
    # -----------------------------
    def handle_event(self, event, resources):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Mine button
            mine_rect = pygame.Rect(self.x + 50, self.y + self.height - 110, self.width - 100, 45)
            if mine_rect.collidepoint(mx, my):
                if self.rover.storage >= self.rover.storage_capacity:
                    self.error_message = "Rover Storage is Full"
                    return None

                if self.mining:
                    self.mining = False
                    self.error_message = ""
                    self.rover.mining_active = False
                else:
                    res = self.resource_under_rover(resources)
                    if res:
                        self.mining = True
                        self.mining_start_time = time.time()
                        self.error_message = ""
                        self.rover.mining_active = True
                        self.current_resource = res
                    else:
                        self.error_message = "No Resources to Mine"

            # Refine button (always visible)
            refine_rect = pygame.Rect(self.x + 50, self.y + self.height - 55, self.width - 100, 45)
            if refine_rect.collidepoint(mx, my):
                if self.is_over_vehicle_bay():
                    self.refine_resources()
                else:
                    self.error_message = "Must be over Vehicle Bay to refine"

        return None

    # -----------------------------
    # Check resource under rover
    # -----------------------------
    def resource_under_rover(self, resources):
        rover_rect = pygame.Rect(self.rover.x - 10, self.rover.y - 10, 20, 20)
        for res in resources:
            for x, y in res.positions:
                res_rect = pygame.Rect(x * 10, y * 10, 10, 10)
                if rover_rect.colliderect(res_rect):
                    self.current_resource = res
                    return res
        self.current_resource = None
        return None

    # -----------------------------
    # Check if over Vehicle Bay
    # -----------------------------
    def is_over_vehicle_bay(self):
        if self.building_manager is None:
            return False
        gx = int(self.rover.x // 10)
        gy = int(self.rover.y // 10)
        for b in self.building_manager.buildings:
            if b["type"] == "Vehicle Bay":
                bx, by = b["gx"], b["gy"]
                bw, bh = b["size"]
                if bx <= gx < bx + bw and by <= gy < by + bh:
                    return True
        return False

    # -----------------------------
    # Update logic
    # -----------------------------
    def update(self, dt, resources):
        self.resource_under_rover(resources)

        if self.rover.storage >= self.rover.storage_capacity:
            self.mining = False
            self.rover.mining_active = False
            self.error_message = "Rover Storage is Full"
            return

        if self.mining and self.current_resource:
            now = time.time()
            elapsed = now - self.mining_start_time
            if elapsed >= self.mine_interval:
                remaining_space = self.rover.storage_capacity - self.rover.storage
                if remaining_space > 0:
                    self.rover.storage += 1
                    res_type = self.current_resource.type.lower()
                    self.rover.resources_held[res_type] = min(
                        self.rover.resources_held.get(res_type, 0) + 1,
                        self.rover.storage_capacity
                    )
                self.mining_start_time = time.time()

            if not self.resource_under_rover(resources):
                self.mining = False
                self.rover.mining_active = False
                self.error_message = "No Resources to Mine"

    # -----------------------------
    # Apply +2 mining per round & reset moves
    # -----------------------------
    def apply_next_round_mining(self):
        # Reset moves each round
        self.rover.move_count = 0

        if self.mining and self.current_resource:
            gain = 2
            remaining_space = self.rover.storage_capacity - self.rover.storage
            gain = min(gain, remaining_space)
            if gain > 0:
                self.rover.storage += gain
                res_type = self.current_resource.type.lower()
                self.rover.resources_held[res_type] = min(
                    self.rover.resources_held.get(res_type, 0) + gain,
                    self.rover.storage_capacity
                )

    # -----------------------------
    # Refine Resources (Vehicle Bay)
    # -----------------------------
    def refine_resources(self):
        if not self.is_over_vehicle_bay() or not self.dashboard:
            self.error_message = "Must be over Vehicle Bay to refine"
            return

        for res_type, amount in self.rover.resources_held.items():
            key = res_type.lower()
            if key == "iron":
                self.dashboard.metals += amount
            elif key == "ice":
                self.dashboard.water += amount
            elif key == "marsium":
                self.dashboard.marsium += amount

        self.rover.resources_held = {}
        self.rover.storage = 0
        self.error_message = "Resources Refined!"

    # -----------------------------
    # Draw UI
    # -----------------------------
    def draw(self, screen, resources):
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        title_text = self.font.render("Rover Inventory", True, (255, 255, 255))
        screen.blit(title_text, (self.x + (self.width - title_text.get_width()) // 2, self.y + 10))

        # X button
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Rover info
        lines = [
            f"Rover Type: Standard",
            f"Rover Battery: {self.rover.power:.0f}%",
            f"Resource Under: {self.current_resource.type if self.current_resource else 'None'}",
            f"Moves Left: {self.rover.max_moves - self.rover.move_count}/{self.rover.max_moves}",
            f"Rover Storage: {self.rover.storage}/{self.rover.storage_capacity}"

        ]
        for i, line in enumerate(lines):
            txt = self.font.render(line, True, (255, 255, 255))
            screen.blit(txt, (self.x + 20, self.y + 50 + i * 28))

        # Held resources
        if self.rover.resources_held:
            y_offset = self.y + 50 + len(lines)*28 + 5
            for res_type, amt in self.rover.resources_held.items():
                txt = self.font.render(f"+{amt} {res_type.capitalize()}", True, (0, 255, 0))
                screen.blit(txt, (self.x + 40, y_offset))
                y_offset += 28

        # Mine button
        mine_rect = pygame.Rect(self.x + 50, self.y + self.height - 110, self.width - 100, 45)
        pygame.draw.rect(screen, (0, 255, 0) if not self.mining else (255, 0, 0), mine_rect)
        mine_text = "Mine" if not self.mining else "Stop Mining"
        txt = self.font.render(mine_text, True, (255, 255, 255))
        screen.blit(txt, (mine_rect.x + (mine_rect.width - txt.get_width()) // 2,
                          mine_rect.y + (mine_rect.height - txt.get_height()) // 2))

        # Refine button (always visible)
        refine_rect = pygame.Rect(self.x + 50, self.y + self.height - 55, self.width - 100, 45)
        pygame.draw.rect(screen, (100, 200, 255), refine_rect)
        txt = self.font.render("Refine", True, (0, 0, 0))
        screen.blit(txt, (refine_rect.x + (refine_rect.width - txt.get_width()) // 2,
                          refine_rect.y + (refine_rect.height - txt.get_height()) // 2))

        # Error message
        if self.error_message:
            err_txt = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_txt, (self.x + (self.width - err_txt.get_width()) // 2,
                                  self.y + self.height - 160))
