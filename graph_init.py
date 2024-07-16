import os
from langgraph.graph import StateGraph, END
from langchain_core.messages import (
    HumanMessage,
)
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START
import functools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint import *
from routers import *
from agents import *
from tools import *

import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import asyncio

from state import message_state

app = FastAPI()

os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "tutor agents"
os.environ["OPENAI_API_KEY"] = "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"
GPT_MODEL = "gpt-4o"
llm = ChatOpenAI(model=GPT_MODEL)

global_prompts_list =[]
agent_activation_order = []
userID = '001'

communicator_agent = create_agent(
    agentName='communicator', 
    llm=llm, 
    tools=[getFiles], 
    system_message="You are the communicator agent, your job is to communicate with the user to generate a learning recommendation for them " #* to be redefined later
    )

communicator_node = functools.partial(agent_node, agent=communicator_agent, name='communicator')

orchestrator_agent = create_agent(
    agentName='orchestrator', 
    llm=llm, 
    tools=[getChunks], 
    system_message="You are the orchester agent, your job is to get the content chunks regrouped by similar goals and agent and provide the sequence of work for this agents " #* to be redefined later
    )

orchestrator_node = functools.partial(agent_node, agent=orchestrator_agent, name='orchestrator')

tracker_agent = create_agent(
    agentName='tracker', 
    llm=llm, 
    tools=[start_signal], 
    system_message="You are the tracker agent, you job is to track agent tutors and to create reports for user progress" #* to be redefined later
    )

tracker_node = functools.partial(agent_node, agent=tracker_agent, name='tracker')

conversational_agent = create_tutor_agent(
    agentName='conversational',
    llm=llm,
    tools=[getTutorPrompt, create_progress_report],
    system_message="You are the conversational agent, your job is to teach the lesson to the student through conversation. CALL YOUR TOOL IMMEDIATELY" # add 'in Luxembourgish' for final tests
)

conversational_node = functools.partial(agent_node, agent=conversational_agent, name='conversational')

reader_agent = create_tutor_agent(
    agentName='reader',
    llm=llm,
    tools=[getTutorPrompt, create_progress_report],
    system_message="You are the reader agent, your job is to teach the lesson to the student through reading comprehension. CALL YOUR TOOL IMMEDIATELY" # add 'in Luxembourgish' for final tests
)

reader_node = functools.partial(agent_node, agent=reader_agent, name='reader')

listening_agent = create_tutor_agent(
    agentName='listening',
    llm=llm,
    tools=[getTutorPrompt, create_progress_report],
    system_message="You are the listening agent, your job is to teach the lesson to the student through listening comprehension. CALL YOUR TOOL IMMEDIATELY" # add 'in Luxembourgish' for final tests
)

listening_node = functools.partial(agent_node, agent=listening_agent, name='listening')

question_answering_agent = create_tutor_agent(
    agentName='questionAnswering',
    llm=llm,
    tools=[getTutorPrompt, create_progress_report],
    system_message="You are the question answering agent, your job is to teach the lesson to the student through question answering comprehension. CALL YOUR TOOL IMMEDIATELY" # add 'in Luxembourgish' for final tests
)

question_answering_node = functools.partial(agent_node, agent=question_answering_agent, name='questionAnswering')

grammar_summary_agent = create_tutor_agent(
    agentName='grammarSummary',
    llm=llm,
    tools=[getTutorPrompt, create_progress_report],
    system_message="You are the grammer summary agent, your job is to teach by summarizing the grammar of the lesson. CALL YOUR TOOL IMMEDIATELY" # add 'in Luxembourgish' for final tests
)

grammar_summary_node = functools.partial(agent_node, agent=grammar_summary_agent, name='grammarSummary')

tracker_tools = [start_signal]
tutor_tools = [getTutorPrompt, create_progress_report]
orchestrator_tools = [getChunks]
communicator_tools = [getFiles]
tracker_tool_node = ToolNode(tracker_tools)
tutor_tool_node = ToolNode(tutor_tools)
orchestrator_tool_node = ToolNode(orchestrator_tools)
communicator_tool_node = ToolNode(communicator_tools)

workflow = StateGraph(AgentState)
workflow.add_node("communicator", communicator_node)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("tracker", tracker_node)
workflow.add_node("conversational", conversational_node)
workflow.add_node("reader", reader_node)
workflow.add_node('listening', listening_node)
workflow.add_node('questionAnswering',question_answering_node)
workflow.add_node('grammarSummary', grammar_summary_node)

workflow.add_node("communicator_call_tool", communicator_tool_node)
workflow.add_node('orchestrator_call_tool', orchestrator_tool_node)
workflow.add_node("tracker_call_tool", tracker_tool_node)
workflow.add_node("tutor_call_tool", tutor_tool_node)

## add conditional edges
workflow.add_conditional_edges(
    "communicator",
    communicator_router,
    {"continue": "communicator", "call_tool": "communicator_call_tool", "go_orchestrator": "orchestrator"}
)

workflow.add_edge(
    "communicator_call_tool",
    "communicator"
)

workflow.add_conditional_edges(
    "orchestrator",
    orchestrator_router,
    {"call_tool": "orchestrator_call_tool", "continue_to_tracker": "tracker"}
)

workflow.add_edge(
    "orchestrator_call_tool",
    "orchestrator"
)

workflow.add_conditional_edges(
    "tracker",
    router_tracker,
    {"call_tool": "tracker_call_tool", "kill_process": END},
)

workflow.add_conditional_edges(
    "conversational",
    router_tutor,
    {"call_tool": "tutor_call_tool", "FINAL REPORT": "tracker", "continue": "conversational"},) #

workflow.add_conditional_edges(
    "reader",
    router_tutor,
    {"call_tool": "tutor_call_tool", "FINAL REPORT": "tracker", "continue": "reader"}
)

workflow.add_conditional_edges(
    "listening",
    router_tutor,
    {"call_tool": "tutor_call_tool", "FINAL REPORT": "tracker", "continue": "listening"}
)

workflow.add_conditional_edges(
    "questionAnswering",
    router_tutor,
    {"call_tool": "tutor_call_tool", "FINAL REPORT": "tracker", "continue": "questionAnswering"}
)

workflow.add_conditional_edges(
    "grammarSummary",
    router_tutor,
    {"call_tool": "tutor_call_tool", "FINAL REPORT": "tracker", "continue": "grammarSummary"}
)

workflow.add_conditional_edges(
    "tracker_call_tool",
    route_to_tutor,
    {"conversational": "conversational", 
     "reader": "reader", 
     "listening": "listening",
     "questionAnswering": "questionAnswering",
     "grammarSummary": "grammarSummary",
     "no_more_lesson": "tracker"}
)

workflow.add_conditional_edges(
    #! for mutliple agents: USE LAMBDA EXPRESSION TO ALWAYS SEND MSG BACK TO SENDER + no need to send back agent type in get prompt
    "tutor_call_tool",
    route_back_to_tutor,
    {'conversational': 'conversational', 
     'reader':'reader',
     'listening': 'listening',
     'questionAnswering': 'questionAnswering',
     'grammarSummary': 'grammarSummary'}
)

workflow.add_edge(START, "communicator")

graph = workflow.compile() #checkpointer=memory

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