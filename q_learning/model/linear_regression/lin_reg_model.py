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


def print_insights(reg, X, y, label=""):
    preds = reg.predict(X)
    print(f"{label} predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
    score = reg.score(X, y)
    rmse = np.sqrt(np.mean((preds - y) ** 2))
    print(f"{label}: score = {score}, RMSE = {rmse}")

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

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

print("Fitting ElasticNet")
reg = ElasticNet().fit(X_train, y_train)

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

print("PCA states")
svd = TruncatedSVD(n_components=512)
X_train_PCA = svd.fit_transform(X_train)
X_test_PCA = svd.transform(X_test)
print(f"PCA explaination: {np.sum(svd.explained_variance_ratio_)}")

print("Fitting linear regression")
reg = LinearRegression().fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")

print("Fitting ElasticNet")
reg = ElasticNet().fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")
