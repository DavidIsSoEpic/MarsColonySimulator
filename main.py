import pygame
from building_manager import BuildingManager
from rover import Rover
from drone import Drone
from terrain import generate_noise_map, draw_terrain
from dashboard import Dashboard
from event import EventManager
from building import Base
from menu import Menu
from resources import ResourceDeposit
from rover_inventory import RoverInventory
from drone_inventory import DroneInventory
from base_inventory import BaseInventory
from vehicle_bay_inventory import VehicleBayInventory

pygame.font.init()
pygame.init()

# ---------------- Window setup ---------------- #
WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 10
COLS = WIDTH // TILE_SIZE
ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Colony Simulator - Top-Down Mars Terrain")


def game_loop():
    noise_map = generate_noise_map(ROWS, COLS)
    base = Base.spawn(noise_map, COLS, ROWS, TILE_SIZE)
    building_manager = BuildingManager(noise_map)

    all_resources = ResourceDeposit.spawn_resources(noise_map, COLS, ROWS, TILE_SIZE)
    resources = []
    base_rect = pygame.Rect(
        base.x * TILE_SIZE - 5, base.y * TILE_SIZE - 5,
        base.radius * TILE_SIZE * 2 + 10, base.radius * TILE_SIZE * 2 + 10
    )
    for res in all_resources:
        filtered_positions = []
        for x, y in res.positions:
            res_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if not base_rect.colliderect(res_rect):
                filtered_positions.append((x, y))
        if filtered_positions:
            res.positions = filtered_positions
            resources.append(res)

    building_manager.set_resources(resources)
    building_manager.set_base(base)

    # --- Units managed dynamically via VehicleBay ---
    units = []  # start empty; spawn via vehicle bay purchases

    selected_unit = None

    # --- Inventories ---
    show_rover_inventory = False
    rover_inventory = None
    show_drone_inventory = False
    drone_inventory = None

    show_base_inventory = False
    base_inventory = BaseInventory(base, None)

    show_vehicle_inventory = False
    vehicle_inventory = None

    bottom_right_message = ""
    message_timer = 0

    placing_building = None
    ignore_next_click = False
    rotate_pressed_last_frame = False

    dashboard = Dashboard(rounds_total=30)
    # start metals = 10 per your request
    try:
        dashboard.update_metrics(population=5, food=50, power=20, water=30, metals=10, soldiers=0, current_event="")
    except Exception:
        # if your Dashboard doesn't have update_metrics signature, set attributes directly
        dashboard.population = 5
        dashboard.food = 50
        dashboard.power = 20
        dashboard.water = 30
        dashboard.metals = 10
        dashboard.soldiers = 0
        dashboard.current_event = ""

    base_inventory.dashboard = dashboard

    event_manager = EventManager(dashboard, WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    running = True

    # helper: show bottom-right messages
    def set_message(msg, duration=2.0):
        nonlocal bottom_right_message, message_timer
        bottom_right_message = msg
        message_timer = duration

    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        # --- Rotate building if placing ---
        if placing_building:
            if keys[pygame.K_r] and not rotate_pressed_last_frame:
                b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                current_size = b_info.get("size", (4, 4))
                b_info["size"] = (current_size[1], current_size[0])
                rotate_pressed_last_frame = True
            elif not keys[pygame.K_r]:
                rotate_pressed_last_frame = False

        clicked_ui = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ---------------- Inventories ---------------- #
            # Note: only forward events to inventory objects when visible
            if show_rover_inventory and rover_inventory:
                action = rover_inventory.handle_event(event, resources)
                if action == "close":
                    show_rover_inventory = False
                    ignore_next_click = True
                clicked_ui = True

            if show_drone_inventory and drone_inventory:
                action = drone_inventory.handle_event(event, resources)
                if action == "close":
                    show_drone_inventory = False
                    ignore_next_click = True
                clicked_ui = True

            if show_base_inventory:
                action = base_inventory.handle_event(event)
                if action == "close":
                    show_base_inventory = False
                elif action and action.startswith("build_"):
                    placing_building = action.replace("build_", "")
                    show_base_inventory = False
                    ignore_next_click = True
                clicked_ui = True

            if show_vehicle_inventory and vehicle_inventory:
                # vehicle_inventory.handle_event should return 'buy_rover'/'buy_drone'/'close' (it doesn't spawn itself)
                action = vehicle_inventory.handle_event(event)
                if action == "close":
                    show_vehicle_inventory = False
                elif action == "buy_rover":
                    # Rover costs 5 metals per your latest ask (you said 5 then 2 earlier; here we use 5)
                    rover_cost = 5
                    if getattr(dashboard, "metals", 0) >= rover_cost:
                        # spawn inside vehicle bay building (center-ish) and layer above
                        vx = vehicle_inventory.vehicle_bay["gx"]
                        vy = vehicle_inventory.vehicle_bay["gy"]
                        vsize = vehicle_inventory.vehicle_bay["size"]
                        spawn_x = (vx + vsize[0] // 2) * TILE_SIZE + TILE_SIZE//2
                        spawn_y = (vy + vsize[1] // 2) * TILE_SIZE + TILE_SIZE//2
                        new_rover = Rover(spawn_x, spawn_y)
                        # ensure required attributes exist for your logic
                        new_rover.storage = getattr(new_rover, "storage", 0)
                        new_rover.resources_held = getattr(new_rover, "resources_held", {})
                        new_rover.mining_active = False
                        new_rover.awaiting_move_confirmation = False
                        new_rover.move_count = 0
                        new_rover.max_moves = 2
                        units.append(new_rover)
                        # deduct metals
                        dashboard.metals = getattr(dashboard, "metals", 0) - rover_cost
                        set_message("Rover constructed!")
                        show_vehicle_inventory = False
                    else:
                        set_message("Not enough metal for Rover")
                elif action == "buy_drone":
                    drone_cost = 10
                    if getattr(dashboard, "metals", 0) >= drone_cost:
                        vx = vehicle_inventory.vehicle_bay["gx"]
                        vy = vehicle_inventory.vehicle_bay["gy"]
                        vsize = vehicle_inventory.vehicle_bay["size"]
                        # spawn drone inside/above bay
                        spawn_x = (vx + vsize[0] // 2) * TILE_SIZE + TILE_SIZE//2
                        spawn_y = (vy + vsize[1] // 2) * TILE_SIZE - TILE_SIZE
                        new_drone = Drone(spawn_x, spawn_y)
                        new_drone.storage = getattr(new_drone, "storage", 0)
                        new_drone.resources_held = getattr(new_drone, "resources_held", {})
                        new_drone.mining_active = False
                        new_drone.awaiting_move_confirmation = False
                        new_drone.move_count = 0
                        new_drone.max_moves = 2
                        units.append(new_drone)
                        dashboard.metals = getattr(dashboard, "metals", 0) - drone_cost
                        set_message("Drone constructed!")
                        show_vehicle_inventory = False
                    else:
                        set_message("Not enough metal for Drone")
                clicked_ui = True

            # ---------------- Mouse Clicks ---------------- #
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                clicked_on_unit = False

                if event.button == 3:  # Right-click
                    if not clicked_ui:
                        # If any inventory is open, right-click shouldn't affect the world (prevent accidental)
                        # We already forwarded events above; if any inventory visible, don't open unit inventories below.
                        pass

                    # open unit inventory if right-click on unit AND no inventory open
                    if not clicked_ui:
                        for u in units:
                            if u.is_clicked(click_pos):
                                if isinstance(u, Rover):
                                    rover_inventory = RoverInventory(u)
                                    show_rover_inventory = not show_rover_inventory
                                elif isinstance(u, Drone):
                                    drone_inventory = DroneInventory(u)
                                    show_drone_inventory = not show_drone_inventory
                                clicked_on_unit = True
                                break

                    if clicked_on_unit:
                        clicked_ui = True
                        # don't process vehicle bay clicks when we opened a unit inventory
                        continue

                    # Vehicle Bay opening (right-click on building)
                    for b in building_manager.buildings:
                        gx, gy, bsize, b_type = b["gx"], b["gy"], b["size"], b["type"]
                        rect = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, bsize[0] * TILE_SIZE, bsize[1] * TILE_SIZE)
                        if b_type == "Vehicle Bay" and rect.collidepoint(click_pos):
                            vehicle_inventory = VehicleBayInventory(vehicle_bay=b, dashboard=dashboard)
                            show_vehicle_inventory = True
                            clicked_ui = True
                            break

                    # Base click (open base inventory)
                    base_rect_px = pygame.Rect(base.x * TILE_SIZE - base.radius * TILE_SIZE,
                                               base.y * TILE_SIZE - base.radius * TILE_SIZE,
                                               base.radius * 2 * TILE_SIZE, base.radius * 2 * TILE_SIZE)
                    if base_rect_px.collidepoint(click_pos) and not clicked_ui:
                        show_base_inventory = not show_base_inventory
                        clicked_ui = True

                elif event.button == 1:  # Left-click
                    if ignore_next_click:
                        ignore_next_click = False
                        continue

                    # If Stop Controlling button clicked (we draw it later), handled below in main
                    # If Next Round button clicked (dashboard.handle_click) handle round
                    # We will check them in order below.

                    # Stop Controlling button check (we compute rect each frame; we'll compute below when drawing)
                    # We'll just set a flag to handle it after event loop

                    # Dashboard Next Round click
# Dashboard button clicks
                    action = dashboard.handle_click(click_pos)
                    if action == "next_round":
                        # Advance round: reset rover move_count and process mining yields
                        try:
                            # update resources consumption etc
                            new_food = max(dashboard.food - dashboard.population * 2, 0)
                            new_water = max(dashboard.water - dashboard.population * 1, 0)
                            dashboard.update_metrics(food=new_food, water=new_water)
                        except Exception:
                            dashboard.food = max(getattr(dashboard, "food", 0) - getattr(dashboard, "population", 0) * 2, 0)
                            dashboard.water = max(getattr(dashboard, "water", 0) - getattr(dashboard, "population", 0) * 1, 0)

                        # Process mining per-unit
                        for u in units:
                            if getattr(u, "mining_active", False):
                                u.storage = getattr(u, "storage", 0) + 1
                                set_message(f"{u.__class__.__name__} mined 1 unit. Total: {u.storage}", 2.0)

                        # Reset rover/drone move counts for the new round
                        for u in units:
                            u.move_count = 0
                        continue  # skip other left-click handling this frame

                    elif action == "stop_control":
                        selected_unit = None   # deselect currently controlled unit
                        set_message("Stopped controlling unit", 1.5)
                        continue


                    # If any inventory/menu is open, ignore world left-click interactions
                    if show_base_inventory or show_vehicle_inventory or show_rover_inventory or show_drone_inventory:
                        continue

                    gx = click_pos[0] // TILE_SIZE
                    gy = click_pos[1] // TILE_SIZE

                    # Building placement (from base inventory)
                    if placing_building:
                        b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
                        b_size = b_info.get("size", (4, 4))
                        cost = b_info["cost"].get("metals", 0)
                        if getattr(dashboard, "metals", 0) >= cost:
                            if building_manager.add_building(gx, gy, size=b_size, color=(200, 200, 200), b_type=placing_building):
                                # subtract metals using update_metrics if available
                                try:
                                    dashboard.update_metrics(metals=dashboard.metals - cost)
                                except Exception:
                                    dashboard.metals = getattr(dashboard, "metals", 0) - cost
                                set_message(f"Placed {placing_building} at {gx},{gy}")
                                placing_building = None
                            else:
                                set_message("Invalid building spot")
                        else:
                            set_message("Not enough metals")
                    else:
                        # Unit selection and movement (only when no menu open)
                        clicked_on_unit = False
                        for u in units:
                            if u.is_clicked(click_pos):
                                selected_unit = u
                                clicked_on_unit = True
                                break

                        # Issue move command to selected unit (when clicked somewhere else)
                        if not clicked_on_unit and selected_unit:
                            # enforce move limits for rovers/drones
                            if isinstance(selected_unit, Rover) or isinstance(selected_unit, Drone):
                                if getattr(selected_unit, "move_count", 0) >= getattr(selected_unit, "max_moves", 9999):
                                    set_message(f"{selected_unit.__class__.__name__} has no moves left this round")
                                else:
                                    # If mining active, use confirmation like before
                                    if getattr(selected_unit, "mining_active", False):
                                        if not getattr(selected_unit, "awaiting_move_confirmation", False):
                                            set_message("This unit is mining. Click again to move it.")
                                            selected_unit.awaiting_move_confirmation = True
                                        else:
                                            selected_unit.awaiting_move_confirmation = False
                                            selected_unit.mining_active = False
                                            # increment move_count when issuing the move
                                            selected_unit.set_target(click_pos)
                                            selected_unit.move_count = getattr(selected_unit, "move_count", 0) + 1
                                    else:
                                        selected_unit.set_target(click_pos)
                                        selected_unit.move_count = getattr(selected_unit, "move_count", 0) + 1

        # ---------------- Updates ---------------- #
        event_manager.update(dt)
        if rover_inventory:
            rover_inventory.update(resources)
        if drone_inventory:
            drone_inventory.update(resources)
        base_inventory.update()
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.update()

        # Move units (call move on each; your classes implement movement)
        for u in units:
            if isinstance(u, Rover):
                u.move(noise_map, TILE_SIZE, COLS, ROWS, dt)  # Rover consumes power while moving
            else:
                u.move(noise_map, TILE_SIZE, COLS, ROWS)     # Drone movement unchanged

        # ---------------- Draw Everything ---------------- #
        screen.fill((0, 0, 0))
        draw_terrain(screen, noise_map, TILE_SIZE)

        for res in resources:
            for x, y in res.positions:
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, res.color, rect)

        building_manager.draw(screen, TILE_SIZE)
        base.draw(screen, TILE_SIZE)

        # draw units AFTER buildings so they layer above
        for u in units:
            u.draw(screen)

        # preview placement
        if placing_building:
            gx = mouse_pos[0] // TILE_SIZE
            gy = mouse_pos[1] // TILE_SIZE
            b_info = next(b for b in base_inventory.buildings if b["name"] == placing_building)
            b_size = b_info.get("size", (4, 4))
            valid = building_manager.can_place(gx, gy, b_size)
            color = (0, 200, 0) if valid else (200, 0, 0)
            preview_rect = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, b_size[0] * TILE_SIZE, b_size[1] * TILE_SIZE)
            pygame.draw.rect(screen, color, preview_rect, 2)

        # Draw inventories (draw on top)
        if show_rover_inventory and rover_inventory:
            rover_inventory.draw(screen, resources)
        if show_drone_inventory and drone_inventory:
            drone_inventory.draw(screen, resources)
        if show_base_inventory:
            base_inventory.draw(screen)
        if show_vehicle_inventory and vehicle_inventory:
            vehicle_inventory.draw(screen)

        # Draw dashboard and Stop Controlling button (top-right area)
        dashboard.draw(screen)
        # Draw Stop Controlling beneath Next Round, using same button size/style
        try:
            padding = 10
            sw = screen.get_width()
            btn_w = dashboard.button_width
            btn_h = dashboard.button_height
            next_x = sw - btn_w - padding
            stop_y = padding + btn_h + 8
            stop_rect = pygame.Rect(next_x, stop_y, btn_w, btn_h)
            dashboard.stop_control_button = stop_rect  # attach so other code can reference
            # draw red filled and white outline (same style as dashboard)
            pygame.draw.rect(screen, (200, 50, 50), stop_rect, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), stop_rect, 2, border_radius=6)
            btn_font = dashboard.button_font
            txt = btn_font.render("Stop Controlling", True, (255, 255, 255))
            txt_rect = txt.get_rect(center=stop_rect.center)
            screen.blit(txt, txt_rect)
        except Exception:
            # if dashboard doesn't have expected attributes, ignore
            pass

        event_manager.draw(screen)

        # bottom-right message handling
        if bottom_right_message and message_timer > 0:
            msg_font = pygame.font.SysFont("Arial", 20, bold=True)
            msg_text = msg_font.render(bottom_right_message, True, (255, 255, 255))
            screen.blit(msg_text, (WIDTH - msg_text.get_width() - 20, HEIGHT - msg_text.get_height() - 20))
            message_timer -= dt
        elif message_timer <= 0:
            bottom_right_message = ""

        pygame.display.flip()


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

    game_loop()


if __name__ == "__main__":
    main()


# ---------------- Git Commands ---------------- #
# git init
# git add .
# git commit -m "Integrated DroneInventory"
# git push -u origin main
