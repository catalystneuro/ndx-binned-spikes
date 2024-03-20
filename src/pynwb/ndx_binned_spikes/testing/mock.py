from typing import Optional

from ndx_binned_spikes import BinnedAlignedSpikes
import numpy as np


def mock_BinnedAlignedSpikes(
    number_of_units: int = 2,
    number_of_event_repetitions: int = 4,
    number_of_bins: int = 3,
    bin_width_in_milliseconds: float = 20.0,
    milliseconds_from_event_to_first_bin: float = 1.0,
    seed: int = 0,
    event_timestamps: Optional[np.ndarray] = None,
    data: Optional[np.ndarray] = None,
) -> "BinnedAlignedSpikes":
    """
    Generate a mock BinnedAlignedSpikes object with specified parameters or from given data.

    Parameters
    ----------
    number_of_units : int, optional
        The number of different units (channels, neurons, etc.) to simulate.
    number_of_event_repetitions : int, optional
        The number of times an event is repeated.
    number_of_bins : int, optional
        The number of bins.
    bin_width_in_milliseconds : float, optional
        The width of each bin in milliseconds.
    milliseconds_from_event_to_first_bin : float, optional
        The time in milliseconds from the event start to the first bin.
    seed : int, optional
        Seed for the random number generator to ensure reproducibility.
    event_timestamps : np.ndarray, optional
        An array of timestamps for each event. If not provided, it will be automatically generated.
        It should have size `number_of_event_repetitions`.
    data : np.ndarray, optional
        A 3D array of shape (number_of_units, number_of_event_repetitions, number_of_bins) representing
        the binned spike data. If provided, it overrides the generation of mock data based on other parameters.
        Its shape should match the expected number of units, event repetitions, and bins.

    Returns
    -------
    BinnedAlignedSpikes
        A mock BinnedAlignedSpikes object populated with the provided or generated data and parameters.

    Raises
    ------
    AssertionError
        If `event_timestamps` is provided and its shape does not match the expected number of event repetitions.

    Notes
    -----
    This function simulates a BinnedAlignedSpikes object, which is typically used for neural data analysis,
    representing binned spike counts aligned to specific events.

    Examples
    --------
    >>> mock_bas = mock_BinnedAlignedSpikes()
    >>> print(mock_bas.data.shape)
    (2, 4, 3)
    """

    if data is not None:
        number_of_units, number_of_event_repetitions, number_of_bins = data.shape
    else:
        rng = np.random.default_rng(seed=seed)
        data = rng.integers(low=0, high=100, size=(number_of_units, number_of_event_repetitions, number_of_bins))

    if event_timestamps is None:
        event_timestamps = np.arange(number_of_event_repetitions, dtype="float64")
    else:
        assert (
            event_timestamps.shape[0] == number_of_event_repetitions
        ), "The shape of `event_timestamps` does not match `number_of_event_repetitions`."
        event_timestamps = np.array(event_timestamps, dtype="float64")

    if event_timestamps.shape[0] != data.shape[1]:
        raise ValueError("The shape of `event_timestamps` does not match `number_of_event_repetitions`.")

    binned_aligned_spikes = BinnedAlignedSpikes(
        bin_width_in_milliseconds=bin_width_in_milliseconds,
        milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin,
        data=data,
        event_timestamps=event_timestamps,
    )
    return binned_aligned_spikes
