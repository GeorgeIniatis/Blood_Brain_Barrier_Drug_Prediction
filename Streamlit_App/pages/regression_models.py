import streamlit as st


def app():
    regression_models = st.container()

    with regression_models:
        st.header("Regression Models")
