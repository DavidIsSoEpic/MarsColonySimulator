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

    def can_place(self, gx, gy, size=4):
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

        # Cannot overlap other buildings
        for bx, by, bsize, _ in self.buildings:
            if (gx < bx + bsize and gx + size > bx and
                gy < by + bsize and gy + size > by):
                return False

        # ---------------- Base connection logic ---------------- #
        # New building outline rect
        new_outline = pygame.Rect(gx - 1, gy - 1, size + 2, size + 2)

        # Home base must exist
        if self.base:
            # Only consider home base outer outline
            base_outline = pygame.Rect(
                self.base.x - self.base.radius - 1,
                self.base.y - self.base.radius - 1,
                self.base.radius * 2 + 2,
                self.base.radius * 2 + 2
            )

            # Build a rect for the base interior (white tiles)
            base_interior = pygame.Rect(
                self.base.x - self.base.radius,
                self.base.y - self.base.radius,
                self.base.radius * 2,
                self.base.radius * 2
            )

            # Must touch outer black border, not interior
            if new_outline.colliderect(base_outline) and not new_outline.colliderect(base_interior):
                return True

            # Must touch outline of another building
            for bx, by, bsize, _ in self.buildings:
                building_outline = pygame.Rect(bx - 1, by - 1, bsize + 2, bsize + 2)
                building_interior = pygame.Rect(bx, by, bsize, bsize)
                if new_outline.colliderect(building_outline) and not new_outline.colliderect(building_interior):
                    return True

            # If not touching any outlines, invalid
            return False

        # If no base exists yet, allow placement anywhere valid
        return True

    def add_building(self, gx, gy, size=4, color=(200, 200, 200)):
        if self.can_place(gx, gy, size):
            self.buildings.append((gx, gy, size, color))
            return True
        return False

    def draw(self, screen, tile_size):
        for gx, gy, size, color in self.buildings:
            # Draw interior
            for dy in range(size):
                for dx in range(size):
                    rect = pygame.Rect(
                        (gx + dx) * tile_size,
                        (gy + dy) * tile_size,
                        tile_size,
                        tile_size
                    )
                    pygame.draw.rect(screen, color, rect)

            # Draw outer black border
            for dy in range(size + 2):
                for dx in range(size + 2):
                    if dx == 0 or dx == size + 1 or dy == 0 or dy == size + 1:
                        rect = pygame.Rect(
                            (gx - 1 + dx) * tile_size,
                            (gy - 1 + dy) * tile_size,
                            tile_size,
                            tile_size
                        )
                        pygame.draw.rect(screen, (0, 0, 0), rect)
