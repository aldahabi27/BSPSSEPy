# Changelog

All notable changes to **BSPSSEPy** will be documented in this file.

---

## [0.4] - 2025-02-11
### Added
- Introduced BSPSSEPy Dashboard using the `textual` Python library.
- Flags added for more control over black-start plan execution.
- `GenUpdate` function introduced to manage non-AGC generator output.

### Changed
- Major updates to simulation logic and plan reading behavior.

### Fixed
- Several bugs in code and improvements in simulation logic.

---

## [0.3] - (date unknown)
### Fixed
- Generator measurement channel issues in `BSPSSEPySim`.
- Corrections in related documentation.

---

## [0.2.1] - (date unknown)
### Added
- Cranking phase modeling for generators.
- Extended `BSPSSEPyGenFunctions` with new phase data.

---

## [0.2] - (date unknown)
### Changed
- Refactored all classes (`BSPSSEPyGen`, `BSPSSEPyBrn`, `BSPSSEPyTrn`, etc.) to support new DataFrame schema.
- Updated Markdown documentation for some modules.

---

## To Do (Upcoming Features)
- Finalize documentation of core classes/functions.
- Clean up remaining debugging code and print statements.