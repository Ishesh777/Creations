import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_WIDTH = 80
PIPE_GAP = 200
PIPE_SPEED = 3
BIRD_SIZE = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, BIRD_SIZE, BIRD_SIZE)

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y

        # Keep bird on screen
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - BIRD_SIZE:
            self.y = SCREEN_HEIGHT - BIRD_SIZE
            self.velocity = 0

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x + BIRD_SIZE // 2), int(self.y + BIRD_SIZE // 2)), BIRD_SIZE // 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + BIRD_SIZE // 2), int(self.y + BIRD_SIZE // 2)), BIRD_SIZE // 2,
                           2)
        # Eye
        pygame.draw.circle(screen, BLACK, (int(self.x + BIRD_SIZE // 2 + 5), int(self.y + BIRD_SIZE // 2 - 5)), 3)


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - 150 - PIPE_GAP)
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, self.gap_y)
        self.bottom_rect = pygame.Rect(x, self.gap_y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - (self.gap_y + PIPE_GAP))
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        pygame.draw.rect(screen, BLACK, self.top_rect, 3)
        pygame.draw.rect(screen, BLACK, self.bottom_rect, 3)

    def collides_with(self, bird):
        return bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.pipe_timer = 0

    def create_pipe(self):
        self.pipes.append(Pipe(SCREEN_WIDTH))

    def update(self):
        if not self.game_over:
            self.bird.update()

            # Create new pipes
            self.pipe_timer += 1
            if self.pipe_timer >= 90:  # Create pipe every 1.5 seconds at 60 FPS
                self.create_pipe()
                self.pipe_timer = 0

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()

                # Check for collision
                if pipe.collides_with(self.bird):
                    self.game_over = True

                # Check if bird passed pipe
                if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                    pipe.passed = True
                    self.score += 1

                # Remove pipes that are off screen
                if pipe.x + PIPE_WIDTH < 0:
                    self.pipes.remove(pipe)

            # Check if bird hit ground or ceiling
            if self.bird.y <= 0 or self.bird.y >= SCREEN_HEIGHT - BIRD_SIZE:
                self.game_over = True

    def draw(self):
        # Draw background
        self.screen.fill(BLUE)

        # Draw clouds
        for i in range(3):
            cloud_x = (i * 150) + (pygame.time.get_ticks() // 50) % (SCREEN_WIDTH + 100)
            pygame.draw.circle(self.screen, WHITE, (cloud_x, 100), 30)
            pygame.draw.circle(self.screen, WHITE, (cloud_x + 25, 100), 25)
            pygame.draw.circle(self.screen, WHITE, (cloud_x - 25, 100), 25)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Draw bird
        self.bird.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press SPACE to restart", True, WHITE)

            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def restart(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.pipe_timer = 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.restart()
                        else:
                            self.bird.jump()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
