from typing import Literal, Optional, Annotated
from typing_extensions import TypedDict
from os import getenv

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langgraph.managed import IsLastStep
from tools import guest_info, weather, scheduler

GROQ_API_KEY = getenv("GROQ_API_KEY")
TAVILY_API_KEY = getenv("TAVILY_API_KEY")


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    agent_output: dict[str, str]

    hotel: str
    city: str
    name: str
    group: Optional[
        Literal[
            "solo",
            "couple",
            "friends-male",
            "friends-female",
            "family",
            "family-kids",
            "family-teens",
            "family-seniors",
        ]
    ]
    num_people: int
    is_last_step: IsLastStep


# ==== Define Tools ====
llm = ChatGroq(model="llama-3.3-70b-versatile")
tavily_search_tool = TavilySearchResults(api_key=TAVILY_API_KEY, max_results=3)


# ==== Hotel Agent ====
def hotel_prompt_setup(state: AgentState):
    return PromptTemplate.from_template(
        "Search the web for information about {hotel} in {city}. It must include the hotel's address, contact information and amenities including dining options.\n\nUse the information returned to provide a brief summary of the hotel.",
    ).format(hotel=state["hotel"], city=state["city"])


hotel_agent = create_react_agent(
    model=llm,
    tools=[tavily_search_tool],
    state_schema=AgentState,
    state_modifier=hotel_prompt_setup,
)


def hotel_node(state: AgentState) -> Command:
    print("\n\n== Hotel Node ==\n")
    print(f"\n\n{state=}")
    result = hotel_agent.invoke(state, debug=True)
    print(f"\n\n{result=}")
    hotel_info = {"hotel_info": result["messages"][-1].content}
    print(f"\n\n{hotel_info=}")
    state["agent_output"] = (
        state["agent_output"].update(hotel_info)
        if state["agent_output"]
        else hotel_info
    )
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="search")
            ],
            "agent_output": hotel_info,
        },
        goto="weather_agent",
    )


# ==== Guest Agent ====
guest_agent = create_react_agent(
    model=llm,
    tools=[guest_info],
    state_schema=AgentState,
    state_modifier="Use the provided guest info tool to find information about the guest staying at our hotel using the information provided.",
)


def guest_node(state: AgentState) -> Command:
    print("== Guest Node ==")
    result = guest_agent.invoke(state, debug=True)
    print(f"{result=}")
    output = {"guest_info": result["messages"][-1].content}
    state["agent_output"] = (
        state["agent_output"].update(output) if state["agent_output"] else output
    )
    return Command(
        update={
            "messages": result["messages"],
            "agent_output": output,
        },
        goto=END,
    )


# ==== Weather Agent ====
def weather_node(state: AgentState) -> Command:
    print("== Weather Node ==")
    print(f"{state=}")
    weather_agent = create_react_agent(
        model=llm,
        tools=[weather],
        state_schema=AgentState,
        state_modifier=f"You are the weather expert for the city of {state["city"]}. Give me the temperature for today. Do not make the values up.",
    )
    result = weather_agent.invoke(state, debug=True)
    print(f"{result=}")
    output = {"weather_info": result["messages"][-1].content}
    state["agent_output"] = (
        state["agent_output"].update(output) if state["agent_output"] else output
    )
    print(f"{state=}")

    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
        goto=END,
    )


# ==== Define Workflow ====
def create_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node(hotel_node)
    workflow.add_node(guest_node)
    workflow.add_node(weather_node)

    workflow.set_entry_point("hotel_node")

    return workflow.compile()
