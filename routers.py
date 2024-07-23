'''
Routers used to decide what path to follow between agent and tool nodes
TODO: add more documentation to the routers, mostly rename variable for more clarity
'''

from typing import Literal
from state import message_state
from langchain_core.messages import (
    AIMessage,
) 

# define the router function
def router_tracker(state) -> Literal["call_tool", "kill_process"]:
    print('-- tracker router --')
    messages = state["messages"]
    last_message = messages[-1]
    # depends only on the start_signal output
    if 'kill_process' in last_message.content:
        return "kill_process"
    else:
        return "call_tool" #to force start_signal call
    
def route_to_tutor(state) -> Literal["conversational", "reader", "listening", "questionAnswering", "grammarSummary", "no_more_lesson"]:
    print('-- tracker_call_tool router --')
    messages = state["messages"]
    #print('testing start_signal output: ', messages[-1].content)
    agent = messages[-1].content
    state['messages'][-1].content += 'TUTOR AGENT PLEASE CALL YOUR TOOL'
    return [agent]

async def router_tutor(state) -> Literal["call_tool", "continue", "FINAL REPORT"]:
    ''' BUG: sometimes the tutor starts the convo without calling its tool, fix asap @urgent'''
    print('-- tutor agent router --')
    messages = state["messages"]
    last_message = messages[-1]

    # print('Chat history: \n')
    # print(messages)

    if last_message.tool_calls:
        return "call_tool"
    
    if "REPORT DONE" in last_message.content:
        return "FINAL REPORT"

    if isinstance(last_message, AIMessage) and last_message.content != '':
        print('succesful test')
        # THIS IS TO UPDATE THE LAST MESSAGE TO THEN SEND IT TO THE CLIENT
        message_state.update_content(last_message.content, last_message.name)
        # WAIT FOR ACK TO SEE IF CLIENT RECIEVED AIMESSAGE
        await message_state.wait_for_acknowledgment()

        print('AI ASSISTANT: ', last_message.content)

        print('You:')
        # WAIT FOR THE CLIENT TO SEND THE USER INPUT
        user_input = await message_state.wait_for_input()
        print(user_input)
      
        last_message.content += " user response: " + user_input
        return "continue" 
    
    return "call_tool" #forcing call tool (sometimes agent starts conversation anyways, need to fix that)

def route_back_to_tutor(state) -> Literal['conversational', 'reader', 'listening', 'grammarSummary', 'questionAnswering']:
    print('-- tutor call tool router --')
    ''' There is 100% a better way to do this, should look into it'''
    messages = state["messages"]
    last_message = messages[-1]
    if 'FINAL REPORT' and 'reader' in last_message.content:
        return 'reader'
    if 'FINAL REPORT' and 'conversational' in last_message.content:
        return 'conversational'
    if 'FINAL REPORT' and 'listening' in last_message.content:
        return 'listening'
    if 'FINAL REPORT' and 'questionAnswering' in last_message.content:
        return 'questionAnswering'
    if 'FINAL REPORT' and 'grammarSummary' in last_message.content:
        return 'grammarSummary'
    if 'conversational' in last_message.content: 
        return 'conversational'
    if 'reader' in last_message.content:
        return 'reader'
    if 'listening' in last_message.content:
        return 'listening'
    if 'questionAnswering' in last_message.content:
        return 'questionAnswering'
    if 'grammarSummary' in last_message.content:
        return 'grammarSummary'
    
def orchestrator_router(state) -> Literal['continue_to_tracker', 'call_tool']:
    print('-- orchestrator router --')
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls: 
        return 'call_tool'
    if 'continue' in last_message.content: #if both tools have been called go to the tracker
        return 'continue_to_tracker'
    
async def communicator_router(state) -> Literal['continue', 'go_orchestrator', 'call_tool']:
    print('-- communicator router --')
    messages = state['messages']
    last_message = messages[-1]

    if last_message.tool_calls:
        return "call_tool"
    
    if 'go_orchestrator' in last_message.content:
        print('AI ASSISTANT: lecture content \n', last_message.content)
        msg = last_message.content.replace('go_orchestrator', '')
        # THIS IS TO UPDATE THE LAST MESSAGE TO THEN SEND IT TO THE CLIENT
        message_state.update_content(msg, last_message.name)
        # WAIT FOR ACK TO SEE IF CLIENT RECIEVED AIMESSAGE
        await message_state.wait_for_acknowledgment()
        # ideally we save in a custom memory the communicator message
        # global custom_communicator_memory_save
        # custom_communicator_memory_save = messages #this saves just in case but not used anywhere atm (could be useful for later?)
        return 'go_orchestrator'

    if isinstance(last_message, AIMessage) and last_message.content != '':
        # THIS IS TO UPDATE THE LAST MESSAGE TO THEN SEND IT TO THE CLIENT
        message_state.update_content(last_message.content, last_message.name)
        # WAIT FOR ACK TO SEE IF CLIENT RECIEVED AIMESSAGE
        await message_state.wait_for_acknowledgment()

        #debugging
        print('AI ASSISTANT: ', last_message.content)

        print('You:')
        # WAIT FOR THE CLIENT TO SEND THE USER INPUT
        user_input = await message_state.wait_for_input()
        print(user_input)
        
        last_message.content += " user response: " + user_input
        return 'continue'