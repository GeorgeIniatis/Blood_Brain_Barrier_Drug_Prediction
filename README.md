# Blood-Brain Barrier Drug Prediction
*Taken directly from the dissertation's abstract

**Background**: The blood-brain barrier (BBB) prevents the vast majority of all compounds from entering the brain, protecting it from diseases and infections. However, it can also prevent useful therapeutics combating brain or central nervous system (CNS) related diseases from reaching their target.

**Motivation**: Checking whether a specific drug or compound can penetrate the BBB with experimental trials is expensive, time consuming and highly inefficient. Therefore, a predictive system can be a highly valuable tool that can test thousands of drugs and compounds in an inexpensive, fast and efficient manner.

**Aims**: This project aimed to create a new curated data set and then using it train machine learning models that make use of a drug's or compound's chemical properties to predict whether it can pass into the BBB or not.

**Methods**: Both classification and regression models were trained using subsets of a curated data set of 2396 publicly available drugs and compounds and 6 hydrogen-bonding chemical descriptors. The classification models were further improved through the addition of the available side effects and indications to the chemical descriptors. Unfortunately this could not be replicated for the case of the regression models due to the subset size. All models were checked for robustness and evaluated using dummy models and holdout test sets.

**Results**: 
- Our best classification model with just chemical descriptors used as features was the Random Forest Classifier which achieved an F1 score of 0.8506, an Accuracy of 0.8116, a Recall score of 0.9250, a Precision score of 0.7872 and a Matthews Correlation Coefficient of 0.6145. 
- Our best classification model with chemical descriptors and a selection of side effects and indications as features was again the Random Forest Classifier, which achieved an F1 score of 0.8642, an Accuracy of 0.8406, a Recall score of 0.8750, a Precision score of 0.8537 and a Matthews Correlation Coefficient of 0.6716. 
- Our best regression model with chemical descriptors used as features was the Support Vector Regression model, which achieved an R2 score of 0.4746, and a Negated Mean Absolute Error of -0.3968.

**Links**:
- Dissertation discussing the project's life-cycle ([Dissertation Link](https://github.com/GeorgeIniatis/Blood_Brain_Barrier_Drug_Prediction/blob/main/Dissertation/Dissertation.pdf))
- Streamlit web application created to showcase all the different models and our work ([Web App Link](https://share.streamlit.io/georgeiniatis/blood_brain_barrier_drug_prediction/main/Streamlit_App/app.py))
- Online version of the notebook hosted on Datalore ([Datalore Link](https://datalore.jetbrains.com/notebook/IczIzzNdfezZefWuhmeMRx/D9Y5hyorcCW5ScYTdMTeab/))
- Static version of the notebook hosted on Datalore ([Static Notebook Link](https://datalore.jetbrains.com/view/notebook/m4eB6bbbxZiNkD3AyMym6t))



