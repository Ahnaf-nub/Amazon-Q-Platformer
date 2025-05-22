import pygame
import sys
import random
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Pixel Adventure"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)         # Dodger Blue
GREEN = (50, 205, 50)         # Lime Green
RED = (255, 69, 0)            # Red-Orange
PURPLE = (147, 112, 219)      # Medium Purple
SKYBLUE = (100, 149, 237)     # Cornflower Blue
YELLOW = (255, 215, 0)        # Gold
PINK = (255, 105, 180)        # Hot Pink
ORANGE = (255, 140, 0)        # Dark Orange
TEAL = (0, 206, 209)          # Dark Turquoise

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = -16

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Load assets
def load_image(name, scale=1):
    try:
        image = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(image, 
                                     (int(image.get_width() * scale), 
                                      int(image.get_height() * scale)))
    except pygame.error:
        print(f"Cannot load image: {name}")
        return pygame.Surface((32, 32))

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')
    os.makedirs('assets/images')
    os.makedirs('assets/sounds')

# Placeholder for images
player_img = pygame.Surface((32, 48))
player_img.fill(BLUE)
platform_img = pygame.Surface((96, 16))
platform_img.fill(GREEN)
coin_img = pygame.Surface((16, 16))
coin_img.fill(YELLOW)
enemy_img = pygame.Surface((32, 32))
enemy_img.fill(RED)

