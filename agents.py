from datetime import datetime, timedelta
from typing import Literal, Optional, Annotated
from typing_extensions import TypedDict
from os import getenv

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate
from langgraph.managed import IsLastStep

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
tavily_search_tool = TavilySearchResults(api_key=TAVILY_API_KEY)


@tool
def scheduler(
    activity_durations: dict[str, timedelta],
    start_time: datetime,
    end_time: datetime,
) -> dict[str, datetime, datetime]:
    # TODO: Replace this placeholder with MILP optimization
    """
    Schedule activities based on their durations and the available time window.
    """
    current_time = start_time
    scheduled_activities = {}
    for activity, duration in activity_durations.items():
        if current_time + duration > end_time:
            break
        scheduled_activities[activity] = (current_time, current_time + duration)
        current_time += duration
    return scheduled_activities


# ==== Hotel Guest Agent ====
def hotel_guest_prompt_setup(
    hotel: str, city: str, name: str, group: str, num_people: int
) -> ChatPromptTemplate:
    prompt = ChatPromptTemplate(
        [
            (
                "system",
                "You are the concierge at the hotel, {hotel} in {city}. You will interact with a guest who is staying at the hotel. To do so, you need to know detailed infomation about the hotel which you can find by searching the web.",
            ),
            ("user", "Make sure you are polite and friendly with your interactions."),
            ("ai", "Hello! I am the concierge at {hotel}. Please tell me your name."),
            ("user", "My name is {name}"),
            (
                "ai",
                "Nice to meet you, {name}! Are you traveling in a group? If so, how many people are in your group?",
            ),
        ]
    )

    # def get_group_message(group: str, num_people: int) -> str:
    #     if group == "solo":
    #         return "I am traveling alone."
    #     elif group == "couple":
    #         return "I am traveling with my partner."
    #     elif group == "friends-male":
    #         return f"I am traveling in a group of {num_people} male friends."
    #     elif group == "friends-female":
    #         return f"I am traveling in a group of {num_people} female friends."
    #     elif group == "family":
    #         return f"I am traveling with my family of {num_people} adults."
    #     elif group == "family-kids":
    #         return f"I am traveling with my family, including young children. We are {num_people} in total."
    #     elif group == "family-teens":
    #         return f"I am traveling with my family, including teenagers. We are {num_people} in total."
    #     elif group == "family-seniors":
    #         return f"I am traveling with my family, including senior members. We are {num_people} in total."
    #     else:
    #         return f"I am traveling with a group of {num_people} people."
    # prompt.append(("user", get_group_message(group, num_people)))

    prompt.append(("user", "I am traveling with a group of 3 people friends."))

    prompt.extend(
        [
            (
                "ai",
                "Thank you for sharing that with me! How can I assist you during your stay at {hotel}?",
            ),
            (
                "user",
                "What can I do at the hotel today? What are the activities available? What are the dining options?",
            ),
        ]
    )

    prompt.append(("placeholder", "{messages}"))

    prompt = prompt.format(hotel=hotel, name=name, city=city)
    return prompt


def hotel_guest_model_setup(state: AgentState) -> AgentState:
    prompt = hotel_guest_prompt_setup(
        state["hotel"],
        state["city"],
        state["name"],
        state["group"],
        state["num_people"],
    )
    print(f"{prompt=}")
    return prompt


hotel_guest_agent = create_react_agent(
    model=llm,
    tools=[tavily_search_tool],  # TODO: Replace with an internal hotel data source?
    state_schema=AgentState,
    state_modifier=hotel_guest_model_setup,
)


def hotel_guest_node(state: AgentState) -> Command:
    print("== Hotel Guest Node ==")
    print(f"{state=}")
    result = hotel_guest_agent.invoke(state)
    print(f"{result=}")
    output = {"hotel_guest_info": str(result["messages"][-1].content)}
    state["agent_output"] = (
        state["agent_output"].update(output) if state["agent_output"] else output
    )
    print(f"{state=}")

    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": [],
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
        tools=[tavily_search_tool],
        state_schema=AgentState,
        state_modifier=f"You are the weather expert for the city of {state["city"]}. Give me the temperature for today. Do not make the values up. Use the search tool to find the information.",
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

    # workflow.add_node("hotel_guest_node", hotel_guest_node)
    workflow.add_node("weather_node", weather_node)

    # workflow.set_entry_point("hotel_guest_node")
    workflow.set_entry_point("weather_node")

    # workflow.add_edge("hotel_guest_node", END)
    # workflow.add_edge("hotel_guest_node", "weather_node")
    workflow.add_edge("weather_node", END)

    return workflow.compile()
