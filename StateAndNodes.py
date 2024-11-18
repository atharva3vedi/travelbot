from langchain.schema import Document
from langgraph.graph import END, StateGraph

from typing_extensions import TypedDict
from typing import List
from chains import identify_chain_generator
#gather_chain_generator,plan_chain_generator
from langchain_community.tools.tavily_search import TavilySearchResults

webSearch=TavilySearchResults(k=3)

class GraphState(TypedDict):
    origin:str
    cities:List[str]
    country:str
    city:str
    date_range:str
    interests:str
    num_steps:int
    #Searcheddata:List[str]

def city_selection_node(state):
    """
    Node to analyze and select the best city for the trip.
    """
    print("---CITY SELECTION NODE---")
    
    # Extract required state values using correct case
    origin = state["origin"]
    country = state["country"]  # Changed from Country to country
    date_range = state["date_range"]
    interests = state["interests"]
    num_steps = int(state['num_steps'])
    num_steps += 1

    # Invoke identify_chain_generator
    city_selection = identify_chain_generator.invoke({
        "origin": origin,
        "country": country,
        "date_range": date_range,
        "interests": interests
    })
    
    # Return the result in the state
    return {
        "city": city_selection,  
        "origin": origin,
        "country": country,
        "date_range": date_range,
        "interests": interests,
        "num_steps": num_steps
    }




def write_markdown(content,filename):
    with open(filename, 'w') as f:
        f.write(content)
'''
def search_cities_for_trip(state):
    """
    Function to search for cities based on the state and populate Searcheddata.
    """
    print("---SEARCHING FOR CITIES---")
    
    # Extract relevant data from the state
    origin = state["origin"]
    Country = state["country"]
    drange = state["drange"]
    interests = state["interests"]
    num_steps = state["num_steps"]
    num_steps += 1  # Increment the step counter
    
    # Generate search keywords based on interests and other details
    keywords = city_keyword_chain.invoke({
        "origin": origin,
        "Country": country,
        "drange": drange,
        "interests": interests
    })
    keywords = keywords['keywords']  # Extract the list of keywords
    
    # Perform web searches and gather results
    searched_data = []
    for keyword in keywords:
        print(f"Searching for: {keyword}")
        search_results = webSearch.invoke({"query": keyword})
        search_content = "\n".join([result["content"] for result in search_results])
        searched_data.append(search_content)
    
    # Return the updated state with the Searcheddata list
    return {
        "Searcheddata": searched_data,
        "num_steps": num_steps
    }

def gather_city_guide_node(state):
    """
    Node to gather a comprehensive city guide for the chosen city.
    """
    print("---GATHER CITY GUIDE NODE---")
    
    # Extract required state values
    origin = state["origin"]
    city = state["city"]  # Assumes 'city' is already selected and in the state
    drange = state["drange"]
    interests = state["interests"]
    num_steps = state['num_steps']
    num_steps += 1

    # Invoke gather_chain_generator
    city_guide = gather_chain_generator.invoke({
        "origin": origin,
        "city": city,
        "drange": drange,
        "interests": interests
    })
    
    # Write result to markdown
    write_markdown(str(city_guide), "city_guide.md")
    
    return {"city_guide": city_guide, "num_steps": num_steps}

def travel_plan_node(state):
    """
    Node to expand the city guide into a detailed travel itinerary.
    """
    print("---TRAVEL PLAN NODE---")
    
    # Extract required state values
    origin = state["origin"]
    city = state["city"]  # Assumes 'city' is already selected and in the state
    drange = state["drange"]
    interests = state["interests"]
    num_steps = state['num_steps']
    num_steps += 1

    # Invoke plan_chain_generator
    travel_plan = plan_chain_generator.invoke({
        "origin": origin,
        "city": city,
        "drange": drange,
        "interests": interests
    })
    
    # Write result to markdown
    write_markdown(str(travel_plan), "travel_plan.md")
    
    return {"travel_plan": travel_plan, "num_steps": num_steps}
'''
def state_printer(state):
    """Print the current state"""
    print("---STATE PRINTER---")
    print(f"Origin: {state.get('origin', 'N/A')} \n")
    print(f"Country: {state.get('country', 'N/A')} \n")
    print(f"Date Range: {state.get('drange', 'N/A')} \n")
    print(f"Traveler Interests: {state.get('interests', 'N/A')} \n")
    print(f"City Guide: {state.get('city_guide', 'N/A')} \n")
    print(f"Travel Plan: {state.get('travel_plan', 'N/A')} \n")
    print(f"Searched Data: {state.get('Searcheddata', 'N/A')} \n")
    print(f"Num Steps: {state.get('num_steps', 'N/A')} \n")
    return
