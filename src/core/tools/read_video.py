#!/usr/bin/python3

import asyncio
import logging
import pathlib
import cv2
import datetime
import dateutil

import src.core as core
import src.core.tools as tools


class ReadVideo(core.WorkflowModuleBase):
    """ """

    def __init__(self, logger=None, logger_name="DefaultLogger"):
        """ """
        super().__init__(logger, logger_name)
        self.clear()

    def clear(self):
        """ """
        super().clear()
        self.capture = None

    def configure(self, config_dict):
        """ """
        super().configure(config_dict)
        p = config_dict.get("parameters", {})

    async def pre_process_data(self):
        """ """
        await super().pre_process_data()

    async def process_data(self, data_dict={}):
        """Put your algorithmic code here."""
        try:
            source_file = data_dict.get("source_file", None)
            if source_file == None:
                return
            source_file = pathlib.Path(source_file)
            video_name = source_file.name
            self.logger.info("Source file: " + video_name)

            # Video stream.
            frame_index = 0
            self.capture = cv2.VideoCapture(source_file)
            if not self.capture.isOpened():
                self.logger.error("Error opening video file: " + source_file.name)
            else:
                try:
                    frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                    frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    video_fps = self.capture.get(cv2.CAP_PROP_FPS)
                    source_file_str = str(source_file)
                    while self.capture.isOpened():
                        # Capture frame-by-frame.
                        ret, frame_bgr = self.capture.read()
                        if not ret:
                            break

                        # Calculate time for frame.
                        date_time_str = None
                        video_name_stem = pathlib.Path(video_name).stem
                        parts = video_name_stem.split("_")
                        if len(parts) >= 2:
                            part = parts[1]
                            date_time = dateutil.parser.parse(part)
                            sec = float(frame_index / video_fps)
                            if sec == 0.0:
                                date_time_str = date_time.isoformat()
                            else:
                                date_time += datetime.timedelta(seconds=sec)
                                date_time_str = date_time.isoformat()[:-3]

                        # Prepare outdata dict.
                        dataout_dict = {
                            "frame": frame_bgr,
                            "video_name": video_name,
                            "source_file": source_file_str,
                            "frame_width": frame_width,
                            "frame_height": frame_height,
                            "video_fps": video_fps,
                            "frame_index": frame_index,
                            "date_time_str": date_time_str,
                        }
                        frame_index += 1
                        await self.data_to_output_queues(dataout_dict, "video_frame")
                finally:
                    if self.capture:
                        self.capture.release()
                        self.capture = None

        except Exception as e:
            message = self.class_name + " - process_data. "
            message += "Exception: " + str(e)
            self.logger.error(message)

    async def post_process_data(self):
        """ """
        await super().post_process_data()

        # This tool is finished. No more data.
        await self.data_to_output_queues(None, "video_frame")
