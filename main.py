import datetime  # Add this line to import datetime
import streamlit as st
import os

# Set environment variables if not already set
env_vars = {"GROQ_API_KEY", "TAVILY_API_KEY"}
for var in env_vars:
    if var not in os.environ:
        os.environ[var] = st.secrets[var]

from workflow import app


# Default date range and today's date for validation
today = datetime.datetime.now().date()  # Now works because datetime is imported
default_date_range = (today, today + datetime.timedelta(days=7))

# Sidebar UI for user input
st.sidebar.header("Enter Trip Details")
origin = st.sidebar.text_input("Your location:", placeholder="Example: New York, USA")
city = st.sidebar.text_input(
    "City you are visiting:", placeholder="Example: Paris, France"
)
hotel = st.sidebar.text_input(
    "Hotel you are staying at:", placeholder="Example: Paris Marriott Champs Elysees"
)
drange = st.sidebar.date_input(
    "Travel dates:", value=default_date_range, min_value=today
)
interests = st.sidebar.text_area(
    "Your interests:", placeholder="Example: Museums, Art, Hiking, Food"
)
group = st.sidebar.selectbox(
    "Group type:",
    [
        "solo",
        "couple",
        "friends - male",
        "friends - female",
        "family",
        "family with kids",
        "family with teens",
        "family with seniors",
    ],
)

# Run workflow when button is clicked
if st.sidebar.button("Plan My Trip"):
    if not origin:
        st.sidebar.error("Please enter your location.")
    elif not city:
        st.sidebar.error("Please enter the city you are visiting.")
    elif not hotel:
        st.sidebar.error("Please enter the hotel you are staying at.")
    elif not drange:
        st.sidebar.error("Please select your travel dates.")
    elif not interests:
        st.sidebar.error("Please enter your interests.")
    elif not group:
        st.sidebar.error("Please select your group type.")
    else:
        inputs = {
            "origin": origin,
            "city": city,
            "hotel": hotel,
            "date_range": str(drange[0]) + " to " + str(drange[1]),
            "interests": interests,
            "group": group,
            "num_steps": 0,
        }

        with st.spinner("Planning your trip..."):
            try:
                output = app.invoke(inputs)

                # Create main content area
                st.title("Your Travel Plan")

                # Create columns for trip details
                col1, col2 = st.columns([1, 3])

                # Display trip details in the first column
                with col1:
                    st.subheader("Trip Details")
                    st.write(f"🛫 From: {output['origin']}")
                    st.write(f"🌍 To: {output['city']}")
                    st.write(f"📅 Dates: {output['date_range']}")
                    st.write(f"🏨 Hotel: {output['hotel']}")
                    st.write(f"❤️ Interests: {output['interests']}")
                    st.write(f"👥 Group: {output['group']}")

                # Display trip plan in the second column
                with col2:
                    with st.expander("City Guide"):
                        st.markdown(output["city_guide"])
                    st.subheader("Daily Plan")
                    st.markdown(output["travel_plan"])

                # Optional: Display debug information in an expander
                with st.expander("Debug Information"):
                    st.json(output)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
