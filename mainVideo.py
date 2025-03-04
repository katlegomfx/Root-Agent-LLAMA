# mainVideo.py
# mainRun.py
import asyncio
from video.code.gui import main_gui


def service_func():
    print('gui service func')


async def run_app_with_messages():
    cli_app = main_gui()
    await cli_app.run()


if __name__ == '__main__':
    service_func()
    asyncio.run(run_app_with_messages())
