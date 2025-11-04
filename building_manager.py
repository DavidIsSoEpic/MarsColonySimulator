import pygame
import random

class BuildingManager:
    def __init__(self, noise_map=None):
        self.noise_map = noise_map
        self.buildings = []
        self.resources = []
        self.base = None

    # -------------------------
    # Utility methods
    # -------------------------
    def _occupied_tiles(self, ignore_airlocks=False):
        occ = set()
        for b in self.buildings:
            if ignore_airlocks and b.get("type") == "Airlock":
                continue
            gx, gy = b["gx"], b["gy"]
            w, h = b["size"]
            for x in range(gx, gx + w):
                for y in range(gy, gy + h):
                    occ.add((x, y))
        return occ

    def _rect_tiles(self, gx, gy, size):
        w, h = size
        return {(x, y) for x in range(gx, gx + w) for y in range(gy, gy + h)}

    def set_resources(self, resources):
        self.resources = resources

    def set_base(self, base):
        self.base = base
        found = False
        for b in self.buildings:
            if b.get("type") == "Base":
                found = True
                break
        if not found and base is not None:
            bdict = {
                "gx": base.x - base.size // 2,
                "gy": base.y - base.size // 2,
                "size": (base.size, base.size),
                "type": "Base",
                "color": (180, 180, 180),
                "object": getattr(base, "object", None)
            }
            self.buildings.append(bdict)

    # -------------------------
    # Placement rules
    # -------------------------
    def can_place(self, gx, gy, size):
        """Only allows placement if the new building is exactly 1 tile away (not touching)."""
        w, h = size
        if self.noise_map is not None:
            rows = len(self.noise_map)
            cols = len(self.noise_map[0]) if rows else 0
            if gx < 0 or gy < 0 or gx + w > cols or gy + h > rows:
                return False

        new_tiles = self._rect_tiles(gx, gy, size)
        occ = self._occupied_tiles(ignore_airlocks=False)

        # Block overlapping
        if new_tiles & occ:
            return False

        # If no buildings yet, allow (for base)
        if not self.buildings:
            return True

        # Must be exactly 1-tile gap (no touching)
        valid_gap = False
        for b in self.buildings:
            if b["type"] == "Airlock":
                continue
            gx2, gy2 = b["gx"], b["gy"]
            w2, h2 = b["size"]

            dx = max(gx2 - (gx + w), gx - (gx2 + w2))
            dy = max(gy2 - (gy + h), gy - (gy2 + h2))

            # exactly 1-tile gap required
            if (dx == 1 and dy <= 0) or (dy == 1 and dx <= 0):
                valid_gap = True
            # touching (0 gap) not allowed
            if dx <= 0 and dy <= 0:
                return False

        return valid_gap

    def add_building(self, gx, gy, size=(4,4), color=(180,180,180), b_type="Generic", obj=None):
        if not self.can_place(gx, gy, size):
            return False

        new_building = {
            "gx": gx,
            "gy": gy,
            "size": size,
            "type": b_type,
            "color": (180, 180, 180)  # match base color
        }
        if obj:
            new_building["object"] = obj

        self.buildings.append(new_building)
        self._maybe_create_airlocks_for(new_building)
        return True

    # -------------------------
    # Airlock logic (single tile connection)
    # -------------------------
    def _maybe_create_airlocks_for(self, new_b):
        gx1, gy1 = new_b["gx"], new_b["gy"]
        new_tiles = self._rect_tiles(gx1, gy1, new_b["size"])
        existing_tiles = self._occupied_tiles(ignore_airlocks=True)

        possible_airlocks = []

        for nx, ny in new_tiles:
            candidates = [(nx+2, ny), (nx-2, ny), (nx, ny+2), (nx, ny-2)]
            for ex, ey in candidates:
                if (ex, ey) in existing_tiles:
                    mid = ((nx + ex) // 2, (ny + ey) // 2)
                    if mid not in self._occupied_tiles(ignore_airlocks=False):
                        possible_airlocks.append(mid)

        # Pick only one airlock (single connecting pixel)
        if possible_airlocks:
            chosen = random.choice(possible_airlocks)
            self._add_airlock_tile(chosen[0], chosen[1])

    def _add_airlock_tile(self, gx, gy):
        for b in self.buildings:
            if b["gx"] == gx and b["gy"] == gy and b["size"] == (1, 1):
                return
        airlock = {
            "gx": gx,
            "gy": gy,
            "size": (1, 1),
            "type": "Airlock",
            "color": (0, 0, 0)
        }
        self.buildings.append(airlock)

    # -------------------------
    # Drawing (match home base perfectly)
    # -------------------------
    def draw(self, screen, tile_size):
        for b in self.buildings:
            gx, gy = b["gx"], b["gy"]
            w, h = b["size"]
            x = gx * tile_size
            y = gy * tile_size
            rect = pygame.Rect(x, y, w * tile_size, h * tile_size)

            if b.get("type") == "Airlock":
                pygame.draw.rect(screen, (0, 0, 0), rect)
                continue

            # Fill (same color as main base)
            pygame.draw.rect(screen, (180, 180, 180), rect)

            # Outer border directly on edge (no gray sliver)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    def debug_print(self):
        print("Buildings:")
        for b in self.buildings:
            print(f" - {b['type']} at ({b['gx']},{b['gy']}) size {b['size']}")
