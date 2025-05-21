import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 1
JUMP_POWER = -15
PLAYER_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PLATFORM_COLORS = [GREEN, BLUE, (100, 100, 255), (255, 100, 100)]

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Amazing Platformer")
clock = pygame.time.Clock()

# Load images (using simple rectangles for now)
def load_images():
    images = {
        'player': pygame.Surface((30, 50)),
        'platform': pygame.Surface((100, 20)),
        'coin': pygame.Surface((15, 15)),
        'enemy': pygame.Surface((30, 30))
    }
    
    images['player'].fill(RED)
    images['platform'].fill(GREEN)
    images['coin'].fill(YELLOW)
    images['enemy'].fill((255, 0, 255))
    
    return images

class Player(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.image = images['player']
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.score = 0
        
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Move horizontally
        self.rect.x += self.velocity_x
        
        # Check for horizontal collisions with screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            
        # Move vertically
        self.rect.y += self.velocity_y
        
        # Check if we're on a platform
        self.on_ground = False
        for platform in platforms:
            if self.rect.bottom >= platform.rect.top and self.rect.bottom <= platform.rect.top + self.velocity_y and \
               self.rect.right > platform.rect.left and self.rect.left < platform.rect.right:
                self.rect.bottom = platform.rect.top
                self.on_ground = True
                self.velocity_y = 0
        
        # Check for vertical collisions with screen boundaries
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0
    
    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_POWER
            
    def move_left(self):
        self.velocity_x = -PLAYER_SPEED
        
    def move_right(self):
        self.velocity_x = PLAYER_SPEED
        
    def stop(self):
        self.velocity_x = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, images, color=None):
        super().__init__()
        self.image = pygame.transform.scale(images['platform'], (width, 20))
        if color:
            self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.image = images['coin']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, images, min_x, max_x):
        super().__init__()
        self.image = images['enemy']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        
    def update(self):
        self.rect.x += self.speed * self.direction
        
        if self.rect.x <= self.min_x:
            self.direction = 1
        elif self.rect.x >= self.max_x:
            self.direction = -1

def create_level(images):
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Create ground
    ground = Platform(0, HEIGHT - 20, WIDTH, images)
    platforms.add(ground)
    
    # Create platforms
    platform_positions = [
        (100, 450, 200),
        (400, 400, 150),
        (200, 350, 100),
        (500, 300, 200),
        (100, 250, 150),
        (400, 200, 100),
        (200, 150, 200),
        (600, 150, 150),
        (300, 100, 100)
    ]
    
    for i, (x, y, width) in enumerate(platform_positions):
        color = PLATFORM_COLORS[i % len(PLATFORM_COLORS)]
        platform = Platform(x, y, width, images, color)
        platforms.add(platform)
        
        # Add coins on some platforms
        if i % 2 == 0:
            coin = Coin(x + width // 2, y - 30, images)
            coins.add(coin)
        
        # Add enemies on some platforms
        if i % 3 == 0:
            enemy = Enemy(x + 20, y - 30, images, x, x + width - 30)
            enemies.add(enemy)
    
    return platforms, coins, enemies

def game_over_screen(score):
    font = pygame.font.SysFont(None, 64)
    text = font.render(f"Game Over! Score: {score}", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    restart_font = pygame.font.SysFont(None, 32)
    restart_text = restart_font.render("Press R to restart or Q to quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        screen.fill(BLACK)
        screen.blit(text, text_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()
        clock.tick(FPS)

def main():
    images = load_images()
    
    while True:
        # Initialize game objects
        player = Player(images)
        platforms, coins, enemies = create_level(images)
        
        # Game variables
        running = True
        game_over = False
        
        # Main game loop
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_LEFT:
                        player.move_left()
                    if event.key == pygame.K_RIGHT:
                        player.move_right()
                
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        player.stop()
            
            # Update game objects
            player.update(platforms)
            enemies.update()
            
            # Check for coin collisions
            coin_collisions = pygame.sprite.spritecollide(player, coins, True)
            for coin in coin_collisions:
                player.score += 10
            
            # Check for enemy collisions
            enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
            if enemy_collisions:
                game_over = True
                running = False
            
            # Draw everything
            screen.fill(BLACK)
            
            # Draw score
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {player.score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            # Draw sprites
            platforms.draw(screen)
            coins.draw(screen)
            enemies.draw(screen)
            screen.blit(player.image, player.rect)
            
            pygame.display.flip()
            clock.tick(FPS)
        
        # Game over, show screen
        restart = game_over_screen(player.score)
        if not restart:
            break

if __name__ == "__main__":
    main()
