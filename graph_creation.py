'''
The graph is being created here, and then being imported in the mainapp file. 
This ensure that mainapp.py is not bloated with code
The graph creation is rather standard for langgraph
All tools, routers and agents prompts are created in other files
'''

import os
import functools

from Tutors_prompts import Conversational_Agent_Prompt,Reader_Agent_Prompt,Listening_Agent_Prompt,QA_Agent_Prompt
#langgraph imports
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

# imports from other files
from routers import *
from agents import *
from tools import *

os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "tutor agents"

GPT_MODEL = "gpt-4o"
llm = ChatOpenAI(model=GPT_MODEL)

#set up the memory
memory = AsyncSqliteSaver.from_conn_string(":memory:")

communicator_agent = create_agent(
    agentName='communicator', 
    llm=llm, 
    tools=[getFiles], 
    system_message="You are the communicator agent, your job is to communicate with the user in Luxembourgish to generate a learning recommendation for them " #* to be redefined later
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
    tools=[getLearningContent, create_progress_report],
    system_message=Conversational_Agent_Prompt
)

conversational_node = functools.partial(agent_node, agent=conversational_agent, name='conversational')

reader_agent = create_tutor_agent(
    agentName='reader',
    llm=llm,
    tools=[getLearningContent, create_progress_report],
    system_message=Reader_Agent_Prompt # add 'in Luxembourgish' for final tests
)

reader_node = functools.partial(agent_node, agent=reader_agent, name='reader')

listening_agent = create_tutor_agent(
    agentName='listening',
    llm=llm,
    tools=[getLearningContent, create_progress_report],
    system_message=Listening_Agent_Prompt
)

listening_node = functools.partial(agent_node, agent=listening_agent, name='listening')

question_answering_agent = create_tutor_agent(
    agentName='questionAnswering',
    llm=llm,
    tools=[getLearningContent, create_progress_report],
    system_message=QA_Agent_Prompt
)

question_answering_node = functools.partial(agent_node, agent=question_answering_agent, name='questionAnswering')

grammar_summary_agent = create_tutor_agent(
    agentName='grammarSummary',
    llm=llm,
    tools=[getLearningContent, create_progress_report],
    system_message="You are the grammer summary agent, your job is to teach by summarizing the grammar of the lesson. CALL YOUR TOOL IMMEDIATELY" # add 'in Luxembourgish' for final tests
)

grammar_summary_node = functools.partial(agent_node, agent=grammar_summary_agent, name='grammarSummary')

tracker_tools = [start_signal]
tutor_tools = [getLearningContent, create_progress_report]
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
    "tutor_call_tool",
    route_back_to_tutor,
    {'conversational': 'conversational', 
     'reader':'reader',
     'listening': 'listening',
     'questionAnswering': 'questionAnswering',
     'grammarSummary': 'grammarSummary'}
)

workflow.add_edge(START, "communicator")

graph = workflow.compile(checkpointer=memory) 