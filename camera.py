# camera.py
import pygame

class Camera:
    def __init__(self, width, height, world_width, world_height):
        """
        Camera for top-down 2D world.

        width, height: screen size in pixels
        world_width, world_height: world size in pixels
        """
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height

        self.x = 0
        self.y = 0
        self.speed = 500  # pixels per second

        # Middle-mouse dragging
        self.dragging = False
        self.last_mouse_pos = (0, 0)

    def apply(self, rect):
        """
        Apply camera offset to a rect for drawing on screen.
        """
        return rect.move(-self.x, -self.y)

    def center_on(self, world_x, world_y):
        """
        Center the camera on a world position (world_x, world_y).
        """
        self.x = int(world_x - self.width // 2)
        self.y = int(world_y - self.height // 2)
        self.clamp()

    def move(self, dx, dy, dt):
        """
        Move camera manually by dx, dy (pixels/sec) with delta time.
        """
        self.x += dx * dt
        self.y += dy * dt
        self.clamp()

    def clamp(self):
        """
        Keep the camera inside the world bounds.
        """
        self.x = max(0, min(self.x, self.world_width - self.width))
        self.y = max(0, min(self.y, self.world_height - self.height))

    def handle_input(self, keys, dt):
        """
        Move camera with arrow keys or WASD.
        """
        # Inside handle_input
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
        if dx != 0 or dy != 0:
            self.move(dx, dy, dt)


    def handle_event(self, event):
        """
        Handle middle-mouse dragging events.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Middle mouse
            self.dragging = True
            self.last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.last_mouse_pos[0]
            dy = event.pos[1] - self.last_mouse_pos[1]
            # invert drag to match typical map movement
            self.x -= dx
            self.y -= dy
            self.clamp()
            self.last_mouse_pos = event.pos
