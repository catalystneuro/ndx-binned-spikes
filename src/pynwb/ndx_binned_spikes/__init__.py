import os
import numpy as np

from pynwb import load_namespaces, get_class
from pynwb import register_class
from pynwb.core import NWBDataInterface
from hdmf.utils import docval, popargs_to_dict

try:
    from importlib.resources import files
except ImportError:
    # TODO: Remove when python 3.9 becomes the new minimum
    from importlib_resources import files

# Get path to the namespace.yaml file with the expected location when installed not in editable mode
__location_of_this_file = files(__name__)
__spec_path = __location_of_this_file / "spec" / "ndx-binned-spikes.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / "ndx-binned-spikes.namespace.yaml"

# Load the namespace
load_namespaces(str(__spec_path))

# BinnedAlignedSpikes = get_class("BinnedAlignedSpikes", "ndx-binned-spikes")


@register_class(neurodata_type="BinnedAlignedSpikes", namespace="ndx-binned-spikes") #noqa
class BinnedAlignedSpikes(NWBDataInterface):
    __nwbfields__ = (
        "name",
        "bin_width_in_milliseconds",
        "milliseconds_from_event_to_first_bin",
        "data",
        "event_timestamps",
        "units",
    )

    DEFAULT_NAME = "BinnedAlignedSpikes"

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "The name of this container",
            "default": DEFAULT_NAME,
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
                "The time in milliseconds from the event (e.g. a stimuli or the beginning of a trial),"
                "to the first bin. Note that this is a negative number if the first bin is before the event."
            ),
            "default": 0.0,
        },
        {
            "name": "data",
            "type": "array_data",
            "shape": [(None, None, None), (None, None)],
            "doc": "The source of the data",
        },
        {
            "name": "event_timestamps",
            "type": "array_data",
            "doc": "The timestamps at which the event occurred.",
            "shape": (None,),
        },
        {
            "name": "units",
            "type": ("DynamicTableRegion"),
            "doc": "A reference to the Units table region that contains the units of the data.",
            "default": None,
        },
    )
    def __init__(self, **kwargs):

        keys_to_set = ("bin_width_in_milliseconds", "milliseconds_from_event_to_first_bin", "units")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        keys_to_process = ("data", "event_timestamps")  # these are properties and cannot be set with setattr
        args_to_process = popargs_to_dict(keys_to_process, kwargs)
        super().__init__(**kwargs)

        # Set the values
        for key, val in args_to_set.items():
            setattr(self, key, val)

        # Post-process / post_init
        data = args_to_process["data"]

        data = data if data.ndim == 3 else data[np.newaxis, ...]

        event_timestamps = args_to_process["event_timestamps"]

        if data.shape[1] != event_timestamps.shape[0]:
            raise ValueError("The number of event timestamps must match the number of event repetitions in the data.")

        self.fields["data"] = data
        self.fields["event_timestamps"] = event_timestamps


# Remove these functions from the package
del load_namespaces, get_class
