#!/usr/bin/env python3
"""
Test runner for Wall Go game
Usage examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --category board   # Run only board tests
    python run_tests.py --verbose          # Run with detailed output
    python run_tests.py --quick            # Run only basic functionality tests
"""

import unittest
import sys
import os
from test_wall_go import *

def run_quick_tests():
    """Run essential tests for basic functionality"""
    suite = unittest.TestSuite()
    
    # Add critical tests
    suite.addTest(TestPiece('test_piece_creation'))
    suite.addTest(TestPiece('test_can_move_to_valid_position'))
    suite.addTest(TestBoard('test_add_and_get_piece'))
    suite.addTest(TestBoard('test_can_move_between_no_walls'))
    suite.addTest(TestBoard('test_can_move_between_with_walls'))
    suite.addTest(TestGameFlow('test_initial_piece_setup'))
    
    return suite

def run_category_tests(category):
    """Run tests for specific category"""
    suite = unittest.TestSuite()
    
    category_map = {
        'piece': TestPiece,
        'wall': TestWall,
        'board': TestBoard,
        'territory': TestTerritoryDetection,
        'game': TestGameFlow,
        'movement': TestMovementLogic,
        'scoring': TestScoring
    }
    
    if category in category_map:
        suite.addTest(unittest.makeSuite(category_map[category]))
    
    return suite

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Wall Go tests')
    parser.add_argument('--category', 
                       choices=['piece', 'wall', 'board', 'territory', 'game', 'movement', 'scoring'], 
                       help='Test category to run')
    parser.add_argument('--quick', action='store_true', 
                       help='Run only essential tests')
    parser.add_argument('--verbose', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    # Choose test suite
    if args.quick:
        suite = run_quick_tests()
        print("Running quick tests...")
    elif args.category:
        suite = run_category_tests(args.category)
        print(f"Running {args.category} tests...")
    else:
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules['test_wall_go'])
        print("Running all tests...")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2]}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())
