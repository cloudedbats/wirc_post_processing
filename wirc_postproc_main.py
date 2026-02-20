#!/usr/bin/python3

import asyncio
import src.core as core


async def main():
    """ """
    engine = core.WorkflowEngine(logger_name=core.logger_name)
    await engine.startup("workflow_standard.yaml")


if __name__ == "__main__":
    """ """
    asyncio.run(main())
