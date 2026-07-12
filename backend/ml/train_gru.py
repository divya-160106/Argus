import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.callbacks import ( EarlyStopping, ModelCheckpoint, ReduceLROnPlateau )
from config import FEATURE_COLUMNS
import pandas as pd

print("Loading processed data...")

data = np.load("ml/processed_data.npz")

X_train = data["X_train"]
X_test = data["X_test"]

Y_train = data["Y_train"]
Y_test = data["Y_test"]

print(X_train.shape)
print(Y_train.shape)

model = Sequential([ GRU( 128, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2]) ),
    Dropout(0.2),
    GRU(64),
    Dropout(0.2),
    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense( len(FEATURE_COLUMNS), activation="linear" )
])

model.compile( optimizer="adam", loss="mse", metrics=["mae"] )

callbacks = [ EarlyStopping( monitor="val_loss", patience=8, restore_best_weights=True ),
    ReduceLROnPlateau( monitor="val_loss", factor=0.5, patience=4 ),
    ModelCheckpoint( "ml/warehouse_gru.keras", save_best_only=True )
]

history = model.fit(
    X_train,
    Y_train,
    validation_data=(X_test, Y_test),
    epochs=50,
    batch_size=32,
    callbacks=callbacks
)

history_df = pd.DataFrame(history.history)
history_df.to_csv("ml/training_history.csv", index=False) 

loss, mae = model.evaluate( X_test, Y_test )
print()
print("Test Loss :", loss)
print("Test MAE :", mae)