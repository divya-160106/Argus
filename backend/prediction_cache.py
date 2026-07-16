_predictions = None

def get_predictions():
    return _predictions

def set_predictions(data):
    global _predictions
    _predictions = data