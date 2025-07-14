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
cubes = [{
    'x': WIDTH // 2,
    'y': HEIGHT // 2,
    'dx': 3,
    'dy': 2
}]

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
player_x = WIDTH // 2
player_y = HEIGHT - 80
player_speed = 8
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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
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
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        player_x = max(0, min(player_x, WIDTH - player_w))
        # Shooting
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            proj_x = player_x + player_w // 2
            proj_y = player_y
            projectiles.append({'x': proj_x, 'y': proj_y, 'dx': 0, 'dy': projectile_speed})
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

    # Draw everything
    win.fill((30, 30, 30))
    # Draw cubes
    for cube in cubes:
        pygame.draw.rect(win, color, (cube['x'], cube['y'], square_size, square_size))
    # Draw projectiles
    for proj in projectiles:
        pygame.draw.circle(win, (0, 255, 0), (int(proj['x']), int(proj['y'])), projectile_radius)
    # Draw player (triangle)
    player_points = [
        (player_x + player_w // 2, player_y),  # top
        (player_x, player_y + player_h),       # bottom left
        (player_x + player_w, player_y + player_h)  # bottom right
    ]
    pygame.draw.polygon(win, (255, 255, 0), player_points)
    # Draw health bar
    health_bar_w = 120
    health_bar_h = 16
    health_x = 10
    health_y = 10
    pygame.draw.rect(win, (80, 80, 80), (health_x, health_y, health_bar_w, health_bar_h))
    health_fill_w = int(health_bar_w * player_health / max_health)
    pygame.draw.rect(win, (255, 60, 60), (health_x, health_y, health_fill_w, health_bar_h))
    health_text = font.render(f"Health: {player_health}", True, (255,255,255))
    win.blit(health_text, (health_x + health_bar_w + 10, health_y))
    # Draw Game Over
    if not player_alive:
        over_text = font.render("Game Over!", True, (255, 0, 0))
        win.blit(over_text, (WIDTH // 2 - 60, HEIGHT // 2 - 20))
    # Draw slider bar
    pygame.draw.rect(win, (180, 180, 180), (slider_x, slider_y, slider_w, slider_h))
    pygame.draw.rect(win, (100, 100, 255), (slider_handle_x, slider_y - 5, slider_handle_w, slider_h + 10))
    # Draw slider label
    speed_label = font.render(f"Speed: {speed}", True, (255, 255, 255))
    win.blit(speed_label, (slider_x, slider_y - 28))
    # Draw button
    pygame.draw.rect(win, button_color, (button_x, button_y, button_w, button_h))
    btn_label = font.render(button_text, True, (0, 0, 0))
    win.blit(btn_label, (button_x + 10, button_y + 5))
    pygame.display.flip()
    clock.tick(60)