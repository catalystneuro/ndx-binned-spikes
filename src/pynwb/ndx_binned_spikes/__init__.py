import os
import numpy as np
from typing import Tuple
from pynwb import load_namespaces, get_class
from pynwb import register_class
from pynwb.core import NWBDataInterface
from hdmf.utils import docval
from hdmf.common import DynamicTableRegion

from importlib.resources import files


# Get path to the namespace.yaml file with the expected location when installed not in editable mode
__location_of_this_file = files(__name__)
__spec_path = __location_of_this_file / "spec" / "ndx-binned-spikes.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / "ndx-binned-spikes.namespace.yaml"

# Load the namespace
load_namespaces(str(__spec_path))

# BinnedAlignedSpikes = get_class("BinnedAlignedSpikes", "ndx-binned-spikes")


@register_class(neurodata_type="BinnedAlignedSpikes", namespace="ndx-binned-spikes")  # noqa
class BinnedAlignedSpikes(NWBDataInterface):
    __nwbfields__ = (
        "name",
        "description",
        "bin_width_in_milliseconds",
        "milliseconds_from_event_to_first_bin",
        "data",
        "event_timestamps",
        {"name": "units_region", "child": True},
    )

    DEFAULT_NAME = "BinnedAlignedSpikes"
    DEFAULT_DESCRIPTION = "Spikes data binned and aligned to event timestamps."

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "The name of this container",
            "default": DEFAULT_NAME,
        },
        {
            "name": "description",
            "type": str,
            "doc": "A description of what the data represents",
            "default": DEFAULT_DESCRIPTION,
        },
        {
            "name": "bin_width_in_milliseconds",
            "type": float,
            "doc": "The length in milliseconds of the bins",
        },
        {
            "name": "milliseconds_from_event_to_first_bin",
            "type": float,
            "doc": (
                "The time in milliseconds from the event to the beginning of the first bin. A negative value indicates"
                "that the first bin is before the event whereas a positive value indicates that the first bin is "
                "after the event."
            ),
            "default": 0.0,
        },
        {
            "name": "data",
            "type": "array_data",
            "shape": [(None, None, None)],
            "doc": (
                "The binned data. It should be an array whose first dimension is the number of units, "
                "the second dimension is the number of events, and the third dimension is the number of bins."
            ),
        },
        {
            "name": "event_timestamps",
            "type": "array_data",
            "doc": "The timestamps at which the events occurred.",
            "shape": (None,),
        },
        {
            "name": "units_region",
            "type": DynamicTableRegion,
            "doc": "A reference to the Units table region that contains the units of the data.",
            "default": None,
        },
    )
    def __init__(self, **kwargs):

        data = kwargs["data"]
        event_timestamps = kwargs["event_timestamps"]

        if data.shape[1] != event_timestamps.shape[0]:
            raise ValueError("The number of event timestamps must match the number of event repetitions in the data.")

        super().__init__(name=kwargs["name"])

        name = kwargs.pop("name")
        super().__init__(name=name)

        for key in kwargs:
            setattr(self, key, kwargs[key])


@register_class(neurodata_type="AggregatedBinnedAlignedSpikes", namespace="ndx-binned-spikes")  # noqa
class AggregatedBinnedAlignedSpikes(NWBDataInterface):
    __nwbfields__ = (
        "name",
        "description",
        "bin_width_in_milliseconds",
        "milliseconds_from_event_to_first_bin",
        "data",
        "timestamps",
        "event_indices",
        {"name": "units_region", "child": True},  # TODO, I forgot why this is included
    )

    DEFAULT_NAME = "AggregatedBinnedAlignedSpikes"
    DEFAULT_DESCRIPTION = "Spikes data binned and aligned to the timestamps of multiple events."

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "The name of this container",
            "default": DEFAULT_NAME,
        },
        {
            "name": "description",
            "type": str,
            "doc": "A description of what the data represents",
            "default": DEFAULT_DESCRIPTION,
        },
        {
            "name": "bin_width_in_milliseconds",
            "type": float,
            "doc": "The length in milliseconds of the bins",
        },
        {
            "name": "milliseconds_from_event_to_first_bin",
            "type": float,
            "doc": (
                "The time in milliseconds from the event to the beginning of the first bin. A negative value indicates"
                "that the first bin is before the event whereas a positive value indicates that the first bin is "
                "after the event."
            ),
            "default": 0.0,
        },
        {
            "name": "data",
            "type": "array_data",
            "shape": [(None, None, None)],
            "doc": (
                "The binned data. It should be an array whose first dimension is the number of units, "
                "the second dimension is the number of events, and the third dimension is the number of bins."
            ),
        },
        {
            "name": "timestamps",
            "type": "array_data",
            "doc": (
                "The timestamps at which the events occurred. It is assumed that they map positionally to "
                "the second index of the data.",
            ),
            "shape": (None,),
        },
        {
            "name": "event_indices",
            "type": "array_data",
            "doc": "The timestamps at which the events occurred.",
            "shape": (None,),
        },
        {
            "name": "units_region",
            "type": DynamicTableRegion,
            "doc": "A reference to the Units table region that contains the units of the data.",
            "default": None,
        },
    )
    def __init__(self, **kwargs):

        name = kwargs.pop("name")
        super().__init__(name=name)

        timestamps = kwargs["timestamps"]
        event_indices = kwargs["event_indices"]
        data = kwargs["data"]

        assert data.shape[1] == timestamps.shape[0], "The number of timestamps must match the second axis of data."
        assert event_indices.shape[0] == timestamps.shape[0], "The number of timestamps must match the event_indices."

        # Assert timestamps are monotonically increasing
        if not np.all(np.diff(kwargs["timestamps"]) >= 0):
            error_msg = (
                "The timestamps must be monotonically increasing and the data and event_indices "
                "must be sorted by timestamps. Use the `sort_data_by_timestamps` method to do this "
                "automatically before passing the data to the constructor."
            )
            raise ValueError(error_msg)

        for key in kwargs:
            setattr(self, key, kwargs[key])

    # Should this return an instance of BinnedAlignedSpikes or just the data as it is?
    # Going with the simple one for the moment
    def get_data_for_stimuli(self, event_index):

        mask = self.event_indices == event_index
        binned_spikes_for_unit = self.data[:, mask, :]

        return binned_spikes_for_unit

    def get_timestamps_for_stimuli(self, event_index):

        mask = self.event_indices == event_index
        timestamps = self.timestamps[mask]

        return timestamps

    @staticmethod
    def sort_data_by_timestamps(
        data: np.ndarray,
        timestamps: np.ndarray,
        event_indices: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

        sorted_indices = np.argsort(timestamps)
        data = data[:, sorted_indices, :]
        timestamps = timestamps[sorted_indices]
        event_indices = event_indices[sorted_indices]

        return data, timestamps, event_indices


# Remove these functions from the package
del load_namespaces, get_class
