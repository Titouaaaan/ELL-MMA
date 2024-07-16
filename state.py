# state.py
import asyncio

class MessageState:
    def __init__(self):
        self.content = "-"
        self.agent_name = "-"
        self.event = asyncio.Event()

    async def wait_for_update(self):
        await self.event.wait()
        self.event.clear()
        print('WAIT FOR UPDATE WORKED!')
        print('test: ', {"content": self.content, "agent_name": self.agent_name})
        return {"content": self.content, "agent_name": self.agent_name}

    def update_content(self, new_content, new_agent_name):
        self.content = new_content
        self.agent_name = new_agent_name
        self.event.set()
        print('UPDATE CONTENT WORKED! \n see values:')
        print(self.content, self.agent_name)

message_state = MessageState()
