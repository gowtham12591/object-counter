import io
import json
import pytest
from pathlib import Path
from PIL import Image
import tempfile

from counter.entrypoints.webapp import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def temp_image():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        image = Image.new('RGB', (100, 100), color=(255, 0, 0))
        image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)
        yield tmp_file.name
        tmp_file.close()
        Path(tmp_file.name).unlink()  # Cleanup

'''
More assertions done
This
	•	Ensures the API response contains the correct structure and keys, not just a 200 status.
	•	Validates business logic more effectively by testing data integrity.
'''
def test_object_detection(client, temp_image):
    with open(temp_image, 'rb') as f:
        image_data = f.read()
    image = io.BytesIO(image_data)

    data = {
        'threshold': '0.9',
        'model_name': 'rfcn',
    }
    data['file'] = (image, 'test.jpg')

    response = client.post('/api/v1/object-detect-count', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'current_objects' in response_data
    assert len(response_data['current_objects']) > 0  # Check that objects are detected

'''
Addition of negative tests
	•	An invalid threshold is provided (e.g., string instead of float).
This
	•	Validates error handling in edge cases.
	•	Improves application robustness by ensuring predictable behavior during failures.

'''

def test_invalid_threshold(client, temp_image):
    with open(temp_image, 'rb') as f:
        image_data = f.read()
    image = io.BytesIO(image_data)

    data = {
        'threshold': 'invalid_value',  # Invalid threshold
        'file': (image, 'test.jpg'),
    }

    response = client.post('/api/v1/object-detect-count', data=data, content_type='multipart/form-data')

    assert response.status_code == 400  # Expect a Bad Request error