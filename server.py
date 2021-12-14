#!/usr/bin/env python3
import json
import asyncio
import websockets
from datetime import datetime


class Server:
    def __init__(self):
        self.channel = "main"
        self.port = "6789"
        self.host = "localhost"
        self.users = set()

        self.messages = []

    def start(self):
        print("starting server...")
        server = websockets.serve(self.handler, self.host, self.port)
        print("Ready for connections...")
        return server

    def register(self, websocket, username):
        # in case of name change
        for user in self.users:
            new_user = dict(user)
            if new_user["websocket"] == websocket:
                new_user["username"] = username
                self.users.remove(user)
                self.users.add(tuple(new_user.items()))
                return
        # new user
        dictionary = {"websocket": websocket, "username": username}
        self.users.add(
            tuple(dictionary.items())
        )

    def unregister(self, websocket):
        for user in self.users:
            new_user = dict(user)
            if new_user["websocket"] == websocket:
                self.users.remove(user)
                break

    def get_author(self, websocket):
        for user in self.users:
            new_user = dict(user)
            if new_user["websocket"] == websocket:
                return new_user["username"]

    async def handler(self, websocket, path):
        # registering user
        registered = False
        for user in self.users:
            new_user = dict(user)
            if new_user["websocket"] == websocket:
                registered = True
        if not registered:
            self.register(websocket, "anonymous")

        # reading the messages
        try:
            async for message in websocket:
                if "log in as" in message:
                    username = message[9:]
                    self.register(websocket, username)
                await self.add_message(message, websocket)
        # when connection breaks
        finally:
            self.unregister(websocket)

    async def add_message(self, message, websocket):
        self.messages.append(
            {
                "message": message,
                "author": self.get_author(websocket),
                "timestamp": str(datetime.now())[:19],
            }
        )

        if len(self.messages) > 100:
            self.messages = self.messages[-100:]
        await self.publish_messages()

    async def publish_messages(self):
        if len(self.users) * len(self.messages) > 0:
            await asyncio.wait(
                [
                    dict(user)["websocket"].send(json.dumps(self.messages))
                    for user in self.users
                ]
            )


if __name__ == "__main__":
    ws = Server()
    asyncio.get_event_loop().run_until_complete(ws.start())
    asyncio.get_event_loop().run_forever()
