import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def app():
    classification_models = st.container()

    with classification_models:
        st.subheader("Just the Chemical Descriptors used as features")
        st.markdown("##### Training Performance")

        training_performance = pd.read_excel("data/Metrics/Classification_Models_CD_Training_Metrics.xlsx", skiprows=1)
        training_performance = training_performance.astype(str)
        """training_performance_fig = go.Figure(data=[go.Table(
            header=dict(values=list(training_performance.columns)),
            cells=dict(
                values=[training_performance["Set"], training_performance["Model"], training_performance["Accuracy"],
                        training_performance["Recall"], training_performance["Precision"], training_performance["F1"],
                        training_performance["Matthews Correlation Coefficient"],
                        training_performance["Permutation Testing P-Value"]]))
        ])
        training_performance_fig.update_layout(height=600, font=dict(size=12))
        st.plotly_chart(training_performance_fig, use_container_width=True)"""
        st.table(training_performance)

        st.subheader("Chemical Descriptors, Side Effects and Indications used as features")
