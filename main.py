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
VIDEO_WIDTH, VIDEO_HEIGHT = 640, 480
FONT_SIZE = 30
FINGER_PAIRS = [
    [(0, 0), (0, 2)],
    [(0, 0), (0, 1)],
    [(1, 0), (1, 1)],
    [(1, 0), (1, 2)]
]

# Create the loading screen
pygame.init()
screen = pygame.display.set_mode((VIDEO_WIDTH + GAME_WIDTH, VIDEO_HEIGHT))
pygame.display.set_caption('Piano tiles')
font = pygame.font.SysFont('Arial', FONT_SIZE)
text = font.render('Initializing...', True, (255, 255, 255))
screen.blit(text, (VIDEO_WIDTH // 2 - text.get_width() // 2, VIDEO_HEIGHT // 2 - text.get_height() // 2))
pygame.display.flip()

# Create default instances: hands detector, video capture
handsDetector = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.85)
cap = cv2.VideoCapture(0)

# Resize the window if camera resolution changed
VIDEO_WIDTH, VIDEO_HEIGHT = int(cap.get(3)), int(cap.get(4))
screen = pygame.display.set_mode((VIDEO_WIDTH + GAME_WIDTH, VIDEO_HEIGHT))


class Tile:
    def __init__(self, column):
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
        self.current_tile = -1
        self.score = 0
        self.ticks = 0
        self.game_over = False

    def add_tile(self):
        """Add a new tile to the game"""
        new_tile = randint(0, 3)
        while new_tile == self.current_tile:
            new_tile = randint(0, 3)
        self.current_tile = new_tile
        self.tiles[new_tile].append(Tile(new_tile))

    def draw(self):
        """Draw all tiles on the screen"""
        for column in range(4):
            for tile in self.tiles[column]:
                tile.draw()

    def move(self):
        """Move all tiles down"""
        for column in range(4):
            new_tiles = []
            for tile in self.tiles[column]:
                if tile.y > VIDEO_HEIGHT:
                    self.score += 1
                else:
                    tile.move()
                    new_tiles.append(tile)
            self.tiles[column] = new_tiles

    def check_touch(self):
        """TODO: Check if the tile is clicked"""
        pass

    def tick(self):
        """Update the game"""
        pygame.draw.rect(screen, (0, 0, 0), (VIDEO_WIDTH, 0, GAME_WIDTH, VIDEO_HEIGHT))

        self.move()
        self.ticks += 1
        if self.ticks % (TILE_HEIGHT // TILE_SPEED) == 0:
            self.add_tile()
        self.draw()
        self.check_touch()

        for column in range(4):
            if control[column]:
                control_color = (0, 255, 0)
            else:
                control_color = (255, 0, 0)
            pygame.draw.circle(screen, control_color, (VIDEO_WIDTH + TILE_WIDTH // 2 + TILE_WIDTH * column, VIDEO_HEIGHT - 100),
                               TILE_WIDTH // 8 * 3)


def get_distance(p1, p2) -> float:
    """Returns distance between two points"""
    return hypot(p1[0] - p2[0], p1[1] - p2[1])


def calculate(landmarks) -> list:
    """Returns list of distances between fingers"""
    return [get_distance(landmarks[pair[0]], landmarks[pair[1]]) for pair in FINGER_PAIRS]


game = TileManager()

while cap.isOpened():
    # Read a frame and check if the video or the game is over
    ret, frame = cap.read()
    quit_flag = not ret or game.game_over
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            quit_flag = True
    if quit_flag:
        break

    # Prepare the image and recognize hands
    frame = np.fliplr(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = handsDetector.process(frame)

    control = [False] * 4
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
                fingers_landmarks[hand_index[hand_id], int(finger // 4) - 1] = [x_tip, y_tip]
                cv2.circle(frame, (x_tip, y_tip), 10, (0, 0, 255), -1)

        # Calculate distances between fingers and detect touches
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

    # Update the game
    if game_on:
        game.tick()
    else:
        text = font.render('Put your both hands in the frame to play', True, (255, 0, 0))
        screen.blit(text, (VIDEO_WIDTH // 2 - text.get_width() // 2, VIDEO_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

pygame.quit()
cap.release()
handsDetector.close()
