from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.kernel_ridge import KernelRidge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import pickle
from os import path
import sys
sys.path.append("../..")
import util
import tqdm
import numpy as np

DATA_DIR = "../../../../data/bughouse-db"

filename = "export2018"
file = path.join(DATA_DIR, "bpgn", f"{filename}.bpgn")
filepath = path.join(DATA_DIR, "pk", f"{filename}.pk")


def print_insights(reg, X, y, label=""):
    preds = reg.predict(X)
    print(f"{label} predictions: min = {np.min(preds)}, max = {np.max(preds)}, mean = {np.mean(preds)}, mean diff from mean: {np.mean(preds - np.mean(preds))}")
    score = reg.score(X, y)
    rmse = np.sqrt(np.mean((preds - y) ** 2))
    print(f"{label}: score = {score}, RMSE = {rmse}")

def save_model(model, save_path):
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)

print("Loading dataset")
with open(filepath, 'rb') as f:
    data_dict = pickle.load(f)

print("Processing dataset")
states, values = util.dataset_to_array(data_dict, tqdm.tqdm, max_n=50000)
print(f"Dataset memory: {sys.getsizeof(states) / 1048576} mb")

split_n = int(0.85 * states.shape[0])
indices = np.random.permutation(states.shape[0])
training_idx, test_idx = indices[:split_n], indices[split_n:]
X_train, X_test = states[training_idx, :], states[test_idx, :]
y_train, y_test = values[training_idx], values[test_idx]

print("Fitting linear regression")
reg = LinearRegression().fit(X_train, y_train)

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

save_model(reg, 'saved_models/LinearRegression.sav')

# with open('saved_models/LinearRegression.sav', 'rb') as f:
#    loaded_model = pickle.load(f)
# diff = loaded_model.predict(X_test) - reg.predict(X_test)
# assert np.abs(np.sum(diff)) < 1e-3

print("Fitting ElasticNet")
reg = ElasticNet().fit(X_train, y_train)

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

save_model(reg, 'saved_models/ElasticNet.sav')

print("Fitting DecisionTreeRegressor")
reg = DecisionTreeRegressor().fit(X_train, y_train)

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

save_model(reg, 'saved_models/DecisionTreeRegessor.sav')

print("Fitting RandomForestRegressor")
reg = RandomForestRegressor(n_estimators=10).fit(X_train, y_train)

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

save_model(reg, 'saved_models/RandomForestRegressor.sav')

print("Fitting KernelRidge")
reg = KernelRidge(kernel="polynomial").fit(X_train, y_train)

print_insights(reg, X_train, y_train, "Train")
print_insights(reg, X_test, y_test, "Test")

save_model(reg, 'saved_models/KernelRidge.sav')

# # Models with PCA

svd = TruncatedSVD(n_components=512)
X_train_PCA = svd.fit_transform(X_train)
print("Fit PCA")
X_test_PCA = svd.transform(X_test)
print(f"PCA explaination: {np.sum(svd.explained_variance_ratio_)}")

with open('saved_models/PCA.sav', 'rb') as f:
    svd = pickle.load(f)
X_train_PCA = svd.transform(X_train)
X_test_PCA = svd.transform(X_test)

save_model(svd, 'saved_models/PCA.sav')

print("Fitting linear regression")
reg = LinearRegression().fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")

save_model(reg, 'saved_models/LinearRegressionPCA.sav')

print("Fitting ElasticNet")
reg = ElasticNet().fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")

save_model(reg, 'saved_modelsElasticNetPCA.sav')

print("Fitting DecisionTreeRegression")
reg = DecisionTreeRegressor().fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")

save_model(reg, 'saved_models/DecisionTreeRegessorPCA.sav')

print("Fitting RandomForestRegressorPCA")
reg = RandomForestRegressor(n_estimators=10).fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")

save_model(reg, 'saved_models/RandomForestRegressorPCA.sav')

print("Fitting KernelRidge")
reg = KernelRidge(kernel="polynomial").fit(X_train_PCA, y_train)

print_insights(reg, X_train_PCA, y_train, "Train")
print_insights(reg, X_test_PCA, y_test, "Test")

save_model(reg, 'saved_models/KernelRidgePCA.sav')
