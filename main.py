import datetime  # Add this line to import datetime
import streamlit as st
from pprint import pprint
from StateAndNodes import GraphState
from workflow import app

# Default date range and today's date for validation
today = datetime.datetime.now().date()  # Now works because datetime is imported
default_date_range = (today, today + datetime.timedelta(days=7))

# Sidebar UI for user input
st.sidebar.header("Enter Trip Details")
origin = st.sidebar.text_input("Your location:", placeholder="Example: New York, USA")
country = st.sidebar.text_input("Target country:", placeholder="Example: France")
searched_data = st.sidebar.text_area("Cities to consider:", placeholder="Example: Paris, Lyon")
drange = st.sidebar.date_input("Travel dates:", value=default_date_range, min_value=today)
interests = st.sidebar.text_area("Your interests:", placeholder="Example: Museums, art, hiking")

# Run workflow when button is clicked
if st.sidebar.button("Plan My Trip"):
    inputs = {
        "origin": origin,
        "country": country,
        "date_range": str(drange[0]) + " to " + str(drange[1]),
        "interests": interests,
        "num_steps": 0
    }
    
    with st.spinner("Planning your trip..."):
        try:
            output = app.invoke(inputs)
            
            # Create main content area
            st.title("Your Travel Plan")
            
            # Create columns for trip details
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Trip Details")
                st.write(f"🛫 From: {output['origin']}")
                st.write(f"🌍 To: {output['country']}")
                st.write(f"📅 Dates: {output['date_range']}")
                if output['interests']:
                    st.write(f"❤️ Interests: {output['interests']}")
            
            with col2:
                if 'city' in output:
                    st.subheader("Selected City")
                    st.write(f"🏰 {output['city']}")
            
            # Display the main recommendation
            if 'city_selection' in output and output['city_selection']:
                st.subheader("Travel Recommendations")
                st.markdown(output['city_selection'])
            
            # Optional: Display debug information in an expander
            with st.expander("Debug Information"):
                st.json(output)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

