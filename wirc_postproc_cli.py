#!/usr/bin/python3
# -*- coding:utf-8 -*-

import click
import pathlib
import src.core as core

global workflow_configs


@click.command()
@click.option(
    "--row",
    default=1,
    prompt="Execute row",
    help="Row number used to select workflow YAML file.",
)
def run_command(row):
    """ """
    global workflow_configs
    if (row <= 0) or (row > len(workflow_configs)):
        print("\n\nERROR: Wrong value. Please try again.\n\n")
        return
    #
    engine = core.WorkflowEngine(logger_name=core.logger_name)
    engine.run_startup(workflow_configs[row - 1])


def main():
    # async def main():
    global workflow_configs
    workflow_configs = []
    for file_path in pathlib.Path(".").glob("workflow_*.yaml"):
        workflow_configs.append(str(file_path))
    workflow_configs = sorted(workflow_configs)
    # Print before command.
    print("\n")
    print("WIRC Post Processing")
    print("--------------------")
    print("Select configuration file")
    print("by entering line number.")
    print("Ctrl-C to terminate.\n")
    for index, row in enumerate(workflow_configs):
        print(index + 1, "  ", row)
    print("\n")
    # Execute command.
    run_command()


if __name__ == "__main__":
    main()
    # asyncio.run(main())
