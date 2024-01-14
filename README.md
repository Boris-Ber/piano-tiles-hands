# Piano tiles: hands

### Description

Piano tiles game for desktop with controls using hand gestures recognition.
Improve your coordination in a fun game format!

### Installation

> Make sure you have git and python installed on your computer

1. Clone the repository:
    ```bash
   git clone https://github.com/Boris-Ber/piano-tiles-hands.git
   cd piano-tiles-hands
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

### Usage

- After opening the game, put your open palms in front of the camera (~40 centimeters away,
  adjust the distance for convenient control).
  The game will pause if you take your hands out of the camera's field of view.
  It is recommended to keep your palm open most of the time (including not controlling fingers)
  for better hands recognition.
- Tiles will constantly appear on the game screen.
  You need to touch the specified pair of fingers to click the lowest tile, which was not clicked before.
  You need to release fingers and touch them again to click the tile in the same column.
- Controls (pairs of fingers to touch - column where the lowest tile is clicked):
    - Left hand:
        - middle+thumb - 1st column
        - index+thumb - 2nd column
    - Right hand:
        - index+thumb - 3rd column
        - middle+thumb - 4th column
- After a wrong click or a missed tile the game will end,
  and for 5 seconds you will be able to see your mistake. After that the game will automatically restart.
- To exit the game close the window or press Q on the keyboard.

### Status

Released
