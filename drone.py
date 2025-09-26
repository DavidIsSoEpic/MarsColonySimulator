import pygame

class Drone:
    def __init__(self, x, y, speed=180, radius=12, color=(255, 105, 180)):
        self.x = x
        self.y = y
        self.target = None
        self.speed = speed  # pixels per second
        self.color = color
        self.radius = radius

    def set_target(self, pos):
        self.target = pos

    def move(self, noise_map, tile_size, cols, rows):
        # Simple flying movement (ignores terrain)
        if self.target:
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            dist = (dx**2 + dy**2)**0.5
            if dist < self.speed / 60:  # assuming 60 FPS
                self.x, self.y = self.target
                self.target = None
            else:
                self.x += dx / dist * self.speed / 60
                self.y += dy / dist * self.speed / 60

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        return (mx - self.x)**2 + (my - self.y)**2 <= self.radius**2
