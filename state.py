import asyncio

class MessageState:
    def __init__(self):
        self.content = "-"
        self.agent_name = "-"
        self.event = asyncio.Event()
        self.user_input_event = asyncio.Event()
        self.acknowledgment_event = asyncio.Event()
        self.user_input = ""

    async def wait_for_update(self):
        await self.event.wait()
        self.event.clear()
        return {"content": self.content, "agent_name": self.agent_name}

    def update_content(self, new_content, new_agent_name):
        self.content = new_content
        self.agent_name = new_agent_name
        self.event.set()

    async def wait_for_input(self):
        await self.user_input_event.wait()
        self.user_input_event.clear()
        return self.user_input

    def update_user_input(self, user_input):
        self.user_input = user_input
        self.user_input_event.set()

    async def wait_for_acknowledgment(self):
        await self.acknowledgment_event.wait()
        self.acknowledgment_event.clear()

    def acknowledge_message(self):
        self.acknowledgment_event.set()

message_state = MessageState()
