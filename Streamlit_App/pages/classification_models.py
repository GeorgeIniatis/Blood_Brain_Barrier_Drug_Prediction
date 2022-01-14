import streamlit as st

def app():
    classification_models = st.container()

    with classification_models:
        st.header("Classification Models")