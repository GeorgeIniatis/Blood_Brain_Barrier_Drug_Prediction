import streamlit as st
from multipage import MultiPage
from pages import home, dataset, classification_models, regression_models, references

# Create an instance of the app
app = MultiPage()

st.set_page_config(layout="wide")
st.title("Blood-Brain Barrier Prediction")

# Add all your applications (pages) here
app.add_page("Home", home.app)
app.add_page("Dataset", dataset.app)
app.add_page("Classification Models", classification_models.app)
app.add_page("Regression Models", regression_models.app)
app.add_page("References", references.app)

# The main app
app.run()
