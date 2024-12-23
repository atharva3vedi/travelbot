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
    prompt = prompt.format(hotel=hotel, name=name, city=city)

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

    prompt.append(
        (
            "ai",
            "Thank you for sharing that with me! How can I assist you during your stay at {hotel}?",
        )
    )

    prompt.append(("placeholder", "{messages}"))

    return prompt


def hotel_guest_model_setup(state: AgentState) -> AgentState:
    prompt = hotel_guest_prompt_setup(
        state["hotel"],
        state["city"],
        state["name"],
        state["group"],
        state["num_people"],
    )
    return prompt.invoke({"messages": state["messages"]})


hotel_guest_agent = create_react_agent(
    model=llm,
    tools=[tavily_search_tool],  # TODO: Replace with an internal hotel data source?
    state_schema=AgentState,
    state_modifier=hotel_guest_model_setup,
)


# ==== Weather Agent ====
weather_agent = create_react_agent(
    model=llm,
    tools=[tavily_search_tool],
    state_modifier="You are the weather expert for the city. Give the weather forecast for the next 12 hours. Do not make the values up. Use the search tool to find the information.",
)
