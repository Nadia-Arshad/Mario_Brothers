import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 500

# Colors
BLUE = (107, 140, 255)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Mario Bros")

# Clock for controlling frame rate
clock = pygame.time.Clock()

class Mario:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = GROUND_HEIGHT - self.height
        self.vel_y = 0
        self.jumping = False
        self.on_ground = True
        self.direction = 1  # 1 for right, -1 for left
        self.lives = 3
        self.score = 0
        
    def update(self):
        # Apply gravity
        self.vel_y += 1
        self.y += self.vel_y
        
        # Check if on ground
        if self.y >= GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True
            self.jumping = False
        else:
            self.on_ground = False
            
    def jump(self):
        if self.on_ground and not self.jumping:
            self.vel_y = -20
            self.jumping = True
            self.on_ground = False
            
    def move_left(self):
        self.x -= 5
        self.direction = -1
        if self.x < 0:
            self.x = 0
            
    def move_right(self):
        self.x += 5
        self.direction = 1
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
    def draw(self):
        # Draw Mario (simple rectangle for now)
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        
        # Draw face direction indicator (simple triangle)
        if self.direction == 1:  # facing right
            pygame.draw.polygon(screen, WHITE, [(self.x + self.width, self.y + self.height//3), 
                                              (self.x + self.width - 10, self.y + self.height//4),
                                              (self.x + self.width - 10, self.y + self.height//2)])
        else:  # facing left
            pygame.draw.polygon(screen, WHITE, [(self.x, self.y + self.height//3), 
                                              (self.x + 10, self.y + self.height//4),
                                              (self.x + 10, self.y + self.height//2)])
    
    def check_collision(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.width > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.height > obj.y)

class Block:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
        
    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, (255, 215, 0), (self.x + self.width//2, self.y + self.height//2), self.width//2)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.vel_x = -2
        self.alive = True
        
    def update(self):
        if self.alive:
            self.x += self.vel_x
            
            # Reverse direction if hitting edge of screen
            if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
                self.vel_x *= -1
                
    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

# Create game objects
mario = Mario()
blocks = [
    Block(300, 400, 100, 30),
    Block(500, 350, 100, 30),
    Block(200, 250, 100, 30),
    Block(400, 200, 100, 30),
    Block(600, 300, 100, 30)
]
coins = [
    Coin(330, 370),
    Coin(530, 320),
    Coin(230, 220),
    Coin(430, 170),
    Coin(630, 270)
]
enemies = [
    Enemy(400, GROUND_HEIGHT - 40),
    Enemy(600, GROUND_HEIGHT - 40)
]

# Game loop
running = True
game_over = False
font = pygame.font.SysFont(None, 36)

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                mario.jump()
            if event.key == pygame.K_r and game_over:
                # Reset game
                mario = Mario()
                game_over = False
                for coin in coins:
                    coin.collected = False
                for enemy in enemies:
                    enemy.alive = True
                    enemy.x = random.randint(400, 700)
    
    if not game_over:
        # Get pressed keys for continuous movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            mario.move_left()
        if keys[pygame.K_RIGHT]:
            mario.move_right()
        
        # Update game objects
        mario.update()
        
        # Platform collision
        for block in blocks:
            # Check if Mario is on top of a block
            if (mario.x + mario.width > block.x and 
                mario.x < block.x + block.width and 
                mario.y + mario.height >= block.y and 
                mario.y + mario.height <= block.y + 10):
                mario.y = block.y - mario.height
                mario.vel_y = 0
                mario.on_ground = True
                mario.jumping = False
        
        # Coin collection
        for coin in coins:
            if not coin.collected and mario.check_collision(coin):
                coin.collected = True
                mario.score += 100
        
        # Enemy interaction
        for enemy in enemies:
            enemy.update()
            if enemy.alive and mario.check_collision(enemy):
                # If Mario lands on top of enemy
                if mario.vel_y > 0 and mario.y + mario.height < enemy.y + enemy.height/2:
                    enemy.alive = False
                    mario.vel_y = -10  # Bounce off
                    mario.score += 200
                else:
                    # Mario gets hit
                    mario.lives -= 1
                    if mario.lives <= 0:
                        game_over = True
                    else:
                        # Reset Mario position
                        mario.x = 100
                        mario.y = GROUND_HEIGHT - mario.height
                        mario.vel_y = 0
    
    # Drawing
    screen.fill(BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, BROWN, (0, GROUND_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
    
    # Draw blocks
    for block in blocks:
        block.draw()
    
    # Draw coins
    for coin in coins:
        coin.draw()
    
    # Draw enemies
    for enemy in enemies:
        enemy.draw()
    
    # Draw Mario
    mario.draw()
    
    # Draw UI
    score_text = font.render(f"Score: {mario.score}", True, WHITE)
    lives_text = font.render(f"Lives: {mario.lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
    
    # Game over screen
    if game_over:
        game_over_text = font.render("GAME OVER - Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()
