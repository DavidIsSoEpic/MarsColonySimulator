import pygame

class BuildingManager:
    def __init__(self, noise_map):
        self.noise_map = noise_map
        self.buildings = []
        self.resources = []
        self.base = None

    def set_resources(self, resources):
        self.resources = resources

    def set_base(self, base):
        self.base = base

    def can_place(self, gx, gy, size=3):
        # Bounds check
        if gx < 0 or gy < 0 or gx + size > len(self.noise_map[0]) or gy + size > len(self.noise_map):
            return False

        # Cannot place on mountains
        for x in range(gx, gx + size):
            for y in range(gy, gy + size):
                if self.noise_map[y][x] > 0.6:  # mountain threshold
                    return False

        # Cannot overlap resources
        for res in self.resources:
            for (rx, ry) in res.positions:
                if gx <= rx < gx + size and gy <= ry < gy + size:
                    return False

        # Cannot overlap base (including its outline)
        if self.base:
            base_rect = pygame.Rect(
                (self.base.x - self.base.radius - 1), 
                (self.base.y - self.base.radius - 1),
                (self.base.radius * 2 + 2),
                (self.base.radius * 2 + 2)
            )
            new_building_rect = pygame.Rect(gx, gy, size, size)
            if base_rect.colliderect(new_building_rect):
                return False

        # Cannot overlap other buildings
        for bx, by, bsize, _ in self.buildings:
            if (gx < bx + bsize and gx + size > bx and
                gy < by + bsize and gy + size > by):
                return False

        return True

    def add_building(self, gx, gy, size=3, color=(0, 200, 0)):
        if self.can_place(gx, gy, size):
            self.buildings.append((gx, gy, size, color))
            return True
        return False

    def draw(self, screen, tile_size):
        for gx, gy, size, color in self.buildings:
            # Draw each tile of the building
            for dy in range(size):
                for dx in range(size):
                    rect = pygame.Rect(
                        (gx + dx) * tile_size,
                        (gy + dy) * tile_size,
                        tile_size,
                        tile_size
                    )
                    pygame.draw.rect(screen, color, rect)

            # Draw exterior outline like the base
            outline_rect = pygame.Rect(
                gx * tile_size,
                gy * tile_size,
                size * tile_size,
                size * tile_size
            )
            pygame.draw.rect(screen, (0, 0, 0), outline_rect, 2)
