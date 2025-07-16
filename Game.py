import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 640, 480
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Square Game")

# Set up square(s)
square_size = 50
color = (0, 200, 255)

# Cube state: list of dicts with x, y, dx, dy
cubes = []

# Slider state
slider_x = 100
slider_y = HEIGHT - 40
slider_w = 200
slider_h = 10
slider_handle_w = 20
slider_handle_x = slider_x + 100 # initial position
slider_dragging = False
min_speed = 1
max_speed = 10

# Button state
button_x = slider_x + slider_w + 40
button_y = slider_y - 10
button_w = 120
button_h = 30
button_color = (100, 200, 100)
button_text = "Add Cube"

font = pygame.font.SysFont(None, 28)

# Player state
player_w = 40
player_h = 30
player_x = WIDTH // 2 - player_w // 2
player_y = (HEIGHT - 60) // 2 - player_h // 2
player_speed = 8
player_angle = 0  # Facing up (0 degrees is up)
player_turn_speed = 5  # degrees per frame
player_health = 5
max_health = 5
player_alive = True

# Projectiles: list of dicts with x, y, dx, dy
projectiles = []
projectile_radius = 10
projectile_speed = -12
shoot_cooldown = 0
shoot_cooldown_max = 10

clock = pygame.time.Clock()

# --- Menu State ---
MENU_HOME = 0
MENU_GAME = 1
MENU_SETTINGS = 2
menu_state = MENU_HOME

# Settings defaults
settings_difficulty = 1
slider_dragging = False
slider_drag_offset = 0

def reset_game():
    global player_x, player_y, player_angle, player_health, player_alive, cubes, projectiles, shoot_cooldown, cube_spawn_timer
    player_x = WIDTH // 2 - player_w // 2
    player_y = (HEIGHT - 60) // 2 - player_h // 2
    player_angle = 0
    player_health = max_health
    player_alive = True
    cubes = []
    # Spawn a few cubes at the start based on difficulty
    initial_cubes = 2 + settings_difficulty
    cube_speed = 2 + settings_difficulty
    for _ in range(initial_cubes):
        cubes.append({
            'x': random.randint(60, WIDTH-60),
            'y': random.randint(60, HEIGHT-200),
            'dx': random.choice([-1,1]) * cube_speed,
            'dy': random.choice([-1,1]) * cube_speed
        })
    projectiles = []
    shoot_cooldown = 0
    cube_spawn_timer = 0


