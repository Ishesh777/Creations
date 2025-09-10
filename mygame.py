
import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
GROUND_HEIGHT = 50
SCROLL_SPEED = 7

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
BLUE = (135, 206, 235)
RED = (220, 20, 60)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.ground_y = self.y
        self.velocity_y = 0
        self.is_jumping = False
        self.animation_frame = 0
        self.animation_timer = 0
        
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True
            return True  # Return True to indicate jump sound should play
        return False
            
    def update(self):
        # Apply gravity
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
            
            # Check if landed
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.velocity_y = 0
                self.is_jumping = False
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 10:  # Change frame every 10 ticks
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
    
    def draw(self, screen):
        # Draw simple character (placeholder)
        # Body
        pygame.draw.rect(screen, GREEN, (self.x, self.y + 20, self.width, self.height - 20))
        # Head
        pygame.draw.circle(screen, GREEN, (self.x + self.width//2, self.y + 15), 15)
        # Eyes
        pygame.draw.circle(screen, BLACK, (self.x + self.width//2 - 5, self.y + 10), 3)
        pygame.draw.circle(screen, BLACK, (self.x + self.width//2 + 5, self.y + 10), 3)
        
        # Simple running animation - legs
        leg_offset = 5 if self.animation_frame < 2 else -5
        if not self.is_jumping:
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 10 + leg_offset, self.y + self.height - 15, 8, 15))
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 22 - leg_offset, self.y + self.height - 15, 8, 15))
        else:
            # Jumping pose
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 10, self.y + self.height - 15, 8, 15))
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 22, self.y + self.height - 15, 8, 15))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self, x, obstacle_type):
        self.x = x
        self.type = obstacle_type
        if obstacle_type == "trash":
            self.width = 30
            self.height = 40
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            self.color = GRAY
        elif obstacle_type == "pollution":
            self.width = 50
            self.height = 30
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 80
            self.color = GRAY
    
    def update(self):
        self.x -= SCROLL_SPEED
    
    def draw(self, screen):
        if self.type == "trash":
            # Draw trash can
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
            # Lid
            pygame.draw.rect(screen, GRAY, (self.x - 2, self.y - 5, self.width + 4, 5))
        elif self.type == "pollution":
            # Draw pollution cloud
            pygame.draw.circle(screen, self.color, (self.x + 15, self.y + 15), 15)
            pygame.draw.circle(screen, self.color, (self.x + 35, self.y + 15), 12)
            pygame.draw.circle(screen, self.color, (self.x + 25, self.y + 5), 10)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EcoItem:
    def __init__(self, x, item_type):
        self.x = x
        self.type = item_type
        self.width = 25
        self.height = 25
        
        if item_type == "recycle":
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 30
            self.color = YELLOW
        elif item_type == "tree":
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 40
            self.color = GREEN
        elif item_type == "water":
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 60
            self.color = BLUE
    
    def update(self):
        self.x -= SCROLL_SPEED 
    
    def draw(self, screen):
        if self.type == "recycle":
            # Draw recycling symbol (simplified)
            pygame.draw.circle(screen, self.color, (self.x + 12, self.y + 12), 12)
            pygame.draw.circle(screen, BLACK, (self.x + 12, self.y + 12), 12, 2)
            pygame.draw.polygon(screen, BLACK, [(self.x + 12, self.y + 5), (self.x + 8, self.y + 15), (self.x + 16, self.y + 15)])
        elif self.type == "tree":
            # Draw tree
            pygame.draw.rect(screen, BROWN, (self.x + 10, self.y + 15, 5, 10))
            pygame.draw.circle(screen, self.color, (self.x + 12, self.y + 10), 10)
        elif self.type == "water":
            # Draw water drop
            pygame.draw.circle(screen, self.color, (self.x + 12, self.y + 15), 8)
            pygame.draw.polygon(screen, self.color, [(self.x + 12, self.y + 5), (self.x + 8, self.y + 12), (self.x + 16, self.y + 12)])
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Eco Runner")
        self.clock = pygame.time.Clock()
        
        # Sound removed
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.reset_game()
        self.game_state = "menu"  # "menu", "playing", "game_over"
        
        # Background elements
        self.clouds = []
        self.trees = []
        self.init_background()
    
    
    
    def init_background(self):
        # Initialize clouds
        for i in range(3):
            self.clouds.append({
                'x': i * 200 + random.randint(0, 100),
                'y': random.randint(50, 150),
                'speed': random.uniform(0.5, 1.5)
            })
        
        # Initialize background trees
        for i in range(5):
            self.trees.append({
                'x': i * 120 + random.randint(0, 50),
                'y': SCREEN_HEIGHT - GROUND_HEIGHT - 60,
                'height': random.randint(40, 70)
            })
    
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.eco_items = []
        self.score = 0
        self.spawn_timer = 0
        self.distance = 0
    
    def spawn_objects(self):
        self.spawn_timer += 1
        
        # Spawn obstacles and items
        if self.spawn_timer >= random.randint(60, 120):  # 1-2 seconds at 60 FPS
            spawn_x = SCREEN_WIDTH + 50
            
            # Decide what to spawn (30% obstacle, 70% eco item)
            if random.random() < 0.3:
                obstacle_type = random.choice(["trash", "pollution"])
                self.obstacles.append(Obstacle(spawn_x, obstacle_type))
            else:
                item_type = random.choice(["recycle", "tree", "water"])
                self.eco_items.append(EcoItem(spawn_x, item_type))
            
            self.spawn_timer = 0
    
    def update_background(self):
        # Update clouds
        for cloud in self.clouds:
            cloud['x'] -= cloud['speed']
            if cloud['x'] < -100:
                cloud['x'] = SCREEN_WIDTH + random.randint(0, 100)
                cloud['y'] = random.randint(50, 150)
        
        # Update trees
        for tree in self.trees:
            tree['x'] -= SCROLL_SPEED * 0.3  # Slower parallax effect
            if tree['x'] < -50:
                tree['x'] = SCREEN_WIDTH + random.randint(0, 50)
                tree['height'] = random.randint(40, 70)
    
    def draw_background(self):
        # Sky
        self.screen.fill(BLUE)
        
        # Clouds
        for cloud in self.clouds:
            pygame.draw.circle(self.screen, WHITE, (int(cloud['x']), int(cloud['y'])), 20)
            pygame.draw.circle(self.screen, WHITE, (int(cloud['x'] + 25), int(cloud['y'])), 15)
            pygame.draw.circle(self.screen, WHITE, (int(cloud['x'] - 20), int(cloud['y'] + 5)), 18)
        
        # Background trees
        for tree in self.trees:
            pygame.draw.rect(self.screen, BROWN, (tree['x'] + 15, tree['y'] + tree['height'] - 20, 8, 20))
            pygame.draw.circle(self.screen, DARK_GREEN, (tree['x'] + 19, tree['y'] + tree['height'] - 30), 25)
        
        # Ground
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(self.screen, BROWN, (0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))
    
    def draw_score(self):
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_shadow = self.font_medium.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_shadow, (11, 11))
        self.screen.blit(score_text, (10, 10))
    
    def main_menu(self):
        self.draw_background()
        
        title_text = self.font_large.render("ECO RUNNER", True, WHITE)
        title_shadow = self.font_large.render("ECO RUNNER", True, BLACK)
        start_text = self.font_medium.render("Press SPACE to Start", True, WHITE)
        start_shadow = self.font_medium.render("Press SPACE to Start", True, BLACK)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_text, title_rect)
        self.screen.blit(start_shadow, (start_rect.x + 2, start_rect.y + 2))
        self.screen.blit(start_text, start_rect)
        
        # Instructions
        instructions = [
            "Collect eco items for points!",
            "Avoid trash and pollution clouds!",
            "Press SPACE to jump!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80 + i * 25))
            self.screen.blit(text, text_rect)
    
    def game_over_screen(self):
        self.draw_background()
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_shadow = self.font_large.render("GAME OVER", True, BLACK)
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_shadow = self.font_medium.render(f"Final Score: {self.score}", True, BLACK)
        restart_text = self.font_medium.render("Press SPACE to Restart", True, WHITE)
        restart_shadow = self.font_medium.render("Press SPACE to Restart", True, BLACK)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        self.screen.blit(game_over_shadow, (game_over_rect.x + 2, game_over_rect.y + 2))
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_shadow, (restart_rect.x + 2, restart_rect.y + 2))
        self.screen.blit(restart_text, restart_rect)
    
    def game_loop(self):
        # Spawn objects
        self.spawn_objects()
        
        # Update player
        self.player.update()
        
        # Update and check obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.x < -obstacle.width:
                self.obstacles.remove(obstacle)
            elif self.player.get_rect().colliderect(obstacle.get_rect()):
                self.game_state = "game_over"
        
        # Update and check eco items
        for item in self.eco_items[:]:
            item.update()
            if item.x < -item.width:
                self.eco_items.remove(item)
            elif self.player.get_rect().colliderect(item.get_rect()):
                self.eco_items.remove(item)
                self.score += 10
        
        # Update background
        self.update_background()
        
        # Draw everything
        self.draw_background()
        
        # Draw obstacles and items
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for item in self.eco_items:
            item.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_score()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.game_state = "playing"
                    elif self.game_state == "playing":
                        self.player.jump()
                    elif self.game_state == "game_over":
                        self.reset_game()
                        self.game_state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if self.game_state == "menu":
                self.main_menu()
            elif self.game_state == "playing":
                self.game_loop()
            elif self.game_state == "game_over":
                self.game_over_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
