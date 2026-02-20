#!/usr/bin/python3

import asyncio
import logging
import pathlib
import dateutil
from datetime import datetime
import matplotlib.figure
import datetime
import dateutil.parser
import gc

import src.core as core
import src.core.tools as tools


class SaveDiagram(core.WorkflowModuleBase):
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
        self.target_dir = p.get("target_dir", "./video_target/diagrams")

    async def pre_process_data(self):
        """ """
        await super().pre_process_data()

        self.init_matplotlib()

        self.parent_old = None
        self.frame_counter_dict = {}

    async def process_data(self, data_dict={}):
        """Put your algorithmic code here."""
        try:
            # frame_bgr = data_dict.get("frame", None)
            source_file = data_dict.get("source_file", None)
            video_fps = data_dict.get("video_fps", 30.0)

            video_name_path = pathlib.Path(source_file)
            parent = video_name_path.parent.name
            video_name_stem = video_name_path.stem
            parts = video_name_stem.split("_")
            prefix = parts[0]
            date_time_part = parts[1]
            date_time = dateutil.parser.parse(date_time_part)
            date_time_minute = date_time.replace(
                microsecond=0,
                second=0,
                minute=date_time.minute,
                hour=date_time.hour,
            )
            # If first received frame.
            if self.parent_old == None:
                self.parent_old = parent
            # Create plot when new parent directory.
            if parent != self.parent_old:
                self.parent_old = parent
                self.create_plot()
                self.frame_counter_dict = {}

            # Add 1 to counter for each minute.
            key = parent + "+"
            key += prefix + "+"
            key += str(date_time_minute)
            # Increment.
            if key in self.frame_counter_dict:
                self.frame_counter_dict[key] += 1.0 / float(video_fps)
            else:
                # First frame is always present.
                self.frame_counter_dict[key] = 0.0

        except Exception as e:
            message = self.class_name + " - process_data. "
            message += "Exception: " + str(e)
            self.logger.error(message)

    async def post_process_data(self):
        """ """
        await super().post_process_data()

        # Create last plot.
        if len(self.frame_counter_dict) > 0:
            self.create_plot()

    def init_matplotlib(self):
        """ """
        matplotlib.rcParams.update({"font.size": 6})
        self.figure = matplotlib.figure.Figure(
            figsize=(10, 3),
            dpi=300,
        )
        self.ax1 = self.figure.add_subplot(111)

    def create_plot(self):
        """ """
        try:
            first_key = [*self.frame_counter_dict][0]
            parts = first_key.split("+")
            parent_dir = parts[0]
            prefix = parts[1]
            date_time_str = parts[2]

            plot_name = parent_dir + "_" + prefix
            self.logger.debug("Processing diagram: " + plot_name)

            # Data.
            x = []
            ymin = []
            ymax = []
            xmove = []
            ymove = []
            min_datetime = None
            max_datetime = None
            for key in sorted([*self.frame_counter_dict]):
                parts = key.split("+")
                parent_dir = parts[0]
                prefix = parts[1]
                date_time_str = parts[2]
                # X.
                date_time = dateutil.parser.parse(date_time_str)
                x.append(date_time)
                # Y.
                value_per_minute = self.frame_counter_dict[key]
                value_percent_of_max = value_per_minute / 60.0 * 100.0
                if value_per_minute > 0.0:
                    xmove.append(date_time)
                    ymove.append(-2.0)
                ymin.append(0.0)
                ymax.append(value_percent_of_max)
                # Time limits.
                if (min_datetime == None) or (date_time < min_datetime):
                    min_datetime = date_time
                if (max_datetime == None) or (date_time > max_datetime):
                    max_datetime = date_time

            # Time limits.
            start_datetime = min_datetime - datetime.timedelta(minutes=10)
            end_datetime = max_datetime + datetime.timedelta(minutes=10)

            # Create scatter and vline plots.
            self.ax1.scatter(x, ymin, marker=".", color="black", s=0.8)
            self.ax1.vlines(x, ymin, ymax, color="k", linestyles="solid", lw=0.4)
            self.ax1.scatter(xmove, ymove, marker=".", color="red", s=0.8)

            # Title and labels.
            title = plot_name.replace("_", " ")
            if len(x) == 1:
                title += "     (One minute checked)"
            else:
                title += "     (" + str(len(x)) + " minutes checked)"
            self.ax1.set_title(title, fontsize=8)
            self.ax1.set_xlim((start_datetime, end_datetime))

            # Time axis.
            xfmt = matplotlib.dates.DateFormatter("%H:%M")
            self.ax1.xaxis.set_major_formatter(xfmt)
            self.ax1.xaxis.set(
                major_locator=matplotlib.dates.AutoDateLocator(
                    minticks=3,
                    maxticks=15,
                ),
                minor_locator=matplotlib.dates.AutoDateLocator(
                    minticks=15,
                    maxticks=100,
                ),
            )

            # Value axis.
            self.ax1.set_ylabel("Frames with movements (%)")
            self.ax1.set_ylim((-4.0, 105.0))

            # Grid.
            # self.ax1.minorticks_on()
            self.ax1.grid(which="major", linestyle="-", linewidth="0.5", alpha=0.5)
            # self.ax1.grid(which="minor", linestyle="-", linewidth="0.4", alpha=0.2)
            self.ax1.tick_params(
                which="both", top="off", left="off", right="off", bottom="off"
            )

            # Save.
            self.figure.tight_layout()
            target_path = pathlib.Path(
                self.target_dir, parent_dir, plot_name + "_SCANNER.png"
            )
            if not target_path.parent.exists():
                target_path.parent.mkdir(parents=True)
            self.figure.savefig(str(target_path))
            self.ax1.cla()
            # Run garbage collector to avoid memory overload.
            gc.collect()

        except Exception as e:
            print("EXCEPTION in create_plots: ", e)
