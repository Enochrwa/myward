=# import pytest
# import pytest_asyncio # Not strictly needed for @pytest.mark.asyncio but good for consistency
# import httpx
# from fastapi import HTTPException
# from unittest.mock import AsyncMock, patch, MagicMock # Import MagicMock

# # Import the function to test
# from ..services.weather_service import get_weather_data, WEATHER_API_URL

# # Fixture for mocking httpx.AsyncClient
# @pytest_asyncio.fixture
# def mock_async_client():
#     mock = AsyncMock(spec=httpx.AsyncClient)
#     # Mock the response object
#     mock_response = MagicMock(spec=httpx.Response)
#     mock_response.status_code = 200
#     # The .json() method should be a regular callable, not async
#     mock_response.json.return_value = {
#         "coord": {"lon": -0.1257, "lat": 51.5085},
#         "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
#         "main": {"temp": 15.0, "feels_like": 14.5, "temp_min": 13.0, "temp_max": 17.0, "pressure": 1012, "humidity": 72},
#         "name": "London",
#     }
    
#     # Configure the mock client's get method to be an async function returning the mock response
#     mock.get = AsyncMock(return_value=mock_response)
    
#     # Make the mock usable in an 'async with' block
#     mock.__aenter__.return_value = mock
#     mock.__aexit__.return_value = None
    
#     return mock

# # --- Tests for get_weather_data ---

# @pytest.mark.asyncio
# @patch('httpx.AsyncClient') # Patch the AsyncClient where it's used
# async def test_get_weather_data_success(mock_async_client_constructor, mock_async_client):
#     # Configure the constructor to return our specific mock instance
#     mock_async_client_constructor.return_value = mock_async_client

#     location = "London"
#     result = await get_weather_data(location)

#     # Assertions
#     assert result is not None
#     assert result["name"] == "London"
#     assert "main" in result
#     assert result["main"]["temp"] == 15.0
    
#     # Verify that the mock was called correctly
#     expected_url = f"{WEATHER_API_URL}?q={location}&appid=test_api_key&units=metric"
#     mock_async_client.get.assert_called_once_with(expected_url)

# @pytest.mark.asyncio
# @patch('httpx.AsyncClient')
# async def test_get_weather_data_api_error(mock_async_client_constructor, mock_async_client):
#     # Simulate an API error (e.g., 404 Not Found)
#     mock_response = MagicMock(spec=httpx.Response)
#     mock_response.status_code = 404
#     mock_response.json.return_value = {"message": "city not found"}
#     # Make raise_for_status raise an exception
#     mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
#         "404 Client Error: Not Found for url...",
#         request=MagicMock(),
#         response=mock_response
#     ))
    
#     mock_async_client.get.return_value = mock_response
#     mock_async_client_constructor.return_value = mock_async_client

#     with pytest.raises(HTTPException) as exc_info:
#         await get_weather_data("UnknownCity")

#     assert exc_info.value.status_code == 503 # Service unavailable
#     assert "Could not fetch weather data" in exc_info.value.detail

# @pytest.mark.asyncio
# @patch('httpx.AsyncClient')
# async def test_get_weather_data_request_exception(mock_async_client_constructor, mock_async_client):
#     # Simulate a network error
#     mock_async_client.get.side_effect = httpx.RequestError("Network error", request=MagicMock())
#     mock_async_client_constructor.return_value = mock_async_client

#     with pytest.raises(HTTPException) as exc_info:
#         await get_weather_data("London")

#     assert exc_info.value.status_code == 503
#     assert "Could not fetch weather data" in exc_info.value.detail

# @pytest.mark.asyncio
# @patch('your_module_path.settings', MagicMock(WEATHER_API_KEY=None)) # Patch settings directly
# async def test_get_weather_data_no_api_key():
#     with pytest.raises(HTTPException) as exc_info:
#         await get_weather_data("London")

#     assert exc_info.value.status_code == 500
#     assert "Weather API key not configured" in exc_info.value.detail

# # Note: Remember to replace 'your_module_path' with the actual path to your settings object
# # if you implement the no_api_key test. For example, if settings is in `backend.app.config`,
# # the path would be 'backend.app.config.settings'.
# # Given the current structure, this might be tricky if `settings` is imported dynamically.
# # A more robust way is to use dependency injection for settings if it becomes complex.
