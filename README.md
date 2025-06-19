### What is the major purpose of pygame module here?

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
