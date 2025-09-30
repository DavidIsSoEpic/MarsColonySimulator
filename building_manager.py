import pygame

class Building:
    def __init__(self, x, y, size, color=(100, 200, 100)):
        self.x = x  # grid position
        self.y = y
        self.size = size  # size in tiles (e.g., 2 = 2x2 building)
        self.color = color

    def draw(self, screen, tile_size):
        # Rectangle covering the building area
        rect = pygame.Rect(
            self.x * tile_size,
            self.y * tile_size,
            self.size * tile_size,
            self.size * tile_size
        )

        # Fill the building
        pygame.draw.rect(screen, self.color, rect)

        # Add an outline so it stands out
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        # Debug: confirm this method runs
        # (you can remove later when it works)
        # print(f"Drawing building at grid {self.x},{self.y}")
        

class BuildingManager:
    def __init__(self, noise_map, mountain_threshold=0.7):
        self.noise_map = noise_map
        self.mountain_threshold = mountain_threshold
        self.buildings = []

    def can_place(self, x, y, size):
        rows, cols = self.noise_map.shape

        # Bounds check
        if x < 0 or y < 0 or x + size > cols or y + size > rows:
            return False

        # Avoid overlaps & mountains
        for by in range(y, y + size):
            for bx in range(x, x + size):
                if self.noise_map[by][bx] >= self.mountain_threshold:
                    return False
                for b in self.buildings:
                    if (bx >= b.x and bx < b.x + b.size and
                        by >= b.y and by < b.y + b.size):
                        return False
        return True

    def add_building(self, x, y, size, color=(100, 200, 100)):
        if self.can_place(x, y, size):
            self.buildings.append(Building(x, y, size, color))
            return True
        return False

    def draw(self, screen, tile_size):
        for b in self.buildings:
            b.draw(screen, tile_size)
