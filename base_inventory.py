import pygame
import time

class BaseInventory:
    def __init__(self, base, dashboard):
        self.base = base
        self.dashboard = dashboard
        self.width = 600  # wider menu
        self.height = 450
        self.x = (1280 - self.width) // 2
        self.y = (720 - self.height) // 2
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.error_message = ""
        self.build_queue = []  # list of tuples (building_name, finish_time, build_time)
        self.buildings = [
            {"name": "Housing", "cost": {"metals": 5}, "build_time": 1},
            {"name": "Farm", "cost": {"metals": 3}, "build_time": 2},
            {"name": "Power Generator", "cost": {"metals": 4}, "build_time": 3},
            {"name": "Factory", "cost": {"metals": 6}, "build_time": 4},
            {"name": "Vehicle Bay", "cost": {"metals": 5}, "build_time": 3},
            {"name": "Home Base", "cost": {"metals": 10}, "build_time": 5},
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # X button
            x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
            if x_rect.collidepoint(mx, my):
                return "close"

            # Check clicks on building buttons
            for i, b in enumerate(self.buildings):
                btn_rect = pygame.Rect(self.x + 20, self.y + 50 + i*50, self.width - 40, 40)
                if btn_rect.collidepoint(mx, my):
                    # Check resources
                    can_build = True
                    for res, amt in b["cost"].items():
                        if getattr(self.dashboard, res, 0) < amt:
                            can_build = False
                            break
                    if can_build:
                        finish_time = time.time() + b["build_time"] * 1  # each build_time unit = 1 second/round
                        self.build_queue.append((b["name"], finish_time, b["build_time"]))
                        # Deduct resources
                        for res, amt in b["cost"].items():
                            setattr(self.dashboard, res, getattr(self.dashboard, res) - amt)
                        self.error_message = ""
                    else:
                        self.error_message = "Not enough resources"
        return None

    def update(self):
        now = time.time()
        finished = [b for b in self.build_queue if b[1] <= now]
        for b in finished:
            # Apply building effects
            if b[0] == "Housing":
                self.dashboard.population += 5
            elif b[0] == "Farm":
                self.dashboard.food += 5
            elif b[0] == "Power Generator":
                self.dashboard.power += 5
            # Remove finished buildings from queue
            self.build_queue = [q for q in self.build_queue if q[1] > now]

    def draw(self, screen):
        # Panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

        # Title
        title_text = self.font.render("Base Build Menu", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 20, self.y + 10))  # left-aligned

        # X button (top-right)
        x_rect = pygame.Rect(self.x + self.width - 35, self.y + 5, 30, 30)
        pygame.draw.rect(screen, (255, 0, 0), x_rect)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (x_rect.x + (x_rect.width - x_text.get_width()) // 2,
                             x_rect.y + (x_rect.height - x_text.get_height()) // 2))

        # Draw building list
        for i, b in enumerate(self.buildings):
            btn_rect = pygame.Rect(self.x + 20, self.y + 50 + i * 50, self.width - 40, 40)
            pygame.draw.rect(screen, (50, 50, 50), btn_rect)

            # Format cost nicely
            cost_str = ', '.join(f"{amt} {res.capitalize()}" for res, amt in b["cost"].items())

            # Format time
            time_str = "INSTANT" if b["build_time"] <= 1 else f"{b['build_time']} Rounds"

            # Render text left-to-right
            name_text = self.font.render(f"{b['name']} - {cost_str} - Time: {time_str}", True, (255, 255, 255))
            screen.blit(name_text, (btn_rect.x + 10, btn_rect.y + 8))

        # Draw build queue below
        queue_y = self.y + 50 + len(self.buildings) * 50 + 10
        queue_title = self.font.render("Build Queue:", True, (200, 200, 255))
        screen.blit(queue_title, (self.x + 20, queue_y))
        queue_y += 30

        now = time.time()
        for b in self.build_queue:
            name, finish_time, build_time = b
            remaining = max(finish_time - now, 0)
            remaining_rounds = int(remaining)
            progress = 1 - (remaining / build_time)
            progress = max(0, min(progress, 1))

            # Progress bar
            bar_width = self.width - 40
            bar_height = 20
            bar_rect = pygame.Rect(self.x + 20, queue_y, bar_width, bar_height)
            pygame.draw.rect(screen, (100, 100, 100), bar_rect)
            inner_rect = pygame.Rect(self.x + 20, queue_y, int(bar_width * progress), bar_height)
            pygame.draw.rect(screen, (0, 200, 0), inner_rect)

            # Text
            text = self.font.render(f"{name} - {remaining_rounds} Rounds left", True, (255, 255, 255))
            text_y = queue_y + (bar_height - text.get_height()) // 2
            screen.blit(text, (self.x + 25, text_y))

            queue_y += bar_height + 10

        # Error message at bottom-left
        if self.error_message:
            err_text = self.font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_text, (self.x + 20, self.y + self.height - 40))
