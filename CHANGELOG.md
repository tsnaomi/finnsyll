# Change Log
This change log is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased](#unreleased)
#### Added
- Add rule tracking with corresponding documentation.
- Add string preservation testing.

#### Changed
- Treat all input punctuation as delimiters in the syllabifier and compound splitter.

#### Fixed
- Preserve umlauts and capitalization.

## [1.0.1](#1.0.1) - 2016-12-22
#### Added
- Add umlaut testing.

#### Changed
- Return syllabifications in order of predicted *frequency* (i.e., from most frequent to least frequent).
- Return syllabifications in lowercase (temporary change).
