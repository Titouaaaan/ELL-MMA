from openai import OpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import (
    BaseMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
import operator
from typing import Sequence 
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from langgraph.checkpoint import *
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", )

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str

# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }

def set_agent_prompt(agentName: str, tools) -> str:
    ''' function to determine custom prompt based on the agent type (only 3 atm)
    need to add tools available to prompts
    '''
    try:
        if agentName == 'tracker':
            return (
                "system",
                "You are the tracker,"
                "Your role is to supervise the role of the tutoring agents."
                "DO NOT ANALYSE WHAT THE TUTORS HAVE OUTPUTED"
                "1. ALWAYS call your start_signal tool BEFORE ANYTHING YOU DO"
                "2. ONLY IF start_signal responds with no_more_lessons, then"
                " OUTPUT ONLY kill_process"
                f"your tools are {[tool.name for tool in tools]}"
            )
        elif agentName == 'orchestrator':
            return ( 
                "system",
                "your are the orchestrator"
                "YOU MUST FOLLOW these steps TO COMPLETE your task IN THIS SPECIFIC ORDER:"
                "1. FIRST ouput call_tool to use your tool getChunks TO RETRIEVE THE CONTENT "
                "pass as a parameter ONLY THE KAPITEL AND THEMA"
                "2. DO NOT ANALYSE TEXTS"
                "WHEN YOUR TOOL OUTPUTS continue, YOU MUST OUTPUT continue_to_tracker"
                f"your tools are {[tool.name for tool in tools]}"
            )
        elif agentName == 'communicator':
            return ( #*DEFINITELY NEEDS SOME TESTING AND PROMPT ENGINEERING
                "system",
                "you are the communicator"
                "to KEEP TALKING WITH THE USER until they confirm your recommendation, ouput: continue"
                "you communicate in a friendly way with the user"
                f"your tools are {[tool.name for tool in tools]}"
                "your role is to give user recommendations about learning by following those steps:"
                "1. RETRIEVE THE FILES with your tools by providing the userID as a parameter"
                "2. GENERATE a learning recommendation based on:"
                "the user's progress IMPORTANTLY based on what they already did in the CURRICULUM." #? might be too complex?
                "THEN there are TWO OPTIONS"
                "3. If user ACCEPTS, OUTPUT A QUERY following the template with ONLY:"
                "Kapitel: ... \nThema: ..."
                "AND output go_orchestrator"
                "4. If user REJECTS, ask for new preferences from the user and"
                #" call your tool updateUserPreferences with the appropriate parameters"  #? MAYBE ADD THIS STEP LATER?
                "then go back to step 2. GENERATE a learning recommendation based on ..."
            )
    except:
        raise 'agentName is incorrect'   
    
''' FUNCTION TO CREATE THEE FOLLOWING AGENTS: TRACKER, COMMUNICATOR, ORCHESTRATOR'''
''' the system_message var is used for the general personality of the agent, determined during its creation '''

def create_agent(agentName: str, llm, tools, system_message: str): #* for tracker, communicator and orchestor
    """Create main agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
            set_agent_prompt(agentName=agentName, tools=tools)
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)

def create_tutor_agent(agentName: str, llm, tools, system_message: str): #* for converastional, listener etc...
    """Create the dfferents tutor agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
            "system",
            "you are the {agent_name} agent."
            f"your tools are {[tool.name for tool in tools]}"
            "BEFORE TALKING TO THE USER PLEASE CALL your tool: getLearningContent"
            "This tool retrieves the learning content you need to teach to the user"
            "DO NOT MOVE ON TO ANOTHER STEP BEFORE THIS"    
            "without it you cannot proceed!!"        
            "after, YOUR TASK IS TO follow those steps:"
            "START INTERACTING with the user, "
            "do not stop interacting with the user unless:"
            "-they understood all the lesson material OR"
            "-they explicitely said they want to stop"
            "3. if you covered all the lesson material,"
            "call the create_progress_report tool and provide your agent name as a parameter" #! add prompt for the report generation (give template to follow)
            "THEN output REPORT DONE in all caps"
            "{system_message}"),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    prompt = prompt.partial(agent_name=agentName)
    prompt = prompt.partial(system_message=system_message)

    return prompt | llm.bind_tools(tools)