# Changelog

## First working version
- Implemented check_touch() function to check if the controlling fingers touch
- Added user interface: score count and a game over screen with automatic restart
- The game is now playable!
- Refactored code, improved functions and added type hints

## Add pygame
- Add new requirement - pygame
- Create a loading screen and a game field
- Create Tile and TileManager classes to process the game field
- Modify the main loop to include the game start and end

## Add hand recognition
- Create CHANGELOG.md
- Add two new requirements - mediapipe and numpy
- Add detection of distances between fingers for game control using mediapipe hand recognition module

## Initial and test commits
- Create .gitignore, README.md
- Create main.py, requirements.txt
- Add first requirement - opencv
