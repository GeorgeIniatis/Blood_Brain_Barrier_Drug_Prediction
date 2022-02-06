import streamlit as st
import pandas as pd
from joblib import load

cd_model_name_to_file = {
    '-': '-',
    'Dummy Regressor': 'dr_cd.joblib',
    'Linear Regression': 'lr_cd.joblib',
    'Support Vector Regression': 'optimised_svr_cd.joblib',
    'K-Nearest Neighbour Regressor': 'optimised_knnr_cd.joblib',
    'Random Forest Regressor': 'optimised_rfr_cd.joblib',
    'Stochastic Gradient Descent Regressor': 'optimised_sgdr_cd.joblib',
}


def render_dataframe_as_table(dataframe):
    dataframe = dataframe.round(5)
    st.table(dataframe)


def user_inputs_section():
    mw = st.number_input("Molecular Weight (MW)", min_value=0.0,
                         help="Molecular weight or molecular mass refers to the mass of a molecule. It is calculated as the sum of the mass of each constituent atom multiplied by the number of atoms of that element in the molecular formula.")
    tpsa = st.number_input("Topological Polar Surface Area (TPSA)", min_value=0.0,
                           help="The topological polar surface area (TPSA) of a molecule is defined as the surface sum over all polar atoms in a molecule.")
    xlogp = st.number_input("XLogP3-AA (XLogP)", min_value=0.0,
                            help="Computed Octanol/Water Partition Coefficient")
    nhd = st.number_input("Hydrogen Bond Donor Count (NHD)", min_value=0.0,
                          help="The number of hydrogen bond donors in the structure.")
    nha = st.number_input("Hydrogen Bond Acceptor Count (NHA)", min_value=0.0,
                          help="The number of hydrogen bond acceptors in the structure.")
    nrb = st.number_input("Rotatable Bond Count (NRB)", min_value=0.0,
                          help="A rotatable bond is defined as any single-order non-ring bond, where atoms on either side of the bond are in turn bound to nonterminal heavy (i.e., non-hydrogen) atoms. That is, where rotation around the bond axis changes the overall shape of the molecule, and generates conformers which can be distinguished by standard fast spectroscopic methods.")

    return mw, tpsa, xlogp, nhd, nha, nrb


def app():
    useful_info = st.container()
    cd_models = st.container()
    cd_chosen_model_and_inputs, cd_prediction_metrics = st.columns(2)

    with useful_info:
        st.subheader("Regression Models")
        st.markdown("""
                    - Regression models will make use of the LogBB as the label
                    - All models were optimised for R2 score using a 10-Fold Cross Validation except for the case of the Dummy Regressor and the Linear Regression models
                    - Training set:
                        - A subset of the dataset will be used, those entries that have LogBB available, again excluding the entries used in the Test set
                    - Test set:
                        - Will be used to compare the models against against each other
                        - 20% subset of the training set
                    """)

    with cd_models:
        st.markdown("##### Training Performance")
        training_performance_cd = pd.read_csv(
            "Streamlit_App/data/Metrics/Regression_Models_CD_Training_Metrics.csv",
            skiprows=1)
        render_dataframe_as_table(training_performance_cd)
        st.markdown(
            "*The Decision Tree Regressor model won't be available for predictions since it is not robust (Permutation Testing P-Value > 0.05)")

        st.markdown("##### Testing Performance")
        testing_performance_cd = pd.read_csv(
            "Streamlit_App/data/Metrics/Regression_Models_CD_Testing_Metrics.csv", skiprows=1)
        render_dataframe_as_table(testing_performance_cd)

    with cd_chosen_model_and_inputs:
        st.markdown("##### Make Predictions")
        st.markdown("""
                    - Please choose a model and enter a decimal number for each of the 6 chemical descriptors
                    - Helpful definitions are available for each descriptor. To access them click the question mark icon
                    """)
        cd_chosen_model = st.selectbox('Please choose a model to make predictions',
                                       cd_model_name_to_file.keys(),
                                       key="cd")
        if cd_chosen_model != "-":
            mw, tpsa, xlogp, nhd, nha, nrb = user_inputs_section()

            if st.button("Predict", key="cd"):
                with cd_prediction_metrics:
                    st.markdown("##### Result")

                    model = load(
                        f"Streamlit_App/data/Regression_Models/CD/{cd_model_name_to_file[cd_chosen_model]}")
                    user_inputs = pd.DataFrame([[mw, tpsa, xlogp, nhd, nha, nrb]],
                                               columns=['MW', 'TPSA', 'XLogP', 'NHD', 'NHA', 'NRB'])

                    predicted_logBB = model.predict(user_inputs)[0]
                    st.markdown(f"Predicted LogBB: **{predicted_logBB}**")

                    if predicted_logBB >= -1:
                        st.markdown("""
                                    The model has predicted that the compound/drug with the specific chemical properties you have specified **Can cross the BBB**
                                    """)
                    else:
                        st.markdown("""
                                    The model has predicted that the compound/drug with the specific chemical properties you have specified **Cannot cross the BBB**
                                    """)
