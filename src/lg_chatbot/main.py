from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain.chat_models import init_chat_model
from typing import TypedDict, Literal, Annotated

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, AIMessageChunk, HumanMessage, BaseMessage
import operator
from langchain_openrouter import ChatOpenRouter

# persistance memory
from langgraph.checkpoint.memory import MemorySaver

from uuid import uuid7

load_dotenv()

model = ChatOpenRouter(model="auto")

# Reducer concept
# BaseMessage combines Human and AI messages
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    # take user query from state
    messages = state['messages']
    print(f"user message = {messages}")

    # send to model
    response = model.invoke(messages)
    print(f"model response = {response}")
    return {'messages': [response]}


# Checkpoint, persistance, memorysaver in ram
checkpointer = MemorySaver()

graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# Use checkpointer
workflow = graph.compile(checkpointer=checkpointer)

# # visualize graph
# from IPython.display import Image, display
# png_data = workflow.get_graph().draw_mermaid_png()
# with open("workflow.png", "wb") as f:
#     f.write(png_data)
# display(Image(filename="workflow.png"))




thread_id = uuid7()
# thread_id = "t1"
# thread_uuid = 01a09eb2-6ad2-7377-8dfa-147e2f5f429a
print(f"thread_id = {thread_id}")
while True:
    user_message = input('Type here: ')
    print(f'User: {user_message}')

    if user_message.strip().lower() in ['exit', 'quit', 'bye']:
        break

    config = {'configurable': {'thread_id': thread_id}}

    # # how to check the state, stores the snapshot
    # state_history = workflow.get_state(config=config)
    # print(f"state_history = {state_history}")


    # print reesponse
    # response = workflow.invoke({
    #     "messages": [HumanMessage(content=user_message)]

    # }, config=config)
    # print(f"AI: {response['messages'][-1].content}")


    # # streaming only tokens
    # for message, metadata in workflow.stream(
    #     {
    #         "messages": [HumanMessage(content=user_message)]
    #     },
    #     config=config,
    #     stream_mode="messages",
    # ):
    #     if isinstance(message, AIMessageChunk):
    #         print(message.content, end="", flush=True)

    # print()

    # Streaming tokens and node updates
    for message, metadata in workflow.stream(
        {
            "messages": [HumanMessage(content=user_message)]
        },
        config=config,
        stream_mode="messages",
    ):
        if isinstance(message, AIMessageChunk):
            print(
                message.content,
                end="",
                flush=True,
            )

        # e.g. metadata["langgraph_node"]

# get state history
state_history = list(workflow.get_state_history(config))
print(f"state_history = {state_history}")



# this is added to check persistance of memory
# thread_id = "t1"
# config = {'configurable': {'thread_id': thread_id}}
# initial_state = {
#      "messages": [HumanMessage(content='who am i?')]
# }

# result = workflow.invoke(initial_state, config=config)

# print(f"final = {result['messages'][-1].content}")

