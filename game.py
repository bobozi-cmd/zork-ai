
from typing import List
from browser_use.browser.context import BrowserContext
from playwright.async_api import ElementHandle
import re

from client import Client, Contents, MaunalClient

url = "https://eblong.com/infocom/visi-zork1/"

class Game:
    header = "=== {place}, Score: {score}, moves: {moves} ==="

    def __init__(self, context: BrowserContext, client: Client, step_limit: int = 50) -> None:
        self.context = context
        self.client = client

        self.step_limit = step_limit

        self.message = []
        self.moves = 0
        self.score = 0
        self.place = ""
        self.playground_content = []
        self.input_handle: ElementHandle = None

    async def _init(self):
        assert((playground_handler := await self.page.query_selector("#window1")) != None)
        assert((place_handler := await self.page.query_selector("#window2")) != None)
        self.playground_handler = playground_handler
        self.place_handler = place_handler

        await self._get_place()
        self.message = await self._get_playground_content()
        
        print(self.header.format(place=self.place, score=self.score, moves=self.moves))
        for line in self.playground_content:
            print(line)

    async def _get_playground_content(self) -> List[str]:
        """Get lastest content in playground and Update history and input handle."""
        content_list: List[ElementHandle] = await self.playground_handler.query_selector_all(".BufferLine")
        
        start = len(self.playground_content)
        ret = []
        for content in content_list[start: -1]:
            ret.append(await content.inner_text())
        
        self.playground_content.extend(ret)
        self.input_handle = await content_list[-1].query_selector("input")
        assert(self.input_handle)
        return ret
    
    async def _get_place(self) -> str:
        """Get current place and Update score and moves."""
        header = await self.place_handler.inner_text()
        try:
            pattern = r"(.*)Score:([ 0-9]*)Moves:([ 0-9]*)"
            res = re.search(pattern, header, re.DOTALL)
            assert(res)
            self.place = res.group(1).strip()
            self.score = int(res.group(2).strip())
            self.moves = int(res.group(3).strip())
        except Exception as e:
            print(e)
        return self.place

    async def _input_cmd(self, cmd: str):
        await self.input_handle.fill(cmd)
        await self.page.keyboard.press("Enter")
        # await self.context._wait_for_page_and_frames_load()

    async def play(self):
        self.page = await self.context.get_current_page()
        await self.page.goto(url)
        await self.context._wait_for_page_and_frames_load()

        await self._init()

        while (await self.step()) and self.step_limit >= self.moves:
            pass
        
    async def step(self) -> bool:
        cmd = self.client.chat(Contents(content=self.message, place=self.place, score=self.score, moves=self.moves))
        if cmd.lower() == "q" or cmd.lower() == "quit":
            return False
        
        try:
            self.playground_content.append(f">{cmd}")
            await self._input_cmd(cmd)
            await self._get_place()
            self.message = await self._get_playground_content()
        except Exception as e:
            print(e)
            return False

        print(self.header.format(place=self.place, score=self.score, moves=self.moves))
        for line in self.message:
            print(line)
        return True