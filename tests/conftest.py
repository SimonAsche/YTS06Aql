import pytest
import logging
import sys
import tracemalloc

def pytest_configure(config):
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('test_debug.log')
    file_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Optionally, reduce verbosity for external libraries
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)

    """Enable tracemalloc for debugging resource warnings"""
    tracemalloc.start()
 