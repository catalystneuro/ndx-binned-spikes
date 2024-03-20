"""Unit and integration tests for the example BinnedAlignedSpikes extension neurodata type.

TODO: Modify these tests to test your extension neurodata type.
"""

import numpy as np

from pynwb import NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase, remove_test_file

from ndx_binned_spikes import BinnedAlignedSpikes
from ndx_binned_spikes.testing.mock import mock_BinnedAlignedSpikes


class TestBinnedAlignedSpikesConstructor(TestCase):
    """Simple unit test for creating a BinnedAlignedSpikes."""

    def setUp(self):
        """Set up an NWB file. Necessary because BinnedAlignedSpikes requires references to electrodes."""
        self.nwbfile = mock_NWBFile()

    def test_constructor(self):
        """Test that the constructor for BinnedAlignedSpikes sets values as expected."""

        number_of_units = 2
        number_of_bins = 3
        number_of_event_repetitions = 4
        bin_width_in_milliseconds = 20.0
        milliseconds_from_event_to_first_bin = 1.0
        
        rng = np.random.default_rng(seed=0)
        data = rng.integers(low=0, high=100, size=(number_of_units, number_of_event_repetitions, number_of_bins))
        event_timestamps = np.arange(number_of_event_repetitions, dtype="float64") 
        
        binned_aligned_spikes = BinnedAlignedSpikes(
            bin_width_in_milliseconds=bin_width_in_milliseconds,
            milliseconds_from_event_to_first_bin=milliseconds_from_event_to_first_bin,
            data=data,
            event_timestamps=event_timestamps
        )
        
        np.testing.assert_array_equal(binned_aligned_spikes.data, data)
        np.testing.assert_array_equal(binned_aligned_spikes.event_timestamps, event_timestamps)
        self.assertEqual(binned_aligned_spikes.bin_width_in_milliseconds, bin_width_in_milliseconds)
        self.assertEqual(
            binned_aligned_spikes.milliseconds_from_event_to_first_bin, milliseconds_from_event_to_first_bin
        )
        
        self.assertEqual(binned_aligned_spikes.data.shape[0], number_of_units)
        self.assertEqual(binned_aligned_spikes.data.shape[1], number_of_event_repetitions)
        self.assertEqual(binned_aligned_spikes.data.shape[2], number_of_bins)




class TestBinnedAlignedSpikesSimpleRoundtrip(TestCase):
    """Simple roundtrip test for BinnedAlignedSpikes."""



    def setUp(self):
        self.nwbfile = mock_NWBFile()

        self.binned_aligned_spikes = mock_BinnedAlignedSpikes()

        self.path = "test.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_roundtrip_acquisition(self):
        """
        Add a BinnedAlignedSpikes to an NWBFile, write it to file, read the file
        and test that the BinnedAlignedSpikes from the file matches the original BinnedAlignedSpikes.
        """

        self.nwbfile.add_acquisition(self.binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(self.binned_aligned_spikes, read_nwbfile.acquisition["BinnedAlignedSpikes"])

    def test_roundtrip_processing_module(self):
        
        
        ecephys_processinng_module = self.nwbfile.create_processing_module(
            name="ecephys", description="a description"
        )
        ecephys_processinng_module.add(self.binned_aligned_spikes)
        
        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.processing["ecephys"]["BinnedAlignedSpikes"]
            self.assertContainerEqual(self.binned_aligned_spikes, read_container)