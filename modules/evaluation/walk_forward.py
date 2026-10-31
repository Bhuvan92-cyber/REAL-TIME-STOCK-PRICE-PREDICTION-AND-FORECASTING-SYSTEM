from __future__ import annotations

import numpy as np

from modules.evaluation.forecast_metrics import evaluate_forecast


def chronological_split(values, train_ratio=0.6, validation_ratio=0.2):
    data = np.asarray(values)
    if data.ndim != 1 or len(data) < 10:
        raise ValueError("At least 10 ordered observations are required")
    train_end = int(len(data) * train_ratio)
    validation_end = train_end + int(len(data) * validation_ratio)
    if train_end < 2 or validation_end >= len(data):
        raise ValueError("Split ratios must leave non-empty train, validation, and test sets")
    return data[:train_end], data[train_end:validation_end], data[validation_end:]


def walk_forward_forecast(model_factory, values, initial_train_size, horizon=1, step=1):
    data = np.asarray(values, dtype=float)
    if initial_train_size < 2 or initial_train_size + horizon > len(data):
        raise ValueError("Invalid walk-forward window")
    actual, predicted = [], []
    for end in range(initial_train_size, len(data) - horizon + 1, step):
        model = model_factory()
        train = data[:end]
        model.train(train[:-horizon], train[horizon:])
        output = np.asarray(model.predict(data[end - 1:end].reshape(1, -1)), dtype=float).reshape(-1)
        actual.append(data[end])
        predicted.append(output[0])
    return np.asarray(actual), np.asarray(predicted), evaluate_forecast(actual, predicted)


def walk_forward_regression(model_factory, X, y, initial_train_size, step=1):
    """Refit a feature model only on rows available before each test row."""
    features = np.asarray(X)
    target = np.asarray(y, dtype=float)
    if len(features) != len(target) or initial_train_size < 2:
        raise ValueError("X and y must have equal length and a valid initial window")
    actual, predicted = [], []
    for end in range(initial_train_size, len(target), step):
        model = model_factory()
        model.train(features[:end], target[:end])
        predicted.append(float(np.asarray(model.predict(features[end:end + 1])).reshape(-1)[0]))
        actual.append(float(target[end]))
    return np.asarray(actual), np.asarray(predicted), evaluate_forecast(actual, predicted)
