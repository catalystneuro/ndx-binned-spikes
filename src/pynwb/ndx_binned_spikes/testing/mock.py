from typing import Optional

from ndx_binned_spikes import BinnedAlignedSpikes, AggregatedBinnedAlignedSpikes
import numpy as np
from pynwb import NWBFile
from pynwb.misc import Units
from hdmf.common import DynamicTableRegion


def mock_BinnedAlignedSpikes(
    number_of_units: int = 2,
    number_of_events: int = 4,
    number_of_bins: int = 3,
    bin_width_in_milliseconds: float = 20.0,
    milliseconds_from_event_to_first_bin: float = 1.0,
    seed: int = 0,
    event_timestamps: Optional[np.ndarray] = None,
    data: Optional[np.ndarray] = None,
    units_region: Optional[DynamicTableRegion] = None,
) -> "BinnedAlignedSpikes":
    """
    Generate a mock BinnedAlignedSpikes object with specified parameters or from given data.

    Parameters
    ----------
    number_of_units : int, optional
        The number of different units (channels, neurons, etc.) to simulate.
    number_of_events : int, optional
        The number of timestamps of the event that the data is aligned to.
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
        It should have size `number_of_events`.
    data : np.ndarray, optional
        A 3D array of shape (number_of_units, number_of_events, number_of_bins) representing
        the binned spike data. If provided, it overrides the generation of mock data based on other parameters.
        Its shape should match the expected number of units, event repetitions, and bins.
    units_region: DynamicTableRegion, optional
        A reference to the Units table region that contains the units of the data.

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
        number_of_units, number_of_events, number_of_bins = data.shape
    else:
        rng = np.random.default_rng(seed=seed)
        data = rng.integers(low=0, high=100, size=(number_of_units, number_of_events, number_of_bins))

    if event_timestamps is None:
        event_timestamps = np.arange(number_of_events, dtype="float64")
    else:
        assert (
            event_timestamps.shape[0] == number_of_events
        ), "The shape of `event_timestamps` does not match `number_of_events`."
        event_timestamps = np.array(event_timestamps, dtype="float64")

    if event_timestamps.shape[0] != data.shape[1]:
        raise ValueError("The shape of `event_timestamps` does not match `number_of_events`.")

    binned_aligned_spikes = BinnedAlignedSpikes(
        bin_width_in_milliseconds=bin_width_in_milliseconds,
        milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin,
        data=data,
        event_timestamps=event_timestamps,
        units_region=units_region,
    )
    return binned_aligned_spikes


# TODO: Remove once pynwb 2.7.0 is released and use the mock class there
def mock_Units(
    num_units: int = 10,
    max_spikes_per_unit: int = 10,
    seed: int = 0,
    nwbfile: Optional[NWBFile] = None,
) -> Units:

    units_table = Units(name="units")  # This is for nwbfile.units= mock_Units() to work
    units_table.add_column(name="unit_name", description="a readable identifier for the unit")

    rng = np.random.default_rng(seed=seed)

    times = rng.random(size=(num_units, max_spikes_per_unit)).cumsum(axis=1)
    spikes_per_unit = rng.integers(1, max_spikes_per_unit, size=num_units)

    spike_times = []
    for unit_index in range(num_units):

        # Not all units have the same number of spikes
        spike_times = times[unit_index, : spikes_per_unit[unit_index]]
        unit_name = f"unit_{unit_index}"
        units_table.add_unit(spike_times=spike_times, unit_name=unit_name)

    if nwbfile is not None:
        nwbfile.units = units_table

    return units_table


"""
Ok, so for the first structure what we can align to:
- A specific stimulus (the event here is every time the stimulus occurs)
- A column of the trials table (e.g. ). The event here is every trial
- A time column of any dynamic table.
- Add event from ndx-events

