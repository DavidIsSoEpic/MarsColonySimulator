import pygame
from building_manager import BuildingManager
from rover import Rover
from drone import Drone
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu
from camera import Camera
from resources import ResourceDeposit
from rover_inventory import RoverInventory
from drone_inventory import DroneInventory
from base_inventory import BaseInventory
from vehicle_bay_inventory import VehicleBayInventory
from power_generator_inventory import PowerGeneratorInventory
from power_generator import PowerGenerator
from housing_inventory import HousingInventory
from farm_inventory import FarmInventory

pygame.font.init()
pygame.init()

# ---------------- Window setup ---------------- #
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = 200
ROWS = 150

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")

# Try to load game over image; fallback to None if not found
try:
    game_over_image = pygame.image.load("game_over_image.png")
    game_over_image = pygame.transform.scale(game_over_image, (WIDTH, HEIGHT))
except Exception:
    game_over_image = None


def game_loop():
    noise_map = generate_noise_map(ROWS, COLS)
    base = Base.spawn(noise_map, COLS, ROWS, TILE_SIZE)
    building_manager = BuildingManager(noise_map)
    camera = Camera(WIDTH, HEIGHT, COLS * TILE_SIZE, ROWS * TILE_SIZE)
    camera.center_on(base.x * TILE_SIZE, base.y * TILE_SIZE)

    # Filter resources outside base
    all_resources = ResourceDeposit.spawn_resources(noise_map, COLS, ROWS, TILE_SIZE)
    resources = []
    half = base.size // 2
    base_rect = pygame.Rect((base.x - half) * TILE_SIZE - 5,
                            (base.y - half) * TILE_SIZE - 5,
                            base.size * TILE_SIZE + 10,
                            base.size * TILE_SIZE + 10)

    for res in all_resources:
        filtered_positions = [(x, y) for x, y in res.positions
                              if not base_rect.collidepoint(x * TILE_SIZE, y * TILE_SIZE)]
        if filtered_positions:
            res.positions = filtered_positions
            resources.append(res)

    building_manager.set_resources(resources)
    building_manager.set_base(base)

    # --- Units ---
    units = []
    selected_unit = None

    # --- Inventories ---
    open_unit_inventory = None
    show_base_inventory = False
    base_inventory = BaseInventory(base, None)
    base_inventory.dashboard = Dashboard(rounds_total=30)  # temporary until dashboard is fully defined
    show_vehicle_inventory = False
    vehicle_inventory = None
    show_power_inventory = False
    power_inventory = None
    show_housing_inventory = False
    housing_inventory = None
    show_farm_inventory = False
    farm_inventory = None

    bottom_right_message = ""
    message_timer = 0
    placing_building = None
    ignore_next_click = False
    rotate_pressed_last_frame = False
    next_round_triggered = False  # Freeze units during next round processing

    # --- Dashboard ---
    dashboard = Dashboard(rounds_total=30)
    dashboard.food = 15
    dashboard.water = 30
    dashboard.power = 20
    dashboard.metals = 25
    dashboard.marsium = 0
    dashboard.population = 5
    dashboard.soldiers = 0
    dashboard.current_event = ""
    base_inventory.dashboard = dashboard
    dashboard.building_manager = building_manager
    dashboard.noise_map = noise_map
    dashboard.resources = resources

    # --- Event manager ---
    event_manager = EventManager(dashboard, WIDTH, HEIGHT)
    clock = pygame.time.Clock()
    running = True

    # --- Message helper ---
    def set_message(msg, duration=2.0):
        nonlocal bottom_right_message, message_timer
        bottom_right_message = msg
        message_timer = duration

    # ------------------- Helper: Recharge units ------------------- #
    def recharge_units_at_generators(dt):
        for b in building_manager.buildings:
            if b.get("type") == "Power Generator" and "object" in b:
                generator = b["object"]
                generator.update_power(dt)

                rect = pygame.Rect(generator.gx * TILE_SIZE, generator.gy * TILE_SIZE,
                                   generator.size[0] * TILE_SIZE, generator.size[1] * TILE_SIZE)

                for u in units:
                    if isinstance(u, (Rover, Drone)):
                        ux, uy = int(u.x), int(u.y)
                        if rect.collidepoint(ux, uy) and u.power < u.max_power and generator.power > 0:
                            u.recharge(dt)
                            generator.power -= 2 * dt
                            if generator.power < 0:
                                generator.power = 0

    # ------------------- Main Loop ------------------- #
    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()
        world_click = (mouse_pos[0] + camera.x, mouse_pos[1] + camera.y)
        keys = pygame.key.get_pressed()

        # Game Over check
        if dashboard.population <= 0:
            # show game over and return to menu
            if game_over_image:
                screen.blit(game_over_image, (0, 0))
                pygame.display.flip()
            else:
                screen.fill((120, 0, 0))
                go_font = pygame.font.SysFont("Arial", 48, bold=True)
                go_text = go_font.render("GAME OVER", True, (255, 255, 255))
                screen.blit(go_text, ((WIDTH - go_text.get_width()) // 2, (HEIGHT - go_text.get_height()) // 2))
                pygame.display.flip()
            pygame.time.wait(2000)
            return "Menu"

        if ignore_next_click:
            # We reset ignore flag at the start of the frame (prevents immediate double processing)
            ignore_next_click = False

        camera.handle_input(keys, dt)

        # Rotate building if placing
        if placing_building:
            if keys[pygame.K_r] and not rotate_pressed_last_frame:
                b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                current_size = b_info.get("size", (4, 4))
                b_info["size"] = (current_size[1], current_size[0])
                rotate_pressed_last_frame = True
            elif not keys[pygame.K_r]:
                rotate_pressed_last_frame = False

        clicked_ui = False

        # ---------------- Main Event Loop ---------------- #
        for event in pygame.event.get():
            camera.handle_event(event)

            if event.type == pygame.QUIT:
                running = False

            # --- Handle unit inventories ---
            if open_unit_inventory and hasattr(open_unit_inventory, "inventory"):
                action = open_unit_inventory.inventory.handle_event(event, resources)
                if action == "close":
                    open_unit_inventory = None
                    ignore_next_click = True
                    selected_unit = None
                clicked_ui = True

            # --- Handle building/base inventories ---
            if show_base_inventory:
                action = base_inventory.handle_event(event)
                if action == "close":
                    show_base_inventory = False
                    ignore_next_click = True
                    selected_unit = None
                elif action and action.startswith("build_"):
                    placing_building = action.replace("build_", "")
                    show_base_inventory = False
                    ignore_next_click = True
                    selected_unit = None
                clicked_ui = True

            if show_vehicle_inventory and vehicle_inventory:
                action = vehicle_inventory.handle_event(event)
                if action == "close":
                    show_vehicle_inventory = False
                    ignore_next_click = True
                    selected_unit = None
                elif action in ("buy_rover", "buy_drone"):
                    spawn_x = (vehicle_inventory.vehicle_bay["gx"] + vehicle_inventory.vehicle_bay["size"][0] // 2) * TILE_SIZE + TILE_SIZE // 2
                    spawn_y = (vehicle_inventory.vehicle_bay["gy"] + vehicle_inventory.vehicle_bay["size"][1] // 2) * TILE_SIZE + TILE_SIZE // 2
                    if action == "buy_rover" and dashboard.metals >= 5:
                        new_rover = Rover(spawn_x, spawn_y)
                        new_rover.inventory = RoverInventory(new_rover, building_manager, dashboard, units)
                        units.append(new_rover)
                        dashboard.metals -= 5
                        set_message("Rover constructed!")
                        show_vehicle_inventory = False
                    elif action == "buy_drone" and dashboard.metals >= 10:
                        new_drone = Drone(spawn_x, spawn_y - TILE_SIZE)
                        new_drone.move_count = 0
                        new_drone.max_moves = 2
                        new_drone.inventory = DroneInventory(new_drone, [r for r in units if isinstance(r, Rover)], dashboard, building_manager)
                        units.append(new_drone)
                        dashboard.metals -= 10
                        set_message("Drone constructed!")
                        show_vehicle_inventory = False
                    else:
                        set_message("Not enough metal for this unit")
                    selected_unit = None
                clicked_ui = True

            # --- Handle other inventories ---
            if show_power_inventory and power_inventory:
                action = power_inventory.handle_event(event)
                if action == "close":
                    show_power_inventory = False
                    ignore_next_click = True
                    selected_unit = None
                clicked_ui = True

            if show_housing_inventory and housing_inventory:
                action = housing_inventory.handle_event(event)
                if action == "close":
                    show_housing_inventory = False
                    ignore_next_click = True
                    selected_unit = None
                clicked_ui = True

            if show_farm_inventory and farm_inventory:
                action = farm_inventory.handle_event(event)
                if action == "close":
                    show_farm_inventory = False
                    ignore_next_click = True
                    selected_unit = None
                clicked_ui = True

            # --- Handle mouse clicks ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Use event.pos for UI detection (screen coordinates)
                ui_pos = event.pos
                # world_click uses camera offset (map coordinates)
                world_click = (ui_pos[0] + camera.x, ui_pos[1] + camera.y)

                # If an inventory just closed and set ignore_next_click, skip this click
                if ignore_next_click:
                    ignore_next_click = False
                    continue

                # ---------- Dashboard buttons (UI) ----------
                # capture current round to clamp accidental big jumps
                before_round = dashboard.current_round
                action = dashboard.handle_click(ui_pos, units=units, building_manager=building_manager)

                if action == "next_round":
                    # dashboard.handle_click might itself call next_round; clamp to +1 max
                    # If it already incremented by >1, clamp to only +1 effective change
                    if dashboard.current_round - before_round > 1:
                        # clamp to exactly +1
                        dashboard.current_round = before_round + 1

                    # perform the per-round housekeeping (reset move counts, etc.)
                    for u in units:
                        if hasattr(u, "move_count"):
                            u.move_count = 0
                        if hasattr(u, "awaiting_move_confirmation"):
                            u.awaiting_move_confirmation = False

                    # Additional starvation/population logic: if food low, reduce pop
                    # (you previously used threshold 10)
                    if dashboard.food < 10:
                        old_pop = dashboard.population
                        dashboard.population = max(int(dashboard.population * 0.8), 0)
                        # apply next-round mining effects on inventories if present
                        for u in units:
                            if hasattr(u, "inventory") and u.inventory:
                                if hasattr(u.inventory, "apply_next_round_mining"):
                                    try:
                                        u.inventory.apply_next_round_mining()
                                    except Exception:
                                        pass

                    set_message(f"Advanced to round {dashboard.current_round}")
                    selected_unit = None
                    # Prevent accidental immediate re-triggering
                    ignore_next_click = True
                    next_round_triggered = True
                    continue  # do not process world click for this event

                elif action == "stop_control":
                    selected_unit = None
                    set_message("Stopped controlling unit", 1.5)
                    # We don't consume world click necessarily; still continue to next checks
                    continue

                # If any inventory UI is open, ignore world clicks
                if open_unit_inventory or show_base_inventory or show_vehicle_inventory or show_power_inventory or show_housing_inventory or show_farm_inventory:
                    continue

                # ---------- World clicks ----------
                # Left button: place building / move units
                if event.button == 1:
                    if placing_building:
                        b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                        b_size = (int(b_info.get("size", (4, 4))[0]), int(b_info.get("size", (4, 4))[1]))
                        cost = b_info["cost"].get("metals", 0)
                        new_obj = PowerGenerator if placing_building == "Power Generator" else None
                        if dashboard.metals >= cost:
                            gx = int(world_click[0] // TILE_SIZE)
                            gy = int(world_click[1] // TILE_SIZE)
                            obj_instance = new_obj(gx=gx, gy=gy) if new_obj else None
                            if building_manager.add_building(gx, gy, size=b_size, color=(200, 200, 200),
                                                            b_type=placing_building, obj=obj_instance):
                                dashboard.metals -= cost
                                set_message(f"Placed {placing_building} at {gx},{gy}")
                                placing_building = None
                            else:
                                set_message("Invalid building spot")
                        else:
                            set_message("Not enough metals")
                    else:
                        clicked_on_unit = False
                        for u in units:
                            if u.is_clicked(world_click):
                                selected_unit = u
                                clicked_on_unit = True
                                break
                        if not clicked_on_unit and selected_unit:
                            if getattr(selected_unit, "move_count", 0) >= getattr(selected_unit, "max_moves", 9999):
                                set_message(f"{selected_unit.__class__.__name__} has no moves left this round")
                            else:
                                if getattr(selected_unit, "mining_active", False):
                                    if not getattr(selected_unit, "awaiting_move_confirmation", False):
                                        set_message("This unit is mining. Click again to move it.")
                                        selected_unit.awaiting_move_confirmation = True
                                    else:
                                        selected_unit.awaiting_move_confirmation = False
                                        selected_unit.mining_active = False
                                        selected_unit.set_target(world_click)
                                        selected_unit.move_count += 1
                                else:
                                    selected_unit.set_target(world_click)
                                    selected_unit.move_count += 1

                # Right click: open unit/building/base inventories
                elif event.button == 3:
                    clicked_on_unit = False
                    for u in units:
                        if u.is_clicked(world_click):
                            if isinstance(u, Rover):
                                if not hasattr(u, "inventory") or u.inventory is None:
                                    u.inventory = RoverInventory(u, building_manager, dashboard, units)
                                open_unit_inventory = u
                            elif isinstance(u, Drone):
                                if not hasattr(u, "inventory") or u.inventory is None:
                                    u.inventory = DroneInventory(u, [r for r in units if isinstance(r, Rover)], dashboard, building_manager)
                                open_unit_inventory = u
                            clicked_on_unit = True
                            break
                    if clicked_on_unit:
                        clicked_ui = True
                        continue

                    # Check buildings
                    for b in building_manager.buildings:
                        gx, gy, bsize, b_type = b["gx"], b["gy"], b["size"], b["type"]
                        rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, bsize[0]*TILE_SIZE, bsize[1]*TILE_SIZE)
                        if rect.collidepoint(world_click):
                            if b_type == "Power Generator" and "object" in b:
                                power_inventory = PowerGeneratorInventory(b["object"], dashboard)
                                show_power_inventory = True
                                selected_unit = None
                                clicked_ui = True
                                break
                            elif b_type == "Vehicle Bay":
                                vehicle_inventory = VehicleBayInventory(b, dashboard)
                                show_vehicle_inventory = True
                                selected_unit = None
                                clicked_ui = True
                                break
                            elif b_type == "Housing":
                                housing_inventory = HousingInventory(b, dashboard)
                                show_housing_inventory = not show_housing_inventory
                                selected_unit = None
                                clicked_ui = True
                                break
                            elif b_type == "Farm":
                                if "object" not in b:
                                    b["object"] = FarmInventory(b, dashboard)
                                farm_inventory = b["object"]
                                show_farm_inventory = not show_farm_inventory
                                selected_unit = None
                                clicked_ui = True
                                break

                    # Base click
                    half = base.size // 2
                    base_rect_px = pygame.Rect((base.x - half) * TILE_SIZE,
                                               (base.y - half) * TILE_SIZE,
                                               base.size * TILE_SIZE,
                                               base.size * TILE_SIZE)
                    if base_rect_px.collidepoint(world_click) and not clicked_ui:
                        show_base_inventory = not show_base_inventory
                        selected_unit = None
                        clicked_ui = True

        # ---------------- Updates ---------------- #
        event_manager.update(dashboard.current_round)

        # Move units only if next round not currently processing and no inventories open
        if not next_round_triggered and not (open_unit_inventory or show_base_inventory or show_vehicle_inventory or show_power_inventory or show_housing_inventory or show_farm_inventory):
            for u in units:
                u.move(noise_map, TILE_SIZE, COLS, ROWS, dt)

        recharge_units_at_generators(dt)

        for u in units:
            if hasattr(u, "inventory") and u.inventory:
                u.inventory.update(dt, resources)
        if open_unit_inventory:
            open_unit_inventory.inventory.update(dt, resources)
        if base_inventory:
            base_inventory.update()
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.update()
        if show_power_inventory and power_inventory:
            power_inventory.update(dt)
        if show_housing_inventory and housing_inventory:
            housing_inventory.update()
        if show_farm_inventory and farm_inventory:
            farm_inventory.update()

        if dashboard.current_event != "Dust Storm":
            dashboard.power = round(sum(
                b["object"].power for b in building_manager.buildings
                if b.get("type") == "Power Generator" and "object" in b
            ), 1)

        # ---------------- Drawing ---------------- #
        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE, camera=camera)

        for res in resources:
            for x, y in res.positions:
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                rect = camera.apply(rect)
                pygame.draw.rect(screen, res.color, rect)

        building_manager.draw(screen, TILE_SIZE, camera=camera)
        base.draw(screen, TILE_SIZE, camera=camera)
        for u in units:
            u.draw(screen, camera=camera)

        if placing_building:
            gx = int((mouse_pos[0] + camera.x) // TILE_SIZE)
            gy = int((mouse_pos[1] + camera.y) // TILE_SIZE)
            b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
            b_size = (int(b_info.get("size", (4, 4))[0]), int(b_info.get("size", (4, 4))[1]))
            valid = building_manager.can_place(gx, gy, b_size)
            color = (0, 200, 0) if valid else (200, 0, 0)
            rect = pygame.Rect(gx*TILE_SIZE, gy*TILE_SIZE, b_size[0]*TILE_SIZE, b_size[1]*TILE_SIZE)
            rect = camera.apply(rect)
            pygame.draw.rect(screen, color, rect, 2)

        if open_unit_inventory:
            open_unit_inventory.inventory.draw(screen, resources)
        if show_base_inventory:
            base_inventory.draw(screen)
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.draw(screen)
        if show_power_inventory and power_inventory:
            power_inventory.draw(screen)
        if show_housing_inventory and housing_inventory:
            housing_inventory.draw(screen)
        if show_farm_inventory and farm_inventory:
            farm_inventory.draw(screen)

        event_manager.draw(screen)
        dashboard.draw(screen)

        if bottom_right_message and message_timer > 0:
            msg_font = pygame.font.SysFont("Arial", 20, bold=True)
            msg_text = msg_font.render(bottom_right_message, True, (255, 255, 255))
            screen.blit(msg_text, (WIDTH - msg_text.get_width() - 20, HEIGHT - msg_text.get_height() - 20))
            message_timer -= dt
        elif message_timer <= 0:
            bottom_right_message = ""

        # Reset round-processing flag
        next_round_triggered = False

        pygame.display.flip()

    # end while running
    return None


def main():
    menu = Menu(WIDTH, HEIGHT)
    in_menu = True
    in_settings = False

    while in_menu:
        mouse_pos = pygame.mouse.get_pos()
        mouse_held = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            result = menu.handle_events(event, in_settings=in_settings, mouse_pos=mouse_pos, mouse_held=mouse_held)
            if result == "start":
                in_menu = False
            elif result == "quit":
                pygame.quit()
                return
            elif result == "settings":
                in_settings = True
            elif result == "back":
                in_settings = False

        if in_settings:
            menu.draw_settings_menu(screen)
        else:
            menu.draw_main_menu(screen)

        pygame.display.flip()

    # start game loop
    result = game_loop()
    # if game loop directed back to menu (game over), show menu again
    if result == "Menu":
        main()


if __name__ == "__main__":
    main()


# ---------------- Git Commands ---------------- #
# git init
# git add .
# git commit -m "Merge game over + population system; fix Next Round double-trigger bug; keep original features"
# git push -u origin main
