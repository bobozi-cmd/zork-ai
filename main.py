from dotenv import load_dotenv
load_dotenv()

import os
import asyncio

from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig

from client import *
from game import Game

config = BrowserContextConfig(
    cookies_file=os.getenv("cookies", "./.save/cookies.json"),
    wait_for_network_idle_page_load_time=3.0,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    highlight_elements=False,
)
browser_instance_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
browser_config = BrowserConfig(headless=False, chrome_instance_path=browser_instance_path)


async def main():
    browser = Browser(browser_config)
    context = BrowserContext(browser=browser, config=config)

    await context.refresh_page()
    await context._wait_for_page_and_frames_load()

    client = MaunalClient()
    player = Game(context, client)
    await player.play()

    await context.close()
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
