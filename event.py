import pygame
import random

class EventManager:
    def __init__(self, dashboard, width, height):
        self.dashboard = dashboard
        self.width = width
        self.height = height
        self.active_event = None
        self.timer = random.randint(5, 20)  # seconds until next event
        self.counter = 0
        self.duration_frames = 120  # frames to display event (~2 sec at 60 FPS)

        # Simple event: Dust Storm
        self.events = [
            {
                "title": "!! WARNING !!",
                "description": ["Dust Storm Incoming!", "-5 Energy"],
                "effect": lambda: self.dashboard.update_metrics(
                    power=max(self.dashboard.power - 5, 0)
                )
            }
        ]
        self.frames_left = 0

    def update(self, dt):
        if not self.active_event:
            self.counter += dt
            if self.counter >= self.timer:
                self.trigger_event()
        else:
            self.frames_left -= 1
            if self.frames_left <= 0:
                self.active_event = None
                self.counter = 0
                self.timer = random.randint(5, 20)

    def trigger_event(self):
        self.active_event = random.choice(self.events)
        self.active_event["effect"]()
        self.frames_left = self.duration_frames

    def draw(self, screen):
        if self.active_event:
            font = pygame.font.SysFont(None, 40, bold=True)  # simple system font
            all_lines = [line for line in [self.active_event["title"]] + self.active_event["description"] if line]

            total_height = len(all_lines) * 50
            start_y = (self.height - total_height) // 2

            for i, line in enumerate(all_lines):
                text_surface = font.render(line, True, (255, 0, 0))
                # Draw black outline
                for dx in [-2, 0, 2]:
                    for dy in [-2, 0, 2]:
                        if dx != 0 or dy != 0:
                            outline = font.render(line, True, (0, 0, 0))
                            screen.blit(outline, (self.width // 2 - text_surface.get_width() // 2 + dx,
                                                  start_y + i * 50 + dy))
                screen.blit(text_surface, (self.width // 2 - text_surface.get_width() // 2,
                                           start_y + i * 50))
