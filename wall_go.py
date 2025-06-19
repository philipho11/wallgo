import pygame
import sys
import time
from enum import Enum
from typing import List, Tuple, Optional, Set

# Initialize Pygame
pygame.init()

# Game constants
BOARD_SIZE = 7
CELL_SIZE = 80
WALL_THICKNESS = 6
SCREEN_WIDTH = BOARD_SIZE * CELL_SIZE + 300  # Extra space for UI
SCREEN_HEIGHT = BOARD_SIZE * CELL_SIZE + 100
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_RED = (255, 100, 100)
LIGHT_BLUE = (100, 100, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class GamePhase(Enum):
    PLACEMENT = "placement"
    ACTION = "action"
    GAME_OVER = "game_over"

class Player(Enum):
    RED = "red"
    BLUE = "blue"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class WallSide(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"

class Piece:
    def __init__(self, x: int, y: int, player: Player):
        self.x = x
        self.y = y
        self.player = player
        self.has_acted = False
    
    def reset_action(self):
        self.has_acted = False
    
    def can_move_to(self, new_x: int, new_y: int, board) -> bool:
        """Check if piece can move to the given position"""
        if not (0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE):
            return False
        
        # Check if there's another piece at the destination
        if board.get_piece_at(new_x, new_y):
            return False
        
        # Check if path is blocked by walls
        return board.can_move_between(self.x, self.y, new_x, new_y)

class Wall:
    def __init__(self, x: int, y: int, side: WallSide, player: Player):
        self.x = x
        self.y = y
        self.side = side
        self.player = player
    
    def __eq__(self, other):
        if not isinstance(other, Wall):
            return False
        return (self.x == other.x and self.y == other.y and 
                self.side == other.side)
    
    def __hash__(self):
        return hash((self.x, self.y, self.side))

class Board:
    def __init__(self):
        self.pieces: List[Piece] = []
        self.walls: Set[Wall] = set()
        
    def add_piece(self, piece: Piece):
        self.pieces.append(piece)
    
    def get_piece_at(self, x: int, y: int) -> Optional[Piece]:
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece
        return None
    
    def get_pieces_by_player(self, player: Player) -> List[Piece]:
        return [piece for piece in self.pieces if piece.player == player]
    
    def add_wall(self, wall: Wall):
        self.walls.add(wall)
    
    def has_wall(self, x: int, y: int, side: WallSide) -> bool:
        return Wall(x, y, side, Player.RED) in self.walls or Wall(x, y, side, Player.BLUE) in self.walls
    
    def can_move_between(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if movement between two adjacent cells is possible"""
        dx = x2 - x1
        dy = y2 - y1
        
        # Must be adjacent cells
        if abs(dx) + abs(dy) != 1:
            return False
        
        # Check for walls blocking the movement
        if dx == 1:  # Moving right
            return not self.has_wall(x1, y1, WallSide.RIGHT)
        elif dx == -1:  # Moving left
            return not self.has_wall(x1, y1, WallSide.LEFT)
        elif dy == 1:  # Moving down
            return not self.has_wall(x1, y1, WallSide.BOTTOM)
        elif dy == -1:  # Moving up
            return not self.has_wall(x1, y1, WallSide.TOP)
        
        return False
    
    def get_available_wall_sides(self, x: int, y: int) -> List[WallSide]:
        """Get available wall sides for a cell"""
        available = []
        for side in WallSide:
            if not self.has_wall(x, y, side):
                # Check if it's not a border wall (borders are implicit)
                if side == WallSide.TOP and y == 0:
                    continue
                if side == WallSide.BOTTOM and y == BOARD_SIZE - 1:
                    continue
                if side == WallSide.LEFT and x == 0:
                    continue
                if side == WallSide.RIGHT and x == BOARD_SIZE - 1:
                    continue
                available.append(side)
        return available
    
    def find_territories(self) -> dict:
        """Find all territories using flood fill algorithm"""
        visited = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        territories = {Player.RED: [], Player.BLUE: []}
        
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if not visited[y][x]:
                    territory = self._flood_fill(x, y, visited)
                    if territory:
                        # Determine territory owner
                        players_in_territory = set()
                        for tx, ty in territory:
                            piece = self.get_piece_at(tx, ty)
                            if piece:
                                players_in_territory.add(piece.player)
                        
                        # Territory belongs to a player only if it contains only their pieces
                        if len(players_in_territory) == 1:
                            player = list(players_in_territory)[0]
                            territories[player].append(territory)
        
        return territories
    
    def _flood_fill(self, start_x: int, start_y: int, visited: List[List[bool]]) -> List[Tuple[int, int]]:
        """Flood fill to find connected territory"""
        if visited[start_y][start_x]:
            return []
        
        territory = []
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            if visited[y][x]:
                continue
            
            visited[y][x] = True
            territory.append((x, y))
            
            # Check all four directions
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 
                    not visited[ny][nx] and self.can_move_between(x, y, nx, ny)):
                    stack.append((nx, ny))
        
        return territory
    
    def is_game_over(self) -> bool:
        """Check if all pieces are in separate territories"""
        territories = self.find_territories()
        
        # Count pieces in territories
        red_pieces_in_territory = 0
        blue_pieces_in_territory = 0
        
        for player_territories in territories.values():
            for territory in player_territories:
                for x, y in territory:
                    piece = self.get_piece_at(x, y)
                    if piece:
                        if piece.player == Player.RED:
                            red_pieces_in_territory += 1
                        else:
                            blue_pieces_in_territory += 1
        
        # Game ends when all pieces are in territories
        total_pieces = len(self.pieces)
        return red_pieces_in_territory + blue_pieces_in_territory == total_pieces

class WallGoGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Wall Go")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.board = Board()
        self.phase = GamePhase.PLACEMENT
        self.current_player = Player.RED
        self.placement_count = 0
        self.turn_start_time = time.time()
        self.turn_time_limit = 90  # seconds
        
        # UI state
        self.selected_piece = None
        self.possible_moves = []
        self.possible_wall_sides = []
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize game
        self.setup_initial_pieces()
    
    def setup_initial_pieces(self):
        """Setup initial piece positions"""
        # Fixed starting positions for 2-player game
        red_fixed = [(1, 1), (5, 5)]
        blue_fixed = [(1, 5), (5, 1)]
        
        for x, y in red_fixed:
            self.board.add_piece(Piece(x, y, Player.RED))
        
        for x, y in blue_fixed:
            self.board.add_piece(Piece(x, y, Player.BLUE))
    
    def get_player_color(self, player: Player) -> tuple:
        return RED if player == Player.RED else BLUE
    
    def get_light_player_color(self, player: Player) -> tuple:
        return LIGHT_RED if player == Player.RED else LIGHT_BLUE
    
    def handle_placement_phase(self, mouse_pos):
        """Handle piece placement during placement phase"""
        if self.placement_count >= 4:  # All pieces placed
            self.phase = GamePhase.ACTION
            self.current_player = Player.RED
            self.turn_start_time = time.time()
            return
        
        # Convert mouse position to board coordinates
        board_x, board_y = self.screen_to_board(mouse_pos)
        if board_x is None or board_y is None:
            return
        
        # Check if position is empty
        if self.board.get_piece_at(board_x, board_y):
            return
        
        # Determine which player places next piece
        if self.placement_count == 0:  # Red's first extra piece
            player = Player.RED
        elif self.placement_count == 1:  # Blue's first extra piece
            player = Player.BLUE
        elif self.placement_count == 2:  # Blue's second extra piece
            player = Player.BLUE
        else:  # Red's second extra piece
            player = Player.RED
        
        self.board.add_piece(Piece(board_x, board_y, player))
        self.placement_count += 1
    
    def handle_action_phase(self, mouse_pos):
        """Handle actions during action phase"""
        board_x, board_y = self.screen_to_board(mouse_pos)
        if board_x is None or board_y is None:
            return
        
        if self.selected_piece is None:
            # Select a piece
            piece = self.board.get_piece_at(board_x, board_y)
            if piece and piece.player == self.current_player and not piece.has_acted:
                self.selected_piece = piece
                self.calculate_possible_moves()
                self.calculate_possible_wall_sides()
        else:
            # Try to move
            if (board_x, board_y) in self.possible_moves:
                # Move piece
                self.selected_piece.x = board_x
                self.selected_piece.y = board_y
                # After moving, clear possible moves and only allow wall placement
                self.possible_moves = []
                self.calculate_possible_wall_sides()
            elif self.selected_piece.x == board_x and self.selected_piece.y == board_y:
                # Clicked on same piece - if no moves made yet, show options
                if self.possible_moves:  # Still can move
                    pass
                else:  # Already moved, only wall placement allowed
                    pass
            else:
                # Deselect piece only if they haven't moved yet
                if self.possible_moves:  # Can still move, allow deselection
                    self.selected_piece = None
                    self.possible_moves = []
                    self.possible_wall_sides = []
                # If they've already moved, don't allow deselection until wall is placed
    
    def handle_wall_placement(self, mouse_pos):
        """Handle wall placement"""
        if not self.selected_piece:
            return
        
        # Check if click is on a wall side
        wall_side = self.get_wall_side_from_mouse(mouse_pos, self.selected_piece.x, self.selected_piece.y)
        if wall_side and wall_side in self.possible_wall_sides:
            # Place wall
            wall = Wall(self.selected_piece.x, self.selected_piece.y, wall_side, self.current_player)
            self.board.add_wall(wall)
            
            # Mark piece as acted and end turn
            self.selected_piece.has_acted = True
            self.end_turn()
    
    def calculate_possible_moves(self):
        """Calculate possible moves for selected piece"""
        if not self.selected_piece:
            return
        
        self.possible_moves = []
        start_x, start_y = self.selected_piece.x, self.selected_piece.y
        
        # Add current position (0 steps)
        self.possible_moves.append((start_x, start_y))
        
        # Check 1-step moves
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = start_x + dx, start_y + dy
            if self.selected_piece.can_move_to(new_x, new_y, self.board):
                self.possible_moves.append((new_x, new_y))
                
                # Check 2-step moves from this position
                for dx2, dy2 in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    new_x2, new_y2 = new_x + dx2, new_y + dy2
                    if (0 <= new_x2 < BOARD_SIZE and 0 <= new_y2 < BOARD_SIZE and
                        not self.board.get_piece_at(new_x2, new_y2) and
                        self.board.can_move_between(new_x, new_y, new_x2, new_y2) and
                        (new_x2, new_y2) not in self.possible_moves):
                        self.possible_moves.append((new_x2, new_y2))
    
    def calculate_possible_wall_sides(self):
        """Calculate possible wall sides for selected piece"""
        if not self.selected_piece:
            return
        
        self.possible_wall_sides = self.board.get_available_wall_sides(
            self.selected_piece.x, self.selected_piece.y)
    
    def end_turn(self):
        """End current player's turn"""
        self.selected_piece = None
        self.possible_moves = []
        self.possible_wall_sides = []
        
        # Check if all current player's pieces have acted
        current_pieces = self.board.get_pieces_by_player(self.current_player)
        if all(piece.has_acted for piece in current_pieces):
            # Reset all pieces for next round
            for piece in self.board.pieces:
                piece.reset_action()
        
        # Switch player
        self.current_player = Player.BLUE if self.current_player == Player.RED else Player.RED
        self.turn_start_time = time.time()
        
        # Check game over condition
        if self.board.is_game_over():
            self.phase = GamePhase.GAME_OVER
    
    def screen_to_board(self, pos) -> Tuple[Optional[int], Optional[int]]:
        """Convert screen coordinates to board coordinates"""
        x, y = pos
        if x < 0 or y < 0 or x >= BOARD_SIZE * CELL_SIZE or y >= BOARD_SIZE * CELL_SIZE:
            return None, None
        return x // CELL_SIZE, y // CELL_SIZE
    
    def get_wall_side_from_mouse(self, mouse_pos, cell_x, cell_y) -> Optional[WallSide]:
        """Determine which wall side was clicked"""
        mx, my = mouse_pos
        cell_screen_x = cell_x * CELL_SIZE
        cell_screen_y = cell_y * CELL_SIZE
        
        # Check if mouse is within cell bounds
        if not (cell_screen_x <= mx < cell_screen_x + CELL_SIZE and
                cell_screen_y <= my < cell_screen_y + CELL_SIZE):
            return None
        
        # Determine which side based on relative position
        rel_x = mx - cell_screen_x
        rel_y = my - cell_screen_y
        
        margin = 15  # Pixels from edge to consider as wall side
        
        if rel_y < margin:
            return WallSide.TOP
        elif rel_y > CELL_SIZE - margin:
            return WallSide.BOTTOM
        elif rel_x < margin:
            return WallSide.LEFT
        elif rel_x > CELL_SIZE - margin:
            return WallSide.RIGHT
        
        return None
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.phase == GamePhase.PLACEMENT:
                        self.handle_placement_phase(event.pos)
                    elif self.phase == GamePhase.ACTION:
                        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            # Shift+click for wall placement
                            self.handle_wall_placement(event.pos)
                        else:
                            self.handle_action_phase(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update game state"""
        # Check turn time limit
        if self.phase == GamePhase.ACTION:
            elapsed_time = time.time() - self.turn_start_time
            if elapsed_time > self.turn_time_limit:
                # Time's up - place random wall and end turn
                if self.selected_piece:
                    available_sides = self.board.get_available_wall_sides(
                        self.selected_piece.x, self.selected_piece.y)
                    if available_sides:
                        import random
                        random_side = random.choice(available_sides)
                        wall = Wall(self.selected_piece.x, self.selected_piece.y, 
                                  random_side, self.current_player)
                        self.board.add_wall(wall)
                        self.selected_piece.has_acted = True
                self.end_turn()
    
    def draw(self):
        """Draw the game"""
        self.screen.fill(WHITE)
        
        # Draw board
        self.draw_board()
        
        # Draw pieces
        self.draw_pieces()
        
        # Draw walls
        self.draw_walls()
        
        # Draw UI
        self.draw_ui()
        
        # Draw possible moves and wall sides
        if self.phase == GamePhase.ACTION and self.selected_piece:
            self.draw_possible_moves()
            self.draw_possible_wall_sides()
        
        pygame.display.flip()
    
    def draw_board(self):
        """Draw the game board"""
        for x in range(BOARD_SIZE + 1):
            pygame.draw.line(self.screen, BLACK, 
                           (x * CELL_SIZE, 0), 
                           (x * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
        
        for y in range(BOARD_SIZE + 1):
            pygame.draw.line(self.screen, BLACK, 
                           (0, y * CELL_SIZE), 
                           (BOARD_SIZE * CELL_SIZE, y * CELL_SIZE))
    
    def draw_pieces(self):
        """Draw game pieces"""
        for piece in self.board.pieces:
            x = piece.x * CELL_SIZE + CELL_SIZE // 4
            y = piece.y * CELL_SIZE + CELL_SIZE // 4
            size = CELL_SIZE // 2
            
            color = self.get_player_color(piece.player)
            if piece == self.selected_piece:
                color = self.get_light_player_color(piece.player)
            
            pygame.draw.circle(self.screen, color, (x + size//2, y + size//2), size//2)
            
            # Draw border
            pygame.draw.circle(self.screen, BLACK, (x + size//2, y + size//2), size//2, 2)
            
            # Mark pieces that have acted
            if piece.has_acted:
                pygame.draw.circle(self.screen, BLACK, (x + size//2, y + size//2), size//4)
    
    def draw_walls(self):
        """Draw walls"""
        for wall in self.board.walls:
            color = self.get_player_color(wall.player)
            x = wall.x * CELL_SIZE
            y = wall.y * CELL_SIZE
            
            if wall.side == WallSide.TOP:
                pygame.draw.rect(self.screen, color, 
                               (x, y - WALL_THICKNESS//2, CELL_SIZE, WALL_THICKNESS))
            elif wall.side == WallSide.BOTTOM:
                pygame.draw.rect(self.screen, color, 
                               (x, y + CELL_SIZE - WALL_THICKNESS//2, CELL_SIZE, WALL_THICKNESS))
            elif wall.side == WallSide.LEFT:
                pygame.draw.rect(self.screen, color, 
                               (x - WALL_THICKNESS//2, y, WALL_THICKNESS, CELL_SIZE))
            elif wall.side == WallSide.RIGHT:
                pygame.draw.rect(self.screen, color, 
                               (x + CELL_SIZE - WALL_THICKNESS//2, y, WALL_THICKNESS, CELL_SIZE))
    
    def draw_possible_moves(self):
        """Draw possible move positions"""
        for x, y in self.possible_moves:
            screen_x = x * CELL_SIZE + CELL_SIZE // 4
            screen_y = y * CELL_SIZE + CELL_SIZE // 4
            size = CELL_SIZE // 2
            
            pygame.draw.rect(self.screen, GREEN, (screen_x, screen_y, size, size), 3)
    
    def draw_possible_wall_sides(self):
        """Draw possible wall placement sides"""
        if not self.selected_piece:
            return
        
        x = self.selected_piece.x * CELL_SIZE
        y = self.selected_piece.y * CELL_SIZE
        
        # Use different color if wall placement is mandatory (after moving)
        wall_color = RED if not self.possible_moves else YELLOW
        
        for side in self.possible_wall_sides:
            if side == WallSide.TOP:
                pygame.draw.rect(self.screen, wall_color, 
                               (x, y - WALL_THICKNESS//2, CELL_SIZE, WALL_THICKNESS))
            elif side == WallSide.BOTTOM:
                pygame.draw.rect(self.screen, wall_color, 
                               (x, y + CELL_SIZE - WALL_THICKNESS//2, CELL_SIZE, WALL_THICKNESS))
            elif side == WallSide.LEFT:
                pygame.draw.rect(self.screen, wall_color, 
                               (x - WALL_THICKNESS//2, y, WALL_THICKNESS, CELL_SIZE))
            elif side == WallSide.RIGHT:
                pygame.draw.rect(self.screen, wall_color, 
                               (x + CELL_SIZE - WALL_THICKNESS//2, y, WALL_THICKNESS, CELL_SIZE))
    
    def draw_ui(self):
        """Draw user interface"""
        ui_x = BOARD_SIZE * CELL_SIZE + 20
        
        # Current phase
        phase_text = f"Phase: {self.phase.value.title()}"
        text_surface = self.font.render(phase_text, True, BLACK)
        self.screen.blit(text_surface, (ui_x, 20))
        
        if self.phase == GamePhase.PLACEMENT:
            # Placement instructions
            remaining = 4 - self.placement_count
            placement_text = f"Place {remaining} more pieces"
            text_surface = self.small_font.render(placement_text, True, BLACK)
            self.screen.blit(text_surface, (ui_x, 60))
        
        elif self.phase == GamePhase.ACTION:
            # Current player
            player_text = f"Current: {self.current_player.value.title()}"
            color = self.get_player_color(self.current_player)
            text_surface = self.font.render(player_text, True, color)
            self.screen.blit(text_surface, (ui_x, 60))
            
            # Turn timer
            elapsed = time.time() - self.turn_start_time
            remaining_time = max(0, self.turn_time_limit - elapsed)
            timer_text = f"Time: {remaining_time:.1f}s"
            text_surface = self.small_font.render(timer_text, True, BLACK)
            self.screen.blit(text_surface, (ui_x, 100))
            
            # Instructions
            if self.selected_piece and not self.possible_moves:
                # Player has moved and must place wall
                instructions = [
                    "MUST place wall!",
                    "Shift+click yellow areas",
                    "to place wall",
                    "",
                    "R - Restart",
                    "ESC - Quit"
                ]
            else:
                instructions = [
                    "Click piece to select",
                    "Click green squares to move",
                    "Shift+click yellow areas",
                    "to place walls",
                    "",
                    "R - Restart",
                    "ESC - Quit"
                ]
            
            for i, instruction in enumerate(instructions):
                text_surface = self.small_font.render(instruction, True, BLACK)
                self.screen.blit(text_surface, (ui_x, 140 + i * 25))
        
        elif self.phase == GamePhase.GAME_OVER:
            # Calculate and display scores
            territories = self.board.find_territories()
            red_score = sum(len(territory) for territory in territories[Player.RED])
            blue_score = sum(len(territory) for territory in territories[Player.BLUE])
            
            game_over_text = "GAME OVER"
            text_surface = self.font.render(game_over_text, True, BLACK)
            self.screen.blit(text_surface, (ui_x, 60))
            
            red_score_text = f"Red: {red_score}"
            text_surface = self.font.render(red_score_text, True, RED)
            self.screen.blit(text_surface, (ui_x, 100))
            
            blue_score_text = f"Blue: {blue_score}"
            text_surface = self.font.render(blue_score_text, True, BLUE)
            self.screen.blit(text_surface, (ui_x, 140))
            
            # Winner
            if red_score > blue_score:
                winner_text = "Red Wins!"
                color = RED
            elif blue_score > red_score:
                winner_text = "Blue Wins!"
                color = BLUE
            else:
                # Check largest territory
                red_largest = max((len(t) for t in territories[Player.RED]), default=0)
                blue_largest = max((len(t) for t in territories[Player.BLUE]), default=0)
                
                if red_largest > blue_largest:
                    winner_text = "Red Wins! (Largest Territory)"
                    color = RED
                elif blue_largest > red_largest:
                    winner_text = "Blue Wins! (Largest Territory)"
                    color = BLUE
                else:
                    winner_text = "Draw!"
                    color = BLACK
            
            text_surface = self.font.render(winner_text, True, color)
            self.screen.blit(text_surface, (ui_x, 180))
            
            restart_text = "Press R to restart"
            text_surface = self.small_font.render(restart_text, True, BLACK)
            self.screen.blit(text_surface, (ui_x, 220))
    
    def restart_game(self):
        """Restart the game"""
        self.board = Board()
        self.phase = GamePhase.PLACEMENT
        self.current_player = Player.RED
        self.placement_count = 0
        self.selected_piece = None
        self.possible_moves = []
        self.possible_wall_sides = []
        self.turn_start_time = time.time()
        self.setup_initial_pieces()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = WallGoGame()
    game.run()
