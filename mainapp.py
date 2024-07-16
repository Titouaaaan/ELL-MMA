'''
This file contains the app creation using FastAPI.
The graph is created in another file and imported here (see graph_creation.py).
All functions are async to avoid problems with client communication.
See https://fastapi.tiangolo.com for more information.
'''

# Langchain import
from langchain_core.messages import (
    HumanMessage,
)

# Multi-Agent graph import
from graph_creation import graph

# FastAPI imports
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import asyncio

from state import message_state

app = FastAPI()

global_prompts_list =[]
agent_activation_order = []

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

class ConversationRequest(BaseModel):
    startBool: bool
    userID: str

class UserInputRequest(BaseModel):
    content: str

class AcknowledgmentRequest(BaseModel):
    ack: bool

async def continue_graph_execution(messages):
    async for s in graph.astream({"messages": messages}, {"recursion_limit": 100}):
        if "__end__" not in s:
            print(s)
            print("----")
            # Update the shared state with the current content and agent name
            await asyncio.sleep(0)  # Yield control to the event loop


@app.post("/startConversation")
async def begin_graph_stream(request: ConversationRequest, background_tasks: BackgroundTasks):
    if request.startBool:
        try:
            messages = [
                HumanMessage(content=f"Communicator, the user ID is {request.userID}. Please start with your task.")
            ]
            background_tasks.add_task(continue_graph_execution, messages)
            return JSONResponse(content={"message": "Conversation started"}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    else:
        raise HTTPException(status_code=400, detail="startBool must be true")

@app.get("/getAIMessage")
async def get_ai_message():
    print('entering get function...')
    message_data = await message_state.wait_for_update()
    response_payload = {
        "agent_name": message_data["agent_name"],
        "content": message_data["content"]
    }
    print('exiting get function...')
    return JSONResponse(content=response_payload, status_code=200)

@app.post("/userInput")
async def receive_user_input(request: UserInputRequest):
    try:
        message_state.update_user_input(request.content)
        return JSONResponse(content={"message": "User input received"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/acknowledgeMessage")
async def acknowledge_message(request: AcknowledgmentRequest):
    try:
        if request.ack:
            message_state.acknowledge_message()
            return JSONResponse(content={"message": "Acknowledgment received"}, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Acknowledgment must be true")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)