import pygame
import cv2
import numpy as np
import random
import sys
import threading
import time
from deepface import DeepFace

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
GROUND_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class EmotionDetector:
    def __init__(self):
        self.current_emotion = "neutral"
        self.emotion_confidence = 0.0
        self.cap = None
        self.running = False
        self.frame = None
        self.detection_active = True
        
    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.running = True
            
            # Start emotion detection in separate thread
            self.detection_thread = threading.Thread(target=self.detect_emotions, daemon=True)
            self.detection_thread.start()
            return True
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def detect_emotions(self):
        last_detection = time.time()
        
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                self.frame = frame.copy()
                
                # Detect emotions every 2 seconds to avoid overloading
                current_time = time.time()
                if current_time - last_detection > 2.0 and self.detection_active:
                    try:
                        # Analyze emotions using DeepFace
                        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                        
                        if isinstance(result, list):
                            result = result[0]
                        
                        emotions = result['emotion']
                        dominant_emotion = max(emotions, key=emotions.get)
                        confidence = emotions[dominant_emotion]
                        
                        # Update emotion if confidence is high enough
                        if confidence > 30:  # Threshold for emotion detection
                            self.current_emotion = dominant_emotion.lower()
                            self.emotion_confidence = confidence
                        
                        last_detection = current_time
                        
                    except Exception as e:
                        print(f"Emotion detection error: {e}")
                        # Continue with current emotion on error
                        pass
            
            time.sleep(0.1)  # Small delay to prevent CPU overload
    
    def get_pygame_frame(self):
        if self.frame is not None:
            # Convert BGR to RGB and resize for display
            rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            rgb_frame = cv2.resize(rgb_frame, (160, 120))
            # Rotate for pygame
            rgb_frame = np.rot90(rgb_frame)
            rgb_frame = np.flipud(rgb_frame)
            return pygame.surfarray.make_surface(rgb_frame)
        return None
    
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

