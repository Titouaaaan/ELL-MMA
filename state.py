# state.py
import asyncio

class MessageState:
    def __init__(self):
        self.content = "-"
        self.agent_name = "-"
        self.user_input = None  # New attribute for user input
        self.event = asyncio.Event()
        self.input_event = asyncio.Event()  # New event for user input

    async def wait_for_update(self):
        print("Waiting for update...")
        await self.event.wait()
        self.event.clear()
        print('WAIT FOR UPDATE WORKED!')
        return {"content": self.content, "agent_name": self.agent_name}

    def update_content(self, new_content, new_agent_name):
        self.content = new_content
        self.agent_name = new_agent_name
        self.event.set()
        print('UPDATE CONTENT WORKED! \n see values:')
        print(self.content, self.agent_name)

    async def wait_for_input(self):
        print("Waiting for user input...")
        await self.input_event.wait()
        self.input_event.clear()
        print('USER INPUT RECEIVED:', self.user_input)
        return self.user_input

    def update_user_input(self, new_input):
        self.user_input = new_input
        self.input_event.set()
        print('USER INPUT UPDATED:', self.user_input)

message_state = MessageState()
