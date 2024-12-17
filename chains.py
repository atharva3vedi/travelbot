import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

GROQ_LLM = ChatGroq(model="llama-3.3-70b-versatile")
# ... existing imports ...

# Add the search tool
search = TavilySearchResults(api_key=TAVILY_API_KEY)


# Function to perform search and combine results
def search_and_analyze(inputs, search_query_prompt):
    # Generate search query
    search_query = search_query_prompt.format(**inputs)

    print(f"Searching with query: {search_query}")  # Debug print

    # Perform search
    search_results = search.invoke(search_query)

    # Format search results into a string
    formatted_results = "\n\n".join(
        [f"Source: {result['url']}\n{result['content']}" for result in search_results]
    )

    # Combine original inputs with search results
    analysis_input = {**inputs, "search_results": formatted_results}

    return analysis_input


# # First, create a search query prompt
# search_query_prompt = PromptTemplate(
#     template="""Create a search query to find information about cities in {country}
#     that would be good to visit during {date_range} for someone interested in {interests}.""",
#     input_variables=["country", "date_range", "interests"],
# )


# # Update the identify chain template to include search results
# identify_chain = PromptTemplate(
#     template="""Based on the following search results and criteria, analyze and select the best city for the trip:

# SEARCH RESULTS:
# {search_results}

# TRIP CRITERIA:
# Traveling from: {origin}
# Country: {country}
# Trip Date: {date_range}
# Traveler Interests: {interests}

# Select and recommend the best city to visit. Your response must include:
# 1. Name of the recommended city (clearly stated)
# 2. Why this city was selected (based on search results and criteria)
# 3. Current or typical weather during {date_range}
# 4. Main attractions that match the interests
# 5. Any special events or seasonal highlights during {date_range}
# 6. Estimated travel costs from {origin}

# Format your response in a clear, markdown-style format with headers and bullet points.""",
#     input_variables=["search_results", "origin", "country", "date_range", "interests"],
# )

# # Update the chain to include search
# identify_chain_generator = (
#     RunnableLambda(search_and_analyze)  # First perform search
#     | identify_chain  # Then format prompt with search results
#     | GROQ_LLM  # Generate response
#     | StrOutputParser()  # Parse to string
# )

gather_chain = PromptTemplate(
    template="""
            As a local expert on this {city} you must compile an
            in-depth guide for someone traveling there and wanting
            to have THE BEST trip ever!
            Gather information about  key attractions, local customs,
            special events, and daily activity recommendations.
            Find the best spots to go to, the kind of place only a
            local would know.
            This guide should provide a thorough overview of what
            the {city} has to offer, including hidden gems, cultural
            hotspots, must-visit landmarks, weather forecasts, and
            high level costs.

            The final answer must be a comprehensive {city} guide,
            rich in cultural insights and practical tips,
            tailored to enhance the travel experience.

            City:{city}
            Trip Date: {date_range}
            Traveling from: {origin}
            Traveler Interests: {interests}
            expected_output=A comprehensive city guide with cultural insights and practical tips.""",
    input_variable=["origin", "city", "date_range", "interests"],
)
gather_chain_generator = gather_chain | GROQ_LLM | StrOutputParser()

plan_chain = PromptTemplate(
    template="""
            City Guide:
            {city_guide}
    
            Expand this guide into a full travel itinerary for this time {date_range} with detailed per-day plans, including
            weather forecasts, places to eat, and a budget breakdown.

            You MUST suggest actual places to visit and actual restaurants to go to.

            This itinerary should cover all aspects of the trip, 
            keeping in mind the traveler's interests and preferences,
            starting and ending each day at the traveler's hotel, {hotel},
            and integrating the city guide information with practical travel logistics.

            Your final answer MUST be a complete expanded travel plan,
            formatted as markdown, encompassing a daily schedule,
            anticipated weather conditions, and a detailed budget, 
            ensuring THE BEST TRIP EVER. Be specific and give a reason why 
            you picked each place, what makes them special!

            Consider the traveler's group type when planning activities:
            - "solo": Focus on individual activities and personal experiences.
            - "couple": Include romantic spots and activities for two.
            - "friends - male": Suggest activities and places that might appeal to a group of male friends.
            - "friends - female": Suggest activities and places that might appeal to a group of female friends.
            - "family": Include activities suitable for a family with all adult members.
            - "family with kids": Focus on kid-friendly activities and places.
            - "family with teens": Include activities that would interest teenagers.
            - "family with seniors": Suggest activities suitable for older adults.

            Trip Date: {date_range}
            Traveling from: {origin}
            Hotel in the city: {hotel}
            Traveler Interests: {interests}
            Traveler Group: {group}
            expected_output="A complete 7-day travel plan, formatted as markdown, with a daily schedule and budget.""",
    input_variables=[
        "origin",
        "city",
        "date_range",
        "interests",
        "hotel",
        "group",
        "city_guide",
    ],
)
plan_chain_generator = plan_chain | GROQ_LLM | StrOutputParser()
