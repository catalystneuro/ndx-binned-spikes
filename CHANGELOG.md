# Changelog for ndx-binned-spikes
## [0.3.0] - 2025-10-06

### Added
- New `BinnedSpikes` class for storing non-aligned binned spike counts across entire sessions
- Comprehensive overview section in README explaining both data interfaces
- Enhanced installation instructions highlighting PyPI availability
- Support for Python 3.13

### Changed
- **BREAKING**: Renamed `bin_width_in_milliseconds` → `bin_width_in_ms` in both `BinnedAlignedSpikes` and `BinnedSpikes`
- **BREAKING**: Renamed `milliseconds_from_event_to_first_bin` → `event_to_bin_offset_in_ms` in `BinnedAlignedSpikes`
- **BREAKING**: Renamed `milliseconds_from_event_to_first_bin` → `start_time_in_ms` in `BinnedSpikes`
- Improved field documentation with clearer descriptions
- Updated SVG diagrams to reflect new field names
- Minimum Python version now 3.10 (dropped 3.9)
- Updated dependencies: `pynwb>=3.0.0`, `hdmf>=4.0.0`
- Enhanced package description

### Fixed
- Improved clarity of field names for better API usability

## [0.2.1] - 2024-10-30

### Added
- Support for NaN values in binned spike data

### Fixed
- Fixed `get_data_for_condition` method

## [0.2.0] - 2024-09-06

### Added
- Convenience properties for data access
- Simplified data structure

## [0.1.1] - 2024-08-27

### Changed
- Minor improvements and bug fixes

## [0.1.0] - 2024-07-18

### Added
- Initial release of ndx-binned-spikes
- `BinnedAlignedSpikes` class for storing event-aligned binned spike counts
- Support for multiple conditions and event timestamps
- Integration with NWB Units table via DynamicTableRegion
- Comprehensive documentation and examples
