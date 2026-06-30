# Translating PlayAural

PlayAural is an audio-first game platform, so translations are part of the
accessibility experience. A good translation should be clear when heard through
speech, not only when read visually.

English (`en`) and Vietnamese (`vi`) are PlayAural's official default
languages. English is the source template for community translations. Partial
community translations are allowed: if a language is missing a string, the
clients and server must fall back to English instead of showing a raw key.

## Where Strings Live

- Server and game strings: `server/locales/<locale>/*.ftl`
- Server translator metadata: `server/locales/<locale>/metadata.json`
- Server documentation and game manuals:
  `server/documentation/content/<locale>/**/*.md`
- Desktop client strings: `client/locales/<locale>/client.ftl`
- Web client strings: `web_client/locales/<locale>.js`
- Web language metadata: `web_client/locales/manifest.js`
- Mobile client strings: `mobile_client/locales/<locale>/client.json`
- Mobile language metadata: `mobile_client/locales/metadata.json`

When adding a new mobile language, update `mobile_client/locales/metadata.json`
and run:

```bash
cd mobile_client
cmd /c npm run generate:locales
```

For server languages, keep `languages.ftl` in place. It provides localized
language names for each viewer, while `metadata.json` stores translator credit
and whether the language is an official PlayAural default. A server metadata
file should look like this:

```json
{
  "code": "fr",
  "name": "French",
  "native_name": "Français",
  "translators": ["Translator name"],
  "official": false
}
```

## Fluent Files

Server and desktop strings use Mozilla Fluent (`.ftl`). Keep the key name the
same and translate only the value:

```ftl
game-started = The game has started.
score-line = { $player } has { $score } points.
```

Rules:

- Do not rename, remove, or translate variables such as `{ $player }` or
  `{ $score }`.
- Keep every plural/select arm that exists in English.
- Keep message attributes such as `.label` when English has them.
- Do not define the same Fluent key twice, even in different files. The server
  loads each locale as one namespace, so duplicate ids can silently shadow the
  string a player should hear.
- Translate the whole sentence naturally. Do not preserve English word order if
  it sounds unnatural in your language.
- Make speech output concise and understandable. Very long menu labels are hard
  to navigate with a screen reader.
- Reuse parameterized source strings when they already exist. For example, a
  single `{ $status }` option label is easier to maintain than separate "on"
  and "off" sentences.
- Keep identical short labels separate when their UI context is different, such
  as a login password field versus a registration password field. Context helps
  translators choose the right wording.

## Web and Mobile Files

Web and mobile strings use JavaScript or JSON objects with placeholders such as
`{player}`:

```json
"chat-global": "On the global channel, {player} says: {message}"
```

Rules:

- Keep each placeholder name exactly the same.
- Do not add HTML. The web client treats server and translation text as plain
  text for safety.
- Keep button labels short and action-focused.

## Perspective Rules

Gameplay broadcasts must respect listener perspective:

- The acting player hears first person, for example "You drew a card."
- Other players and spectators hear third person, for example
  "Rory drew a card."

Do not merge these into one generic key when the actor can hear the message.
The English and translated files must keep the same key structure and
variables for both forms.

## Documentation Rules

Documentation is player-facing. Before translating or writing a manual, read a
finished manual in the same language and follow its structure and tone.

- Write for beginners.
- Explain what the player does, hears, chooses, and wins.
- Do not write changelog-style notes or development details.
- Keep the English and translated documents synchronized in structure and
  meaning.
- Use the same game names and UI terms that appear in the matching locale
  files.

If a translated document is missing, PlayAural falls back to the English
document so players never receive an empty manual.

## Validation

Run the server locale comparison tool before submitting a translation:

```bash
uv run --project server --extra dev python server/tools/compare_locales.py vi
```

Replace `vi` with your locale code, or omit the locale code to check every
non-English server locale. The tool reports:

- missing files and keys
- obsolete files and keys
- duplicate Fluent keys in one file or across files in the same locale
- missing or extra variables
- attribute mismatches
- plural/select arm differences for review

Fix every blocking issue unless a maintainer confirms that the English source
string should change instead. Review plural/select differences carefully:
languages that do not inflect plurals may intentionally use one natural
sentence, but translations must still preserve every variable needed by the
English source.

## Contributor Credits

When a language is added or significantly maintained, update the supported
language metadata in the README and client manifests so translators receive
visible credit.
