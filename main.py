import cv2
import mediapipe as mp
import numpy as np
import pygame
from math import hypot
from random import randint

# Constants
TOUCH_DIST = 30
GAME_WIDTH = 256
TILE_WIDTH = GAME_WIDTH // 4
TILE_HEIGHT = 100
TILE_SPEED = 10
FONT_SIZE = 30
FINGER_PAIRS = [
    [(0, 0), (0, 2)],
    [(0, 0), (0, 1)],
    [(1, 0), (1, 1)],
    [(1, 0), (1, 2)]
]

# Create default instances: hands detector, video capture
handsDetector = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.85)
cap = cv2.VideoCapture(0)

# Create the pygame window
pygame.init()
VIDEO_WIDTH, VIDEO_HEIGHT = int(cap.get(3)), int(cap.get(4))
screen = pygame.display.set_mode((VIDEO_WIDTH + GAME_WIDTH, VIDEO_HEIGHT))
pygame.display.set_caption('Piano tiles')
FONT = pygame.font.SysFont('Arial', FONT_SIZE)
pygame.display.flip()


class Tile:
    def __init__(self, column: int):
        """Create a new tile in the given column"""
        self.column = column
        self.x, self.y = VIDEO_WIDTH + column * TILE_WIDTH, -TILE_HEIGHT
        self.color = (255, 255, 255)
        self.clicked = False

    def draw(self):
        """Draw the tile on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, TILE_WIDTH, TILE_HEIGHT))
        pygame.draw.rect(screen, (128, 128, 128), (self.x, self.y, TILE_WIDTH, TILE_HEIGHT), 5)

    def move(self):
        """Move the tile down"""
        self.y += TILE_SPEED


class TileManager:
    def __init__(self):
        """Create a new tile manager"""
        self.tiles = [[] for _ in range(4)]
        self.tiles_queue = []
        self.previous_clicks = []
        self.control = [False] * 4
        self.current_tile = -1
        self.score = 0
        self.ticks = 0
        self.game_over = False

        self.render()

    def add_tile(self):
        """Add a new tile to the game"""
        new_tile = randint(0, 3)
        while new_tile == self.current_tile:
            new_tile = randint(0, 3)
        self.current_tile = new_tile
        self.tiles_queue.append(new_tile)
        self.tiles[new_tile].append(Tile(new_tile))

    def render(self):
        """Render the game"""

        # Draw the background
        pygame.draw.rect(screen, (0, 0, 0), (VIDEO_WIDTH, 0, GAME_WIDTH, VIDEO_HEIGHT))

        # Draw all tiles on the screen
        for column in range(4):
            for tile in self.tiles[column]:
                tile.draw()

        # Draw the field: score and control buttons
        score = FONT.render(f'Score: {self.score}', True, (0, 0, 255))
        screen.blit(score, (VIDEO_WIDTH + GAME_WIDTH // 2 - score.get_width() // 2, 50))

        for column in range(4):
            if self.control[column]:
                control_color = (0, 255, 0)
            else:
                control_color = (255, 0, 0)
            pygame.draw.circle(screen, control_color,
                               (VIDEO_WIDTH + TILE_WIDTH // 2 + TILE_WIDTH * column, VIDEO_HEIGHT - TILE_HEIGHT),
                               TILE_WIDTH // 8 * 3)
            pygame.draw.circle(screen, (128, 128, 128),
                               (VIDEO_WIDTH + TILE_WIDTH // 2 + TILE_WIDTH * column, VIDEO_HEIGHT - TILE_HEIGHT),
                               TILE_WIDTH // 8 * 3, 3)

    def move(self):
        """Move all tiles down"""
        for column in range(4):
            new_tiles = []
            for tile in self.tiles[column]:
                if tile.y <= VIDEO_HEIGHT - TILE_HEIGHT:
                    tile.move()
                    new_tiles.append(tile)
                elif not tile.clicked:
                    self.game_over = True
                    tile.color = (255, 0, 0)
                    new_tiles.append(tile)
            self.tiles[column] = new_tiles

    def check_touch(self):
        """Check if the tile is clicked"""
        clicks = []
        for column in range(4):
            if not self.control[column]:
                continue
            clicks.append(column)
            if column in self.previous_clicks:
                continue
            if not self.tiles_queue:
                break
            if column != self.tiles_queue[0]:
                self.game_over = True
                break

            for tile in self.tiles[column]:
                if not tile.clicked:
                    self.score += 1
                    self.tiles_queue.pop(0)
                    tile.clicked = True
                    tile.color = (0, 255, 0)
                    break
        self.previous_clicks = clicks

    def tick(self):
        """Update the game state and render the screen"""
        self.control = control
        self.move()
        self.ticks += 1
        if self.ticks % (TILE_HEIGHT // TILE_SPEED) == 0:
            self.add_tile()
        self.render()
        self.check_touch()


def close_all():
    """Close all windows and release resources"""
    pygame.quit()
    cap.release()
    handsDetector.close()


def check_exit() -> bool:
    """Checks if the user wants to exit"""
    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or event.type == pygame.QUIT:
            return True
    return False


def get_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Returns distance between two points"""
    return hypot(p1[0] - p2[0], p1[1] - p2[1])


