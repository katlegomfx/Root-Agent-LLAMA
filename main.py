import asyncio
from Bot.build.code.llm.prompts import process_user_messages_with_model, load_message_template
from Bot.build.code.cli.cli_application import CLIApplication


def service_func():
    print('service func')


messages_context = []


async def send_message_later(cli_app, delay, message):
    await asyncio.sleep(delay)  # Wait for `delay` seconds
    await cli_app.background_sender(message)


async def run_app_with_messages():
    cli_app = CLIApplication()

    # Build initial messages
    attempts = 0
    while attempts < 10:
        messages = load_message_template(sys_type='bot') + messages_context
        messages.append(
            {'role': 'user', 'content': "You should work with a bot to complete the task: Build A nextjs application for a SAAS company to start developing from"})
        
        # Process the user message with the model
        base_response = await process_user_messages_with_model(messages)
        if base_response is None:
            base_response = "(No response received)"

        # Append the assistant response to the session chat history
        messages_context.append({'role': 'assistant', 'content': base_response})

        async def send_from_bg(main_ai_response):
            # Schedule a background task to send a message after 1 seconds
            sender_task = asyncio.create_task(
                send_message_later(cli_app, 1, main_ai_response))

            # Run the CLI, allowing user interaction
            await cli_app.run()

            # Cancel the sender task if the application stops before sending
            sender_task.cancel()
            with asyncio.suppress(asyncio.CancelledError):
                await sender_task

            # Return the message that was supposed to be sent
            return main_ai_response

        # Await the background sending of the message after CLI starts
        secondary_response = await send_from_bg(base_response)
        # Append the secondary response as if the assistant sent it again
        messages_context.append(
            {'role': 'assistant', 'content': secondary_response})

        # Increment the attempt counter
        attempts += 1
        
if __name__ == '__main__':
    service_func()
    asyncio.run(run_app_with_messages())
