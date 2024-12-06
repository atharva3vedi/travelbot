from typing_extensions import TypedDict
from chains import (
    # identify_chain_generator,
    gather_chain_generator,
    plan_chain_generator,
)
from langchain_community.tools.tavily_search import TavilySearchResults

webSearch = TavilySearchResults(k=3)


class GraphState(TypedDict):
    origin: str
    city: str
    hotel: str
    date_range: str
    interests: str
    group: str
    num_steps: int
    city_guide: str
    travel_plan: str
    # Searcheddata:List[str]


# def city_selection_node(state):
#     """
#     Node to analyze and select the best city for the trip.
#     """
#     print("---CITY SELECTION NODE---")

#     # Extract required state values using correct case
#     origin = state["origin"]
#     country = state["country"]  # Changed from Country to country
#     date_range = state["date_range"]
#     interests = state["interests"]
#     num_steps = int(state["num_steps"])
#     num_steps += 1

#     # Invoke identify_chain_generator
#     city_selection = identify_chain_generator.invoke(
#         {
#             "origin": origin,
#             "country": country,
#             "date_range": date_range,
#             "interests": interests,
#         }
#     )

#     # Return the result in the state
#     return {
#         "city": city_selection,
#         "origin": origin,
#         "country": country,
#         "date_range": date_range,
#         "interests": interests,
#         "num_steps": num_steps,
#     }


def write_markdown(content, filename):
    with open(filename, "w") as f:
        f.write(content)


def gather_city_guide_node(state):
    """
    Node to gather a comprehensive city guide for the chosen city.
    """
    print("---GATHER CITY GUIDE NODE---")

    # Extract required state values
    origin = state["origin"]
    city = state["city"]  # Assumes 'city' is already selected and in the state
    hotel = state["hotel"]
    date_range = state["date_range"]
    interests = state["interests"]
    group = state["group"]
    num_steps = state["num_steps"]
    num_steps += 1

    # Invoke gather_chain_generator
    city_guide = gather_chain_generator.invoke(
        {
            "origin": origin,
            "city": city,
            "hotel": hotel,
            "date_range": date_range,
            "interests": interests,
            "group": group,
        }
    )

    # Write result to markdown
    write_markdown(str(city_guide), "city_guide.md")
    state["city_guide"] = city_guide

    return {"city_guide": city_guide, "num_steps": num_steps}


def travel_plan_node(state):
    """
    Node to expand the city guide into a detailed travel itinerary.
    """
    print("---TRAVEL PLAN NODE---")

    # Extract required state values
    origin = state["origin"]
    city = state["city"]  # Assumes 'city' is already selected and in the state
    hotel = state["hotel"]
    date_range = state["date_range"]
    interests = state["interests"]
    group = state["group"]
    city_guide = state["city_guide"]  # Assumes 'city_guide' is already gathered
    num_steps = state["num_steps"]
    num_steps += 1

    # Invoke plan_chain_generator
    travel_plan = plan_chain_generator.invoke(
        {
            "origin": origin,
            "city": city,
            "hotel": hotel,
            "date_range": date_range,
            "interests": interests,
            "group": group,
            "city_guide": city_guide,
        }
    )

    # Write result to markdown
    write_markdown(str(travel_plan), "travel_plan.md")
    state["travel_plan"] = travel_plan

    return {"travel_plan": travel_plan, "num_steps": num_steps}


def state_printer(state):
    """Print the current state"""
    print("---STATE PRINTER---")
    print(f"Origin: {state.get('origin', 'N/A')} \n")
    print(f"City: {state.get('city', 'N/A')} \n")
    print(f"Date Range: {state.get('date_range', 'N/A')} \n")
    print(f"Traveler Interests: {state.get('interests', 'N/A')} \n")
    print(f"Hotel: {state.get('hotel', 'N/A')} \n")
    print(f"Group: {state.get('group', 'N/A')} \n")
    print(f"City Guide: {state.get('city_guide', 'N/A')} \n")
    print(f"Travel Plan: {state.get('travel_plan', 'N/A')} \n")
    print(f"Num Steps: {state.get('num_steps', 'N/A')} \n")
    return
