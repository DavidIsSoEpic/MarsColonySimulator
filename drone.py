import pygame

class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target = None
        self.speed = 100  # pixels per second
        self.storage = 0

        # Add attributes to behave like Rover
        self.mining_active = False
        self.awaiting_move_confirmation = False

        # Restore radius and color for inventory compatibility and visuals
        self.radius = 10  # matches previous visuals
        self.color = (255, 255, 0)  # original drone color

    def set_target(self, pos):
        self.target = pos

    def move(self, noise_map, tile_size, cols, rows):
        if self.target:
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            dist = (dx**2 + dy**2)**0.5
            if dist < 1:
                self.target = None
            else:
                step = self.speed / 60  # assuming 60 FPS
                self.x += dx/dist * step
                self.y += dy/dist * step

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_clicked(self, pos):
        mx, my = pos
        return (self.x - mx)**2 + (self.y - my)**2 <= self.radius**2
