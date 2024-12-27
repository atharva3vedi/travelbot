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
    # TODO: Make this prompt actually return the information from the search results, not just call the search tool
    return PromptTemplate.from_template(
        "Search the web for information about {hotel} in {city}. It must include the hotel's address and phone number."
        # \n\nUse the information returned to provide a brief summary of the hotel.",
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

    print(f"\n\n{result["messages"][-1].content=}")
    output = state["agent_output"]
    output["hotel_info"] = result["messages"][-1].content

    print(f"{state=}")
    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
        goto="guest_node",
    )


# ==== Guest Agent ====
def guest_node(state: AgentState) -> Command:
    print("== Guest Node ==")
    guest_agent = create_react_agent(
        model=llm,
        tools=[guest_info],
        state_schema=AgentState,
        state_modifier=f"""
        Use the provided guest info tool to find information about the guest staying at our hotel using the information provided.
        Guest Name: {state["name"]}
        Group: {state["group"]}
        Number of People: {state["num_people"]}
        """,
    )
    result = guest_agent.invoke(state, debug=True)
    print(f"{result=}")

    print(f"{result['messages'][-1].content=}")
    output = state["agent_output"]
    output["guest_info"] = result["messages"][-1].content

    print(f"{state=}")
    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
        goto="weather_node",
    )


# ==== Weather Agent ====
def weather_node(state: AgentState) -> Command:
    print("== Weather Node ==")
    print(f"{state=}")
    weather_agent = create_react_agent(
        model=llm,
        tools=[weather],
        state_schema=AgentState,
        state_modifier=f"You are the weather expert for the city of {state["city"]}. Give me the temperature for today. Do not make the values up. Include the returned information in the output.",
    )
    result = weather_agent.invoke(state)
    print(f"{result=}")

    print(f"{result['messages'][-1].content=}")
    output = state["agent_output"]
    output["weather_info"] = result["messages"][-1].content

    print(f"{state=}")

    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
        goto="food_expert_node",
    )


def food_expert_node(state: AgentState) -> Command:
    print("== Food Expert Node ==")
    print(f"{state=}")
    food_expert_agent = create_react_agent(
        model=llm,
        tools=[tavily_search_tool],
        state_schema=AgentState,
        state_modifier=f"""
        You are a local food gourmet who knows the ins-and-outs of the local specialities and the best places to eat in {state["city"]}. What are the 5 best local foods to eat in the city? What are the best places to eat in the city? You could include stand-out dishes, restaurants, or street food stalls.
        Are there any dishes that are popular on days with weather like today? (Today\'s weather: {state["agent_output"]["weather_info"]})
        Keep in mind that the information should be relevant to the guest staying at the hotel.
        Guest Info: {state["agent_output"]["guest_info"]}
        Hotel Info: {state["agent_output"]["hotel_info"]}
        """,
    )
    result = food_expert_agent.invoke(state)
    print(f"{result=}")

    print(f"{result['messages'][-1].content=}")
    output = state["agent_output"]
    output["food_info"] = result["messages"][-1].content

    print(f"{state=}")

    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
        goto="attraction_expert_node",
    )


def attraction_expert_node(state: AgentState) -> Command:
    print("== Attraction Expert Node ==")
    print(f"{state=}")
    attraction_expert_agent = create_react_agent(
        model=llm,
        tools=[tavily_search_tool],
        state_schema=AgentState,
        state_modifier=f"""
        You are a local attraction expert who knows the ins-and-outs of the local attractions and the best places to visit in {state["city"]}. What are the 5 best attractions to visit in the city? What are the best places to visit in the city? You could include stand-out monuments, museums, or parks.
        Keep in mind that the information should be relevant to the guest staying at the hotel.
        Guest Info: {state["agent_output"]["guest_info"]}
        Hotel Info: {state["agent_output"]["hotel_info"]}
        """,
    )
    result = attraction_expert_agent.invoke(state)
    print(f"{result=}")

    print(f"{result['messages'][-1].content=}")
    output = state["agent_output"]
    output["attraction_info"] = result["messages"][-1].content

    print(f"{state=}")

    return Command(
        update={
            "messages": [],
            "agent_output": output,
        },
        goto="planning_node",
    )


def planning_node(state: AgentState) -> Command:
    print("== Planning Node ==")
    print(f"{state=}")
    planning_agent = create_react_agent(
        model=llm,
        tools=[],
        state_schema=AgentState,
        state_modifier=f"""
        You are the planner for the guest staying at the hotel. Plan the guest's activities for the day based on the guest's interests and the weather in the city. Ensure they visit the most relevant attractions and eat the best local foods.\n
        Hotel Info: {state["agent_output"]["hotel_info"]}\n
        Guest Info: {state["agent_output"]["guest_info"]}\n
        Weather Info: {state["agent_output"]["weather_info"]}\n
        Food Info: {state["agent_output"]["food_info"]}\n
        Attraction Info: {state["agent_output"]["attraction_info"]}
        """,
    )
    result = planning_agent.invoke(state)
    print(f"{result=}")

    print(f"{result['messages'][-1].content=}")
    output = state["agent_output"]
    output["planning_info"] = result["messages"][-1].content

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
    workflow.add_node(food_expert_node)
    workflow.add_node(attraction_expert_node)
    workflow.add_node(planning_node)

    workflow.set_entry_point("guest_node")

    return workflow.compile()
