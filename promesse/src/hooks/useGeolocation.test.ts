import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import useGeolocation from './useGeolocation'; // Assuming useGeolocation.ts is in the same dir or adjust path

describe('useGeolocation hook', () => {
  const mockGeolocation = {
    getCurrentPosition: vi.fn(),
    watchPosition: vi.fn(),
    clearWatch: vi.fn(),
  };

  beforeEach(() => {
    // Stub global navigator.geolocation with our mock
    vi.stubGlobal('navigator', {
        ...global.navigator, // Keep other navigator properties
        geolocation: mockGeolocation
    });
  });

  afterEach(() => {
    // Clear mocks and restore original navigator object if necessary
    vi.unstubAllGlobals();
    mockGeolocation.getCurrentPosition.mockReset();
  });

  it('test_initial_state', () => {
    const { result } = renderHook(() => useGeolocation());

    expect(result.current.coordinates).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it('test_get_location_success', () => {
    const mockPosition = {
      coords: {
        latitude: 50,
        longitude: 10,
        accuracy: 10,
        altitude: null,
        altitudeAccuracy: null,
        heading: null,
        speed: null,
      },
      timestamp: Date.now(),
    };

    mockGeolocation.getCurrentPosition.mockImplementationOnce((successCallback) => {
      successCallback(mockPosition);
    });

    const { result } = renderHook(() => useGeolocation());

    act(() => {
      result.current.getLocation();
    });

    // Vitest doesn't automatically advance timers or handle async state updates in the same way Jest might with RTL's waitFor.
    // For this hook, isLoading is set to true then immediately to false upon callback execution.
    // If there were truly async operations within the hook not tied to geolocation callbacks,
    // you might need @testing-library/react's waitFor or similar.

    expect(result.current.isLoading).toBe(false); // Should be false after success callback
    expect(result.current.coordinates).toEqual({ lat: 50, lon: 10 });
    expect(result.current.error).toBeNull();
    expect(mockGeolocation.getCurrentPosition).toHaveBeenCalledTimes(1);
  });

  it('test_get_location_error_permission_denied', () => {
    const mockError = {
      code: 1, // PERMISSION_DENIED
      message: 'User denied geolocation prompt',
    };

    mockGeolocation.getCurrentPosition.mockImplementationOnce((_, errorCallback) => {
      if (errorCallback) errorCallback(mockError as GeolocationPositionError);
    });

    const { result } = renderHook(() => useGeolocation());

    act(() => {
      result.current.getLocation();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Specific: Permission Denied'); // Updated expected message
    expect(result.current.coordinates).toBeNull();
    expect(mockGeolocation.getCurrentPosition).toHaveBeenCalledTimes(1);
  });

  it('test_get_location_error_position_unavailable', () => {
    const mockError = {
      code: 2, // POSITION_UNAVAILABLE
      message: 'Location information is unavailable.', // This message will be part of "Default: ..." if switch fails
    };
    mockGeolocation.getCurrentPosition.mockImplementationOnce((_, errorCallback) => {
      if (errorCallback) errorCallback(mockError as GeolocationPositionError);
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => { result.current.getLocation(); });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Specific: Position Unavailable'); // Updated expected message
    expect(result.current.coordinates).toBeNull();
  });

  it('test_get_location_error_timeout', () => {
    const mockError = {
      code: 3, // TIMEOUT
      message: 'The request to get user location timed out.', // This message will be part of "Default: ..." if switch fails
    };
    mockGeolocation.getCurrentPosition.mockImplementationOnce((_, errorCallback) => {
      if (errorCallback) errorCallback(mockError as GeolocationPositionError);
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => { result.current.getLocation(); });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Specific: Timeout'); // Updated expected message
    expect(result.current.coordinates).toBeNull();
  });

  it('test_geolocation_not_supported', () => {
    vi.stubGlobal('navigator', { geolocation: undefined }); // Simulate no geolocation support

    const { result } = renderHook(() => useGeolocation());
    act(() => { result.current.getLocation(); });

    expect(result.current.error).toBe('Geolocation is not supported by your browser.');
    expect(result.current.coordinates).toBeNull();
    expect(result.current.isLoading).toBe(false);
    // getCurrentPosition should not be called if navigator.geolocation is undefined
    expect(mockGeolocation.getCurrentPosition).not.toHaveBeenCalled();
  });
});
