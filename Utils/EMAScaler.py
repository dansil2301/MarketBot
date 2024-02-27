import pandas as pd
import numpy as np


class EMAScaler:
    def __init__(self, span):
        self.span = span
        self.ema_values = None

    def fit(self, data):
        # Compute initial EMA values using the provided data
        self.ema_values = data.ewm(span=self.span).mean()

    def transform(self, data):
        # Scale the data using the current EMA values
        ema_scaled_data = pd.DataFrame()
        for column in data.columns:
            ema = self.ema_values[column]
            ema_scaled_data[column] = data[column] / ema
        return ema_scaled_data

    def update_ema(self, new_data):
        # Compute the EMA values for the new data point using the existing EMA values
        new_ema_values = (2 / (self.span + 1)) * new_data + (1 - 2 / (self.span + 1)) * self.ema_values.iloc[-1]

        # Update the existing EMA values with the newly computed EMA values
        self.ema_values = new_ema_values