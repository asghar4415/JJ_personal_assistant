#!/usr/bin/env python
"""
run_jj.py - Simple entry point for JJ Assistant

Usage: python run_jj.py
"""

import logging
from src.utils.logger import setup_logger
from src.main import JJApplication
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


logger = setup_logger(__name__, log_level=logging.INFO)


def main():
    """Main entry point"""

    # Check for GROQ API key
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        print("\n" + "="*60)
        print("⚠️  WARNING: GROQ_API_KEY not configured")
        print("="*60)
        print("\nTo use JJ with LLM capabilities, set your Groq API key:\n")
        print("  On Windows PowerShell:")
        print("    $env:GROQ_API_KEY = 'your-api-key-here'")
        print("\n  On Windows Command Prompt:")
        print("    set GROQ_API_KEY=your-api-key-here")
        print("\n  On Linux/Mac:")
        print("    export GROQ_API_KEY='your-api-key-here'")
        print("\nGet your free API key at: https://console.groq.com")
        print("="*60 + "\n")

        response = input("Continue without LLM? (y/n): ").strip().lower()
        if response != 'y':
            print("Exiting.")
            sys.exit(1)

    # Create and run application
    try:
        app = JJApplication()
        app.initialize()
        app.start()
    except KeyboardInterrupt:
        print("\n\nShutdown requested.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
