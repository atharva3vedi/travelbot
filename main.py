import datetime  # Add this line to import datetime
import os

import streamlit as st

# Set environment variables if not already set
env_vars = {"GROQ_API_KEY", "TAVILY_API_KEY"}
for var in env_vars:
    if var not in os.environ:
        os.environ[var] = st.secrets[var]

from agents import create_workflow


app = create_workflow()
if st.button("Plan my stay!"):
    with st.spinner("Planning your trip..."):
        try:
            output = app.invoke(
                {
                    "name": "Bob",
                    "hotel": "The Park, New Delhi",
                    "city": "New Delhi",
                    "group": "friends-male",
                    "num_people": 3,
                    "agent_output": {},
                },
                {"recursion_limit": 5},
            )

            # Create main content area
            st.title("Your Travel Plan")

            # Display trip plan in the second column
            # with st.expander(""):
            #     st.markdown(output["city_guide"])
            # with st.expander("Hotel Guest Information"):
            #     st.markdown(output["guest_hotel_info"])
            st.subheader("State")
            st.markdown(
                f"Hotel: {output['hotel']}\n\nCity: {output['city']}\n\nGuest Name: {output['name']}\n\ngroup: {output['group']}\n\nNumber of People: {output['num_people']}"
            )
            st.subheader("Agents Outputs")
            st.markdown([f"## {k} \n\n {v}" for k, v in output["agent_output"].items()])

            # # Optional: Display debug information in an expander
            # with st.expander("Debug Information"):
            #     st.json(output)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
