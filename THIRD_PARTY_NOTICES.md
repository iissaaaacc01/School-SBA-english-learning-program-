# Third-party notices

## Wordle allowed-guess dictionary

`wordle_dictionary.sql` contains 7,052 distinct five-letter words derived from
SCOWLv2, now called the English Speller Database (ESDB), by Kevin Atkinson and its
credited contributors. The source is the upstream **2026.02.25 release** of the
American and British large dictionaries (SCOWL size 70):

- [Project website](https://wordlist.aspell.net/)
- [Upstream generated word lists](https://github.com/en-wl/wordlist-diff/tree/rel-2026.02.25)
- [American English source](https://raw.githubusercontent.com/en-wl/wordlist-diff/rel-2026.02.25/en_US-large.txt)
- [British English source](https://raw.githubusercontent.com/en-wl/wordlist-diff/rel-2026.02.25/en_GB-large.txt)
- [Upstream copyright and license](https://raw.githubusercontent.com/en-wl/wordlist-diff/rel-2026.02.25/Copyright)

The dictionary is supplied as a SQL bootstrap asset. The application imports it
into the SQLite `allowed_words` table, then checks guesses against SQLite. No
internet connection or external dictionary package is required at runtime. This
list expands permitted guesses; it does not select the puzzle answers.

### Modifications and generation rule

Downloaded on 2026-09-05. Read each upstream UTF-8 source as lines; retain only
lines that fully match the case-sensitive ASCII regular expression `[a-z]{5}`;
take the union, deduplicate and sort in ascending order. Do not lowercase source
entries, which would accidentally add capitalized proper names. Emit SQLite
`INSERT OR IGNORE INTO allowed_words(word) VALUES ...` statements in batches of
500 rows. No other changes or manual additions were made to this asset.

The upstream large spell-checking dictionaries include inflected and less common
words. They are general English dictionaries, not the official Wordle word list.

### Source integrity

SHA-256 hashes of the downloaded source bytes:

| Source file | SHA-256 |
| --- | --- |
| en_US-large.txt | `fa1f9a1382df724be887d3a5d2d743095e6f33fc0949ebb22415c1554bb42fa7` |
| en_GB-large.txt | `cde5031d8719181cb03c045c4af1e7c20052e9afe09118c5a5e616beed95ea61` |

### Applicable upstream notice (verbatim)

The upstream license says that for a non-Australian official speller dictionary,
the notice before its first `===` separator is sufficient. Both source lists are
non-Australian size-70 speller dictionaries. That complete notice follows:

```text
Copyright 2000-2026 by Kevin Atkinson

Permission to use, copy, modify, distribute, and sell any part of SCOWLv2, or
word lists created from it, is hereby granted without fee, provided that the
above copyright notice appears in all copies and that both the above
copyright notice and this notice appear in supporting documentation.  Kevin
Atkinson makes no representations about the suitability of this database for
any purpose.  It is provided "as is" without express or implied warranty.

SCOWL is derived from many sources, most of which are in the Public Domain.
Data from the Corpus of Contemporary American English (COCA) was also used.

All data from COCA comes from 3-gram data that is not freely available;
however, the usage is within the rights given by the NDA that was signed when
purchasing the data.  More information on COCA is available at
https://www.english-corpora.org/coca/.

The primary source of words for SCOWL comes from 12dicts and ENABLE2K.  Both
are in the Public Domain, but Alan Beale <biljir@pobox.com> deserves special
credit as he is the author of 12dicts and a major contributor to ENABLE2K.  In
addition, he gave me an incredible amount of feedback and created a number of
special lists in order to help improve the overall quality of SCOWL.
```
