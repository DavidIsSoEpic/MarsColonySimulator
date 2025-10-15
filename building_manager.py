import pygame

class BuildingManager:
    def __init__(self, noise_map):
        self.noise_map = noise_map
        # Each building is stored as a dict with keys: gx, gy, size, color, type, object
        self.buildings = []
        self.resources = []  # list of ResourceDeposit objects (with .positions list of (x,y))
        self.base = None     # Base instance

    def set_resources(self, resources):
        self.resources = resources

    def set_base(self, base):
        self.base = base

    def get_interior_tiles(self, gx, gy, size):
        if isinstance(size, int):
            w = h = size
        else:
            w, h = size
        return {(x, y) for x in range(gx, gx + w) for y in range(gy, gy + h)}

    def get_outline_tiles(self, gx, gy, size):
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
        interior, outline = set(), set()
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

    def can_place(self, gx, gy, size=(4, 4)):
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

        # Check mountains
        for x, y in new_interior | new_outline:
            if self.noise_map[y][x] > 0.6:
                return False

        # Check resources
        for res in self.resources:
            for rx, ry in res.positions:
                if (rx, ry) in new_interior or (rx, ry) in new_outline:
                    return False

        # Check existing buildings
        for b in self.buildings:
            existing_interior = self.get_interior_tiles(b["gx"], b["gy"], b["size"])
            if new_interior & existing_interior or new_outline & existing_interior:
                return False

        # Check base
        base_interior, base_outline = self.get_base_interior_and_outline()
        if new_interior & base_interior or new_outline & base_interior:
            return False

        # Must be connected
        connected = self.tiles_adjacent(new_outline, base_outline)
        if not connected:
            for b in self.buildings:
                existing_outline = self.get_outline_tiles(b["gx"], b["gy"], b["size"])
                if self.tiles_adjacent(new_outline, existing_outline):
                    connected = True
                    break

        return connected

    def add_building(self, gx, gy, size=(4, 4), color=(200, 200, 200), b_type="Generic", obj=None):
        if self.can_place(gx, gy, size):
            building_dict = {
                "gx": gx,
                "gy": gy,
                "size": size,
                "color": color,
                "type": b_type
            }
            if obj is not None:
                building_dict["object"] = obj
            self.buildings.append(building_dict)
            return True
        return False


    def draw(self, screen, tile_size):
        for b in self.buildings:
            gx, gy = b["gx"], b["gy"]
            size, color = b["size"], b["color"]
            if isinstance(size, int):
                w = h = size
            else:
                w, h = size

            # Draw interior
            for dy in range(h):
                for dx in range(w):
                    rect = pygame.Rect((gx + dx) * tile_size, (gy + dy) * tile_size, tile_size, tile_size)
                    pygame.draw.rect(screen, color, rect)

            # Draw outline
            for dy in range(h + 2):
                for dx in range(w + 2):
                    if dx == 0 or dx == w + 1 or dy == 0 or dy == h + 1:
                        rect = pygame.Rect((gx - 1 + dx) * tile_size, (gy - 1 + dy) * tile_size, tile_size, tile_size)
                        pygame.draw.rect(screen, (0, 0, 0), rect)
