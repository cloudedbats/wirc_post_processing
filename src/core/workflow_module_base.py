#!/usr/bin/python3

import abc
import asyncio
import logging


class WorkflowModuleBase:
    """ """

    def __init__(self, logger=None, logger_name="DefaultLogger"):
        """ """
        self.logger = logger
        if self.logger == None:
            self.logger = logging.getLogger(logger_name)
        # Used in logging messages to point out class.
        self.class_name = self.__class__.__name__

    @abc.abstractmethod
    def clear(self):
        """ """
        self.worker_task = None
        self.input_queue = None
        self.output_queues = []
        self.input_queue_size = 100

    @abc.abstractmethod
    def configure(self, config_dict):
        """ """
        # Create input queue.
        if config_dict.get("input_from", None) != None:
            self.input_queue_size = config_dict.get(
                "input_queue_size", self.input_queue_size
            )
            self.input_queue = asyncio.Queue(maxsize=self.input_queue_size)

    @abc.abstractmethod
    async def pre_process_data(self):
        """ """
        message = self.class_name + ": Started. "
        self.logger.info(message)

    @abc.abstractmethod
    async def process_data(self, data_dict={}):
        """ """
        pass

    @abc.abstractmethod
    async def post_process_data(self):
        """ """
        message = self.class_name + ": Ended. "
        self.logger.info(message)

    # Methods below for base class only.

    def get_input_queue(self):
        """ """
        return self.input_queue

    async def startup(self):
        """ """
        try:
            # Read data from input queue.
            self.worker_task = asyncio.create_task(
                self._worker(), name="Module " + self.class_name
            )
            return self.worker_task
        except Exception as e:
            message = self.class_name + " - startup. "
            message += "Exception: " + str(e)
            self.logger.error(message)

    async def shutdown(self):
        """ """
        try:
            self.capture_is_active = False
            if self.worker_task != None:
                self.worker_task.cancel()
                self.worker_task = None
        except Exception as e:
            message = self.class_name + " - shutdown. Exception: " + str(e)
            self.logger.error(message)

    async def _worker(self):
        """ """
        is_cancelled = False
        try:
            await self.pre_process_data()
            await asyncio.sleep(0)

            if self.input_queue == None:
                await self.process_data()
                return
            while True:
                try:
                    item = await self.input_queue.get()
                    try:
                        if item == None:
                            # Terminated by earlier workflow module.
                            break
                        elif item == False:
                            continue
                        else:
                            await self.process_data(item)
                    finally:
                        self.input_queue.task_done()
                        await asyncio.sleep(0)

                except asyncio.CancelledError:
                    is_cancelled = True
                    self.logger.info(self.class_name + " - Worker cancelled.")
                    await asyncio.sleep(0)
                    break
                except Exception as e:
                    message = self.class_name + " - Worker(1): " + str(e)
                    self.logger.error(message)
                await asyncio.sleep(0)
        except Exception as e:
            message = self.class_name + " - Worker(2). Exception: " + str(e)
            self.logger.error(message)
        finally:
            if is_cancelled:
                self.output_queues = []
            await self.post_process_data()
            # self.logger.info(self.class_name + " - Worker ended.")
            await asyncio.sleep(0)

    def set_input_queue(self, queue, format):
        """ """
        self.input_queue = queue
        self.input_queue_format = format

    def add_output_queue(self, queue, format):
        """ """
        queue_dict = {
            "queue": queue,
            "format": format,
        }
        self.output_queues.append(queue_dict)

    async def data_to_output_queues(self, data_dict, format):
        """ """
        try:
            for output_queue_dict in self.output_queues:
                if output_queue_dict["format"] == format:
                    try:
                        queue = output_queue_dict["queue"]
                        await queue.put(data_dict)
                    except Exception as e:
                        message = (
                            self.class_name + " - data_to_output_queues: " + str(e)
                        )
                        self.logger.error(message)
        except asyncio.QueueShutDown:
            message = self.class_name + " - data_to_output_queues: QueueShutDown."
            self.logger.info(message)
        except Exception as e:
            message = self.class_name + " - data_to_output_queues. Exception: " + str(e)
            self.logger.error(message)
