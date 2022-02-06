# Blood Brain Barrier Drug Prediction

The brain is surrounded by a permeable boundary that prevents many pathogens from getting in, however, it can also stop many useful drugs from entering the brain. This is especially important when trying to deliver critical therapeutics, such as chemotherapy, to brain tumours. Accurate prediction of whether a drug will easily cross the blood-brain barrier is a valuable tool for developing and testing new drugs for various diseases.

**Original Aims**: This project aimed to gather publicly available data on drugs known to cross into the brain and those that cannot and place them into a new dataset and then using that new dataset train machine learning models that use a drug's or compound's chemical descriptors to predict whether it can pass into the brain or not

**Actual Achievements**: A dataset of 2396 publicly available compounds and drugs was gathered from various academic papers and APIs. The models built were split into two categories, Classification and Regression. Classification models would try to predict whether a particular compound or drug can pass the barrier and Regression models would try to predict the logBB value.

Various models were built for both categories using the chemical descriptors of each specific compound or drug. In the case of the Classification models, these were further improved by including the side effects and indications of each compound or drug. Unfortunately, this could not be replicated in the case of the Regression models due to the small size of the subset

A streamlit web application was then built to showcase all the different models built. [You can access the application using this link](https://share.streamlit.io/georgeiniatis/blood_brain_barrier_drug_prediction/main/Streamlit_App/app.py)


