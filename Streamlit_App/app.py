import streamlit as st

# Custom imports
from multipage import MultiPage
from pages import home

# Create an instance of the app
app = MultiPage()

# Title of the main page
st.title("Blood-Brain Barrier Prediction System")

# Add all your applications (pages) here
app.add_page("Home", home.app)

# The main app
app.run()