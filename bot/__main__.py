import asyncio
from asyncio import get_event_loop, sleep as asleep, gather
from traceback import format_exc

from aiohttp import web
from pyrogram import idle

from bot import __version__, LOGGER
from bot.config import Telegram
from bot.server import web_server
from bot.telegram import StreamBot, UserBot
from bot.telegram.clients import initialize_clients

# Ensure an event loop is set to avoid issues with Pyrogram's sync wrappers
loop = asyncio.get_event_loop() or asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def start_services():
    LOGGER.info(f'Initializing Surf-TG v-{__version__}')
    await asleep(1.2)
    
    await StreamBot.start()
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"Bot Client : [@{StreamBot.username}]")
    if len(Telegram.SESSION_STRING) != 0:
        await UserBot.start()
        UserBot.username = UserBot.me.username or UserBot.me.first_name or UserBot.me.id
        LOGGER.info(f"User Client : {UserBot.username}")
    
    await asleep(1.2)
    LOGGER.info("Initializing Multi Clients")
    await initialize_clients()
    
    await asleep(2)
    LOGGER.info('Initializing Surf Web Server..')
    server = await web_server()
    app_runner = web.AppRunner(server)
    await app_runner.setup()
    
    await asleep(2)
    LOGGER.info("Server Setup Started !")
    
    site = web.TCPSite(app_runner, '0.0.0.0', Telegram.PORT)
    await site.start()

    LOGGER.info("Surf-TG Started Revolving !")
    await idle()

async def stop_clients():
    await StreamBot.stop()
    if len(Telegram.SESSION_STRING) != 0:
        await UserBot.stop()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info('Service Stopping...')
    except Exception:
        LOGGER.error(format_exc())
    finally:
        loop.run_until_complete(stop_clients())
        loop.stop()
        loop.close()
