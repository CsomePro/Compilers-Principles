"""
MIT License

Copyright (c) 2023 Csome陈绍民

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations
from typing import Dict


class MQueueSever:
    title_map: Dict[str, list[MQueueClient]] = {}

    def __new__(cls, *args, **kw):
        if not hasattr(MQueueSever, "_instance"):
            MQueueSever._instance = object.__new__(cls)
        return MQueueSever._instance

    def __init__(self):
        pass

    def create(self, title: str):
        self.title_map[title] = []

    def publish(self, title: str, msg: Message):
        assert title in self.title_map, f"未创建title: {title}"
        for client in self.title_map[title]:
            client.submit(msg)

    def subscribe(self, title, client: MQueueClient):
        assert title in self.title_map, f"未创建title: {title}"
        self.title_map[title].append(client)
        return True

    def __repr__(self):
        return repr(self.title_map)


class MQueueClient:

    def __init__(self, name: str):
        self.name = name
        self.sever = MQueueSever()
        self.msgs: [Message] = []

    def submit(self, msg):
        self.msgs.append(msg)

    def clear(self):
        self.msgs.clear()

    def subscribe(self, title):
        self.sever.subscribe(title, self)

    def __iter__(self):
        return iter(self.msgs)

    def __repr__(self):
        return f"{self.name} > {repr(self.msgs)}"


class Message:
    def __init__(self, brief: str, detail: str = ""):
        self.brief = brief
        self.detail = detail
        if not self.detail:
            self.detail = self.brief

    def __repr__(self):
        return f"Msg({repr(self.brief)}, {repr(self.detail)})"

