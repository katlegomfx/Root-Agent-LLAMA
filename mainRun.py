# mainRun.py
import asyncio
from Bot.build.code.llm.prompts import process_user_messages_with_model, load_message_template
from Bot.build.code.cli.cli_application import CLIApplication


def service_func():
    print('service func')


async def run_app_with_messages():
    cli_app = CLIApplication()

    await cli_app.run()


if __name__ == '__main__':
    service_func()
    asyncio.run(run_app_with_messages())
