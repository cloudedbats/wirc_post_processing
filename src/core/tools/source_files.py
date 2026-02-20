#!/usr/bin/python3

import asyncio
import logging
import pathlib
from datetime import datetime

import src.core as core
import src.core.tools as tools


class SourceFiles(core.WorkflowModuleBase):
    """ """

    def __init__(self, logger=None, logger_name="DefaultLogger"):
        """ """
        super().__init__(logger, logger_name)
        self.clear()

    def clear(self):
        """ """
        super().clear()

    def configure(self, config_dict):
        """ """
        super().configure(config_dict)
        p = config_dict.get("parameters", {})
        self.source_dir = p.get("source_dir", "./wirc_recordings/")
        self.path_glob_string = p.get("path_glob_string", "**/rpi-cam0_*.mp4")

    async def pre_process_data(self):
        """ """
        await super().pre_process_data()

    async def process_data(self, data_dict={}):
        """Put your algorithmic code here."""
        try:
            results = []
            source_file = pathlib.Path(self.source_dir)
            # Create empty source dir if not exists.
            if not source_file.exists():
                source_file.mkdir(parents=True)

            source_files = list(source_file.glob(self.path_glob_string))

            for source_file in source_files:
                if source_file:
                    results.append(str(source_file))
            self.logger.info("Source dir: " + str(source_file.resolve()))
            self.logger.info("Number of source files found: " + str(len(results)))
            results.sort()

            for path in results:
                data_dict = {
                    "source_file": path,
                }
                await self.data_to_output_queues(data_dict, "source_file")

        except Exception as e:
            message = self.class_name + " - process_data. "
            message += "Exception: " + str(e)
            self.logger.error(message)

    async def post_process_data(self):
        """ """
        await super().post_process_data()

        # This tool is finished. No more data.
        await self.data_to_output_queues(None, "source_file")
