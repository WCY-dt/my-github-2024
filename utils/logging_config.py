"""
This module contains a function that configures the logging module to log to a file named app.log 
with INFO level and a specific format.

Functions:
    setup_logging() -> None:
        Configures the logging module to log to a file named app.log with INFO level and a specific
        format.
"""

import logging


def setup_logging() -> None:
    """
    Configures the logging module to log to a file named
    app.log with INFO level and a specific format.
    """
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(message)s",
    )
