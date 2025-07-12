import pytest
import pytest_asyncio # Not strictly needed for @pytest.mark.asyncio but good for consistency
import httpx
import os
from unittest.mock import AsyncMock, patch, MagicMock # Import MagicMock

# Import the function to test
from backend.app.services.weather_service import get_weather_data, WEATHER_API_URL

# Fixture for mocking httpx.AsyncClient
@pytest_asyncio.fixture
async def mock_async_client():
    mock = AsyncMock(spec=httpx.AsyncClient)
    # Ensure the context manager protocol is mocked
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    return mock

@pytest.mark.asyncio
async def test_get_weather_data_success_with_api_key(mock_async_client):
    # Mock the response from the API
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"main": {"temp": 15.0}, "weather": [{"main": "Clear"}]}

    # Configure the client's get method to return our mock response
    mock_async_client.get.return_value = mock_response

    # Patch the module-level variable OPENWEATHERMAP_API_KEY within the weather_service module
    with patch('backend.app.services.weather_service.OPENWEATHERMAP_API_KEY', "test_key"):
        with patch('backend.app.services.weather_service.httpx.AsyncClient', return_value=mock_async_client):
            result = await get_weather_data(latitude=10.0, longitude=10.0)

    assert result == {"temperature_celsius": 15.0, "condition": "Clear"}
    expected_url = f"{WEATHER_API_URL}"
    mock_async_client.get.assert_called_once()
    call_args = mock_async_client.get.call_args
    assert call_args[0][0] == expected_url
    assert call_args[1]['params'] == {
        "lat": 10.0,
        "lon": 10.0,
        "appid": "test_key",
        "units": "metric"
    }

@pytest.mark.asyncio
async def test_get_weather_data_success_mocked_response_no_api_key(mock_async_client):
    # Ensure no API key is set for this test
    with patch.dict(os.environ, {}, clear=True):
      # Patch httpx.AsyncClient just to ensure it's not unexpectedly called
      with patch('backend.app.services.weather_service.httpx.AsyncClient', return_value=mock_async_client) as patched_http_client:
        # Test with coordinates that trigger a specific mock in weather_service.py
        result_cold = await get_weather_data(latitude=10.0, longitude=10.0)
        assert result_cold == {"temperature_celsius": 5.0, "condition": "Snow"}

        result_rain = await get_weather_data(latitude=20.0, longitude=20.0)
        assert result_rain == {"temperature_celsius": 15.0, "condition": "Rain"}

        result_clear = await get_weather_data(latitude=0.0, longitude=0.0)
        assert result_clear == {"temperature_celsius": 25.0, "condition": "Clear"}

        result_generic = await get_weather_data(latitude=5.0, longitude=5.0) # Different coords
        assert result_generic == {"temperature_celsius": 22.0, "condition": "Clear"}

        # Assert that the actual HTTP client was NOT called because API key is missing
        patched_http_client.assert_not_called()


@pytest.mark.asyncio
async def test_get_weather_data_api_http_status_error(mock_async_client):
    mock_response = AsyncMock(spec=httpx.Response) # This is the response object from client.get()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    # httpx.Response.raise_for_status() is a synchronous method.
    # It needs to be a MagicMock if we are mocking it on an AsyncMock response.
    # However, the actual response object returned by httpx.AsyncClient().get() is a real httpx.Response.
    # So, we need to ensure the mocked response object behaves like a real one.
    # Let's make the whole mock_response a MagicMock if we control its methods like raise_for_status.
    # Or, more simply, ensure the side_effect is raised by the *call* to raise_for_status.

    mock_httpx_request_obj = MagicMock(spec=httpx.Request) # Mock for the request object
    mock_httpx_response_obj = MagicMock(spec=httpx.Response) # Mock for the response object in HTTPStatusError
    mock_httpx_response_obj.status_code = 500
    mock_httpx_response_obj.text = "Internal Server Error"

    # Configure the mock_response that client.get() returns
    mock_response_from_get = AsyncMock(spec=httpx.Response)
    mock_response_from_get.status_code = 500 # Keep status code for any checks before raise_for_status
    mock_response_from_get.text = "Internal Server Error"
    mock_response_from_get.raise_for_status = MagicMock( # raise_for_status is synchronous
        side_effect=httpx.HTTPStatusError(
            "Simulated API error",
            request=mock_httpx_request_obj,
            response=mock_httpx_response_obj
        )
    )

    mock_async_client.get.return_value = mock_response_from_get

    with patch('backend.app.services.weather_service.OPENWEATHERMAP_API_KEY', "test_key"):
        with patch('backend.app.services.weather_service.httpx.AsyncClient', return_value=mock_async_client):
            result = await get_weather_data(latitude=10.0, longitude=10.0)

    assert result is None
    mock_async_client.get.assert_called_once() # Ensure API was called
    mock_response_from_get.raise_for_status.assert_called_once() # Ensure it was called

@pytest.mark.asyncio
async def test_get_weather_data_network_error(mock_async_client):
    mock_httpx_request_obj = MagicMock(spec=httpx.Request) # Mock for the request object
    mock_async_client.get.side_effect = httpx.RequestError("Simulated network error", request=mock_httpx_request_obj)

    with patch('backend.app.services.weather_service.OPENWEATHERMAP_API_KEY', "test_key"):
        with patch('backend.app.services.weather_service.httpx.AsyncClient', return_value=mock_async_client):
            result = await get_weather_data(latitude=10.0, longitude=10.0)

    assert result is None
    mock_async_client.get.assert_called_once() # Ensure API was called

@pytest.mark.asyncio
async def test_get_weather_data_json_decode_error(mock_async_client):
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.side_effect = Exception("JSON Decode Error") # Or more specific like json.JSONDecodeError

    mock_async_client.get.return_value = mock_response

    with patch('backend.app.services.weather_service.OPENWEATHERMAP_API_KEY', "test_key"):
        with patch('backend.app.services.weather_service.httpx.AsyncClient', return_value=mock_async_client):
            result = await get_weather_data(latitude=10.0, longitude=10.0)

    assert result is None # Or however your service handles JSON errors
    mock_async_client.get.assert_called_once()
    mock_response.json.assert_called_once()
