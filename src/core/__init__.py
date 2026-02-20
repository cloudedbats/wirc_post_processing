#!/usr/bin/python3

import os
from os import getcwd
import sys
import pathlib
import logging

import src.utils as utils

__version__ = "2026.0.0-development"

# Absolute paths to working directory and executable.
workdir_path = pathlib.Path(__file__).parent.parent.resolve()
executable_path = pathlib.Path(os.path.dirname(sys.argv[0]))
getcwd_path = pathlib.Path(getcwd())  # TODO - for test.
# print()
# print("DEBUG: Working directory path: ", str(workdir_path))
# print("DEBUG: Executable path: ", str(executable_path))
# print("DEBUG: getcwd path (for test): ", str(getcwd_path))

logger_name = "WircPPLogger"
logging_dir = pathlib.Path(executable_path.parent, "wircpp_logging")
log_file_name = "wircpp_info_log.txt"
debug_log_file_name = "wircpp_debug_log.txt"

from src.core.workflow_module_base import WorkflowModuleBase
from src.core.workflow_engine import WorkflowEngine

# Instances of classes.

# Logger.
logger = utils.Logger(logger_name=logger_name)
logger.setup_rotating_log(
    logging_dir=logging_dir,
    log_name=log_file_name,
    debug_log_name=debug_log_file_name,
)
logger_name = logger.get_logger_name()
logger = logging.getLogger(logger_name)
logger.info("")
logger.info("=== WIRC Post Processing ===")
logger.info("Version: " + __version__)
logger.info("")
logger.debug("Working directory path: " + str(workdir_path))
logger.debug("Executable path: " + str(executable_path))

# Workflow.
# workflow_engine = WorkflowEngine(logger_name=logger_name)
