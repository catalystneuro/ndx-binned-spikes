# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec, NWBDatasetSpec


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



    binned_aligned_spikes_data = NWBDatasetSpec(
        name="data",
        doc=(
            "The binned data. It should be an array whose first dimension is the number of units, the second dimension "
            "is the number of events, and the third dimension is the number of bins."
            ),
        dtype="numeric",  
        shape=[None, None, None],
        dims=["num_units", "number_of_events", "number_of_bins"],
    )
    
    units_region = NWBDatasetSpec(
        name="units_region",
        neurodata_type_inc="DynamicTableRegion",
        doc="A reference to the Units table region that contains the units of the data.",
        quantity="?",
        
    )
    
    event_timestamps = NWBDatasetSpec(
        name="event_timestamps",
        doc="The timestamps at which the events occurred.",
        dtype="float64",
        shape=[None],
        dims=["number_of_events"],
    )    

    condition_indices = NWBDatasetSpec(
        name="condition_indices",
        doc= (
            "The index of the condition that each timestamps corresponds to "
            "(e.g. a stimulus type, trial number, category, etc.)."
            "This is only used when the data is aligned to multiple conditions"
            ),
        dtype="uint64",
        shape=[None],
        dims=["number_of_events"],
        quantity="?",
    )
    
    condition_labels = NWBDatasetSpec(
        name="condition_labels",
        doc=(
            "The labels of the conditions that the data is aligned to. The size of this array should match "
            "the number of conditions. This is only used when the data is aligned to multiple conditions. "
            "First condition is index 0, second is index 1, etc."
        ),
        dtype="text",
        shape=[None],
        dims=["number_of_conditions"],
        quantity="?",
    )
    
    binned_aligned_spikes = NWBGroupSpec(
        neurodata_type_def="BinnedAlignedSpikes",
        neurodata_type_inc="NWBDataInterface",
        default_name="BinnedAlignedSpikes",
        doc="A data interface for binned spike data aligned to an event (e.g. a stimulus or the beginning of a trial).",
        datasets=[binned_aligned_spikes_data, event_timestamps, condition_indices, condition_labels, units_region],
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
                value="Spikes data binned and aligned to the event timestamps of one or multiple conditions.",
            ),
            NWBAttributeSpec(
                name="bin_width_in_ms",
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
    

    # Define BinnedSpikes - a 2D array of unit x bin for non-aligned spike counts
    binned_spikes_data = NWBDatasetSpec(
        name="data",
        doc=(
            "The binned data. It should be an array whose first dimension is the number of units, "
            "and the second dimension is the number of bins."
            ),
        dtype="numeric",  
        shape=[None, None],
        dims=["num_units", "number_of_bins"],
    )
    
    binned_spikes = NWBGroupSpec(
        neurodata_type_def="BinnedSpikes",
        neurodata_type_inc="NWBDataInterface",
        default_name="BinnedSpikes",
        doc="A data interface for non-aligned binned spike counts.",
        datasets=[binned_spikes_data, units_region],
        attributes=[
            NWBAttributeSpec(
                name="name",
                doc="The name of this container",
                dtype="text",
                value="BinnedSpikes",
            ),
            NWBAttributeSpec(
                name="description",
                doc="A description of what the data represents",
                dtype="text",
                value="Binned spike counts.",
            ),
            NWBAttributeSpec(
                name="bin_width_in_ms",
                doc="The length in milliseconds of the bins",
                dtype="float64",
            ),
            NWBAttributeSpec(
                name="start_time_in_ms",
                doc=(
                "The timestamp of the beginning of the first bin in milliseconds. The default "
                "value is 0, which represents the beginning of the session."
                ),
                dtype="float64",
                default_value=0.0,
                required=False,
            )
        ],
    )
    
    new_data_types = [binned_aligned_spikes, binned_spikes]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