def calculate(landmarks: np.ndarray) -> list:
    """Returns list of distances between fingers"""
    return [get_distance(landmarks[pair[0]], landmarks[pair[1]]) for pair in FINGER_PAIRS]


game = TileManager()

while cap.isOpened():
    # Read a frame and check if the video is over or user wants to exit
    ret, frame = cap.read()
    if not ret or check_exit():
        break

    # Prepare the image and recognize hands
    frame = np.fliplr(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = handsDetector.process(frame)

    # Check if the game is on
    game_on = results.multi_handedness is not None and len(results.multi_handedness) == 2
    if game_on:
        # If 2 hands are detected, calculate the coordinates of fingertips
        fingers_landmarks = np.zeros((2, 3, 2), dtype=int)
        hand_index = [0, 0]
        for hand_id in range(2):
            hand = 'Right' in str(results.multi_handedness[hand_id])
            hand_index[hand] = hand_id
        for hand_id in range(2):
            for finger in [4, 8, 12]:
                x_tip = int(results.multi_hand_landmarks[hand_id].landmark[finger].x *
                            frame.shape[1])
                y_tip = int(results.multi_hand_landmarks[hand_id].landmark[finger].y *
                            frame.shape[0])
                fingers_landmarks[hand_index[hand_id], int(finger // 4) - 1] = (x_tip, y_tip)
                cv2.circle(frame, (x_tip, y_tip), 10, (0, 0, 255), -1)

        # Calculate distances between fingers and detect touches
        control = [False] * 4
        dist = calculate(fingers_landmarks)
        for i in range(4):
            pair = FINGER_PAIRS[i]
            if dist[i] < TOUCH_DIST:
                line_color = (0, 255, 0)
                control[i] = True
            else:
                line_color = (255, 0, 0)
            cv2.line(frame, fingers_landmarks[pair[0]], fingers_landmarks[pair[1]], line_color, 3)

    # Place the image on the pygame screen
    frame = np.rot90(np.fliplr(frame))
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))

    # Update the game screen
    if game_on:
        game.tick()
        if game.game_over:
            game_over = FONT.render('Game over', True, (255, 0, 0))
            info = FONT.render('Restarting in 5 seconds', True, (255, 0, 0))
            screen.blit(game_over, (VIDEO_WIDTH // 2 - game_over.get_width() // 2, VIDEO_HEIGHT // 2 - FONT_SIZE // 2))
            screen.blit(info, (VIDEO_WIDTH // 2 - info.get_width() // 2, VIDEO_HEIGHT // 2 + FONT_SIZE // 2))
            pygame.display.flip()

            for i in range(100):
                pygame.time.wait(50)
                if check_exit():
                    close_all()
                    exit(0)
            game.__init__()
    else:
        reminder = FONT.render('Put your both hands in the frame to play', True, (255, 0, 0))
        screen.blit(reminder, (VIDEO_WIDTH // 2 - reminder.get_width() // 2, VIDEO_HEIGHT // 2 - FONT_SIZE // 2))
    pygame.display.flip()

close_all()
