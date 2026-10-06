# Cards Against Humanity data provenance

PlayAural vendors the structured source files listed below. No card was
transcribed from a printed card or extracted from a PDF.

## English

- File: `humanity_packs.json`
- Source: [FireRat666/Json-Against-Humanity](https://github.com/FireRat666/Json-Against-Humanity/blob/a93662cab36babe6f9ed5c79308c2c3ed1027cc1/cah-all-full.json)
- Revision: `a93662cab36babe6f9ed5c79308c2c3ed1027cc1`
- SHA-256: `57c7c6c29380daa05ddff7d4afce562042befc0b1a2123ec584a71406f840247`
- Imported unchanged as `cah-all-full.json`.
- Source license: Creative Commons Attribution-NonCommercial-ShareAlike 4.0.

This is the actively maintained successor to the older
`crhallberg/json-against-humanity` snapshot previously shipped by PlayAural.
It contains official products, historical editions, and community packs. The
current US 3.0 main deck is PlayAural's default; hosts can opt into other packs.
Three optional community cards contain HTML presentation tags. At load time,
PlayAural converts line breaks and simple emphasis or strikethrough markup to
readable plain text so raw markup never reaches assistive technology.
Runs of soft hyphens used as visual blanks are likewise converted to the
canonical `_` placeholder. Two community prompts print a `Draw 2, Pick 3`
instruction whose structured fields are incomplete; the loader derives those
two counts from the explicit end-of-card directive.

## Spanish

- File: `humanity_packs_es.json`
- Source: [juandjara/cards-against](https://github.com/juandjara/cards-against/blob/79a806927a9ad00532cc94816a5e6ebdc2e53a9b/www/src/assets/CAH-es-set.json)
- Revision: `79a806927a9ad00532cc94816a5e6ebdc2e53a9b`
- SHA-256: `ff51192e6528a153bce57169e4ae6277b41bd1fd25b981288bef49bb39fe8ed3`
- Imported unchanged as `CAH-es-set.json`.
- Repository license: The Unlicense. Cards Against Humanity writing is
  separately distributed under CC BY-NC-SA 4.0.

The source stores Unicode punctuation and accents as HTML character references.
PlayAural decodes those references with Python's standard HTML parser when the
data is loaded. Card wording, capitalization, punctuation, and declared pick
counts are otherwise unchanged.

## Brazilian Portuguese

- Files: `humanity_black_cards_pt_br.json` and
  `humanity_white_cards_pt_br.json`
- Source: [MarcusAldrey/cah-unity](https://github.com/MarcusAldrey/cah-unity/tree/13e6c5b6050b1f223e20a310e257828d6fb6724b/Assets/Files)
- Revision: `13e6c5b6050b1f223e20a310e257828d6fb6724b`
- SHA-256 (`black_cards.json`):
  `f8feca521c559cda060119c67ec5902c3ba37841f819e0c2b12e04d944949e42`
- SHA-256 (`white_cards.json`):
  `dd15dc1dc2edc04d1a84a69055753344f1b4935c981cd30d00fe4ebe7b3bf0a2`
- Imported unchanged as `black_cards.json` and `white_cards.json`.
- The upstream repository does not declare a repository-wide license. Cards
  Against Humanity writing is distributed under CC BY-NC-SA 4.0.

The source uses `$` as the prompt placeholder. PlayAural converts that marker
to its canonical `_` placeholder when loading the data. Card wording,
capitalization, punctuation, and declared pick counts are otherwise unchanged.

## Runtime integrity rules

Every source is validated before use. Pack names must be non-empty and unique;
card text must be non-empty Unicode text; and every prompt must declare a
positive integer pick count and a nonnegative integer draw count. PlayAural
trusts structured mechanics except for an explicit printed `Pick N, Draw N` or
`Draw N, Pick N` directive at the end of a card; it never guesses from the
number of placeholder characters, because legitimate prompts may ask for
multiple answers without containing multiple blanks. When selected packs
overlap, exact duplicate answers and exact duplicate prompt/pick/draw tuples
enter the game deck only once. Any presentation tag outside the small, audited
set above causes loading to fail instead of leaking ambiguous markup to players.
