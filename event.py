import pygame
import random
import math

class EventManager:
    def __init__(self, dashboard, width, height):
        self.dashboard = dashboard
        self.width = width
        self.height = height
        self.active_event = None
        self.duration_frames = 120  # ~2 seconds
        self.frames_left = 0

        # round timing
        self.last_event_round = 0
        self.event_interval = 5  # trigger every 5 rounds

        # --- EVENT DEFINITIONS ---
        self.events = [
            {
                "title": "!! WARNING !!",
                "description": ["Dust Storm Incoming!", "-5 Power"],
                "effect": self.apply_dust_storm
            },
            {
                "title": "!! ALERT !!",
                "description": ["Wind Storm Strikes!", "-3 Iron", "-5 Power"],
                "effect": self.apply_wind_storm
            },
            {
                "title": "!! EMERGENCY !!",
                "description": ["Mars Quake Shakes the Colony!", "-10 Iron"],
                "effect": self.apply_mars_quake
            },
            {
                "title": "!! RAID ALERT !!",
                "description": ["Colony Under Attack!", "-3 Population"],
                "effect": self.apply_raids
            },
            {
                "title": "!! AVALANCHE !!",
                "description": ["Avalanche near mountains!", "A resource deposit was lost!"],
                "effect": self.apply_avalanche
            },
            {
                "title": "!! SHUTTLE CRASH !!",
                "description": ["A shuttle has crashed nearby!", "Salvaging materials..."],
                "effect": self.apply_shuttle_crash
            },
            {
                "title": "!! VOLCANIC ERUPTION !!",
                "description": [
                    "A volcano has erupted nearby!",
                    "-5 Iron, -2 Population",
                    "But new resources have appeared!"
                ],
                "effect": self.apply_volcanic_eruption
            },
            {
                "title": "!! METEORITE IMPACT !!",
                "description": [
                    "Meteorite crashed nearby!",
                    "Valuable resources detected!"
                ],
                "effect": self.apply_meteorite_impact
            }
        ]

    # -------------------------------
    # EVENT EFFECTS
    # -------------------------------
    def apply_dust_storm(self):
        new_power = max(self.dashboard.power - 5, 0)
        self.dashboard.update_metrics(power=new_power, current_event="Dust Storm")

        if hasattr(self.dashboard, "building_manager"):
            for b in self.dashboard.building_manager.buildings:
                if b["type"] == "Power Generator" and "object" in b:
                    gen = b["object"]
                    gen.power = max(gen.power - 5, 0)

    def apply_wind_storm(self):
        new_power = max(self.dashboard.power - 5, 0)
        new_metals = max(self.dashboard.metals - 3, 0)
        self.dashboard.update_metrics(power=new_power, metals=new_metals, current_event="Wind Storm")

        if hasattr(self.dashboard, "building_manager"):
            for b in self.dashboard.building_manager.buildings:
                if b["type"] == "Power Generator" and "object" in b:
                    gen = b["object"]
                    gen.power = max(gen.power - 5, 0)

    def apply_mars_quake(self):
        new_metals = max(self.dashboard.metals - 10, 0)
        self.dashboard.update_metrics(metals=new_metals, current_event="Mars Quake")

    def apply_raids(self):
        new_population = max(self.dashboard.population - 3, 0)
        self.dashboard.update_metrics(population=new_population, current_event="Raids")

    def apply_avalanche(self):
        self.dashboard.update_metrics(current_event="Avalanche")

        if not hasattr(self.dashboard, "resources") or not hasattr(self.dashboard, "noise_map"):
            print("[Avalanche] Missing resource or terrain data.")
            return

        noise_map = self.dashboard.noise_map
        deposits = self.dashboard.resources
        mountain_threshold = 0.7
        candidates = []

        for deposit in deposits:
            for (x, y) in deposit.positions:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < noise_map.shape[1] and 0 <= ny < noise_map.shape[0]:
                        if noise_map[ny][nx] >= mountain_threshold:
                            candidates.append(deposit)
                            break
                if deposit in candidates:
                    break

        if candidates:
            to_remove = random.choice(candidates)
            deposits.remove(to_remove)
            print(f"[Avalanche] Removed a {to_remove.type} deposit near mountains.")
        else:
            print("[Avalanche] No nearby mountain deposits found to remove.")

    def apply_shuttle_crash(self):
        iron_gain = random.randint(1, 5)
        marsium_gain = random.randint(0, 2)

        self.dashboard.metals += iron_gain
        if hasattr(self.dashboard, "marsium"):
            self.dashboard.marsium += marsium_gain

        self.dashboard.update_metrics(current_event="Shuttle Crash")

        self.active_event["description"] = [
            "A shuttle has crashed nearby!",
            f"Salvaged +{iron_gain} Iron, +{marsium_gain} Marsium"
        ]

    def apply_volcanic_eruption(self):
        new_metals = max(self.dashboard.metals - 5, 0)
        new_population = max(self.dashboard.population - 2, 0)
        self.dashboard.update_metrics(
            metals=new_metals,
            population=new_population,
            current_event="Volcanic Eruption"
        )

        if hasattr(self.dashboard, "resources") and hasattr(self.dashboard, "noise_map"):
            from resources import ResourceDeposit
            noise_map = self.dashboard.noise_map
            deposits = self.dashboard.resources
            rows, cols = noise_map.shape

            for _ in range(random.randint(2, 5)):
                resource_type = random.choice(["iron", "ice", "marsium"])
                for _ in range(1000):
                    x = random.randint(0, cols - 1)
                    y = random.randint(0, rows - 1)
                    if resource_type == "iron":
                        color = (0, 0, 0)
                        break
                    elif resource_type == "ice":
                        color = (150, 200, 255)
                        break
                    elif resource_type == "marsium":
                        color = (160, 32, 240)
                        break
                patch = [(x + dx, y + dy) for dx, dy in random.sample(
                    [(-1,0),(1,0),(0,-1),(0,1),(0,0)], random.randint(1, 3)
                ) if 0 <= x+dx < cols and 0 <= y+dy < rows]

                deposits.append(ResourceDeposit(resource_type, patch, color))

            print("[Volcanic Eruption] New visible resources have appeared!")

    def apply_meteorite_impact(self):
        """Spawn a small 3x3 meteorite crater packed with resources."""
        self.dashboard.update_metrics(current_event="Meteorite Impact")

        if not hasattr(self.dashboard, "resources") or not hasattr(self.dashboard, "noise_map"):
            print("[Meteorite Impact] Missing map or resource data.")
            return

        from resources import ResourceDeposit

        rows, cols = self.dashboard.noise_map.shape
        crater_radius = 1  # half of 3x3 area (radius ≈ 1 tile)
        crater_diameter = 3

        # Find a valid spot not near base or buildings
        for _ in range(1000):
            cx = random.randint(2, cols - 3)
            cy = random.randint(2, rows - 3)

            # Avoid near base
            if hasattr(self.dashboard, "base_pos"):
                bx, by = self.dashboard.base_pos
                if (cx - bx) ** 2 + (cy - by) ** 2 < 10**2:
                    continue

            # Avoid near buildings
            too_close = False
            if hasattr(self.dashboard, "building_manager"):
                for b in self.dashboard.building_manager.buildings:
                    bx = b.get("x") or (b.get("pos")[0] if "pos" in b else None)
                    by = b.get("y") or (b.get("pos")[1] if "pos" in b else None)
                    if bx is not None and by is not None:
                        if (cx - bx) ** 2 + (cy - by) ** 2 < 6**2:
                            too_close = True
                            break
            if too_close:
                continue
            break

        deposits = self.dashboard.resources
        resource_types = ["iron", "marsium", "ice"]

        crater_positions = []
        for x in range(cx - 1, cx + 2):  # 3x3 area
            for y in range(cy - 1, cy + 2):
                if 0 <= x < cols and 0 <= y < rows:
                    crater_positions.append((x, y))
                    # Randomly scatter ores inside crater
                    if random.random() < 0.8:
                        r_type = random.choice(resource_types)
                        color = {
                            "iron": (50, 50, 50),
                            "marsium": (160, 32, 240),
                            "ice": (180, 220, 255)
                        }[r_type]
                        deposits.append(ResourceDeposit(r_type, [(x, y)], color))

                    # Slightly darken terrain (visual scorch)
                    self.dashboard.noise_map[y][x] *= 0.6

        # Add brown border rim around crater
        rim_color = (120, 80, 40)
        for (x, y) in crater_positions:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in crater_positions and 0 <= nx < cols and 0 <= ny < rows:
                    deposits.append(ResourceDeposit("rock", [(nx, ny)], rim_color))

        print(f"[Meteorite Impact] Small meteorite crater created at ({cx}, {cy}).")



    # -------------------------------
    # EVENT LOGIC
    # -------------------------------
    def update(self, current_round):
        if self.active_event is None and current_round - self.last_event_round >= self.event_interval:
            self.trigger_event()
            self.last_event_round = current_round

        if self.active_event:
            self.frames_left -= 1
            if self.frames_left <= 0:
                self.active_event = None

    def trigger_event(self):
        self.active_event = random.choice(self.events)
        self.active_event["effect"]()
        self.frames_left = self.duration_frames

    # -------------------------------
    # DRAW POPUP
    # -------------------------------
    def draw(self, screen):
        if not self.active_event:
            return

        font = pygame.font.SysFont(None, 40, bold=True)
        lines = [self.active_event["title"]] + self.active_event["description"]
        total_height = len(lines) * 50
        start_y = (self.height - total_height) // 2

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 0, 0))
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx or dy:
                        outline = font.render(line, True, (0, 0, 0))
                        screen.blit(outline, (self.width // 2 - text_surface.get_width() // 2 + dx,
                                              start_y + i * 50 + dy))
            screen.blit(text_surface, (self.width // 2 - text_surface.get_width() // 2,
                                       start_y + i * 50))
