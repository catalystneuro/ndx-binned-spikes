from typing import Optional

from ndx_binned_spikes import BinnedAlignedSpikes
import numpy as np
from pynwb import NWBFile
from pynwb.misc import Units
from hdmf.common import DynamicTableRegion

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


def mock_BinnedAlignedSpikes(
    number_of_units: int = 2,
    number_of_events: int = 10,
    number_of_bins: int = 3,
    number_of_conditions: int = 5,
    bin_width_in_milliseconds: float = 20.0,
    milliseconds_from_event_to_first_bin: float = 1.0,
    seed: int = 0,
    timestamps: Optional[np.ndarray] = None,
    data: Optional[np.ndarray] = None,
    condition_indices: Optional[np.ndarray] = None,
    units_region: Optional[DynamicTableRegion] = None,
    sort_data: bool = True,
) -> BinnedAlignedSpikes:
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
    number_of_conditions : int, optional
        The number of different conditions that the data is aligned to. It should be less than `number_of_events`.
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
    condition_indices : np.ndarray, optional
        An array of indices characterizing each condition. If not provided, it will be automatically generated.
    units_region: DynamicTableRegion, optional
        A reference to the Units table region that contains the units of the data.
    sort_data: bool, optional
        If True, the data will be sorted by timestamps. 
    Returns
    -------
    BinnedAlignedSpikes
        A mock BinnedAlignedSpikes object populated with the provided or generated data and parameters.
    """

    if data is not None:
        number_of_units, number_of_events, number_of_bins = data.shape
    else:
        rng = np.random.default_rng(seed=seed)
        data = rng.integers(low=0, high=100, size=(number_of_units, number_of_events, number_of_bins))

    # Assert data shapes
    assertion_msg = (
        "The shape of `data` should be `(number_of_units, number_of_events, number_of_bins)`, "
        f"The actual shape is {data.shape} \n "
        f"but {number_of_bins=}, {number_of_events=}, {number_of_units=} was passed"
    )
    assert data.shape == (number_of_units, number_of_events, number_of_bins), assertion_msg

    if timestamps is None:
        timestamps = np.arange(number_of_events, dtype="float64")

    if timestamps.shape[0] != number_of_events:
        raise ValueError("The shape of `timestamps` does not match `number_of_events`.")
    
    if condition_indices is None and number_of_conditions > 0:
        
        
        assert number_of_conditions < number_of_events, (
            "The number of conditions should be less than the number of events."
        )
        
        condition_indices = np.zeros(number_of_events, dtype=int)
        all_indices = np.arange(number_of_conditions, dtype=int)

        # Ensure all conditions indices appear at least once
        condition_indices[:number_of_conditions] = rng.choice(all_indices, size=number_of_conditions, replace=False)
        # Then fill the rest with random samples
        condition_indices[number_of_conditions:] = rng.choice(
            condition_indices[:number_of_events],
            size=number_of_events - number_of_conditions,
            replace=True,
        )

    if condition_indices is not None:
        assert (
            condition_indices.shape[0] == number_of_events
        ), "The shape of `condition_indices` does not match `number_of_events`."
        condition_indices = np.array(condition_indices, dtype=int)

    # Sort the data by timestamps
    if sort_data:
        sorted_indices = np.argsort(timestamps)
        data = data[:, sorted_indices, :]
        if condition_indices is not None:
            condition_indices = condition_indices[sorted_indices]

    binned_aligned_spikes = BinnedAlignedSpikes(
        bin_width_in_milliseconds=bin_width_in_milliseconds,
        milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin,
        data=data,
        timestamps=timestamps,
        condition_indices=condition_indices,
        units_region=units_region,
    )
    return binned_aligned_spikes
