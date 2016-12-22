# Change Log
This change log is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased](#unreleased)
#### Add
- Add rule tracking with corresponding documentation.
- Add string preservation testing.

#### Change
- Treat all input punctuation as delimiters in the syllabifier and compound splitter.

#### Fix
- Preserve umlauts and capitalization.

## [1.0.2](#1.0.2) - 2016-12-22
#### Fixed
- Fix code block formatting to cooperate with PyPI.

## [1.0.1](#1.0.1) - 2016-12-22
#### Added
- Add umlaut testing.

#### Changed
- Return syllabifications in order of predicted *frequency* (i.e., from most frequent to least frequent).
- Return syllabifications in lowercase (temporary change).
