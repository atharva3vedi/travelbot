from StateAndNodes import (
    city_selection_node,
    #gather_city_guide_node,
    #travel_plan_node,
    GraphState,
    state_printer
)
from langgraph.graph import END, StateGraph
import streamlit as st

def create_workflow():
    """Create the workflow graph"""
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("city_selection", city_selection_node)
    workflow.add_node("state_printer", state_printer)
    
    # Set entry point
    workflow.set_entry_point("city_selection")
    
    # Add edges
    workflow.add_edge("city_selection", "state_printer")
    workflow.add_edge("state_printer", END)
    
    return workflow.compile()

# Create the workflow
app = create_workflow()
'''
workflow.add_node("gather_city_guide", gather_city_guide_node)
workflow.add_node("travel_plan", travel_plan_node)
workflow.add_node("state_printer", state_printer)

# Set entry point
workflow.set_entry_point("city_selection")

# Define conditional edges
workflow.add_conditional_edges(
    "city_selection",
    route_to_city_guide,
    {
        "gather_city_guide": "gather_city_guide",
        "state_printer": "state_printer",
    },
)
workflow.add_conditional_edges(
    "gather_city_guide",
    route_to_travel_plan,
    {
        "travel_plan": "travel_plan",
        "state_printer": "state_printer",
    },
)

workflow.add_edge("travel_plan", "state_printer")
workflow.add_edge("state_printer", END)

# Define routing logic
def route_to_city_guide(state):
    """Determine the next step after city selection."""
    if "city" in state and state["city"]:
        return {"next_step": "gather_city_guide"}
    return {"next_step": "state_printer"}

def route_to_travel_plan(state):
    """Determine the next step after gathering a city guide."""
    if "city_guide" in state and state["city_guide"]:
        return {"next_step": "travel_plan"}
    return {"next_step": "state_printer"}
'''