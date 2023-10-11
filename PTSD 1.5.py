import pygame
import sys
import math
import random

# Here's a comment, scrub
print("deez nuts")

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (222, 222, 222)
TOWER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)
PROJECTILE_COLOR = (0, 255, 0)
ATTACK_RANGE_COLOR = (0, 255, 0)
HEALTH_BAR_COLOR = (0, 255, 0)

# Are these really constants? Are they going to buffed or upgraded later?
# If so, these can stay constants, but be modified by other values later
ATTACK_RANGE_RADIUS = 100
TOWER_DPS = 1
ENEMY_HEALTH = 1
TOWER_COST = 5
ENEMY_REWARD = 1
PLAYER_HEALTH = 10
MAX_ENEMIES = 10
SPAWN_INTERVAL = 500  # 0.5 seconds in milliseconds
ROUND_DURATION = 20000  # 15 seconds in milliseconds
TRACK_WIDTH = 100  # Width of the enemy track
BORDER_COLOR = (0, 0, 0)  # Color of the track boundaries and map edge
TOWER_DISTANCE = 45  # Minimum distance between towers
TOWER_AREA_COLOR = (200, 200, 200)  # Light grey color for tower placement area
TRACK_COLOR = (210, 180, 140)  # Light brown color for the track

# Constants - Buy button
BUY_BUTTON_COLOR = (150, 150, 150)
BUY_BUTTON_HOVER_COLOR = (200, 200, 200)
BUY_BUTTON_WIDTH = 100
BUY_BUTTON_HEIGHT = 50
BUY_BUTTON_X = SCREEN_WIDTH - BUY_BUTTON_WIDTH - 10
BUY_BUTTON_Y = SCREEN_HEIGHT - BUY_BUTTON_HEIGHT - 10
BUY_BUTTON_TEXT = "BUY"

# Enemy info
ENEMY_SIZE = 20
ENEMY_SPEED = 8
ENEMY_PATH = [
    {'x': TRACK_WIDTH/2 + ENEMY_SIZE/2, 'y': TRACK_WIDTH/2 + ENEMY_SIZE/2, 'dx': ENEMY_SPEED, 'dy': 0},  # Start (top-left) to top-right
    {'x': SCREEN_WIDTH - TRACK_WIDTH/2 - ENEMY_SIZE/2, 'y': TRACK_WIDTH/2 + ENEMY_SIZE/2, 'dx': 0, 'dy': ENEMY_SPEED},  # Top-right to bottom-right
    {'x': SCREEN_WIDTH - TRACK_WIDTH/2 - ENEMY_SIZE/2, 'y': SCREEN_HEIGHT - TRACK_WIDTH/2 - ENEMY_SIZE/2, 'dx': -ENEMY_SPEED, 'dy': 0},  # Bottom-right to bottom-left
    {'x': TRACK_WIDTH/2 + ENEMY_SIZE/2, 'y': SCREEN_HEIGHT - TRACK_WIDTH/2 - ENEMY_SIZE/2, 'dx': 0, 'dy': -ENEMY_SPEED},  # Bottom-left to top-left
    {'x': TRACK_WIDTH/2 + ENEMY_SIZE/2, 'y': TRACK_WIDTH/2 + ENEMY_SIZE/2, 'dx': ENEMY_SPEED, 'dy': 0}  # Top-left back to start (top-right)
]
class TowerTier:
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3

TOWER_COLORS = {
    TowerTier.TIER_1: (255, 255, 255),  # White
    TowerTier.TIER_2: (0, 0, 255),      # Blue
    TowerTier.TIER_3: (255, 255, 0)     # Yellow
}

TOWER_DPS_VALUES = {
    TowerTier.TIER_1: 1,
    TowerTier.TIER_2: 3,
    TowerTier.TIER_3: 7
}
def spawn_tower(tier):
    while True:
        x = random.choice([random.randint(0, TRACK_WIDTH), random.randint(SCREEN_WIDTH - TRACK_WIDTH, SCREEN_WIDTH)])
        y = random.randint(0, SCREEN_HEIGHT)
        if not any([math.sqrt((t['x'] - x)**2 + (t['y'] - y)**2) < TOWER_DISTANCE for t in towers]):
            towers.append({'x': x, 'y': y, 'tier': tier})
            break

def tower_posn(x, y, towers):
    # Check if the position is within the field and not on the track
    if x < TRACK_WIDTH or x > SCREEN_WIDTH - TRACK_WIDTH or y < TRACK_WIDTH or y > SCREEN_HEIGHT - TRACK_WIDTH:
        return False
    # Check if the position is too close to existing towers
    for tower in towers:
        distance = math.sqrt((tower['x'] - x)**2 + (tower['y'] - y)**2)
        if distance < TOWER_DISTANCE:
            return False
    return True

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pixel Tower Defense')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Game variables
towers = []
enemies = []
projectiles = []
player_money = 30
player_health = PLAYER_HEALTH
enemies_spawned = 0
level = 1
spawn_timer = 0
round_timer = 0
bonus_message_timer = 0
bonus_message = ""
killcount = 0
selected_towers = []

