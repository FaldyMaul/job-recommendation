# backend/load_competencies.py

import pandas as pd

def load_competency_data(path="data/competency_list.csv"):
    df = pd.read_csv(path)
    return df
