# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec, NWBRefSpec, NWBDatasetSpec


def main():
    # these arguments were auto-generated from your cookiecutter inputs
    ns_builder = NWBNamespaceBuilder(
        name="""ndx-binned-spikes""",
        version="""0.1.0""",
        doc="""to-do""",
        author=[
            "Ben Dicther",
            "Heberto Mayorquin",
        ],
        contact=[
            "ben.dichter@gmail.com",
            "h.mayorquin@gmail.com",
        ],
    )
    ns_builder.include_namespace("core")

    # TODO: if your extension builds on another extension, include the namespace
    # of the other extension below
    # ns_builder.include_namespace("ndx-other-extension")

    binned_aligned_spikes_data = NWBDatasetSpec(
        name="data",
        doc=(
            "The binned data. It should be an array whose first dimension is the number of units, the second dimension "
            "is the number of events, and the third dimension is the number of bins."
            ),
        dtype="numeric",  # TODO should this be a uint64?
        shape=[None, None, None],
        dims=["num_units", "number_of_events", "number_of_bins"],
    )

    event_timestamps = NWBDatasetSpec(
        name="event_timestamps",
        doc="The timestamps at which the events occurred.",
        dtype="float64",
        shape=[None],
        dims=["number_of_events"],
    )
    
    units_region = NWBDatasetSpec(
        name="units_region",
        neurodata_type_inc="DynamicTableRegion",
        doc="A reference to the Units table region that contains the units of the data.",
        # dtype=NWBRefSpec(target_type="Units", reftype="region"),
        shape=[None],
        dims=["number_of_units"],
        quantity="?",
        
    )
    
    binned_aligned_spikes = NWBGroupSpec(
        neurodata_type_def="BinnedAlignedSpikes",
        neurodata_type_inc="NWBDataInterface",
        default_name="BinnedAlignedSpikes",
        doc="A data interface for binned spike data aligned to an event (e.g. a stimuli or the beginning of a trial).",
        datasets=[binned_aligned_spikes_data, event_timestamps, units_region],
        attributes=[
            NWBAttributeSpec(
                name="name",
                doc="The name of this container",
                dtype="text",
                value="BinnedAlignedSpikes",
            ),
            NWBAttributeSpec(
                name="description",
                doc="A description of what the data represents",
                dtype="text",
                value="Spikes data binned and aligned to event timestamps.",
            ),
            NWBAttributeSpec(
                name="bin_width_in_milliseconds",
                doc="The length in milliseconds of the bins",
                dtype="float64",
            ),
            NWBAttributeSpec(
                name="milliseconds_from_event_to_first_bin",
                doc=(
                "The time in milliseconds from the event to the beginning of the first bin. A negative value indicates"
                "that the first bin is before the event whereas a positive value indicates that the first bin is "
                "after the event." 
                ),
                dtype="float64",
                default_value=0.0,
            )
        ],
    )

    # TODO: add all of your new data types to this list
    new_data_types = [binned_aligned_spikes]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