class Player:
    def __init__(self):
        self.width = 50
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.ground_y = self.y
        self.velocity_y = 0
        self.is_jumping = False
        self.speed_boost = 1.0
        self.boost_timer = 0
        
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True
            
    def update(self):
        # Apply gravity
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
            
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.velocity_y = 0
                self.is_jumping = False
        
        # Update speed boost
        if self.boost_timer > 0:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.speed_boost = 1.0
    
    def apply_speed_boost(self):
        self.speed_boost = 1.5
        self.boost_timer = 300  # 5 seconds at 60 FPS
    
    def draw(self, screen):
        # Player color changes with speed boost
        color = YELLOW if self.speed_boost > 1.0 else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Simple face
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 15), 3)
        pygame.draw.circle(screen, BLACK, (self.x + 35, self.y + 15), 3)
        pygame.draw.arc(screen, BLACK, (self.x + 15, self.y + 25, 20, 15), 0, 3.14, 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self, x, speed_multiplier=1.0):
        self.width = 30
        self.height = 50
        self.x = x
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.speed = 5 * speed_multiplier
        
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Collectible:
    def __init__(self, x):
        self.width = 25
        self.height = 25
        self.x = x
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 60
        self.speed = 5
        
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (self.x + self.width//2, self.y + self.height//2), self.width//2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Mirror Game")
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.game_state = "menu"  # "menu", "playing", "game_over"
        self.reset_game()
        
        # Emotion detection
        self.emotion_detector = EmotionDetector()
        self.emotion_feedback = ""
        self.feedback_timer = 0
        
        # Difficulty modifiers based on emotion
        self.difficulty_modifier = 1.0
        self.lives = 3
        self.max_lives = 5
        
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.collectibles = []
        self.score = 0
        self.spawn_timer = 0
        self.lives = 3
        self.difficulty_modifier = 1.0
        
    def start_camera(self):
        if not self.emotion_detector.start_camera():
            print("Warning: Could not start camera. Emotion detection disabled.")
            
    def process_emotion(self, emotion):
        """Process detected emotion and apply game effects"""
        if emotion == "happy":
            self.player.apply_speed_boost()
            self.emotion_feedback = "You look happy! Speed boost activated! 😃"
            self.feedback_timer = 180  # 3 seconds
            self.score += 5  # Bonus points
            
        elif emotion == "angry":
            self.difficulty_modifier = 1.8  # More obstacles
            self.emotion_feedback = "Angry mode: Extra obstacles incoming! 😠"
            self.feedback_timer = 180
            
        elif emotion == "sad":
            self.difficulty_modifier = 0.6  # Fewer obstacles
            if self.lives < self.max_lives:
                self.lives += 1
                self.emotion_feedback = "Sad face detected. Extra life granted! 😢"
            else:
                self.emotion_feedback = "Sad face detected. Difficulty reduced! 😢"
            self.feedback_timer = 180
            
        else:  # neutral or unknown
            self.difficulty_modifier = 1.0
            self.emotion_feedback = "Neutral expression. Normal gameplay! 😐"
            self.feedback_timer = 120
    
    def spawn_objects(self):
        self.spawn_timer += 1
        
        # Adjust spawn rate based on emotion and difficulty
        spawn_rate = int(90 / self.difficulty_modifier)  # Base rate: every 1.5 seconds
        
        if self.spawn_timer >= spawn_rate:
            spawn_x = SCREEN_WIDTH + 50
            
            # 70% obstacles, 30% collectibles
            if random.random() < 0.7:
                self.obstacles.append(Obstacle(spawn_x, self.player.speed_boost))
            else:
                self.collectibles.append(Collectible(spawn_x))
            
            self.spawn_timer = 0
    
    def draw_ui(self):
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Current emotion
        emotion_text = self.font_small.render(f"Emotion: {self.emotion_detector.current_emotion.title()}", True, WHITE)
        self.screen.blit(emotion_text, (10, 90))
        
        # Emotion feedback
        if self.feedback_timer > 0:
            feedback_surface = self.font_small.render(self.emotion_feedback, True, YELLOW)
            feedback_rect = feedback_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
            pygame.draw.rect(self.screen, BLACK, feedback_rect.inflate(20, 10))
            self.screen.blit(feedback_surface, feedback_rect)
            self.feedback_timer -= 1
        
        # Camera feed
        camera_surface = self.emotion_detector.get_pygame_frame()
        if camera_surface:
            camera_rect = pygame.Rect(SCREEN_WIDTH - 170, 10, 160, 120)
            pygame.draw.rect(self.screen, WHITE, camera_rect.inflate(4, 4))
            self.screen.blit(camera_surface, camera_rect)
            
            # Camera label
            cam_label = self.font_small.render("AI Mirror", True, WHITE)
            self.screen.blit(cam_label, (SCREEN_WIDTH - 170, 135))
    
    def main_menu(self):
        self.screen.fill(BLACK)
        
        title_text = self.font_large.render("AI MIRROR GAME", True, WHITE)
        subtitle_text = self.font_medium.render("Your emotions control the game!", True, GREEN)
        start_text = self.font_medium.render("Press SPACE to Start", True, WHITE)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(start_text, start_rect)
        
        # Instructions
        instructions = [
            "😃 Happy: Speed boost + bonus points",
            "😠 Angry: Extra obstacles",
            "😢 Sad: Reduced difficulty + extra life",
            "😐 Neutral: Normal gameplay",
            "",
            "Use SPACE to jump over obstacles!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60 + i * 25))
            self.screen.blit(text, text_rect)
    
    def game_over_screen(self):
        self.screen.fill(BLACK)
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font_medium.render("Press SPACE to Restart", True, WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def game_loop(self):
        # Process current emotion
        current_emotion = self.emotion_detector.current_emotion
        if hasattr(self, 'last_processed_emotion'):
            if current_emotion != self.last_processed_emotion:
                self.process_emotion(current_emotion)
                self.last_processed_emotion = current_emotion
        else:
            self.last_processed_emotion = current_emotion
            self.process_emotion(current_emotion)
        
        # Spawn objects
        self.spawn_objects()
        
        # Update player
        self.player.update()
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.x < -obstacle.width:
                self.obstacles.remove(obstacle)
            elif self.player.get_rect().colliderect(obstacle.get_rect()):
                self.obstacles.remove(obstacle)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_state = "game_over"
        
        # Update collectibles
        for collectible in self.collectibles[:]:
            collectible.update()
            if collectible.x < -collectible.width:
                self.collectibles.remove(collectible)
            elif self.player.get_rect().colliderect(collectible.get_rect()):
                self.collectibles.remove(collectible)
                self.score += 10
        
        # Draw everything
        self.screen.fill(BLACK)
        
        # Draw ground
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Draw game objects
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for collectible in self.collectibles:
            collectible.draw(self.screen)
        
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.start_camera()
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
        
        # Cleanup
        self.emotion_detector.stop()
        pygame.quit()
        cv2.destroyAllWindows()
        sys.exit()

if __name__ == "__main__":
    print("Starting AI Mirror Game...")
    print("Make sure your webcam is connected and working!")
    game = Game()
    game.run()
