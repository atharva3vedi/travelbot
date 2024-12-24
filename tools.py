from datetime import datetime, timedelta

from langchain_core.tools import tool


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


@tool
def weather(city: str) -> str:
    """
    Get the current weather in the city.
    """
    return f"Today's temperature in {city} is 25 degrees Celsius."


@tool
def guest_info(name: str, group: str, num_people: int) -> str:
    """
    Get detailed information about the guest from the provided inputs.

    Args:
        name (str): The name of the guest.
        group (str): The group type of the guest.
        num_people (int): The number of people in the guest's group.
    """

    def get_group_message(group: str, num_people: int) -> str:
        if group == "solo":
            return "alone"
        elif group == "couple":
            return "with my partner"
        elif group == "friends-male":
            return f"in a group of {num_people} male friends"
        elif group == "friends-female":
            return f"in a group of {num_people} female friends"
        elif group == "family":
            return f"with my family of {num_people} adults"
        elif group == "family-kids":
            return f"with my family, including young children. We are {num_people} in total"
        elif group == "family-teens":
            return f"with my family, including teenagers. We are {num_people} in total"
        elif group == "family-seniors":
            return f"with my family, including senior members. We are {num_people} in total"
        else:
            return f"with a group of {num_people} people"

    return f"Guest name is {name}. They are traveling {get_group_message(group, num_people)}."
