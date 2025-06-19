# Introduction
I told AI to create a game based on "Wall Go", a 2-player boardgame that is depicted in Korea drama "Devil's plan" season 2.

## Input prompt to AI in one go
【Objective】

Move your pieces on a 7×7 board and build walls to carve out your own ‘territory’ (an enclosed area containing only your pieces). When the game ends, count the squares in each player’s territory; the player with the most wins.

【Equipment & Players】
 • Board: 7×7 squares
 • Players:
   • 2-player: Red and Blue, each with 4 pieces
   • 3/4-player: Add Yellow/Light Blue, each color has 2 pieces
 • Walls: Unlimited, color-coded by player

【Game Flow】
Placement Phase
 • 2-player: Starting positions fixed: Red [1,1],[5,5]; Blue [1,5],[5,1]. The other two are placed alternately: Red, Blue, Blue, Red
 • 3/4-player: Each player places 2 pieces, in alternating order (e.g. A→B→C→C→B→A)

Action Phase (turn-based)
 1. Choose any of your pieces that can still act
 2. Move 0, 1, or 2 steps:
   • Each step must be up, down, left, or right
   • Cannot cross or pass through walls or other pieces
 3. After moving, you must place a wall on an open side of that piece’s square (even if you moved 0 steps)

【Walls & Borders】
 • The board’s outer edge counts as a wall
 • 2-player: Walls cannot be removed once placed
 • 3/4-player: Each player gets one “wall break” per game, usable on their turn

【Time Limit】
 • 90 seconds per turn
 • If time runs out, a wall is placed randomly and the turn ends

【End Condition】
 • The game ends when all players’ pieces are in separate territories

【Scoring】
 • Each square in a territory is worth 1 point
 • If total scores are tied, the player with the largest single territory wins

【Victory】
 • Highest score wins
 • If both total and largest territory are tied, it’s a draw
 
## Output from AI
### Game Features:

Board & Setup:
• 7×7 grid board
• 2-player game (Red vs Blue)
• Each player starts with 4 pieces

Game Phases:
1. Placement Phase:
   • Fixed positions: Red at (1,1) and (5,5), Blue at (1,5) and (5,1)
   • Remaining pieces placed alternately: Red, Blue, Blue, Red

2. Action Phase:
   • Turn-based gameplay with 90-second time limit per turn
   • Each turn: select piece → move 0-2 steps → place wall

Game Mechanics:
• **Movement**: Up to 2 steps in cardinal directions, can't pass through walls/pieces
• **Wall Placement**: Must place a wall after each action, even if you don't move
• **Territory Building**: Create enclosed areas containing only your pieces
• **Victory**: Player with most territory squares wins

Controls:
• **Click** piece to select it
• **Click** green highlighted squares to move
• **Shift+Click** yellow highlighted areas to place walls
• **R** - Restart game
• **ESC** - Quit

Visual Elements:
• Red and Blue circular pieces
• Color-coded walls
• Green highlights for possible moves
• Yellow highlights for possible wall placements
• Real-time turn timer
• Score display at game end

End Conditions:
• Game ends when all pieces are in separate territories
• Scoring: 1 point per territory square
• Tiebreaker: Largest single territory wins
• If still tied: Draw

The game implements all the rules you specified including the territory detection algorithm using flood fill, proper
wall mechanics, and the exact scoring system. You can run it with:

bash
python wall_go.py

### Below is the initial screenshot
![alt text](http://github.com/philipho11/wallgo/wallgo-1.png)

### Below is the movement screenshot
![alt text](http://github.com/philipho11/wallgo/wallgo-2.png)

### Below is another movement screenshot
![alt text](http://github.com/philipho11/wallgo/wallgo-3.png)


# Debugging experience with AI

I tested and found that the initial board setup and pieces placement is fine. But in the main game loop, after a player moves their piece, they can continue moving
it multiple times instead of being forced to place a wall and end their turn. **AI can fix the code in one go.**

# Unit tests?
I ask AI to suggest unit tests to test the implementation as i don't think it is effective for me to test it manually. It may take over 10 minutes to test one round from step 0. AI answered, 
Absolutely! Manual testing is inefficient for a complex game like this. Let me create comprehensive unit tests to verify the game
logic systematically.

In addition to normal tests that he created, he also create a specific test for the wall placement issue that I encountered earlier. **That's amazing##! After writing tests, he will also run the unit test and got a **pass**!

# Ask AI to understand more about python related programming techniques
It is worthwhile for AI to teach me more about the domain (game) specific programming techniques.

## What is the major purpose of pygame module here?

Specifically, pygame serves these key functions:

## Graphics & Rendering
• **Window Management**: Creates and manages the game window (pygame.display.set_mode())
• **Drawing Operations**: Renders the game board, pieces, walls, and UI elements using functions like:
  • pygame.draw.rect() for walls and board grid
  • pygame.draw.circle() for game pieces
  • pygame.draw.line() for board lines

## User Input Handling
• **Mouse Events**: Captures mouse clicks for piece selection, movement, and wall placement
• **Keyboard Events**: Handles key presses (R for restart, ESC to quit, Shift for wall placement mode)
• **Event Loop**: Processes all user interactions through pygame.event.get()

## Game Loop & Timing
• **Frame Rate Control**: Maintains consistent 60 FPS using pygame.time.Clock()
• **Real-time Updates**: Enables smooth animation and responsive gameplay
• **Timer Management**: Supports the 90-second turn timer feature

## Text & UI Display
• **Font Rendering**: Displays game information like current player, scores, instructions, and timer
• **Dynamic UI Updates**: Shows game phase, remaining time, and end-game results

Without pygame, this would just be game logic code with no visual interface. Pygame transforms the strategic board game rules into an
interactive, playable desktop application that users can see and interact with using mouse and keyboard.
