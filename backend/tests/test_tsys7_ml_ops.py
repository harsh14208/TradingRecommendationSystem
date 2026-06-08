from services.signal_ml import validate_feature_schema


def test_validate_feature_schema():
    expected = ["feat1", "feat2", "feat3"]

    # Valid
    assert validate_feature_schema([1.0, 2, 3.5], expected) is True
    assert validate_feature_schema([1.0, None, 3.5], expected) is True

    # Invalid length
    assert validate_feature_schema([1.0, 2], expected) is False

    # Type shift (string instead of numeric)
    assert validate_feature_schema([1.0, "wrong", 3.5], expected) is False

    # Type shift (dict instead of numeric)
    assert validate_feature_schema([1.0, {"val": 2}, 3.5], expected) is False
