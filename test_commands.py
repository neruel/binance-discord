#!/usr/bin/env python3
"""
Test script to verify slash command registration and handlers
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockCommandTree:
    def __init__(self):
        self.commands = []

    def command(self, name=None, description=None):
        def decorator(func):
            cmd_name = name or func.__name__
            self.commands.append((cmd_name, description, func))
            return func
        return decorator

def test_setup_commands():
    print("Testing slash command setup...")
    try:
        from bot.commands import setup_commands
        tree = MockCommandTree()
        setup_commands(tree)

        registered_names = [c[0] for c in tree.commands]
        print(f"   Registered commands ({len(registered_names)}): {registered_names}")

        required_commands = ["시세검색", "search", "market"]
        for req in required_commands:
            if req in registered_names:
                print(f"   [OK] Command '/{req}' is registered successfully")
            else:
                print(f"   [FAIL] Required command '/{req}' missing!")
                return False

        print("\nAll command registration tests PASSED!")
        return True
    except Exception as e:
        print(f"   Error during command setup test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_setup_commands()
    sys.exit(0 if success else 1)