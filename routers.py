
import time
from typing import Literal
from state import message_state

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
    
def route_to_tutor(state) -> Literal["conversational", "no_more_lesson"]:
    print('-- tracker_call_tool router --')
    messages = state["messages"]
    print('testing start_signal output: ', messages[-1].content)
    return [messages[-1].content]

def router_tutor(state) -> Literal["call_tool", "continue", "FINAL REPORT"]:
    ''' BUG: sometimes the tutor starts the convo without calling its tool, fix asap @urgent'''
    #? create seperate router for each tutor agent or generalise it? -should be able to generalize
    print('-- tutor agent router --')
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    if "REPORT DONE" in last_message.content:
        return "FINAL REPORT"
    elif "USER TURN":
        #! So this print statement here should be what is being returned to the front end !!
        print('AI ASSISTANT: ', last_message.content)
        
        message_state.update_content(last_message.content, last_message.name)

        time.sleep(1) #! just to check if its a speed problem, THIS SHOULD NOT BE IN THE FINAL PROTOTYPE/DEMO
        print('You:')
        #! and this here should be a get request to the front end !!
        user_input = input()
        #print('YOU: ', user_input)
        #add this to messages
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
    if 'conversational' in last_message.content: #? might have to change for multiple tutors
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
    if last_message.tool_calls: #otherwise call your tool
        return 'call_tool'
    if 'continue' in last_message.content: #if both tools have been called go to the tracker
        # clear_memory(memory=memory, thread_id="123456", thread_ts="123456")
        return 'continue_to_tracker'
    
def communicator_router(state) -> Literal['continue', 'go_orchestrator', 'call_tool']:
    print('-- communicator router --')
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    if 'go_orchestrator' in last_message.content:
        return 'go_orchestrator'
    #! So this print statement here should be what i
    print('AI ASSISTANT: ', last_message.content)

    message_state.update_content(last_message.content, last_message.name)

    time.sleep(1) #! just to check if its a speed problem, THIS SHOULD NOT BE IN THE FINAL PROTOTYPE/DEMO
    print('You:')
    #! and this here should be a get request to the front end !!
    user_input = input()
    # print('YOU: ', user_input)
    #add this to messages
    last_message.content += " user response: " + user_input
    return 'continue'