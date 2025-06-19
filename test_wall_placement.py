#!/usr/bin/env python3
"""
Specific tests for wall placement functionality
This addresses the issue where yellow wall areas weren't showing up
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wall_go import Board, Piece, Wall, WallSide, Player

class TestWallPlacement(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.piece = Piece(3, 3, Player.RED)
        self.board.add_piece(self.piece)
    
    def test_available_wall_sides_empty_board(self):
        """Test that all wall sides are available on empty board"""
        available = self.board.get_available_wall_sides(3, 3)
        
        print(f"Available wall sides at (3,3): {[side.value for side in available]}")
        
        # Should have all 4 sides available
        self.assertEqual(len(available), 4)
        self.assertIn(WallSide.TOP, available)
        self.assertIn(WallSide.BOTTOM, available)
        self.assertIn(WallSide.LEFT, available)
        self.assertIn(WallSide.RIGHT, available)
    
    def test_available_wall_sides_with_existing_wall(self):
        """Test wall sides when some walls already exist"""
        # Add a wall on top side
        wall = Wall(3, 3, WallSide.TOP, Player.RED)
        self.board.add_wall(wall)
        
        available = self.board.get_available_wall_sides(3, 3)
        
        print(f"Available wall sides after adding TOP wall: {[side.value for side in available]}")
        
        # Should have 3 sides available (not TOP)
        self.assertEqual(len(available), 3)
        self.assertNotIn(WallSide.TOP, available)
        self.assertIn(WallSide.BOTTOM, available)
        self.assertIn(WallSide.LEFT, available)
        self.assertIn(WallSide.RIGHT, available)
    
    def test_corner_piece_wall_sides(self):
        """Test wall sides for corner pieces"""
        # Test top-left corner
        corner_piece = Piece(0, 0, Player.BLUE)
        self.board.add_piece(corner_piece)
        
        available = self.board.get_available_wall_sides(0, 0)
        
        print(f"Available wall sides at corner (0,0): {[side.value for side in available]}")
        
        # All sides should still be available (borders don't prevent wall placement)
        self.assertEqual(len(available), 4)
    
    def test_edge_piece_wall_sides(self):
        """Test wall sides for edge pieces"""
        # Test top edge
        edge_piece = Piece(3, 0, Player.RED)
        self.board.add_piece(edge_piece)
        
        available = self.board.get_available_wall_sides(3, 0)
        
        print(f"Available wall sides at top edge (3,0): {[side.value for side in available]}")
        
        # All sides should be available
        self.assertEqual(len(available), 4)
    
    def test_wall_blocking_detection(self):
        """Test that walls properly block movement"""
        # Add wall on right side of piece at (3,3)
        wall = Wall(3, 3, WallSide.RIGHT, Player.RED)
        self.board.add_wall(wall)
        
        # Should not be able to move right
        can_move_right = self.board.can_move_between(3, 3, 4, 3)
        print(f"Can move right with RIGHT wall: {can_move_right}")
        self.assertFalse(can_move_right)
        
        # Should still be able to move in other directions
        can_move_up = self.board.can_move_between(3, 3, 3, 2)
        can_move_down = self.board.can_move_between(3, 3, 3, 4)
        can_move_left = self.board.can_move_between(3, 3, 2, 3)
        
        print(f"Can move up: {can_move_up}, down: {can_move_down}, left: {can_move_left}")
        
        self.assertTrue(can_move_up)
        self.assertTrue(can_move_down)
        self.assertTrue(can_move_left)
    
    def test_multiple_walls_same_cell(self):
        """Test multiple walls on same cell"""
        walls = [
            Wall(3, 3, WallSide.TOP, Player.RED),
            Wall(3, 3, WallSide.RIGHT, Player.BLUE),
        ]
        
        for wall in walls:
            self.board.add_wall(wall)
        
        available = self.board.get_available_wall_sides(3, 3)
        
        print(f"Available wall sides with 2 walls: {[side.value for side in available]}")
        
        # Should have 2 sides available
        self.assertEqual(len(available), 2)
        self.assertNotIn(WallSide.TOP, available)
        self.assertNotIn(WallSide.RIGHT, available)
        self.assertIn(WallSide.BOTTOM, available)
        self.assertIn(WallSide.LEFT, available)

def run_wall_placement_tests():
    """Run wall placement tests with detailed output"""
    print("=" * 60)
    print("WALL PLACEMENT DIAGNOSTIC TESTS")
    print("=" * 60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWallPlacement)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("✅ All wall placement tests passed!")
        print("The wall placement logic should be working correctly.")
        print("\nIf you're still not seeing yellow areas in the game:")
        print("1. Check that pieces are being selected properly")
        print("2. Verify the drawing order (walls drawn after board)")
        print("3. Ensure the wall thickness is visible")
    else:
        print("❌ Some tests failed - this explains the wall placement issue!")
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}")
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_wall_placement_tests()
