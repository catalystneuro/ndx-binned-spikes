# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec, NWBRefSpec, NWBDatasetSpec

# TODO: import other spec classes as needed
# from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec


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

    # TODO: define your new data types
    # see https://pynwb.readthedocs.io/en/stable/tutorials/general/extensions.html
    # for more information


    binned_aligned_spikes_data = NWBDatasetSpec(
        name="data",
        doc="TODO",
        dtype="numeric",  # TODO should this be a uint64?
        shape=[(None, None), (None, None, None)],
        dims=[("number_of_event_repetitions", "number_of_bins"), ("number_of_event_repetitions", "number_of_bins", "num_units")],
    )
    
    event_timestamps = NWBDatasetSpec(
        name="event_timestamps",
        doc="The timestamps at whic the event occurred.",
        dtype="float64",
        shape=(None,),
        dims=("number_of_event_repetitions",),
    )

    binned_aligned_spikes = NWBGroupSpec(
        neurodata_type_def="BinnedAlignedSpikes",
        neurodata_type_inc="NWBDataInterface",
        default_name="BinnedAlignedSpikes",
        doc="A data interface for binned spike data aligned to an event (e.g. a stimuli or the beginning of a trial).",
        datasets=[binned_aligned_spikes_data, event_timestamps],
        attributes=[
            NWBAttributeSpec(
                name="bin_width_in_milliseconds",
                doc="The lenght in milliseconds of the bins",
                dtype="float64",
            ),
            NWBAttributeSpec(
                name="milliseconds_from_event_to_first_bin",
                doc=(
                    "The time in milliseconds from the event (e.g. a stimuli or the beginning of a trial),"
                    "to the first bin. Note that this is a negative number if the first bin is before the event."
                ),
                dtype="float64",
                default_value=0.0,
            ),
            NWBAttributeSpec(
                name="units",
                doc="A link to the units Table that contains the units of the data.",
                required=False,
                dtype=NWBRefSpec(target_type="Units", reftype="object"),
            ),
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
