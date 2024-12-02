from unittest.mock import Mock
import pytest
from counter.domain.actions import CountDetectedObjects
from counter.domain.models import ObjectCount
from tests.domain.helpers import generate_prediction
import logging

logger = logging.getLogger("TestLogger")

'''
In test_update_count_object_repo, instead of just checking if count_object_repo.update_values was called, validation of the exact arguments passed
has been tested.
This
	•	Improves confidence that the repository is called with the correct data.
	•	Ensures tighter integration between the domain and persistence layers.
'''

class TestCountDetectedObjects:
    @pytest.fixture
    def object_detector(self) -> Mock:
        object_detector = Mock()
        object_detector.predict.return_value = [
            generate_prediction('cat', 0.9),
            generate_prediction('cat', 0.8),
            generate_prediction('dog', 0.8),
            generate_prediction('dog', 0.1),
            generate_prediction('rabbit', 0.9),
        ]
        return object_detector

    @pytest.fixture
    def count_object_repo(self) -> Mock:
        return Mock()

    def test_count_valid_predictions(self, object_detector, count_object_repo) -> None:
        logger.info("Testing count of valid predictions")
        response = CountDetectedObjects(object_detector, count_object_repo).execute(None, 0.5)
        logger.debug(f"Response: {response}")
        assert sorted(response.current_objects, key=lambda x: x.object_class) == [
            ObjectCount('cat', 2), ObjectCount('dog', 1), ObjectCount('rabbit', 1)
        ]

    def test_update_count_object_repo(self, object_detector, count_object_repo):
        logger.info("Testing repository update")
        CountDetectedObjects(object_detector, count_object_repo).execute(None, 0)
        count_object_repo.update_values.assert_called_once_with(
            [ObjectCount('cat', 2), ObjectCount('dog', 2), ObjectCount('rabbit', 1)]
        )

    def test_repository_failure(self, object_detector, count_object_repo):
        logger.info("Testing repository failure scenario")
        count_object_repo.update_values.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            CountDetectedObjects(object_detector, count_object_repo).execute(None, 0)