from dataclasses import dataclass
from typing import List

@dataclass
class Contents:
    content: List
    place: str
    score: int
    moves: int


class Client:

    def chat(self, content: List) -> str:
        raise NotImplementedError()


class MaunalClient(Client):

    def chat(self, content: Contents) -> str:
        cmd = input("[q to exit]> ")
        return cmd
