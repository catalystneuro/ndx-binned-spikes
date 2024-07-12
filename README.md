# ndx-binned-spikes Extension for NWB

⚠️ **Warning: This extension is currently in alpha and subject to change before the first release.**


## Installation
Python:
```bash
pip install -U git+https://github.com/catalystneuro/ndx-binned-spikes.git
```

## Usage

The `BinnedAlignedSpikes` object is designed to store counts of spikes around a set of events (e.g., stimuli or behavioral events such as licks). The events are characterized by their timestamps and a bin data structure is used to store the spike counts around each of the event timestamps. The `BinnedAlignedSpikes` object keeps a separate count for each of the units (e.g., neurons), in other words, the spikes of the units are counted separately but aligned to the same set of events.

### Simple example
The following code illustrates a minimal use of this extension:

```python
import numpy as np
from ndx_binned_spikes import BinnedAlignedSpikes


data = np.array(
    [
        [  # Data of the first unit
            [5, 1, 3, 2],  # First timestamp bins
            [6, 3, 4, 3],  # Second timestamp bins
            [4, 2, 1, 4],  # Third timestamp bins
        ],
        [ # Data of the second unit
            [8, 4, 0, 2],  # First timestamp bins
            [3, 3, 4, 2],  # Second timestamp bins
            [2, 7, 4, 1],  # Third timestamp bins
        ],
    ],
)

event_timestamps = np.array([0.25, 5.0, 12.25])  # The timestamps to which we align the counts
milliseconds_from_event_to_first_bin = -50.0  # The first bin is 50 ms before the event
bin_width_in_milliseconds = 100.0  # Each bin is 100 ms wide
binned_aligned_spikes = BinnedAlignedSpikes(
    data=data,
    event_timestamps=event_timestamps,
    bin_width_in_milliseconds=bin_width_in_milliseconds,
    milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin
)

```

The resulting object is usually added to a processing module in an NWB file. The following code illustrates how to add the `BinnedAlignedSpikes` object to an NWB file. We fist create a nwbfile, then add the `BinnedAlignedSpikes` object to a processing module and finally write the nwbfile to disk:

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from pynwb import NWBHDF5IO, NWBFile

session_description = "A session of data where PSTH was produced"
session_start_time = datetime.now(ZoneInfo("Asia/Ulaanbaatar"))
identifier = "a_session_identifier"
nwbfile = NWBFile(
    session_description=session_description,
    session_start_time=session_start_time,
    identifier=identifier,
)

ecephys_processing_module = nwbfile.create_processing_module(
    name="ecephys", description="Intermediate data derived from extracellular electrophysiology recordings."
)
ecephys_processing_module.add(binned_aligned_spikes)

with NWBHDF5IO("binned_aligned_spikes.nwb", "w") as io:
    io.write(nwbfile)
```

### Parameters and data structure
The structure of the bins are characterized with the following parameters:
 
* `milliseconds_from_event_to_first_bin`: The time in milliseconds from the event to the beginning of the first bin. A negative value indicates that the first bin is before the event whereas a positive value indicates that the first bin is after the event. 
* `bin_width_in_milliseconds`: The width of each bin in milliseconds.


<div style="text-align: center;">
    <img src="./assets/parameters.svg" alt="Parameter meaning" style="width: 75%; height: auto;">
</div>

Note that in the diagram above, the `milliseconds_from_event_to_first_bin` is negative.


The `data` argument passed to the `BinnedAlignedSpikes` stores counts across all the event timestamps for each of the units. The data is a 3D array where the first dimension indexes the units, the second dimension indexes the event timestamps, and the third dimension indexes the bins where the counts are stored. The shape of the data is  `(number_of_units`, `number_of_events`, `number_of_bins`). 


The `event_timestamps` is used to store the timestamps of the events and should have the same length as the second dimension of `data`.

The first dimension of `data` works almost like a dictionary. That is, you select a specific unit by indexing the first dimension. For example, `data[0]` would return the data of the first unit. For each of the units, the data is organized with the time on the first axis as this is the convention in the NWB format. As a consequence of this choice the data of each unit is contiguous in memory.

The following diagram illustrates the structure of the data for a concrete example:
<div style="text-align: center;">
<img src="./assets/data.svg" alt="Data meaning" style="width: 75%; height: auto;">
</div>


### Linking to units table
One way to make the information stored in the `BinnedAlignedSpikes` object more useful is to indicate exactly which units or neurons the first dimension of the `data` attribute corresponds to. This is **optional but recommended** as it makes the data more interpretable and useful for future users. In NWB the units are usually stored in a `Units` [table](https://pynwb.readthedocs.io/en/stable/pynwb.misc.html#pynwb.misc.Units). To illustrate how to to create this link let's first create a toy `Units` table:

```python
import numpy as np
from pynwb.misc import Units 

num_units = 5
max_spikes_per_unit = 10

units_table = Units(name="units")
units_table.add_column(name="unit_name", description="name of the unit")

rng = np.random.default_rng(seed=0)

times = rng.random(size=(num_units, max_spikes_per_unit)).cumsum(axis=1)
spikes_per_unit = rng.integers(1, max_spikes_per_unit, size=num_units)

spike_times = []
for unit_index in range(num_units):

    # Not all units have the same number of spikes
    spike_times = times[unit_index, : spikes_per_unit[unit_index]]
    unit_name = f"unit_{unit_index}"
    units_table.add_unit(spike_times=spike_times, unit_name=unit_name)
```

This will create a `Units` table with 5 units. We can then link the `BinnedAlignedSpikes` object to this table by creating a `DynamicTableRegion` object. This allows to be very specific about which units the data in the `BinnedAlignedSpikes` object corresponds to. In the following code, the units described on the `BinnedAlignedSpikes` object correspond to the unit with indices 1 and 3 on the `Units` table. The rest of the procedure is the same as before: 

```python
from ndx_binned_spikes import BinnedAlignedSpikes
from hdmf.common import DynamicTableRegion


# Now we create the BinnedAlignedSpikes object and link it to the units table
data = np.array(
    [
        [  # Data of the unit 1
            [5, 1, 3, 2],  # First timestamp bins
            [6, 3, 4, 3],  # Second timestamp bins
            [4, 2, 1, 4],  # Third timestamp bins
        ],
        [ # Data of the unit 3
            [8, 4, 0, 2],  # First timestamp bins
            [3, 3, 4, 2],  # Second timestamp bins
            [2, 7, 4, 1],  # Third timestamp bins
        ],
    ],
)

region_indices = [1, 3]   
units_region = DynamicTableRegion(
    data=region_indices, table=units_table, description="region of units table", name="units_region"
)

event_timestamps = np.array([0.25, 5.0, 12.25])
milliseconds_from_event_to_first_bin = -50.0  # The first bin is 50 ms before the event
bin_width_in_milliseconds = 100.0
name = "BinnedAignedSpikesForMyPurpose"
description = "Spike counts that is binned and aligned to events."
binned_aligned_spikes = BinnedAlignedSpikes(
    data=data,
    event_timestamps=event_timestamps,
    bin_width_in_milliseconds=bin_width_in_milliseconds,
    milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin,
    description=description,
    name=name,
    units_region=units_region,
)

```

As with the previous example this can be then added to a processing module in an NWB file and written to disk using exactly the same code as before.

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).
