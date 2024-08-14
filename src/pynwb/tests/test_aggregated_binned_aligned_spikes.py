import numpy as np

from pynwb import NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase, remove_test_file

from ndx_binned_spikes import AggregatedBinnedAlignedSpikes
from ndx_binned_spikes.testing.mock import mock_AggregatedBinnedAlignedSpikes, mock_Units
from hdmf.common import DynamicTableRegion


class TestAggregatedBinnedAlignedSpikesConstructor(TestCase):
    """Simple unit test for creating a AggregatedBinnedAlignedSpikes."""

    def setUp(self):
        """Set up an NWB file.."""

        self.number_of_units = 2
        self.number_of_bins = 4
        self.number_of_events = 5

        self.bin_width_in_milliseconds = 20.0
        self.milliseconds_from_event_to_first_bin = -100.0

        # Two units in total and 4 bins, and event with two timestamps
        self.data_for_first_event = np.array(
            [
                # Unit 1 data
                [
                    [0, 1, 2, 3],  # Bin counts around the first timestamp
                    [4, 5, 6, 7],  # Bin counts around the second timestamp
                ],
                # Unit 2 data
                [
                    [8, 9, 10, 11],  # Bin counts around the first timestamp
                    [12, 13, 14, 15],  # Bin counts around the second timestamp
                ],
            ],
        )

        # Also two units and 4 bins but this event appeared three times
        self.data_for_second_event = np.array(
            [
                # Unit 1 data
                [
                    [0, 1, 2, 3],  # Bin counts around the first timestamp
                    [4, 5, 6, 7],  # Bin counts around the second timestamp
                    [8, 9, 10, 11],  # Bin counts around the third timestamp
                ],
                # Unit 2 data
                [
                    [12, 13, 14, 15],  # Bin counts around the first timestamp
                    [16, 17, 18, 19],  # Bin counts around the second timestamp
                    [20, 21, 22, 23],  # Bin counts around the third timestamp
                ],
            ]
        )

        self.timestamps_first_event = [5.0, 15.0]
        self.timestamps_second_event = [0.0, 10.0, 20.0]

        self.event_indices = np.concatenate(
            [
                np.full(event_data.shape[1], event_index)
                for event_index, event_data in enumerate([self.data_for_first_event, self.data_for_second_event])
            ]
        )

        self.data = np.concatenate([self.data_for_first_event, self.data_for_second_event], axis=1)
        self.timestamps = np.concatenate([self.timestamps_first_event, self.timestamps_second_event])

        self.sorted_indices = np.argsort(self.timestamps)

    def test_constructor(self):
        """Test that the constructor for AggregatedBinnedAlignedSpikes sets values as expected."""

        with self.assertRaises(ValueError):
            AggregatedBinnedAlignedSpikes(
                bin_width_in_milliseconds=self.bin_width_in_milliseconds,
                milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
                data=self.data,
                timestamps=self.timestamps,
                event_indices=self.event_indices,
            )
        
        
        data, timestamps, event_indices = AggregatedBinnedAlignedSpikes.sort_data_by_timestamps(
            self.data,
            self.timestamps,
            self.event_indices,
        )
        
        aggregated_binnned_align_spikes = AggregatedBinnedAlignedSpikes(
            bin_width_in_milliseconds=self.bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
            data=data,
            timestamps=timestamps,
            event_indices=event_indices,
        )

        np.testing.assert_array_equal(aggregated_binnned_align_spikes.data, self.data[:, self.sorted_indices, :])
        np.testing.assert_array_equal(
            aggregated_binnned_align_spikes.event_indices, self.event_indices[self.sorted_indices]
        )
        np.testing.assert_array_equal(aggregated_binnned_align_spikes.timestamps, self.timestamps[self.sorted_indices])
        self.assertEqual(aggregated_binnned_align_spikes.bin_width_in_milliseconds, self.bin_width_in_milliseconds)
        self.assertEqual(
            aggregated_binnned_align_spikes.milliseconds_from_event_to_first_bin,
            self.milliseconds_from_event_to_first_bin,
        )

        self.assertEqual(aggregated_binnned_align_spikes.data.shape[0], self.number_of_units)
        self.assertEqual(aggregated_binnned_align_spikes.data.shape[1], self.number_of_events)
        self.assertEqual(aggregated_binnned_align_spikes.data.shape[2], self.number_of_bins)

    def test_get_single_event_data_methods(self):

        
        data, timestamps, event_indices = AggregatedBinnedAlignedSpikes.sort_data_by_timestamps(
            self.data,
            self.timestamps,
            self.event_indices,
        )

        aggregated_binnned_align_spikes = AggregatedBinnedAlignedSpikes(
            bin_width_in_milliseconds=self.bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
            data=data,
            timestamps=timestamps,
            event_indices=event_indices,
        )

        data_for_stimuli_1 = aggregated_binnned_align_spikes.get_data_for_stimuli(event_index=0)
        np.testing.assert_allclose(data_for_stimuli_1, self.data_for_first_event)

        data_for_stimuli_2 = aggregated_binnned_align_spikes.get_data_for_stimuli(event_index=1)
        np.testing.assert_allclose(data_for_stimuli_2, self.data_for_second_event)

        timestamps_stimuli_1 = aggregated_binnned_align_spikes.get_timestamps_for_stimuli(event_index=0)
        np.testing.assert_allclose(timestamps_stimuli_1, self.timestamps_first_event)

        timestamps_stimuli_2 = aggregated_binnned_align_spikes.get_timestamps_for_stimuli(event_index=1)
        np.testing.assert_allclose(timestamps_stimuli_2, self.timestamps_second_event)


class TestAggregatedBinnedAlignedSpikesSimpleRoundtrip(TestCase):
    """Simple roundtrip test for AggregatedBinnedAlignedSpikes."""

    def setUp(self):
        self.nwbfile = mock_NWBFile()

        self.path = "test.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_roundtrip_acquisition(self):

        self.aggregated_binned_aligned_spikes = mock_AggregatedBinnedAlignedSpikes()

        self.nwbfile.add_acquisition(self.aggregated_binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.acquisition["AggregatedBinnedAlignedSpikes"]
            self.assertContainerEqual(self.aggregated_binned_aligned_spikes, read_container)

    def test_roundtrip_processing_module(self):
        self.aggregated_binned_aligned_spikes = mock_AggregatedBinnedAlignedSpikes()

        ecephys_processinng_module = self.nwbfile.create_processing_module(name="ecephys", description="a description")
        ecephys_processinng_module.add(self.aggregated_binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.processing["ecephys"]["AggregatedBinnedAlignedSpikes"]
            self.assertContainerEqual(self.aggregated_binned_aligned_spikes, read_container)

    def test_roundtrip_with_units_table(self):

        units = mock_Units(num_units=3)
        self.nwbfile.units = units
        region_indices = [0, 3]
        units_region = DynamicTableRegion(
            data=region_indices, table=units, description="region of units table", name="units_region"
        )

        aggregated_binned_aligned_spikes_with_region = mock_AggregatedBinnedAlignedSpikes(units_region=units_region)
        self.nwbfile.add_acquisition(aggregated_binned_aligned_spikes_with_region)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.acquisition["AggregatedBinnedAlignedSpikes"]
            self.assertContainerEqual(aggregated_binned_aligned_spikes_with_region, read_container)