while True:
    dt = clock.tick(60)
    spawn_timer += dt
    round_timer += dt
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_hovered = BUY_BUTTON_X <= mouse_x <= BUY_BUTTON_X + BUY_BUTTON_WIDTH and BUY_BUTTON_Y <= mouse_y <= BUY_BUTTON_Y + BUY_BUTTON_HEIGHT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and button_hovered:
            if player_money >= 1:
                player_money -= 1
                tier_chance = random.random()
            if tier_chance < 0.5:
                tier = 2
            else:
                tier = 1
            # Spawn the tower at a random location within the field
            attempts = 0
            while attempts < 100:  # Try up to 100 times to find a valid position
                x = random.randint(TRACK_WIDTH, SCREEN_WIDTH - TRACK_WIDTH - 40)
                y = random.randint(TRACK_WIDTH, SCREEN_HEIGHT - TRACK_WIDTH - 40)
                if tower_posn(x, y, towers):
                    towers.append({'x': x, 'y': y, 'tier': tier})
                    break
            attempts += 1
            """
            # Spawn the tower at a random location along the field/track border
            x, y = random.choice([
                (random.randint(0, SCREEN_WIDTH - 40), TRACK_WIDTH - 40),
                (random.randint(0, SCREEN_WIDTH - 40), SCREEN_HEIGHT - TRACK_WIDTH),
                (TRACK_WIDTH - 40, random.randint(0, SCREEN_HEIGHT - 40)),
                (SCREEN_WIDTH - TRACK_WIDTH, random.randint(0, SCREEN_HEIGHT - 40))
            ])
            towers.append({'x': x, 'y': y, 'tier': tier})
            """

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                towers = []
                enemies = []
                projectiles = []
                player_health = PLAYER_HEALTH
                enemies_spawned = 0
                if player_money > 30:
                    player_money += 5
                else:
                    player_money = 30
                level = 1
                spawn_timer = 0
                round_timer = 0
    # Spawn enemies at intervals
    if spawn_timer >= SPAWN_INTERVAL and enemies_spawned < MAX_ENEMIES:
        new_enemy = {'x': ENEMY_PATH[0]['x'], 'y': ENEMY_PATH[0]['y'], 'speed': 10, 'health': ENEMY_HEALTH, 'path_index': 0}
        enemies.append(new_enemy)
        enemies_spawned += 1
        spawn_timer = 0
    
    # Check round duration
    if round_timer > 21000:  # 20 seconds
        player_health -= len(enemies)  # Player loses health for each remaining enemy
        enemies = []  # Despawn all enemies
        killcount = 0
        enemies_spawned = 0
        if player_health <= 0:
            print('Game Over!')
            pygame.quit()
            sys.exit()
        else:
            bonus_money = (20000 - round_timer) // 1000  # $1 for every extra second
            player_money += bonus_money
            level += 1
            enemies_spawned = 0
            spawn_timer = 0
            round_timer = 0
            print("Goodbye")
            
    
    spawn_timer += dt
    round_timer += dt
    """
    bonus_message_timer += dt
    if bonus_message_timer > 2000:
        bonus_message = ""
        bonus_message_timer = 0
        """
    for enemy in enemies:
        segment = ENEMY_PATH[enemy['path_index']]
        enemy['x'] += segment['dx']
        enemy['y'] += segment['dy']

        next_segment = ENEMY_PATH[(enemy['path_index'] + 1) % len(ENEMY_PATH)]
        if (segment['dx'] > 0 and enemy['x'] >= next_segment['x']) or \
           (segment['dx'] < 0 and enemy['x'] <= next_segment['x']) or \
           (segment['dy'] > 0 and enemy['y'] >= next_segment['y']) or \
           (segment['dy'] < 0 and enemy['y'] <= next_segment['y']):
            enemy['path_index'] = (enemy['path_index'] + 1) % len(ENEMY_PATH)

    for tower in towers:
        for enemy in enemies[:]:
            distance = math.sqrt((tower['x'] - enemy['x'])**2 + (tower['y'] - enemy['y'])**2)
            if distance <= ATTACK_RANGE_RADIUS:
                enemy['health'] -= TOWER_DPS / 60  # Assuming 60 FPS
                projectiles.append({'x': tower['x'] + 20, 'y': tower['y'] + 20, 'target_x': enemy['x'], 'target_y': enemy['y'], 'speed': 5})
                if enemy['health'] <= 0:
                    enemies.remove(enemy)
                    player_money += ENEMY_REWARD
                    killcount +=1
                    if killcount == enemies_spawned:
                        bonus_money = (ROUND_DURATION - round_timer) // 1000  # $1 for every extra second
                        player_money += bonus_money
                        enemies_spawned = 0
                        killcount = 0
                        spawn_timer = 0
                        #round_timer = ROUND_DURATION
                        round_timer = ROUND_DURATION
                        bonus_message = f"Bonus Cash: ${bonus_money}"
                        print("Hello")
                        
    

    to_remove = []
    for projectile in projectiles[:]:
        dx = projectile['target_x'] - projectile['x']
        dy = projectile['target_y'] - projectile['y']
        dist = math.sqrt(dx**2 + dy**2)

        if dist == 0:
            projectiles.remove(projectile)
            continue

        dx /= dist
        dy /= dist
        projectile['x'] += dx * projectile['speed']
        projectile['y'] += dy * projectile['speed']

        # Check if the projectile has reached or overshot its target
        new_dist = math.sqrt((projectile['x'] - projectile['target_x'])**2 + (projectile['y'] - projectile['target_y'])**2)
        if new_dist > dist:
            projectiles.remove(projectile)
        
        # Check if the projectile has reached or overshot its target
        if (dx > 0 and projectile['x'] > projectile['target_x']) or (dx < 0 and projectile['x'] < projectile['target_x']) or \
           (dy > 0 and projectile['y'] > projectile['target_y']) or (dy < 0 and projectile['y'] < projectile['target_y']):
            if dist <= 0:
                to_remove.append(projectile)
                continue
                for projectile in to_remove:
                    if projectile in projectiles:
                        projectiles.remove(projectile)

    # Render game state
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, TRACK_COLOR, (0, 0, SCREEN_WIDTH, TRACK_WIDTH))
    pygame.draw.rect(screen, TRACK_COLOR, (0, SCREEN_HEIGHT - TRACK_WIDTH, SCREEN_WIDTH, TRACK_WIDTH))
    pygame.draw.rect(screen, TRACK_COLOR, (0, 0, TRACK_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, TRACK_COLOR, (SCREEN_WIDTH - TRACK_WIDTH, 0, TRACK_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(screen, BORDER_COLOR, (0, TRACK_WIDTH), (SCREEN_WIDTH, TRACK_WIDTH), 2)
    for tower in towers:
        pygame.draw.rect(screen, TOWER_COLOR, (tower['x'], tower['y'], 40, 40))
        pygame.draw.circle(screen, ATTACK_RANGE_COLOR, (tower['x'] + 20, tower['y'] + 20), ATTACK_RANGE_RADIUS, 2)
        pygame.draw.rect(screen, TOWER_COLORS[tower['tier']], (tower['x'], tower['y'], 40, 40))
    for enemy in enemies:
        pygame.draw.circle(screen, ENEMY_COLOR, (enemy['x'], enemy['y']), 20)
        pygame.draw.rect(screen, HEALTH_BAR_COLOR, (enemy['x'] - 20, enemy['y'] - 30, 40 * (enemy['health'] / ENEMY_HEALTH), 5))
    for projectile in projectiles:
        pygame.draw.circle(screen, PROJECTILE_COLOR, (int(projectile['x']), int(projectile['y'])), 5)
    """
    if bonus_message:
        bonus_text = font.render(bonus_message, True, (0, 0, 0))
        screen.blit(bonus_text, (SCREEN_WIDTH // 2 - bonus_text.get_width() // 2, SCREEN_HEIGHT // 2 - bonus_text.get_height() // 2))
        """
    # UI Render
    money_text = pygame.font.SysFont(None, 36).render(f'Money: ${player_money}', True, (0, 0, 0))
    health_text = pygame.font.SysFont(None, 36).render(f'Health: {player_health}', True, (0, 0, 0))
    level_text = pygame.font.SysFont(None, 36).render(f'Level: {level}', True, (0, 0, 0))
    screen.blit(money_text, (10, 10))
    screen.blit(health_text, (10, 50))
    screen.blit(level_text, (10, 90))
    time_left = (ROUND_DURATION - round_timer) / 1000
    timer_text = font.render(f'Time Left: {time_left:.2f}', True, (0, 0, 0))
    text_width, text_height = font.size(f'Time Left: {time_left:.2f}')
    screen.blit(timer_text, ((SCREEN_WIDTH - text_width) // 2, 10))
    # Render the buy button
    if button_hovered:
        pygame.draw.rect(screen, BUY_BUTTON_HOVER_COLOR, (BUY_BUTTON_X, BUY_BUTTON_Y, BUY_BUTTON_WIDTH, BUY_BUTTON_HEIGHT))
    else:
        pygame.draw.rect(screen, BUY_BUTTON_COLOR, (BUY_BUTTON_X, BUY_BUTTON_Y, BUY_BUTTON_WIDTH, BUY_BUTTON_HEIGHT))
    button_font = pygame.font.SysFont(None, 24)
    button_label = button_font.render(BUY_BUTTON_TEXT, True, (0, 0, 0))
    screen.blit(button_label, (BUY_BUTTON_X + (BUY_BUTTON_WIDTH - button_label.get_width()) // 2, BUY_BUTTON_Y + (BUY_BUTTON_HEIGHT - button_label.get_height()) // 2))

    button_label = button_font.render(BUY_BUTTON_TEXT, True, (0, 0, 0))
    screen.blit(button_label, (BUY_BUTTON_X + (BUY_BUTTON_WIDTH - button_label.get_width()) // 2, BUY_BUTTON_Y + (BUY_BUTTON_HEIGHT - button_label.get_height()) // 2))

    
    # Draw the track and tower area
    pygame.display.flip()
    clock.tick(60)
