#!/usr/bin/python3

import asyncio
import logging
import pathlib
import yaml
from datetime import datetime

import src.core.tools as tools


class WorkflowEngine:
    """ """

    def __init__(self, logger=None, logger_name="DefaultLogger"):
        """ """
        self.logger = logger
        if self.logger == None:
            self.logger = logging.getLogger(logger_name)
        #
        self.class_name = self.__class__.__name__
        self.clear()

    def clear(self):
        """ """
        self.config = None
        self.workflow_tools = []
        self.tool_lookup = {}
        self.tool_config = {}

    def configure(self, parameters):
        """ """

    def run_startup(self, config_file):
        """ """
        asyncio.run(self.startup(config_file))

    async def startup(self, config_file):
        """ """
        self.load_config(config_file)
        await asyncio.sleep(0)
        self.create_tools()
        await asyncio.sleep(0)
        self.config_tools()
        await asyncio.sleep(0)
        self.connect_tools()
        await asyncio.sleep(0)
        await self.execute_tools()
        await asyncio.sleep(0)
        #
        # self.logger.info("Done.")

    def load_config(self, config_file):
        """ """
        config_path = pathlib.Path(config_file)
        with open(config_path) as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

    def create_tools(self):
        """ """
        for tool_dict in self.config.get("workflow", []):
            tool_id = tool_dict.get("tool_id", "")
            self.workflow_tools.append(tool_id)
            self.tool_config[tool_id] = tool_dict
            tool = tool_dict.get("tool", "")
            tool_object = tools.tool_factory(tool)
            if tool_object != None:
                self.tool_lookup[tool_id] = tool_object

    def config_tools(self):
        """ """
        for tool_id in self.workflow_tools:
            tool_dict = self.tool_config[tool_id]
            if tool_id in self.tool_lookup:
                self.tool_lookup[tool_id].configure(tool_dict)

    def connect_tools(self):
        """ """
        for tool_id in self.workflow_tools:
            tool_dict = self.tool_config[tool_id]
            if tool_id in self.tool_lookup:
                input_from = tool_dict.get("input_from", None)
                input_format = tool_dict.get("input_format", None)
                if input_from == None:
                    continue
                input_queue = self.tool_lookup[tool_id].get_input_queue()
                self.tool_lookup[input_from].add_output_queue(input_queue, input_format)

    async def execute_tools(self):
        """ """
        tasks = []
        try:
            try:
                time_start = datetime.now()
                self.logger.info(
                    "Processing started at: "
                    + time_start.isoformat().replace("T", " ")[:-3]
                )
                for tool_id in self.workflow_tools:
                    tool_dict = self.tool_config[tool_id]
                    if tool_id in self.tool_lookup:
                        task = await self.tool_lookup[tool_id].startup()
                        tasks.append(task)
                        await asyncio.sleep(0)
                # Wait until finished.
                await asyncio.wait(tasks)
                time_end = datetime.now()
                time_used = time_end - time_start
                self.logger.info("Finished. Time used: " + str(time_used))
            finally:
                for task in tasks:
                    try:
                        task.cancel()
                    except:
                        pass
        except Exception as e:
            self.logger.debug("Exception: " + str(e))
