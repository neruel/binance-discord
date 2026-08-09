#!/usr/bin/env python3
"""
Test script to verify command setup
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock discord objects to avoid needing a real connection
class MockInteraction:
    pass

class MockCommandTree:
    def __init__(self):
        self.commands = []

    def command(self, name=None, description=None):
        def decorator(func):
            self.commands.append((name or func.__name__, description, func))
            return func
        return decorator

def test_setup_commands():
    print("Testing command setup...")
    try:
        from bot.commands import setup_commands
        # Create a mock tree
        tree = MockCommandTree()
        # Call setup_commands
        setup_commands(tree)
        print(f"   Found {len(tree.commands)} commands")
        for name, desc, func in tree.commands:
            print(f"   - {name}: {desc}")
        # Check that we have the market command
        market_cmd = [c for c in tree.commands if c[0] == 'market']
        if market_cmd:
            print("   � ✓ 'market' command found")
        else:
            print("   � ✗ 'market' command missing")
            return False
        print("   All command tests passed!")
        return True
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_setup_commands()
    sys.exit(0 if success else 1)