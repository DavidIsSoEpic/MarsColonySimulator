import pygame

class BuildingManager:
    def __init__(self, noise_map):
        self.noise_map = noise_map
        self.buildings = []  # list of tuples (gx, gy, size, color), size can be int or (w,h)
        self.resources = []  # list of ResourceDeposit objects (with .positions list of (x,y))
        self.base = None     # Base instance

    def set_resources(self, resources):
        self.resources = resources

    def set_base(self, base):
        self.base = base

    def get_interior_tiles(self, gx, gy, size):
        """Return set of interior tiles for a rectangular building at gx,gy of given size."""
        if isinstance(size, int):
            w = h = size
        else:
            w, h = size
        return {(x, y) for x in range(gx, gx + w) for y in range(gy, gy + h)}

    def get_outline_tiles(self, gx, gy, size):
        """Return set of outline (black border) tiles surrounding interior."""
        if isinstance(size, int):
            w = h = size
        else:
            w, h = size

        outline = set()
        for dx in range(-1, w + 1):
            for dy in range(-1, h + 1):
                if dx in (-1, w) or dy in (-1, h):
                    outline.add((gx + dx, gy + dy))
        return outline

    def get_base_interior_and_outline(self):
        """Return sets: (interior, outline) for the circular base."""
        interior = set()
        outline = set()
        if not self.base:
            return interior, outline

        r = self.base.radius
        cx = self.base.x
        cy = self.base.y
        r_sq = r * r
        r1_sq = (r + 1) * (r + 1)

        for dx in range(-r - 1, r + 2):
            for dy in range(-r - 1, r + 2):
                dist_sq = dx*dx + dy*dy
                tx, ty = cx + dx, cy + dy
                if dist_sq <= r_sq:
                    interior.add((tx, ty))
                elif r_sq < dist_sq <= r1_sq:
                    outline.add((tx, ty))
        return interior, outline

    def tiles_adjacent(self, tiles_a, tiles_b):
        """Return True if any tile in tiles_a is adjacent to any tile in tiles_b (Chebyshev distance 1)."""
        if not tiles_a or not tiles_b:
            return False
        neighbors = set()
        for bx, by in tiles_b:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbors.add((bx + dx, by + dy))
        return any(t in neighbors for t in tiles_a)

    def can_place(self, gx, gy, size=(4,4)):
        """Return True if a building at gx,gy of given size can be placed."""
        cols = len(self.noise_map[0])
        rows = len(self.noise_map)

        if isinstance(size, int):
            w = h = size
        else:
            w, h = size

        if gx < 0 or gy < 0 or gx + w > cols or gy + h > rows:
            return False

        new_interior = self.get_interior_tiles(gx, gy, size)
        new_outline = self.get_outline_tiles(gx, gy, size)

        # ---- Mountains: block both interior and outline ----
        for x, y in new_interior | new_outline:
            if self.noise_map[y][x] > 0.6:
                return False

        # ---- Resources: block interior AND outline ----
        for res in self.resources:
            for rx, ry in res.positions:
                if (rx, ry) in new_interior or (rx, ry) in new_outline:
                    return False

        # ---- Existing buildings: interior cannot overlap interiors; outline cannot overlap interiors ----
        for bx, by, bsize, _ in self.buildings:
            existing_interior = self.get_interior_tiles(bx, by, bsize)
            if new_interior & existing_interior:
                return False
            if new_outline & existing_interior:
                return False

        # ---- Base: interior cannot overlap, outline cannot overlap base interior ----
        base_interior, base_outline = self.get_base_interior_and_outline()
        if new_interior & base_interior:
            return False
        if new_outline & base_interior:
            return False

        # ---- Connection test: outline must touch base outline or existing building outline ----
        connected = False
        if self.tiles_adjacent(new_outline, base_outline):
            connected = True
        if not connected:
            for bx, by, bsize, _ in self.buildings:
                existing_outline = self.get_outline_tiles(bx, by, bsize)
                if self.tiles_adjacent(new_outline, existing_outline):
                    connected = True
                    break

        return connected

    def add_building(self, gx, gy, size=(4,4), color=(200, 200, 200)):
        if self.can_place(gx, gy, size):
            self.buildings.append((gx, gy, size, color))
            return True
        return False

    def draw(self, screen, tile_size):
        for gx, gy, size, color in self.buildings:
            if isinstance(size, int):
                w = h = size
            else:
                w, h = size

            # Draw interior
            for dy in range(h):
                for dx in range(w):
                    rect = pygame.Rect(
                        (gx + dx) * tile_size,
                        (gy + dy) * tile_size,
                        tile_size,
                        tile_size
                    )
                    pygame.draw.rect(screen, color, rect)

            # Draw black outline
            for dy in range(h + 2):
                for dx in range(w + 2):
                    if dx == 0 or dx == w + 1 or dy == 0 or dy == h + 1:
                        rect = pygame.Rect(
                            (gx - 1 + dx) * tile_size,
                            (gy - 1 + dy) * tile_size,
                            tile_size,
                            tile_size
                        )
                        pygame.draw.rect(screen, (0, 0, 0), rect)
