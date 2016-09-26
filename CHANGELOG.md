## Change Log
This change log is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

### [Unreleased](#unreleased)
#### Added
- Add rule tracking with corresponding documentation.

#### Changed
- Make ```FinnSyll(variation=False).syllabify()``` return the most *frequent* variant instead of a random variant.
- Treat all input punctuation as delimiters in the syllabifier and compound splitter.
