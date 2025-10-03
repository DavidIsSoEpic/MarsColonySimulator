import pygame

class BuildingManager:
    def __init__(self, noise_map):
        self.noise_map = noise_map
        self.buildings = []  # list of tuples (gx, gy, size, color)
        self.resources = []  # list of ResourceDeposit objects (with .positions list of (x,y))
        self.base = None     # Base instance

    def set_resources(self, resources):
        self.resources = resources

    def set_base(self, base):
        self.base = base

    def get_interior_tiles(self, gx, gy, size):
        """Return set of interior (filled) tiles for a rectangular building at gx,gy of given size."""
        return {(x, y) for x in range(gx, gx + size) for y in range(gy, gy + size)}

    def get_outline_tiles(self, gx, gy, size):
        """Return set of outline (black border) tiles for a rectangular building at gx,gy of given size.
        Outline is 1 tile thick surrounding the interior."""
        outline = set()
        for dx in range(-1, size + 1):
            for dy in range(-1, size + 1):
                # on border of the rectangle (outer ring)
                if dx in (-1, size) or dy in (-1, size):
                    outline.add((gx + dx, gy + dy))
        return outline

    def get_base_interior_and_outline(self):
        """Return two sets: (interior_tiles, outline_tiles) for the base using circle logic
        that matches Base.draw (interior: dx*dx+dy*dy <= r^2; outline: r^2 < dx*dx+dy*dy <= (r+1)^2)."""
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
        """Return True if any tile in tiles_a is adjacent (Chebyshev distance 1) to any tile in tiles_b.
        Adjacent excludes exact overlap (dx=0,dy=0)."""
        if not tiles_a or not tiles_b:
            return False
        # build a set of neighbors of tiles_b (excluding the tile itself)
        neighbors = set()
        for (bx, by) in tiles_b:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbors.add((bx + dx, by + dy))
        # adjacency exists if any tile in tiles_a is in neighbors
        return any(t in neighbors for t in tiles_a)

    def can_place(self, gx, gy, size=4):
        """Return True if a building interior of size `size` at grid gx,gy is allowed."""
        cols = len(self.noise_map[0])
        rows = len(self.noise_map)

        # 1) Bounds check (ensure interior fits fully on map)
        if gx < 0 or gy < 0 or gx + size > cols or gy + size > rows:
            return False

        # Precompute new building tiles
        new_interior = self.get_interior_tiles(gx, gy, size)
        new_outline = self.get_outline_tiles(gx, gy, size)

        # 2) Mountain check: any interior tile overlapping a mountain blocks placement
        for (x, y) in new_interior:
            if self.noise_map[y][x] > 0.6:
                return False

        # 3) Resource check: interior cannot overlap any resource tile
        for res in self.resources:
            for (rx, ry) in res.positions:
                if (rx, ry) in new_interior:
                    return False

        # 4) Existing buildings: interior must not overlap any existing building's interior
        for bx, by, bsize, _ in self.buildings:
            existing_interior = self.get_interior_tiles(bx, by, bsize)
            if new_interior & existing_interior:
                return False
            # Also do not allow new interior to overlap existing outline
            existing_outline = self.get_outline_tiles(bx, by, bsize)
            if new_interior & existing_outline:
                return False

        # If there's no base and no existing buildings, allow (first base/building)
        if not self.base and not self.buildings:
            return True

        # If base exists, compute base interior + outline (using circular logic)
        base_interior, base_outline = self.get_base_interior_and_outline()

        # 5) Prevent overlapping the base interior or its outline with the building interior
        if new_interior & base_interior:
            return False
        if new_interior & base_outline:
            return False

        # 6) Connection test: new building outline must be adjacent to base OR an existing building's outline.
        connected = False

        # Check adjacency to base outline (adjacent, not overlapping)
        if base_outline:
            if self.tiles_adjacent(new_outline, base_outline):
                connected = True

        # Check adjacency to outlines of existing buildings
        if not connected:
            for bx, by, bsize, _ in self.buildings:
                existing_outline = self.get_outline_tiles(bx, by, bsize)
                if self.tiles_adjacent(new_outline, existing_outline):
                    connected = True
                    break

        return connected

    def add_building(self, gx, gy, size=4, color=(200, 200, 200)):
        if self.can_place(gx, gy, size):
            self.buildings.append((gx, gy, size, color))
            return True
        return False

    def draw(self, screen, tile_size):
        for gx, gy, size, color in self.buildings:
            # Draw interior tiles
            for dy in range(size):
                for dx in range(size):
                    rect = pygame.Rect(
                        (gx + dx) * tile_size,
                        (gy + dy) * tile_size,
                        tile_size,
                        tile_size
                    )
                    pygame.draw.rect(screen, color, rect)

            # Draw outer black border (1-tile ring)
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
