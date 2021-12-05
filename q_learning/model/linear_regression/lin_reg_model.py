from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import ElasticNet, LinearRegression
import pickle
from os import path
import sys
sys.path.append(r"..\..")
import util
import tqdm
import numpy as np

DATA_DIR = r"..\..\..\..\data\bughouse-db"

filename = "export2018"
file = path.join(DATA_DIR, "bpgn", f"{filename}.bpgn")
filepath = path.join(DATA_DIR, "pk", f"{filename}.pk")

print("Loading dataset")
with open(filepath, 'rb') as f:
    data_dict = pickle.load(f)

print("Processing dataset")
states, values = util.dataset_to_array(data_dict, tqdm.tqdm, max_n=2000)

print("Fitting linear regression")
reg = LinearRegression().fit(states, values)

preds = reg.predict(states)
print(f"Predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(states, values)
rmse = np.sqrt(np.mean((preds - values) ** 2))
print(f"Model: score = {score}, RMSE = {rmse}")

print("Fitting ElasticNet")
reg = ElasticNet().fit(states, values)

preds = reg.predict(states)
print(f"Predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(states, values)
rmse = np.sqrt(np.mean((preds - values) ** 2))
print(f"Model: score = {score}, RMSE = {rmse}")

print("PCA states")
svd = TruncatedSVD(n_components=512)
states = svd.fit_transform(states)
print(f"PCA explaination: {svd.explained_variance_ratio_}")

preds = reg.predict(states)
print(f"Predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(states, values)
rmse = np.sqrt(np.mean((preds - values) ** 2))
print(f"Model: score = {score}, RMSE = {rmse}")

print("Fitting ElasticNet")
reg = ElasticNet().fit(states, values)

preds = reg.predict(states)
print(f"Predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(states, values)
rmse = np.sqrt(np.mean((preds - values) ** 2))
print(f"Model: score = {score}, RMSE = {rmse}")
