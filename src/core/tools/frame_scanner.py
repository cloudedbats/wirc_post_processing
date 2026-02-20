#!/usr/bin/python3

import asyncio
import logging
import pathlib
import datetime
import dateutil
import cv2

import src.core as core
import src.core.tools as tools


class FrameScanner(core.WorkflowModuleBase):
    """ """

    def __init__(self, logger=None, logger_name="DefaultLogger"):
        """ """
        super().__init__(logger, logger_name)
        self.clear()

    def clear(self):
        """ """
        super().clear()
        self.background_sub = None
        self.kernel = None

    def configure(self, config_dict):
        """ """
        super().configure(config_dict)
        p = config_dict.get("parameters", {})
        # Kernel size options: 3, 5, 7, etc.
        self.kernel_size = p.get("kernel_size", 5)
        self.min_contour_area = p.get("min_contour_area", 50)
        self.max_contour_area = p.get("max_contour_area", 5000)
        self.text_info = p.get("text_info", False)
        self.font_scale = p.get("font_scale", 1.0)

    async def pre_process_data(self):
        """ """
        await super().pre_process_data()

        # Background subtractor.
        self.background_sub = cv2.createBackgroundSubtractorMOG2()
        # Kernel for morphologyEx.
        kernel_size = (self.kernel_size, self.kernel_size)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)

    async def process_data(self, data_dict={}):
        """Put your algorithmic code here."""
        try:
            frame_bgr = data_dict.get("frame", None)
            video_name = data_dict.get("video_name", None)
            frame_index = data_dict.get("frame_index", None)
            date_time_str = data_dict.get("date_time_str", None)

            # Apply background subtraction.
            frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            foreground_mask_1 = self.background_sub.apply(frame_gray)

            # Apply erosion and dilation.
            foreground_mask = cv2.morphologyEx(
                foreground_mask_1, cv2.MORPH_OPEN, self.kernel
            )

            # Search for contours.
            contours, hierarchy = cv2.findContours(
                foreground_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Remove small and big contours.
            selected_contours = [
                cnt
                for cnt in contours
                if (cv2.contourArea(cnt) > self.min_contour_area)
                and (cv2.contourArea(cnt) < self.max_contour_area)
            ]

            # Always send first frame, or frames with movements.
            if (len(selected_contours) > 0) or (frame_index == 0):

                # Draw bounding box.
                frame_out = frame_bgr.copy()
                for cnt in selected_contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    frame_out = cv2.rectangle(
                        frame_out, (x, y), (x + w, y + h), (0, 0, 200), 1
                    )

                if self.text_info:
                    # cv2.rectangle(
                    #     frame_out,
                    #     (10, 2),
                    #     (100, 20),
                    #     (255, 255, 255),
                    #     -1,
                    # )
                    cv2.putText(
                        frame_out,
                        video_name,
                        (int(20 * self.font_scale), int(35 * self.font_scale)),
                        cv2.FONT_HERSHEY_PLAIN,
                        self.font_scale,
                        (192, 192, 192),
                        1,
                    )
                    text = date_time_str.replace("T", " ")
                    cv2.putText(
                        frame_out,
                        text,
                        (int(20 * self.font_scale), int(60 * self.font_scale)),
                        cv2.FONT_HERSHEY_PLAIN,
                        self.font_scale,
                        (192, 192, 192),
                    )

                # Copy from input.
                dataout_dict = {
                    key: data_dict[key]
                    for key in [
                        "video_name",
                        "source_file",
                        "frame_width",
                        "frame_height",
                        "video_fps",
                        "frame_index",
                        "date_time_str",
                    ]
                }
                # Add frame with movements.
                dataout_dict["frame"] = frame_out

                await self.data_to_output_queues(dataout_dict, "video_frame")
        except Exception as e:
            message = self.class_name + " - process_data. "
            message += "Exception: " + str(e)
            self.logger.error(message)

    async def post_process_data(self):
        """ """
        await super().post_process_data()

        # This tool is finished. No more data.
        await self.data_to_output_queues(None, "video_frame")
