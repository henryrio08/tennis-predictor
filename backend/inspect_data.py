import pandas as pd

df = pd.read_csv("/Users/henryriordan/vscode/tennis-predictor/data/atp_tennis.csv")

print(df.head())
print(df.columns)
print(df.shape)
print(df.isnull().sum())