import numpy as np

from pynwb.testing import TestCase
from ndx_binned_spikes import AggregatedBinnedAlignedSpikes


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

        self.event_timestamps_first_event = [5.0, 15.0]
        self.event_timestamps_second_event = [1.0, 10.0, 35.0]

        self.event_indices = np.concatenate(
            [
                np.full(event_data.shape[1], event_index)
                for event_index, event_data in enumerate([self.data_for_first_event, self.data_for_second_event])
            ]
        )

        self.data = np.concatenate([self.data_for_first_event, self.data_for_second_event], axis=1)
        self.event_timestamps = np.concatenate([self.event_timestamps_first_event, self.event_timestamps_second_event])

        self.sorted_indices = np.argsort(self.event_timestamps)

    def test_constructor(self):
        """Test that the constructor for BinnedAlignedSpikes sets values as expected."""

        aggregated_binnned_align_spikes = AggregatedBinnedAlignedSpikes(
            bin_width_in_milliseconds=self.bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
            data=self.data,
            event_timestamps=self.event_timestamps,
            event_indices=self.event_indices,
        )

        np.testing.assert_array_equal(aggregated_binnned_align_spikes.data, self.data[:, self.sorted_indices, :])
        np.testing.assert_array_equal(
            aggregated_binnned_align_spikes.event_indices, self.event_indices[self.sorted_indices]
        )
        np.testing.assert_array_equal(aggregated_binnned_align_spikes.event_timestamps, self.event_timestamps[self.sorted_indices])
        self.assertEqual(aggregated_binnned_align_spikes.bin_width_in_milliseconds, self.bin_width_in_milliseconds)
        self.assertEqual(
            aggregated_binnned_align_spikes.milliseconds_from_event_to_first_bin,
            self.milliseconds_from_event_to_first_bin,
        )

        self.assertEqual(aggregated_binnned_align_spikes.data.shape[0], self.number_of_units)
        self.assertEqual(aggregated_binnned_align_spikes.data.shape[1], self.number_of_events)
        self.assertEqual(aggregated_binnned_align_spikes.data.shape[2], self.number_of_bins)

    def test_get_single_event_data_methods(self):

        aggregated_binnned_align_spikes = AggregatedBinnedAlignedSpikes(
            bin_width_in_milliseconds=self.bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
            data=self.data,
            event_timestamps=self.event_timestamps,
            event_indices=self.event_indices,
            
        )

        data_for_stimuli_1 = aggregated_binnned_align_spikes.get_data_for_stimuli(event_index=0)
        np.testing.assert_allclose(data_for_stimuli_1, self.data_for_first_event)
        
        data_for_stimuli_2  = aggregated_binnned_align_spikes.get_data_for_stimuli(event_index=1)
        np.testing.assert_allclose(data_for_stimuli_2, self.data_for_second_event)

        timestamps_stimuli_1 = aggregated_binnned_align_spikes.get_timestamps_for_stimuli(event_index=0)
        np.testing.assert_allclose(timestamps_stimuli_1, self.event_timestamps_first_event)
        
        timestamps_stimuli_2 = aggregated_binnned_align_spikes.get_timestamps_for_stimuli(event_index=1)
        np.testing.assert_allclose(timestamps_stimuli_2, self.event_timestamps_second_event)
        