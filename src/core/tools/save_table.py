#!/usr/bin/python3

import asyncio
import logging
import pathlib
import dateutil
from datetime import datetime

import src.core as core
import src.core.tools as tools


class SaveTable(core.WorkflowModuleBase):
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
        self.target_dir = p.get("target_dir", "./video_target/tables")

    async def pre_process_data(self):
        """ """
        await super().pre_process_data()

        # self.video_name_old = ""
        # self.video_out_path_old = ""

    async def process_data(self, data_dict={}):
        """Put your algorithmic code here."""
        try:
            frame_bgr = data_dict.get("frame", None)
            video_name = data_dict.get("video_name", None)

            # Check for each new source file.
            if video_name != self.video_name_old:
                self.video_name_old = video_name

                # Check if new video file should be created.
                video_out_path = self.outdata_file_path(data_dict)
                if video_out_path != self.video_out_path_old:
                    self.video_out_path_old = video_out_path
                    self.new_video_writer(data_dict, video_out_path)
                    #
                    # video_name_name = pathlib.Path(video_out_path).name
                    # self.logger.info("New video file: " + video_name_name)
                    self.logger.info("New video file: " + video_out_path)

                # Fallback for test, should not happen.
                if self.video_out == None:
                    self.logger.error("ERROR. Failed to create video. Try again.")
                    self.new_video_writer(data_dict, video_out_path)

            if self.video_out:
                self.video_out.write(frame_bgr)
            else:
                self.logger.error("Exception: Failed to write frame to file.")

        except Exception as e:
            message = self.class_name + " - process_data. "
            message += "Exception: " + str(e)
            self.logger.error(message)

    async def post_process_data(self):
        """ """
        await super().post_process_data()

        if self.video_out:
            self.video_out.release()
            self.video_out = None

    def outdata_file_path(self, data_dict):
        """ """
        source_file = data_dict.get("source_file", None)
        video_name = data_dict.get("video_name", None)

        # Parent dir and target dir path.
        source_file = pathlib.Path(source_file)
        parent_dir = source_file.parent.name
        target_dir_path = pathlib.Path(self.target_dir, parent_dir)
        if not target_dir_path.exists():
            target_dir_path.mkdir(parents=True)

        # Convert filename to full hour.
        video_name_stem = pathlib.Path(video_name).stem
        video_name_suffix = pathlib.Path(video_name).suffix
        parts = video_name_stem.split("_")
        if len(parts) >= 2:
            prefix = parts[0]
            time_part = parts[1]
            date_time = dateutil.parser.parse(time_part)
            # date_time = dateutil.parser.parse(date_time_str)
            next_time_hour = date_time.replace(
                second=0,
                microsecond=0,
                minute=0,
                hour=date_time.hour,
            )
            next_time_hour_str = (
                str(next_time_hour).replace(" ", "T").replace("-", "").replace(":", "")
            )
            target_file = (
                prefix + "_" + next_time_hour_str + "_SCANNER" + video_name_suffix
            )
        else:
            target_file = video_name

        target_file_path = pathlib.Path(target_dir_path, target_file)
        return str(target_file_path)

    def new_video_writer(self, data_dict, out_path):
        """ """
        # if self.video_out:
        #     self.video_out.release()
        #     self.video_out = None

        # frame_width = data_dict.get("frame_width", None)
        # frame_height = data_dict.get("frame_height", None)
        # fps = data_dict.get("video_fps", None)

        # fourcc = cv2.VideoWriter_fourcc(*"avc1")  # AVC1 is equal to H.264.
        # self.video_out = cv2.VideoWriter(
        #     out_path,
        #     fourcc,
        #     fps,
        #     (frame_width, frame_height),
        # )
