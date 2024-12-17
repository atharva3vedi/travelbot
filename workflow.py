from StateAndNodes import (
    # city_selection_node,
    gather_city_guide_node,
    travel_plan_node,
    GraphState,
    state_printer,
    guest_hotel_node,
)
from langgraph.graph import END, StateGraph


# Define routing logic
def route_to_travel_planner(state):
    """Determine the next step after gathering a city guide."""
    if (
        "city_guide" in state
        and str(state["city_guide"])
        and "guest_hotel_info" in state
        and str(state["guest_hotel_info"])
    ):
        return "travel_planner"
    return "state_printer"


def create_workflow():
    """Create the workflow graph"""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("state_printer", state_printer)
    workflow.add_node("gather_city_guide", gather_city_guide_node)
    workflow.add_node("travel_planner", travel_plan_node)
    workflow.add_node("guest_hotel_expert", guest_hotel_node)

    # Set entry point
    workflow.set_entry_point("gather_city_guide")

    # Add edges
    workflow.add_edge("gather_city_guide", "guest_hotel_expert")
    workflow.add_edge("guest_hotel_expert", "state_printer")
    workflow.add_conditional_edges(
        "guest_hotel_expert",
        route_to_travel_planner,
        then="state_printer",
    )
    workflow.add_edge("state_printer", END)

    return workflow.compile()


# Create the workflow
app = create_workflow()
