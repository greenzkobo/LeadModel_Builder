"""
reports/__init__.py
====================
Public API for the reports package.

Usage (unchanged from old report_generator.py):
    from reports import ReportGenerator

    report = ReportGenerator(trainer, evaluator, selector, client="Humana")
    report.generate_full_report()
"""

from .generator import ReportGenerator

__all__ = ['ReportGenerator']