# Game classes
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.pos = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.facing_right = True
        self.jumping = False
        self.double_jump_available = True
        self.score = 0
        self.lives = 3
        self.animation_timer = 0
        
        # Create a more detailed player sprite
        self.update_sprite()
        
    def update_sprite(self):
        # Create a more detailed player sprite with a face
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(self.image, BLUE, (0, 0, 32, 48))
        # Face details
        pygame.draw.rect(self.image, TEAL, (0, 0, 32, 48), 2)  # Border
        
        # Eyes
        eye_x = 8 if not self.facing_right else 18
        pygame.draw.circle(self.image, WHITE, (eye_x, 12), 5)
        pygame.draw.circle(self.image, WHITE, (eye_x + 16, 12), 5)
        pygame.draw.circle(self.image, BLACK, (eye_x + 2, 12), 2)
        pygame.draw.circle(self.image, BLACK, (eye_x + 18, 12), 2)
        
        # Mouth
        mouth_y = 24 + (1 if self.jumping else 0)
        pygame.draw.arc(self.image, BLACK, (8, mouth_y, 16, 8), 0, 3.14, 2)
        
    def jump(self):
        # Check if standing on a platform
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        
        # First jump - from platform
        if hits and not self.jumping:
            self.jumping = True
            self.double_jump_available = True
            self.vel.y = PLAYER_JUMP
        # Double jump - in mid-air
        elif self.jumping and self.double_jump_available:
            self.double_jump_available = False
            self.vel.y = PLAYER_JUMP * 0.8  # Slightly weaker second jump
            
    def update(self):
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.facing_right = True
            
        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        
        # Equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        
        # Wrap around the sides of the screen
        if self.pos.x > SCREEN_WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = SCREEN_WIDTH
            
        self.rect.midbottom = self.pos
        
        # Update sprite appearance
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.update_sprite()
        
        # Check if we hit the ground
        if self.pos.y > SCREEN_HEIGHT:
            self.pos.y = SCREEN_HEIGHT
            self.vel.y = 0
            self.jumping = False
            self.double_jump_available = True
            self.lives -= 1
            if self.lives <= 0:
                self.game.game_over = True
            else:
                self.pos = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_img, (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Add a colorful border to the platform
        pygame.draw.rect(self.image, TEAL, (0, 0, w, h), 2)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 0
        self.value = 10
        self.animation_timer = 0
        
    def update(self):
        # Add a pulsing animation effect
        self.animation_timer += 1
        if self.animation_timer > 30:
            self.animation_timer = 0
            
        # Make the coin pulse by changing its size slightly
        scale = 1.0 + 0.1 * abs(15 - self.animation_timer) / 15
        size = int(16 * scale)
        self.image = pygame.Surface((size, size))
        self.image.fill(YELLOW)
        pygame.draw.circle(self.image, ORANGE, (size//2, size//2), size//2)
        pygame.draw.circle(self.image, YELLOW, (size//2, size//2), size//3)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, min_x, max_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = 2
        self.min_x = min_x
        self.max_x = max_x
        self.animation_timer = 0
        
    def update(self):
        self.rect.x += self.speedx
        if self.rect.x > self.max_x or self.rect.x < self.min_x:
            self.speedx *= -1
            
        # Add a color-changing effect
        self.animation_timer += 1
        if self.animation_timer > 60:
            self.animation_timer = 0
            
        # Create a gradient effect based on animation timer
        if self.animation_timer < 30:
            color_mix = self.animation_timer / 30
            r = int(RED[0] * (1 - color_mix) + PINK[0] * color_mix)
            g = int(RED[1] * (1 - color_mix) + PINK[1] * color_mix)
            b = int(RED[2] * (1 - color_mix) + PINK[2] * color_mix)
        else:
            color_mix = (self.animation_timer - 30) / 30
            r = int(PINK[0] * (1 - color_mix) + RED[0] * color_mix)
            g = int(PINK[1] * (1 - color_mix) + RED[1] * color_mix)
            b = int(PINK[2] * (1 - color_mix) + RED[2] * color_mix)
            
        self.image.fill((r, g, b))
        
        # Add eyes to the enemy
        eye_size = 8
        pygame.draw.circle(self.image, WHITE, (10, 12), eye_size)
        pygame.draw.circle(self.image, WHITE, (22, 12), eye_size)
        pygame.draw.circle(self.image, BLACK, (10 + self.speedx//2, 12), eye_size//2)
        pygame.draw.circle(self.image, BLACK, (22 + self.speedx//2, 12), eye_size//2)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 36)
        self.animation_timer = 0
        
    def draw(self, surface):
        # Create a glowing effect
        self.animation_timer += 1
        if self.animation_timer > 60:
            self.animation_timer = 0
            
        glow = abs(30 - self.animation_timer) / 30
        glow_size = int(glow * 10)
        
        # Draw glow effect
        for i in range(glow_size, 0, -2):
            alpha = 150 - i * 10
            if alpha < 0:
                alpha = 0
            s = pygame.Surface((self.rect.width + i, self.rect.height + i), pygame.SRCALPHA)
            r = self.current_color[0]
            g = self.current_color[1]
            b = self.current_color[2]
            pygame.draw.rect(s, (r, g, b, alpha), (0, 0, self.rect.width + i, self.rect.height + i), border_radius=10+i//2)
            surface.blit(s, (self.rect.x - i//2, self.rect.y - i//2))
        
        # Draw main button
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
        
    def update(self, pos):
        if self.is_hovered(pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

class Game:
    def __init__(self):
        self.running = True
        self.playing = False
        self.game_over = False
        
    def new(self):
        # Start a new game
        self.score = 0
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        # Create platforms
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
            
        # Create coins
        for i in range(10):
            c = Coin(random.randint(0, SCREEN_WIDTH), 
                     random.randint(0, SCREEN_HEIGHT - 200))
            self.all_sprites.add(c)
            self.coins.add(c)
            
        # Create enemies
        for enemy in ENEMY_LIST:
            e = Enemy(*enemy)
            self.all_sprites.add(e)
            self.enemies.add(e)
            
        self.game_over = False
        self.run()
        
    def run(self):
        # Game loop
        self.playing = True
        while self.playing:
            clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            
    def update(self):
        # Game loop update
        self.all_sprites.update()
        
        # Check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.centery:
                    self.player.pos.y = lowest.rect.top
                    self.player.vel.y = 0
                    self.player.jumping = False
                    self.player.double_jump_available = True
        
        # Check if player collects coins
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            self.player.score += coin.value
            # Spawn a new coin
            c = Coin(random.randint(0, SCREEN_WIDTH), 
                     random.randint(0, SCREEN_HEIGHT - 200))
            self.all_sprites.add(c)
            self.coins.add(c)
            
        # Check if player hits enemies
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if enemy_hits:
            # Check if player is jumping on top of enemy
            for enemy in enemy_hits:
                if self.player.vel.y > 0 and self.player.rect.bottom < enemy.rect.centery:
                    enemy.kill()
                    self.player.vel.y = -10
                    self.player.score += 20
                else:
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                    else:
                        # Reset player position
                        self.player.pos = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        self.player.vel = pygame.math.Vector2(0, 0)
                        break
                        
    def events(self):
        # Game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    
    def draw(self):
        # Game loop draw
        screen.fill(SKYBLUE)
        
        # Draw a simple background with gradient
        for y in range(0, SCREEN_HEIGHT, 5):
            color_value = 255 - int(y * 0.4)
            if color_value < 100:
                color_value = 100
            pygame.draw.line(screen, (100, 149, color_value), (0, y), (SCREEN_WIDTH, y))
            
        self.all_sprites.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        # Draw game over screen
        if self.game_over:
            self.show_game_over()
            
        pygame.display.flip()
        
    def show_start_screen(self):
        # Show the start screen
        screen.fill(SKYBLUE)
        font = pygame.font.Font(None, 64)
        title = font.render(TITLE, True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        font = pygame.font.Font(None, 36)
        instructions = font.render("Use arrow keys to move, Space to jump (double-jump in mid-air)", True, BLACK)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 200))
        
        # Create buttons
        start_button = Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Start Game", GREEN, (100, 255, 100))
        quit_button = Button(SCREEN_WIDTH // 2 - 100, 380, 200, 50, "Quit", RED, (255, 100, 100))
        
        waiting = True
        while waiting and self.running:
            clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.is_hovered(mouse_pos):
                        waiting = False
                    if quit_button.is_hovered(mouse_pos):
                        waiting = False
                        self.running = False
            
            start_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            start_button.draw(screen)
            quit_button.draw(screen)
            
            pygame.display.flip()
            
    def show_game_over(self):
        # Show game over screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 64)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Final Score: {self.player.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
        
        restart_button = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "Play Again", GREEN, (100, 255, 100))
        quit_button = Button(SCREEN_WIDTH // 2 - 100, 420, 200, 50, "Quit", RED, (255, 100, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        restart_button.update(mouse_pos)
        quit_button.update(mouse_pos)
        
        restart_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.playing = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_hovered(mouse_pos):
                        waiting = False
                        self.playing = False
                    if quit_button.is_hovered(mouse_pos):
                        waiting = False
                        self.playing = False
                        self.running = False
            
            restart_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            restart_button.draw(screen)
            quit_button.draw(screen)
            
            pygame.display.flip()

# Platform list - (x, y, width, height)
PLATFORM_LIST = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Ground
    (100, 400, 150, 20),
    (300, 300, 100, 20),
    (500, 200, 150, 20),
    (700, 350, 100, 20),
    (850, 250, 150, 20),
    (200, 150, 100, 20),
    (50, 250, 120, 20),
    (400, 100, 120, 20),
    (600, 450, 150, 20)
]

# Enemy list - (x, y, min_x, max_x)
ENEMY_LIST = [
    (300, 280, 300, 400),
    (500, 180, 500, 650),
    (700, 330, 700, 800),
    (200, 130, 200, 300)
]

# Main game loop
g = Game()
g.show_start_screen()

while g.running:
    g.new()
    if g.game_over:
        g.show_game_over()

pygame.quit()
sys.exit()
