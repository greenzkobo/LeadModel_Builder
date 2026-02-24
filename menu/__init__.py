"""
menu/__init__.py
=================
Entry point for the ML Toolkit menu system.

Usage:
    from menu.main import main
    main()

    # or directly:
    python -m menu.main
"""

from menu.main import main, MLToolkit

__all__ = ['main', 'MLToolkit']