When do we need to aggregate?
Stimulus, because not all stimulus happen the same number of times. 
What else is inhomogeneous in this way? A column of the trials table
"""


def mock_AggregatedBinnedAlignedSpikes(
    number_of_units: int = 2,
    number_of_bins: int = 3,
    aggregated_events_counts: int = 5,
    number_of_events: int = 2,
    bin_width_in_milliseconds: float = 20.0,
    milliseconds_from_event_to_first_bin: float = 1.0,
    seed: int = 0,
    event_indices: Optional[np.ndarray] = None,
    timestamps: Optional[np.ndarray] = None,
    data: Optional[np.ndarray] = None,
    units_region: Optional[DynamicTableRegion] = None,
) -> "AggregatedBinnedAlignedSpikes":
    """
    Generate a mock AggregatedBinnedAlignedSpikes object with specified parameters or from given data.

    Parameters
    ----------
    number_of_units : int, optional
        The number of different units (channels, neurons, etc.) to simulate.
    number_of_events : int, optional
        The number of timestamps of the event that the data is aligned to.
    number_of_bins : int, optional
        The number of bins.
    number_of_different_events : int, optional
        The number of different events that the data is aligned to.
    bin_width_in_milliseconds : float, optional
        The width of each bin in milliseconds.
    milliseconds_from_event_to_first_bin : float, optional
        The time in milliseconds from the event start to the first bin.
    seed : int, optional
        Seed for the random number generator to ensure reproducibility.
    data : np.ndarray, optional
        A 3D array of shape (number_of_units, number_of_events, number_of_bins) representing
        the binned spike data. If provided, it overrides the generation of mock data based on other parameters.
        Its shape should match the expected number of units, event repetitions, and bins.
    timestamps : np.ndarray, optional
        An array of timestamps for each event. If not provided, it will be automatically generated.
        It should have size `number_of_events`.
    units_region: DynamicTableRegion, optional
        A reference to the Units table region that contains the units of the data.
    event_indices : np.ndarray, optional
        An array of indices for each event. If not provided, it will be automatically generated.
    Returns
    -------
    AggregatedBinnedAlignedSpikes
        A mock AggregatedBinnedAlignedSpikes object populated with the provided or generated data and parameters.
    """

    if data is not None:
        number_of_units, aggregated_events_counts, number_of_bins = data.shape
    else:
        rng = np.random.default_rng(seed=seed)
        data = rng.integers(low=0, high=100, size=(number_of_units, aggregated_events_counts, number_of_bins))

    if timestamps is None:
        timestamps = np.arange(aggregated_events_counts, dtype="float64")

    if event_indices is None:
        event_indices = np.zeros(aggregated_events_counts, dtype=int)
        all_indices = np.arange(number_of_events, dtype=int)

        # Ensure all indices appear at least once
        event_indices[:number_of_events] = rng.choice(all_indices, size=number_of_events, replace=False)
        # Then fill the rest randomly
        event_indices[number_of_events:] = rng.choice(
            event_indices[:number_of_events],
            size=aggregated_events_counts - number_of_events,
            replace=True,
        )

    # Assert data shapes
    assertion_msg = (
        "The shape of `data` should be (number_of_units, aggregated_events_counts, number_of_bins), "
        f"The actual shape is {data.shape} \n "
        "but {number_of_bins=}, {aggregated_events_counts=}, {number_of_units=} was passed"
    )
    assert data.shape == (number_of_units, aggregated_events_counts, number_of_bins), assertion_msg

    if timestamps.shape[0] != aggregated_events_counts:
        raise ValueError("The shape of `timestamps` does not match `aggregated_events_counts`.")
        
    assert (
        event_indices.shape[0] == aggregated_events_counts
    ), "The shape of `event_indices` does not match `aggregated_events_counts`."
    event_indices = np.array(event_indices, dtype=int)

    # Sort the data by timestamps
    sorted_indices = np.argsort(timestamps)
    data = data[:, sorted_indices, :]
    event_indices = event_indices[sorted_indices]

    aggreegated_binned_aligned_spikes = AggregatedBinnedAlignedSpikes(
        bin_width_in_milliseconds=bin_width_in_milliseconds,
        milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin,
        data=data,
        timestamps=timestamps,
        event_indices=event_indices,
        units_region=units_region,
    )
    return aggreegated_binned_aligned_spikes
