import random
from collections import deque

class ResourceDeposit:
    def __init__(self, type_, positions, color):
        self.type = type_       # "iron", "ice", "marsium"
        self.positions = positions  # list of (x, y) tile positions
        self.color = color

    @staticmethod
    def spawn_resources(noise_map, cols, rows, tile_size):
        """
        Returns a list of ResourceDeposit objects for Iron, Ice, Marsium
        """
        deposits = []

        # Helper: check if tile is mountain
        def is_mountain(x, y):
            return noise_map[y][x] >= 0.7

        # Helper: check if tile is flat
        def is_flat(x, y):
            return noise_map[y][x] < 0.7

        # Helper: check if tile is peak (higher than 8 neighbors)
        def is_peak(x, y):
            if not is_mountain(x, y):
                return False
            neighbors = [(nx, ny) for nx in range(x-1, x+2)
                                 for ny in range(y-1, y+2)
                                 if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) != (x, y)]
            return all(noise_map[y][x] >= noise_map[ny][nx] for nx, ny in neighbors)

        # Helper: BFS patch generator
        def generate_patch(start_x, start_y, max_size, valid_fn):
            visited = set()
            queue = deque([(start_x, start_y)])
            patch = []

            while queue and len(patch) < max_size:
                x, y = queue.popleft()
                if (x, y) in visited:
                    continue
                visited.add((x, y))

                if not valid_fn(x, y):
                    continue

                patch.append((x, y))

                # Add neighbors randomly to queue
                neighbors = [(x+dx, y+dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]]
                random.shuffle(neighbors)
                for nx, ny in neighbors:
                    if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visited:
                        queue.append((nx, ny))

            return patch

        # -------------------- Iron --------------------
        iron_patches = random.randint(4, 8)  # slightly more patches
        for _ in range(iron_patches):
            for _ in range(1000):
                x = random.randint(0, cols-1)
                y = random.randint(0, rows-1)
                if is_flat(x, y):
                    patch_size = random.randint(4, 12)
                    patch = generate_patch(x, y, patch_size, is_flat)
                    if patch:
                        deposits.append(ResourceDeposit("iron", patch, (0, 0, 0)))  # black
                        break

        # -------------------- Ice --------------------
        ice_patches = random.randint(3, 6)
        for _ in range(ice_patches):
            for _ in range(1000):
                x = random.randint(0, cols-1)
                y = random.randint(0, rows-1)
                if not is_mountain(x, y):
                    neighbors = [(x+dx, y+dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]
                                 if 0 <= x+dx < cols and 0 <= y+dy < rows]
                    if any(is_mountain(nx, ny) and not is_peak(nx, ny) for nx, ny in neighbors):
                        patch_size = random.randint(6, 16)
                        patch = generate_patch(x, y, patch_size, lambda tx, ty: not is_mountain(tx, ty))
                        if patch:
                            deposits.append(ResourceDeposit("ice", patch, (150, 200, 255)))  # light blue
                            break

        # -------------------- Marsium --------------------
        # Flat land rare
        marsium_flat_patches = random.randint(1, 3)  # slightly fewer patches
        for _ in range(marsium_flat_patches):
            for _ in range(1000):
                x = random.randint(0, cols-1)
                y = random.randint(0, rows-1)
                if is_flat(x, y):
                    patch_size = random.randint(1, 2)
                    patch = generate_patch(x, y, patch_size, is_flat)
                    if patch:
                        deposits.append(ResourceDeposit("marsium", patch, (160, 32, 240)))  # purple
                        break

        # Mountain-top patches
        marsium_peak_patches = random.randint(2, 3)  # slightly fewer patches
        for _ in range(marsium_peak_patches):
            for _ in range(1000):
                x = random.randint(1, cols-2)
                y = random.randint(1, rows-2)

                def valid_mountain_top(tx, ty):
                    if not is_mountain(tx, ty):
                        return False
                    neighbors = [(nx, ny) for nx in range(tx-1, tx+2)
                                         for ny in range(ty-1, ty+2)
                                         if 0 <= nx < cols and 0 <= ny < rows]
                    return all(is_mountain(nx, ny) for nx, ny in neighbors)

                if valid_mountain_top(x, y):
                    patch_size = random.randint(3, 7)
                    patch = generate_patch(x, y, patch_size, valid_mountain_top)
                    if patch:
                        deposits.append(ResourceDeposit("marsium", patch, (160, 32, 240)))  # purple
                        break

        return deposits
