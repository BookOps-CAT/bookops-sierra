[![Build Status](https://github.com/BookOps-CAT/bookops-sierra/actions/workflows/unit-tests.yaml/badge.svg?branch=main)](https://github.com/BookOps-CAT/bookops-sierra/actions) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-sierra/badge.svg?branch=main)](https://coveralls.io/github/BookOps-CAT/bookops-sierra?branch=main) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-sierra
A Sierra API wrapper supporting v6.8 and client credential grant flow of the API.

## Installation
## Basic usage
## References
+ [Sierra API documentation](https://techdocs.iii.com/sierraapi/Content/titlePage.htm)
+ [Sierra Developer Network](https://innovative.libguides.com/c.php?g=1181301&p=8637929&preview=a459e4eef162d4da79728b75364a6a8f)
+ [NYPL Test Sierra API version](https://nypl-sierra-test.iii.com/iii/sierra-api/about)
## Sample Test server bibs & items:
+ b217595996
+ i389995009
+ i389994947

## Changelog

## [0.2.0] - (4/10/2026)
### Added
 - support for `/patrons/{id}/holds/requests` and `/patrons/{id}/holds` endpoints to create and get hold requests for patrons.
 - `py.typed` marker and any missing type annotations
 - additional unit tests to bring coverage up to 100%
 - unit tests for Python 3.14 in github actions
 - support for managing dependencies using `uv`.  reformatted `pyproject.toml` to work with `poetry` 2.0 and `uv`.

### Changed
 - separated test coverage and unit tests into two github actions workflows
 - error handling:
   - returns response from API rather than raising for status with each request so that response codes and messages are passed from the API to the user. Removed `Query` class to facilitate this.
   - changed `BookopsSierraError` to `ValueError` or `TypeError` where more appropriate

### Removed
 - unnecessary `List`, `Dict`, `Tuple`, and `Union` type imports (package only supports python 3.12+)
 - magic strings from top of each module 
 - `delay` param from `SierraSession`

[0.2.0]: https://github.com/BookOps-CAT/bookops-sierra/compare/v0.1.0...v0.2.0