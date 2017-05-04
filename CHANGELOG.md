# Change Log
This change log is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased](#unreleased)
#### Add
- Add command line interface.
- Add rule tracking with corresponding documentation.
- Elaborate on syllabifier input/output in documentation.

#### Fix
- Update README.

## [2.0.0](#2.0.0) - 2017-5-4
#### Add
- Enable the syllabification of entire sentences/texts, treating any whitespace, punctuation, and non-alphabetic characters as word delimiters.
- Add stress, weight, and vowel quality annotation.
- Add Travis CI testing.

#### Change
- Always return syllabifications and compound splits in UTF-8 unicode, regardless of the input type.

#### Fix
- Preserve umlauts, capitalization, and any existing punctuation.

## [1.0.2, 1.0.3](#1.0.2) - 2016-12-22
#### Fixed
- Fix code block formatting to cooperate with PyPI.

## [1.0.1](#1.0.1) - 2016-12-22
#### Added
- Add umlaut testing.

#### Changed
- Return syllabifications in order of predicted *frequency*, i.e., from most frequent to least frequent.
- Return syllabifications in lowercase (temporary change).
