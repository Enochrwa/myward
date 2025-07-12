import pytest
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import os # For creating a dummy image file
from unittest.mock import patch, MagicMock # For mocking
from datetime import datetime # For mock_current_user

# Adjust import path as per your project structure
# Assuming the tests directory is at backend/app/tests/
# and services are in backend/app/services/
from ..services.ai_services import analyze_outfit_image_service, get_fashion_trends_service
from ..tables import OutfitAnalysisResponse, TrendForecastResponse, User as UserSchema # Assuming User schema for context

# Helper to create a dummy image file for testing uploads
def create_dummy_image_bytes(filename="test.jpg", size=(100,100), format="JPEG") -> io.BytesIO:
    image = Image.new('RGB', size, color = 'red')
    byte_io = io.BytesIO()
    image.save(byte_io, format=format)
    byte_io.seek(0)
    return byte_io

@pytest.fixture
def mock_db_session():
    # Mock the DB session if needed by the service, though ai_services might not use it heavily for writes.
    return MagicMock()

@pytest.fixture
def mock_current_user():
    # Create a mock user object (Pydantic schema)
    # Ensure all required fields for UserSchema are provided.
    # Based on typical User models, email_verified and is_active might be needed.
    return UserSchema(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="fake_hash", # Add if UserSchema requires it
        is_active=True,             # Add if UserSchema requires it
        email_verified=True,        # Add if UserSchema requires it
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

# --- Tests for analyze_outfit_image_service ---

@pytest.mark.asyncio
@patch('backend.app.services.ai_services.extract_image_embedding')
@patch('backend.app.services.ai_services.extract_colors')
@patch('backend.app.services.ai_services.detect_style')
@patch('backend.app.services.ai_services.identify_items')
async def test_analyze_outfit_image_service_success(
    mock_identify_items_func, # Order of args should match @patch decorators, bottom-up
    mock_detect_style_func,
    mock_extract_colors_func,
    mock_extract_embedding_func,
    mock_db_session, # Fixtures come after mocks
    mock_current_user
):
    # Mock the return values of the individual AI functions
    mock_extract_embedding_func.return_value = [0.1] * 768 # Typical ViT base embedding size from HuggingFace
    mock_extract_colors_func.return_value = ["#FF0000", "#00FF00"]
    mock_detect_style_func.return_value = "Mocked Style (Caption)"
    mock_identify_items_func.return_value = ["Mocked T-Shirt", "Mocked Jeans"]

    # Create a dummy UploadFile
    dummy_image_bytes = create_dummy_image_bytes()
    # When creating UploadFile for testing, ensure the 'file' attribute is a SpooledTemporaryFile or BytesIO
    upload_file = UploadFile(filename="test.jpg", file=dummy_image_bytes, content_type="image/jpeg")

    result = await analyze_outfit_image_service(file=upload_file, db=mock_db_session, user=mock_current_user)

    assert isinstance(result, OutfitAnalysisResponse)
    assert result.fileName == "test.jpg"
    assert result.dominantColors == ["#FF0000", "#00FF00"]
    assert result.style == "Mocked Style (Caption)"
    assert result.identifiedItems == ["Mocked T-Shirt", "Mocked Jeans"]
    # Check that confidenceScore is present and a float (actual value depends on impl)
    assert isinstance(result.confidenceScore, float) and result.confidenceScore >= 0 and result.confidenceScore <=1
    assert len(result.recommendations) > 0 # Some generic recommendations expected

    # Check that mocks were called (with any PIL.Image object)
    mock_extract_embedding_func.assert_called_once()
    # Example of checking the type of the argument passed to the mock:
    # mock_extract_embedding_func.assert_called_once_with(unittest.mock.ANY) # or specifically with an Image object
    # For more specific checks:
    # assert isinstance(mock_extract_embedding_func.call_args[0][0], Image.Image)

    mock_extract_colors_func.assert_called_once()
    mock_detect_style_func.assert_called_once()
    mock_identify_items_func.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_outfit_image_service_invalid_file_type(mock_db_session, mock_current_user):
    dummy_text_bytes = io.BytesIO(b"this is not an image")
    upload_file = UploadFile(filename="test.txt", file=dummy_text_bytes, content_type="text/plain")

    with pytest.raises(HTTPException) as exc_info:
        await analyze_outfit_image_service(file=upload_file, db=mock_db_session, user=mock_current_user)

    assert exc_info.value.status_code == 400
    # The specific error message comes from Image.open(..).convert("RGB") in the service
    assert "Invalid image file" in exc_info.value.detail


# (Add more tests for analyze_outfit_image_service: e.g. model load failures if not mocked, specific image issues)
# For example, if one of the mocked functions returns None or raises an error:

@pytest.mark.asyncio
@patch('backend.app.services.ai_services.extract_image_embedding', MagicMock(return_value=[0.1]*768))
@patch('backend.app.services.ai_services.extract_colors', MagicMock(return_value=["#111111"]))
@patch('backend.app.services.ai_services.detect_style', MagicMock(return_value="Error in style detection")) # Simulate error string
@patch('backend.app.services.ai_services.identify_items', MagicMock(return_value=["Error in item identification"])) # Simulate error string
async def test_analyze_outfit_image_service_with_internal_ai_errors(
    mock_db_session,
    mock_current_user
):
    dummy_image_bytes = create_dummy_image_bytes()
    upload_file = UploadFile(filename="test_error.jpg", file=dummy_image_bytes, content_type="image/jpeg")

    result = await analyze_outfit_image_service(file=upload_file, db=mock_db_session, user=mock_current_user)

    assert isinstance(result, OutfitAnalysisResponse)
    assert result.style == "Error in style detection"
    assert result.identifiedItems == ["Error in item identification"]
    # Check other fields are present with default/fallback values
    assert result.dominantColors == ["#111111"]


# --- Tests for get_fashion_trends_service ---
# This service uses mock data, so the test just checks if it returns the expected structure.
@pytest.mark.asyncio
async def test_get_fashion_trends_service(mock_db_session, mock_current_user):
    result = await get_fashion_trends_service(db=mock_db_session, user=mock_current_user)

    assert isinstance(result, TrendForecastResponse)
    assert len(result.trends) > 0
    # Example check based on current mock data in get_fashion_trends_service
    assert result.trends[0].name == 'Neo-Cottagecore AI'
    assert result.personalizedRecommendations is not None
    assert result.seasonalPredictions is not None

# Note: To run these tests, you'd typically use `pytest` in your terminal.
# Ensure that `pytest` and `pytest-asyncio` are in your requirements-dev.txt or similar.
# The global model loading in ai_services.py will run when tests are collected by pytest.
# For pure unit tests that must avoid any model download/load attempts during test collection,
# you might need to patch the from_pretrained/pipeline calls directly at the top of your test file or in a conftest.py
# e.g., @patch('transformers.ViTFeatureExtractor.from_pretrained', MagicMock())
# However, the current approach of mocking the wrapper functions (extract_colors etc.) is usually sufficient
# if model loading itself isn't excessively slow or problematic during test setup.
# The provided tests mock the functions that *use* the models, not the model loading itself.
# If ai_services.py has top-level `XYZModel.from_pretrained()` calls, those *will* execute.
# The task asks to focus on mocking external *model calls*, which usually means their *inference methods*.
# The current mocks on extract_X functions achieve this for the service logic.
```
