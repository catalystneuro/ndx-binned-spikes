"""Unit and integration tests for the example BinnedAlignedSpikes extension neurodata type.
"""

import numpy as np

from pynwb import NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase, remove_test_file
from hdmf.common import DynamicTableRegion
from pynwb.misc import Units
from ndx_binned_spikes import BinnedAlignedSpikes
from ndx_binned_spikes.testing.mock import mock_BinnedAlignedSpikes, mock_Units


class TestBinnedAlignedSpikesConstructor(TestCase):
    """Simple unit test for creating a BinnedAlignedSpikes."""

    def setUp(self):
        """Set up an NWB file. Necessary because BinnedAlignedSpikes requires references to electrodes."""

        self.number_of_units = 2
        self.number_of_bins = 3
        self.number_of_events = 4
        self.bin_width_in_milliseconds = 20.0
        self.milliseconds_from_event_to_first_bin = -100.0
        self.rng = np.random.default_rng(seed=0)

        self.data = self.rng.integers(
            low=0,
            high=100,
            size=(
                self.number_of_units,
                self.number_of_events,
                self.number_of_bins,
            ),
        )

        self.event_timestamps = np.arange(self.number_of_events, dtype="float64")

        self.nwbfile = mock_NWBFile()

    def test_constructor(self):
        """Test that the constructor for BinnedAlignedSpikes sets values as expected."""

        binned_aligned_spikes = BinnedAlignedSpikes(
            bin_width_in_milliseconds=self.bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
            data=self.data,
            event_timestamps=self.event_timestamps,
        )

        np.testing.assert_array_equal(binned_aligned_spikes.data, self.data)
        np.testing.assert_array_equal(binned_aligned_spikes.event_timestamps, self.event_timestamps)
        self.assertEqual(binned_aligned_spikes.bin_width_in_milliseconds, self.bin_width_in_milliseconds)
        self.assertEqual(
            binned_aligned_spikes.milliseconds_from_event_to_first_bin, self.milliseconds_from_event_to_first_bin
        )

        self.assertEqual(binned_aligned_spikes.data.shape[0], self.number_of_units)
        self.assertEqual(binned_aligned_spikes.data.shape[1], self.number_of_events)
        self.assertEqual(binned_aligned_spikes.data.shape[2], self.number_of_bins)

    def test_constructor_units_region(self):


        units_table = Units()
        units_table.add_column(name="unit_name", description="a readable identifier for the units")

        unit_name_a = "a"
        spike_times_a = [1.1, 2.2, 3.3]
        units_table.add_row(spike_times=spike_times_a, unit_name=unit_name_a)

        unit_name_b = "b"
        spike_times_b = [4.4, 5.5, 6.6]
        units_table.add_row(spike_times=spike_times_b, unit_name=unit_name_b)

        unit_name_c = "c"
        spike_times_c = [7.7, 8.8, 9.9]
        units_table.add_row(spike_times=spike_times_c, unit_name=unit_name_c)

        region_indices = [0, 2]
        units_region = DynamicTableRegion(
            data=region_indices, table=units_table, description="region of units table", name="units_region"
        )

        binned_aligned_spikes = BinnedAlignedSpikes(
            bin_width_in_milliseconds=self.bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
            data=self.data,
            event_timestamps=self.event_timestamps,
            units_region=units_region,
        )

        unit_table_indices = binned_aligned_spikes.units_region.data
        unit_table_names = binned_aligned_spikes.units_region.table["unit_name"][unit_table_indices]

        expected_names = [unit_name_a, unit_name_c]
        self.assertListEqual(unit_table_names, expected_names)

    def test_constructor_inconsistent_timestamps_and_data_error(self):
        shorter_timestamps = self.event_timestamps[:-1]
        
        with self.assertRaises(ValueError):
            BinnedAlignedSpikes(
                bin_width_in_milliseconds=self.bin_width_in_milliseconds,
                milliseconds_from_event_to_first_bin=self.milliseconds_from_event_to_first_bin,
                data=self.data,
                event_timestamps=shorter_timestamps,
            )
            

class TestBinnedAlignedSpikesSimpleRoundtrip(TestCase):
    """Simple roundtrip test for BinnedAlignedSpikes."""

    def setUp(self):
        self.nwbfile = mock_NWBFile()


        self.path = "test.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_roundtrip_acquisition(self):
        """
        Add a BinnedAlignedSpikes to an NWBFile, write it to file, read the file
        and test that the BinnedAlignedSpikes from the file matches the original BinnedAlignedSpikes.
        """
        self.binned_aligned_spikes = mock_BinnedAlignedSpikes()

        self.nwbfile.add_acquisition(self.binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.acquisition["BinnedAlignedSpikes"]
            self.assertContainerEqual(self.binned_aligned_spikes, read_container)

    def test_roundtrip_processing_module(self):
        self.binned_aligned_spikes = mock_BinnedAlignedSpikes()

        ecephys_processinng_module = self.nwbfile.create_processing_module(name="ecephys", description="a description")
        ecephys_processinng_module.add(self.binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.processing["ecephys"]["BinnedAlignedSpikes"]
            self.assertContainerEqual(self.binned_aligned_spikes, read_container)

    def test_roundtrip_with_units_table(self):

        units = mock_Units(num_units=3)
        self.nwbfile.units = units
        region_indices = [0, 3]
        units_region = DynamicTableRegion(
            data=region_indices, table=units, description="region of units table", name="units_region"
        )

        binned_aligned_spikes_with_region = mock_BinnedAlignedSpikes(units_region=units_region)
        self.nwbfile.add_acquisition(binned_aligned_spikes_with_region)

    
        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.acquisition["BinnedAlignedSpikes"]
            self.assertContainerEqual(binned_aligned_spikes_with_region, read_container)