cube_spawn_timer = 0
cube_spawn_interval = 60  # Will be set dynamically by difficulty

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --- HOME MENU ---
        if menu_state == MENU_HOME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Start Game button (match draw: x=WIDTH//2-80, y=HEIGHT//2-30, w=160, h=38)
                start_btn_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2-30, 160, 38)
                settings_btn_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+20, 160, 38)
                if start_btn_rect.collidepoint(mx, my):
                    reset_game()
                    menu_state = MENU_GAME
                if settings_btn_rect.collidepoint(mx, my):
                    menu_state = MENU_SETTINGS

        # Draw debug rectangles for HOME menu buttons
        if menu_state == MENU_HOME:
            start_btn_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2-30, 160, 38)
            settings_btn_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+20, 160, 38)
            pygame.draw.rect(win, (255,0,0), start_btn_rect, 2)
            pygame.draw.rect(win, (255,0,0), settings_btn_rect, 2)
            # Green outlines for clickable boxes
            pygame.draw.rect(win, (0,255,0), start_btn_rect, 2)
            pygame.draw.rect(win, (0,255,0), settings_btn_rect, 2)


        # --- SETTINGS MENU ---
        elif menu_state == MENU_SETTINGS:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Difficulty slider handle
                slider_w = 200
                slider_h = 14
                slider_x = WIDTH//2 - 10
                slider_y = HEIGHT//2 - 60 + 16
                slider_handle_w = 32
                slider_min = 1
                slider_max = 10
                slider_handle_x = int(slider_x + (settings_difficulty - slider_min) / (slider_max - slider_min) * (slider_w - slider_handle_w))
                slider_handle_rect = pygame.Rect(slider_handle_x, slider_y-6, slider_handle_w, slider_h+12)
                back_btn = pygame.Rect(WIDTH//2-80, HEIGHT//2+80, 160, 42)
                # Drag slider
                if slider_handle_rect.collidepoint(mx, my):
                    slider_dragging = True
                    slider_drag_offset = mx - slider_handle_x
                # Back button
                if back_btn.collidepoint(mx, my):
                    menu_state = MENU_HOME
            elif event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = False
            elif event.type == pygame.MOUSEMOTION and slider_dragging:
                mx, my = pygame.mouse.get_pos()
                slider_handle_x = mx - slider_drag_offset
                slider_handle_x = max(slider_x, min(slider_handle_x, slider_x + slider_w - slider_handle_w))
                settings_difficulty = int(round(slider_min + (slider_handle_x - slider_x) / (slider_w - slider_handle_w) * (slider_max - slider_min)))

        # Draw debug rectangles for SETTINGS menu buttons
        if menu_state == MENU_SETTINGS:
            # Only draw for slider handle and back button
            slider_handle_rect = pygame.Rect(slider_handle_x, slider_y-6, slider_handle_w, slider_h+12)
            back_btn = pygame.Rect(WIDTH//2-80, HEIGHT//2+80, 160, 42)
            pygame.draw.rect(win, (255,0,0), slider_handle_rect, 2)
            pygame.draw.rect(win, (255,0,0), back_btn, 2)
            pygame.draw.rect(win, (0,255,0), slider_handle_rect, 2)
            pygame.draw.rect(win, (0,255,0), back_btn, 2)



        # --- GAME ---
        elif menu_state == MENU_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Home button
                home_btn = pygame.Rect(10, 10, 80, 30)
                if home_btn.collidepoint(mx, my):
                    menu_state = MENU_HOME
            # Draw green outline for in-game Home button
            home_btn = pygame.Rect(10, 10, 80, 30)
            pygame.draw.rect(win, (0,255,0), home_btn, 2)

            # (rest of game event handling, e.g. slider, etc)

            mx, my = pygame.mouse.get_pos()
            # Start dragging slider
            if (slider_x <= mx <= slider_x + slider_w and
                slider_y - 5 <= my <= slider_y + slider_h + 5):
                slider_dragging = True
            # Button click
            if (button_x <= mx <= button_x + button_w and
                button_y <= my <= button_y + button_h):
                angle = random.uniform(0, 2 * 3.14159)
                cubes.append({
                    'x': random.randint(0, WIDTH - square_size),
                    'y': random.randint(0, HEIGHT - square_size - 60),
                    'dx': int((slider_handle_x - slider_x) / (slider_w - slider_handle_w) * (max_speed - min_speed) + min_speed) * (1 if random.random() > 0.5 else -1),
                    'dy': int((slider_handle_x - slider_x) / (slider_w - slider_handle_w) * (max_speed - min_speed) + min_speed) * (1 if random.random() > 0.5 else -1)
                })
        elif event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
        elif event.type == pygame.MOUSEMOTION and slider_dragging:
            mx, my = pygame.mouse.get_pos()
            slider_handle_x = max(slider_x, min(mx, slider_x + slider_w - slider_handle_w))

    # Player movement
    keys = pygame.key.get_pressed()
    if player_alive:
        # Rotate
        if keys[pygame.K_LEFT]:
            player_angle = (player_angle - player_turn_speed) % 360
        if keys[pygame.K_RIGHT]:
            player_angle = (player_angle + player_turn_speed) % 360
        # Move forward/backward
        import math
        rad = math.radians(player_angle - 90)
        # Compute tip position for direction
        center = (player_x + player_w // 2, player_y + player_h // 2)
        tip_offset = (0, -player_h // 2)
        tip_x = center[0] + tip_offset[0] * math.cos(rad) - tip_offset[1] * math.sin(rad)
        tip_y = center[1] + tip_offset[0] * math.sin(rad) + tip_offset[1] * math.cos(rad)
        dx = (tip_x - center[0]) / (player_h // 2) * player_speed
        dy = (tip_y - center[1]) / (player_h // 2) * player_speed
        if keys[pygame.K_UP]:
            player_x += dx
            player_y += dy
        if keys[pygame.K_DOWN]:
            player_x -= dx
            player_y -= dy
        # Clamp player within window (above UI area)
        player_x = max(0, min(player_x, WIDTH - player_w))
        player_y = max(0, min(player_y, HEIGHT - 60 - player_h))
        # Shooting
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            # Spawn at tip of triangle (red tip)
            proj_x = tip_x
            proj_y = tip_y
            proj_dx = (tip_x - center[0]) / (player_h // 2) * abs(projectile_speed)
            proj_dy = (tip_y - center[1]) / (player_h // 2) * abs(projectile_speed)
            projectiles.append({'x': proj_x, 'y': proj_y, 'dx': proj_dx, 'dy': proj_dy})
            shoot_cooldown = shoot_cooldown_max
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

    # Update projectiles
    for proj in projectiles:
        proj['x'] += proj['dx']
        proj['y'] += proj['dy']
        # Bounce off walls
        if proj['x'] - projectile_radius <= 0 or proj['x'] + projectile_radius >= WIDTH:
            proj['dx'] *= -1
            proj['x'] = max(projectile_radius, min(proj['x'], WIDTH - projectile_radius))
        if proj['y'] - projectile_radius <= 0:
            proj['dy'] *= -1
            proj['y'] = projectile_radius
        if proj['y'] + projectile_radius >= HEIGHT - 60:
            proj['dy'] *= -1
            proj['y'] = HEIGHT - 60 - projectile_radius

    # Remove projectiles that are out of bounds (bottom only)
    projectiles = [p for p in projectiles if p['y'] + projectile_radius > 0]

    # Calculate speed from slider
    speed = int((slider_handle_x - slider_x) / (slider_w - slider_handle_w) * (max_speed - min_speed) + min_speed)
    if speed == 0:
        speed = 1
    # Update all cubes with the new speed, preserving direction
    for cube in cubes:
        cube['dx'] = speed if cube['dx'] > 0 else -speed
        cube['dy'] = speed if cube['dy'] > 0 else -speed
        cube['x'] += cube['dx']
        cube['y'] += cube['dy']
        # Bounce off edges
        if cube['x'] <= 0 or cube['x'] + square_size >= WIDTH:
            cube['dx'] *= -1
            # Clamp inside invisible wall
            cube['x'] = max(0, min(cube['x'], WIDTH - square_size))
        if cube['y'] <= 0 or cube['y'] + square_size >= HEIGHT - 60:
            cube['dy'] *= -1
            # Clamp inside invisible wall
            cube['y'] = max(0, min(cube['y'], HEIGHT - 60 - square_size))

    # Handle cube-cube collisions (AABB)
    for i in range(len(cubes)):
        for j in range(i + 1, len(cubes)):
            a = cubes[i]
            b = cubes[j]
            if (a['x'] < b['x'] + square_size and
                a['x'] + square_size > b['x'] and
                a['y'] < b['y'] + square_size and
                a['y'] + square_size > b['y']):
                # Swap velocities for a more realistic bounce
                a['dx'], b['dx'] = b['dx'], a['dx']
                a['dy'], b['dy'] = b['dy'], a['dy']
                # Resolve overlap by minimal displacement
                overlap_x = min(a['x'] + square_size - b['x'], b['x'] + square_size - a['x'])
                overlap_y = min(a['y'] + square_size - b['y'], b['y'] + square_size - a['y'])
                if overlap_x < overlap_y:
                    # Separate along x axis
                    if a['x'] < b['x']:
                        a['x'] -= overlap_x // 2
                        b['x'] += overlap_x // 2
                    else:
                        a['x'] += overlap_x // 2
                        b['x'] -= overlap_x // 2
                else:
                    # Separate along y axis
                    if a['y'] < b['y']:
                        a['y'] -= overlap_y // 2
                        b['y'] += overlap_y // 2
                    else:
                        a['y'] += overlap_y // 2
                        b['y'] -= overlap_y // 2

    # Handle projectile-cube collisions
    new_projectiles = []
    new_cubes = []
    for cube in cubes:
        hit = False
        for proj in projectiles:
            # Circle-rectangle collision
            cx, cy = proj['x'], proj['y']
            rx, ry, rw, rh = cube['x'], cube['y'], square_size, square_size
            closest_x = max(rx, min(cx, rx + rw))
            closest_y = max(ry, min(cy, ry + rh))
            dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
            if dist_sq < projectile_radius ** 2:
                hit = True
                break
        if not hit:
            new_cubes.append(cube)
    for proj in projectiles:
        destroyed = False
        for cube in cubes:
            cx, cy = proj['x'], proj['y']
            rx, ry, rw, rh = cube['x'], cube['y'], square_size, square_size
            closest_x = max(rx, min(cx, rx + rw))
            closest_y = max(ry, min(cy, ry + rh))
            dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
            if dist_sq < projectile_radius ** 2:
                destroyed = True
                break
        if not destroyed:
            new_projectiles.append(proj)
    cubes = new_cubes
    projectiles = new_projectiles

    # Handle player-cube collisions (triangle-AABB, use bounding box)
    if player_alive:
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        for cube in cubes:
            cube_rect = pygame.Rect(cube['x'], cube['y'], square_size, square_size)
            if player_rect.colliderect(cube_rect):
                player_health -= 1
                # Reset cube to random top position
                cube['x'] = random.randint(0, WIDTH - square_size)
                cube['y'] = random.randint(0, HEIGHT // 8)
                if player_health <= 0:
                    player_alive = False

    win.fill((30, 30, 30))
    if menu_state == MENU_HOME:
        # Home Screen
        win.fill((25, 27, 37))
        big_font = pygame.font.SysFont(None, 48, bold=True)
        med_font = pygame.font.SysFont(None, 36, bold=True)
        small_font = pygame.font.SysFont(None, 28)
        # Panel background
        panel_rect = pygame.Rect(WIDTH//2-150, HEIGHT//2-110, 300, 220)
        pygame.draw.rect(win, (40, 44, 60), panel_rect, border_radius=18)
        pygame.draw.rect(win, (80, 90, 120), panel_rect, 3, border_radius=18)
        title = big_font.render("Bouncing Square Game", True, (255,255,255))
        win.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
        # Start Game button
        start_btn = pygame.Rect(WIDTH//2-90, HEIGHT//2-20, 180, 40)
        pygame.draw.rect(win, (60,220,120), start_btn, border_radius=10)
        pygame.draw.rect(win, (40,170,90), start_btn, 3, border_radius=10)
        start_text = med_font.render("Start Game", True, (20,20,20))
        win.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2-14))
        # Settings button
        set_btn = pygame.Rect(WIDTH//2-90, HEIGHT//2+40, 180, 40)
        pygame.draw.rect(win, (100,150,240), set_btn, border_radius=10)
        pygame.draw.rect(win, (60,90,160), set_btn, 3, border_radius=10)
        set_text = med_font.render("Settings", True, (20,20,20))
        win.blit(set_text, (WIDTH//2 - set_text.get_width()//2, HEIGHT//2+46))
        pygame.display.update()
    elif menu_state == MENU_SETTINGS:
        # Settings Screen
        win.fill((25, 27, 37))
        big_font = pygame.font.SysFont(None, 48, bold=True)
        med_font = pygame.font.SysFont(None, 36, bold=True)
        small_font = pygame.font.SysFont(None, 28)
        # Make the panel larger for better spacing
        panel_rect = pygame.Rect(WIDTH//2-260, HEIGHT//2-200, 520, 400)
        pygame.draw.rect(win, (40, 44, 60), panel_rect, border_radius=26)
        pygame.draw.rect(win, (80, 90, 120), panel_rect, 4, border_radius=26)
        stitle = big_font.render("Settings", True, (255,255,255))
        win.blit(stitle, (WIDTH//2 - stitle.get_width()//2, HEIGHT//2 - 150))
        # Difficulty slider row
        row_y = HEIGHT//2 - 50
        diff_label = med_font.render("Difficulty:", True, (220,220,220))
        diff_label_x = WIDTH//2 - 200
        diff_label_y = row_y + 8
        win.blit(diff_label, (diff_label_x, diff_label_y))
        slider_w = 260
        slider_h = 14
        slider_x = WIDTH//2 - 30
        slider_y = row_y + 16
        slider_handle_w = 36
        slider_min = 1
        slider_max = 10
        slider_handle_x = int(slider_x + (settings_difficulty - slider_min) / (slider_max - slider_min) * (slider_w - slider_handle_w))
        slider_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
        slider_handle_rect = pygame.Rect(slider_handle_x, slider_y-8, slider_handle_w, slider_h+16)
        pygame.draw.rect(win, (180,180,180), slider_rect, border_radius=8)
        pygame.draw.rect(win, (120,255,120), slider_handle_rect, border_radius=10)
        diff_val = med_font.render(str(settings_difficulty), True, (120,255,120))
        win.blit(diff_val, (slider_x + slider_w + 30, slider_y - 6))
        # Back button
        back_btn = pygame.Rect(WIDTH//2-90, HEIGHT//2+100, 180, 48)
        pygame.draw.rect(win, (160,160,160), back_btn, border_radius=14)
        pygame.draw.rect(win, (100,100,100), back_btn, 2, border_radius=14)
        back_text = med_font.render("Back", True, (40,40,40))
        win.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT//2+112))
        pygame.display.update()

    # --- Difficulty slider interaction logic ---
    if menu_state == MENU_SETTINGS:
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mx, my = pygame.mouse.get_pos()
        if mouse_pressed and slider_handle_rect.collidepoint(mx, my):
            slider_dragging = True
            slider_drag_offset = mx - slider_handle_x
        elif not mouse_pressed:
            slider_dragging = False
        if slider_dragging:
            slider_handle_x = mx - slider_drag_offset
            slider_handle_x = max(slider_x, min(slider_handle_x, slider_x + slider_w - slider_handle_w))
            settings_difficulty = int(round(slider_min + (slider_handle_x - slider_x) / (slider_w - slider_handle_w) * (slider_max - slider_min)))

    elif menu_state == MENU_GAME:
        # Draw Home button
        pygame.draw.rect(win, (220,220,220), (10,10,80,30))
        home_text = small_font.render("Home", True, (0,0,0))
        win.blit(home_text, (22, 16))

        # Draw cubes
        for cube in cubes:
            pygame.draw.rect(win, color, (cube['x'], cube['y'], square_size, square_size))
        # Draw projectiles
        for proj in projectiles:
            pygame.draw.circle(win, (0, 255, 0), (int(proj['x']), int(proj['y'])), projectile_radius)
        # Draw player (rotated triangle)
        import math
        center = (player_x + player_w // 2, player_y + player_h // 2)
        angle_rad = math.radians(player_angle - 90)
        # Outer (yellow) triangle
        rel_points = [
            (0, -player_h // 2),  # tip
            (-player_w // 2, player_h // 2),  # left
            (player_w // 2, player_h // 2)    # right
        ]
        rot_points = []
        for px, py in rel_points:
            rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
            ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
            rot_points.append((center[0] + rx, center[1] + ry))
        pygame.draw.polygon(win, (255, 255, 0), rot_points)
        # Inner (red) triangle for front direction (tip-aligned)
        red_base_offset = player_h * 0.45  # base closer to center
        red_base_width = player_w * 0.3
        red_tip = (0, -player_h // 2)  # exactly at yellow tip
        red_left = (-red_base_width / 2, -player_h // 2 + red_base_offset)
        red_right = (red_base_width / 2, -player_h // 2 + red_base_offset)
        red_rel_points = [red_tip, red_left, red_right]
        red_rot_points = []
        for px, py in red_rel_points:
            rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
            ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
            red_rot_points.append((center[0] + rx, center[1] + ry))
        pygame.draw.polygon(win, (255, 40, 40), red_rot_points)

        # Draw health bar
        health_bar_w = 120
        health_bar_h = 16
        health_x = 10
        health_y = 50
        pygame.draw.rect(win, (80, 80, 80), (health_x, health_y, health_bar_w, health_bar_h))
        health_fill_w = int(health_bar_w * player_health / max_health)
        pygame.draw.rect(win, (255, 60, 60), (health_x, health_y, health_fill_w, health_bar_h))
        health_text = font.render(f"Health: {player_health}", True, (255,255,255))
        win.blit(health_text, (health_x + health_bar_w + 10, health_y))
        # Draw Game Over
        if not player_alive:
            over_text = font.render("Game Over!", True, (255, 0, 0))
            win.blit(over_text, (WIDTH // 2 - 60, HEIGHT // 2 - 20))
        # No Add Cube button
    pygame.display.update()
    clock.tick(60)