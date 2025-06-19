import unittest
import sys
import os

# Add the current directory to the path so we can import wall_go
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wall_go import (
    Piece, Wall, Board, WallGoGame, Player, WallSide, GamePhase, Direction
)

class TestPiece(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.piece = Piece(3, 3, Player.RED)
    
    def test_piece_creation(self):
        """Test piece initialization"""
        self.assertEqual(self.piece.x, 3)
        self.assertEqual(self.piece.y, 3)
        self.assertEqual(self.piece.player, Player.RED)
        self.assertFalse(self.piece.has_acted)
    
    def test_piece_reset_action(self):
        """Test piece action reset"""
        self.piece.has_acted = True
        self.piece.reset_action()
        self.assertFalse(self.piece.has_acted)
    
    def test_can_move_to_valid_position(self):
        """Test valid movement"""
        # Empty adjacent cell
        self.assertTrue(self.piece.can_move_to(3, 4, self.board))
        self.assertTrue(self.piece.can_move_to(4, 3, self.board))
    
    def test_can_move_to_invalid_position(self):
        """Test invalid movement"""
        # Out of bounds
        self.assertFalse(self.piece.can_move_to(-1, 3, self.board))
        self.assertFalse(self.piece.can_move_to(7, 3, self.board))
        
        # Occupied by another piece
        self.board.add_piece(Piece(3, 4, Player.BLUE))
        self.assertFalse(self.piece.can_move_to(3, 4, self.board))

class TestWall(unittest.TestCase):
    def test_wall_creation(self):
        """Test wall initialization"""
        wall = Wall(2, 3, WallSide.TOP, Player.RED)
        self.assertEqual(wall.x, 2)
        self.assertEqual(wall.y, 3)
        self.assertEqual(wall.side, WallSide.TOP)
        self.assertEqual(wall.player, Player.RED)
    
    def test_wall_equality(self):
        """Test wall equality comparison"""
        wall1 = Wall(2, 3, WallSide.TOP, Player.RED)
        wall2 = Wall(2, 3, WallSide.TOP, Player.BLUE)
        wall3 = Wall(2, 3, WallSide.BOTTOM, Player.RED)
        
        self.assertEqual(wall1, wall2)  # Same position and side
        self.assertNotEqual(wall1, wall3)  # Different side

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
    
    def test_add_and_get_piece(self):
        """Test adding and retrieving pieces"""
        piece = Piece(2, 3, Player.RED)
        self.board.add_piece(piece)
        
        retrieved = self.board.get_piece_at(2, 3)
        self.assertEqual(retrieved, piece)
        
        # No piece at empty location
        self.assertIsNone(self.board.get_piece_at(4, 5))
    
    def test_get_pieces_by_player(self):
        """Test filtering pieces by player"""
        red_piece1 = Piece(1, 1, Player.RED)
        red_piece2 = Piece(2, 2, Player.RED)
        blue_piece = Piece(3, 3, Player.BLUE)
        
        self.board.add_piece(red_piece1)
        self.board.add_piece(red_piece2)
        self.board.add_piece(blue_piece)
        
        red_pieces = self.board.get_pieces_by_player(Player.RED)
        blue_pieces = self.board.get_pieces_by_player(Player.BLUE)
        
        self.assertEqual(len(red_pieces), 2)
        self.assertEqual(len(blue_pieces), 1)
        self.assertIn(red_piece1, red_pieces)
        self.assertIn(red_piece2, red_pieces)
        self.assertIn(blue_piece, blue_pieces)
    
    def test_wall_operations(self):
        """Test wall addition and checking"""
        wall = Wall(2, 3, WallSide.TOP, Player.RED)
        self.board.add_wall(wall)
        
        self.assertTrue(self.board.has_wall(2, 3, WallSide.TOP))
        self.assertFalse(self.board.has_wall(2, 3, WallSide.BOTTOM))
    
    def test_can_move_between_no_walls(self):
        """Test movement between adjacent cells without walls"""
        # Horizontal movement
        self.assertTrue(self.board.can_move_between(2, 3, 3, 3))
        self.assertTrue(self.board.can_move_between(3, 3, 2, 3))
        
        # Vertical movement
        self.assertTrue(self.board.can_move_between(2, 3, 2, 4))
        self.assertTrue(self.board.can_move_between(2, 4, 2, 3))
    
    def test_can_move_between_with_walls(self):
        """Test movement blocked by walls"""
        # Add wall blocking rightward movement from (2,3)
        wall = Wall(2, 3, WallSide.RIGHT, Player.RED)
        self.board.add_wall(wall)
        
        self.assertFalse(self.board.can_move_between(2, 3, 3, 3))
        self.assertTrue(self.board.can_move_between(2, 3, 2, 4))  # Other directions still work
    
    def test_can_move_between_non_adjacent(self):
        """Test that non-adjacent moves are invalid"""
        self.assertFalse(self.board.can_move_between(2, 3, 4, 3))  # 2 steps
        self.assertFalse(self.board.can_move_between(2, 3, 3, 4))  # Diagonal
    
    def test_get_available_wall_sides(self):
        """Test getting available wall sides"""
        # All sides should be available initially
        available = self.board.get_available_wall_sides(3, 3)
        self.assertEqual(len(available), 4)
        
        # Add a wall and check it's no longer available
        wall = Wall(3, 3, WallSide.TOP, Player.RED)
        self.board.add_wall(wall)
        
        available = self.board.get_available_wall_sides(3, 3)
        self.assertEqual(len(available), 3)
        self.assertNotIn(WallSide.TOP, available)

class TestTerritoryDetection(unittest.TestCase):
    def setUp(self):
        self.board = Board()
    
    def test_simple_territory(self):
        """Test simple enclosed territory"""
        # Create a 2x2 enclosed area with red piece
        red_piece = Piece(1, 1, Player.RED)
        self.board.add_piece(red_piece)
        
        # Add walls to enclose the area
        walls = [
            Wall(1, 1, WallSide.TOP, Player.RED),
            Wall(1, 1, WallSide.LEFT, Player.RED),
            Wall(1, 1, WallSide.RIGHT, Player.RED),
            Wall(1, 1, WallSide.BOTTOM, Player.RED),
        ]
        
        for wall in walls:
            self.board.add_wall(wall)
        
        territories = self.board.find_territories()
        
        # Should have at least one red territory
        self.assertGreater(len(territories[Player.RED]), 0)
    
    def test_mixed_territory(self):
        """Test territory with multiple players (should not belong to anyone)"""
        # Add both red and blue pieces in same area
        self.board.add_piece(Piece(2, 2, Player.RED))
        self.board.add_piece(Piece(2, 3, Player.BLUE))
        
        territories = self.board.find_territories()
        
        # This area should not be claimed by either player
        # (This test depends on the specific territory detection implementation)
        pass
    
    def test_game_over_condition(self):
        """Test game over detection"""
        # Initially, game should not be over
        self.assertFalse(self.board.is_game_over())
        
        # Add pieces and walls to create separate territories
        # This is a complex scenario that would need specific setup

class TestGameFlow(unittest.TestCase):
    def setUp(self):
        # Create game without initializing pygame (for testing)
        self.game = None  # We'll test individual methods
    
    def test_initial_piece_setup(self):
        """Test initial piece placement"""
        board = Board()
        
        # Simulate initial setup
        red_fixed = [(1, 1), (5, 5)]
        blue_fixed = [(1, 5), (5, 1)]
        
        for x, y in red_fixed:
            board.add_piece(Piece(x, y, Player.RED))
        
        for x, y in blue_fixed:
            board.add_piece(Piece(x, y, Player.BLUE))
        
        # Check pieces are in correct positions
        self.assertIsNotNone(board.get_piece_at(1, 1))
        self.assertIsNotNone(board.get_piece_at(5, 5))
        self.assertIsNotNone(board.get_piece_at(1, 5))
        self.assertIsNotNone(board.get_piece_at(5, 1))
        
        # Check correct players
        self.assertEqual(board.get_piece_at(1, 1).player, Player.RED)
        self.assertEqual(board.get_piece_at(5, 5).player, Player.RED)
        self.assertEqual(board.get_piece_at(1, 5).player, Player.BLUE)
        self.assertEqual(board.get_piece_at(5, 1).player, Player.BLUE)

class TestMovementLogic(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.piece = Piece(3, 3, Player.RED)
        self.board.add_piece(self.piece)
    
    def test_one_step_moves(self):
        """Test all valid 1-step moves"""
        valid_moves = [
            (3, 2),  # Up
            (3, 4),  # Down
            (2, 3),  # Left
            (4, 3),  # Right
        ]
        
        for x, y in valid_moves:
            self.assertTrue(self.piece.can_move_to(x, y, self.board))
    
    def test_two_step_moves(self):
        """Test 2-step moves (would need path checking)"""
        # This would require implementing the full 2-step movement logic
        # For now, we test that the basic movement validation works
        pass
    
    def test_blocked_moves(self):
        """Test moves blocked by other pieces"""
        # Add blocking piece
        blocking_piece = Piece(3, 2, Player.BLUE)
        self.board.add_piece(blocking_piece)
        
        # Should not be able to move to occupied space
        self.assertFalse(self.piece.can_move_to(3, 2, self.board))
    
    def test_wall_blocked_moves(self):
        """Test moves blocked by walls"""
        # Add wall blocking upward movement
        wall = Wall(3, 3, WallSide.TOP, Player.RED)
        self.board.add_wall(wall)
        
        # Should not be able to move up
        self.assertFalse(self.board.can_move_between(3, 3, 3, 2))

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.board = Board()
    
    def test_territory_counting(self):
        """Test territory size calculation"""
        # Create a simple territory and verify counting
        # This would need a complete territory setup
        pass
    
    def test_winner_determination(self):
        """Test winner determination logic"""
        # Test various scoring scenarios:
        # 1. Clear winner by total score
        # 2. Tie broken by largest territory
        # 3. Complete tie (draw)
        pass

if __name__ == '__main__':
    # Run specific test categories
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Wall Go tests')
    parser.add_argument('--category', choices=['piece', 'wall', 'board', 'territory', 'game', 'movement', 'scoring', 'all'], 
                       default='all', help='Test category to run')
    
    args = parser.parse_args()
    
    if args.category == 'all':
        unittest.main(argv=[''])
    else:
        # Run specific test category
        suite = unittest.TestSuite()
        
        if args.category == 'piece':
            suite.addTest(unittest.makeSuite(TestPiece))
        elif args.category == 'wall':
            suite.addTest(unittest.makeSuite(TestWall))
        elif args.category == 'board':
            suite.addTest(unittest.makeSuite(TestBoard))
        elif args.category == 'territory':
            suite.addTest(unittest.makeSuite(TestTerritoryDetection))
        elif args.category == 'game':
            suite.addTest(unittest.makeSuite(TestGameFlow))
        elif args.category == 'movement':
            suite.addTest(unittest.makeSuite(TestMovementLogic))
        elif args.category == 'scoring':
            suite.addTest(unittest.makeSuite(TestScoring))
        
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
