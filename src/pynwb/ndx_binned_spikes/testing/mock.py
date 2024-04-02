from typing import Optional

from ndx_binned_spikes import BinnedAlignedSpikes
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
        units_region=units_region
    )
    return binned_aligned_spikes


#TODO: Remove once pynwb 2.7.0 is released and use the mock class there
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
