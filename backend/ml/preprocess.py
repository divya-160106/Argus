import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from database import warehouse_collection
from backend.config import SEQUENCE_LENGTH, FEATURE_COLUMNS

print("Loading data from MongoDB...")

documents = list( warehouse_collection.find( {}, {"_id": 0} ) )
df = pd.DataFrame(documents)
df = df.sort_values( by=["date", "hour"] ).reset_index(drop=True)
data = df[FEATURE_COLUMNS]

scaler = MinMaxScaler()
scaled = scaler.fit_transform(data)
joblib.dump( scaler, "ml/scaler.pkl" )

X = []
Y = []

for i in range( len(scaled) - SEQUENCE_LENGTH ):
    X.append( scaled [i:i+SEQUENCE_LENGTH] )
    Y.append( scaled [i+SEQUENCE_LENGTH]   )

X = np.array(X)
Y = np.array(Y)
split = int( len(X) * 0.8 )

X_train = X[:split]
X_test = X[split:]

Y_train = Y[:split]
Y_test = Y[split:]

np.savez(
    "ml/processed_data.npz",
    X_train=X_train,
    X_test=X_test,
    Y_train=Y_train,
    Y_test=Y_test
)

print("Done!")

print(X_train.shape)
print(Y_train.shape)