from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from IPython.display import Image, display
from typing import Literal
import os
import functools
import json
import graphviz

os.environ['OPENAI_API_KEY'] = 'sk-proj-1xJeptjFfqBedSaJltruT3BlbkFJCGvIrjfkmvFSzxVpRyGD'

os.environ["LANGSMITH_API_KEY"] = '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'
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangGraph Tutorial"


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


tool = ChatOpenAI(model="gpt-4o") #* this guy will be the summary tool 
tools = [tool] # there shouldnt be any other tools to add to this list normally

llm = ChatOpenAI(model="gpt-4o")


# Create a conversational agent function
# def create_conversational_agent(llm, system_message: str):
#     """Create an agent."""
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ( #! too many directives might be complicated for the agent bc it keeps performing randomly
#                 "system",
#                 "you are a conversational agent. "
#                 "you are speaking to a student. "
#                 "do not write down what the user responds"
#                 "Speak in english with the student."
#                 "as long as the user is making mistakes, they did not learn the lesson properly."
#                 "You have three missions: teach, evaluate, and converse. "
#                 "state those missions clearly to the user."
#                 "1. Teach a lesson based on the user's request. "
#                 "2. Once you have given your lesson, you must evaluate the user by questioning them, "
#                 "keep asking the questions until the student gets the answer correct."
#                 "3. After evaluation, you must have a conversation in the context of the lesson"
#                 "with the user by asking them questions and talking with them by role playing a scenario,"
#                 "keep this conversation going with the user until all the lesson material is covered."
#                 "make sure only the lesson content is needed for the conversation."
#                 "If the user has successfully learned the lesson and you did all three missions"
#                 "Provide a summary of what the user has learned and then quit and stop the conversation. "
#                 "write clearly: lesson learned. "
#                 "{system_message}",
#             ),
#             MessagesPlaceholder(variable_name="messages"),
#         ]
#     )
#     prompt = prompt.partial(system_message=system_message)
#     return prompt | llm


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("conversation_bot", chatbot)

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


# tool_node = BasicToolNode(tools=[tool])
# graph_builder.add_node("tools", tool_node)

def route_tools(
    state: State,
) -> Literal["tools", "__end__"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "__end__" if
# it is fine directly responding. This conditional routing defines the main agent loop.
# graph_builder.add_conditional_edges(
#     "chatbot",
#     route_tools,
#     # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
#     # It defaults to the identity function, but if you
#     # want to use a node named something else apart from "tools",
#     # You can update the value of the dictionary to something else
#     # e.g., "tools": "my_tools"
#     {"tools": "tools", "__end__": "__end__"},
# )
# Any time a tool is called, we return to the chatbot to decide the next step
# graph_builder.add_edge("tools", "chatbot")
# graph_builder.add_edge(START, "chatbot")

graph_builder.set_entry_point("conversation_bot")
graph_builder.set_finish_point("conversation_bot")

graph = graph_builder.compile()

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)