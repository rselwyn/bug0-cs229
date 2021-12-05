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

split_n = int(0.85 * states.shape[0])
indices = np.random.permutation(states.shape[0])
training_idx, test_idx = indices[:split_n], indices[split_n:]
X_train, X_test = states[training_idx, :], states[test_idx, :]
y_train, y_test = values[training_idx], values[test_idx]

print("Fitting linear regression")
reg = LinearRegression().fit(X_train, y_train)

preds = reg.predict(X_train)
print(f"Train predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_train, y_train)
rmse = np.sqrt(np.mean((preds - y_train) ** 2))
print(f"Train: score = {score}, RMSE = {rmse}")

preds = reg.predict(X_test)
print(f"Test predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_test, y_test)
rmse = np.sqrt(np.mean((preds - y_test) ** 2))
print(f"Test: score = {score}, RMSE = {rmse}")


print("Fitting ElasticNet")
reg = ElasticNet().fit(X_train, y_train)

preds = reg.predict(X_train)
print(f"Train predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_train, y_train)
rmse = np.sqrt(np.mean((preds - y_train) ** 2))
print(f"Train: score = {score}, RMSE = {rmse}")

preds = reg.predict(X_test)
print(f"Test predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_test, y_test)
rmse = np.sqrt(np.mean((preds - y_test) ** 2))
print(f"Test: score = {score}, RMSE = {rmse}")

print("PCA states")
svd = TruncatedSVD(n_components=512)
X_train = svd.fit_transform(X_train)
X_test = svd.transform(X_test)
print(f"PCA explaination: {np.sum(svd.explained_variance_ratio_)}")

print("Fitting linear regression")
reg = LinearRegression().fit(X_train, y_train)

preds = reg.predict(X_train)
print(f"Train predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_train, y_train)
rmse = np.sqrt(np.mean((preds - y_train) ** 2))
print(f"Train: score = {score}, RMSE = {rmse}")

preds = reg.predict(X_test)
print(f"Test predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_test, y_test)
rmse = np.sqrt(np.mean((preds - y_test) ** 2))
print(f"Test: score = {score}, RMSE = {rmse}")


print("Fitting ElasticNet")
reg = ElasticNet().fit(X_train, y_train)

preds = reg.predict(X_train)
print(f"Train predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_train, y_train)
rmse = np.sqrt(np.mean((preds - y_train) ** 2))
print(f"Train: score = {score}, RMSE = {rmse}")

preds = reg.predict(X_test)
print(f"Test predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
score = reg.score(X_test, y_test)
rmse = np.sqrt(np.mean((preds - y_test) ** 2))
print(f"Test: score = {score}, RMSE = {rmse}")
