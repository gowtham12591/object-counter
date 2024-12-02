from counter.domain.models import ObjectCount
from counter.domain.predictions import over_threshold, count
from tests.domain.helpers import generate_prediction
import pytest

# pytest.mark.parametrize to make your tests more concise and cover multiple scenarios without duplicating code.
# Makes it easier to add new cases.
@pytest.mark.parametrize("predictions, threshold, expected", [
    ([generate_prediction('dog', 0.9), generate_prediction('cat', 0.8)], 0.9, [generate_prediction('dog', 0.9)]),
    ([generate_prediction('cat', 0.91), generate_prediction('cat', 0.8)], 0.85, [generate_prediction('cat', 0.91)]),
])
def test_filter_predictions_over_threshold(predictions, threshold, expected) -> None:
    assert list(over_threshold(predictions, threshold)) == expected


def test_count_predictions_by_class() -> None:
    predictions = [
        generate_prediction('cat'),
        generate_prediction('cat'),
        generate_prediction('dog'),
    ]
    object_counts = count(predictions)
    assert sorted(object_counts, key=lambda x: x.object_class) == [
        ObjectCount(object_class='cat', count=2), ObjectCount(object_class='dog', count=1)
    ]