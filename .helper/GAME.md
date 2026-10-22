# How Toy Box Arena is built (for the suggestions helper)

The whole game is one file, `index.html` (three.js r147, plain JavaScript, no build step). It runs on the website,
inside the iPad app (which loads this website when online), and offline from the app's built-in copy.

## Map of index.html
- **Constants & rules:** `TYPES`, `LABEL`, `SWATCH` (tile pieces); `PLAYER_COLORS`, `PLAYER_NAMES`.
  Rule variables are `let`s (`G`, `BALL_R`, `FRICTION`, `MAX_STROKES`, `BLAST_TIME`, `FISH_TIME`, …) that
  `resetRules()` restores.
- **`TWISTS`**: rule twists for Random Game and the Game Maker. Each is
  `{ id, word, name, desc, color, games: [...], apply: () => { ...change rule variables... } }`.
  Adding a twist is usually a one-line change; if it uses a new variable, also reset it in `resetRules()`.
- **`GAMES`**: one entry per game, plus `GAME_HOWTO`, `SHORT`, and a card in `GAME_CARDS` (home shelf).
  Game ids: golf, blast, rush, splat, race, pitch, bowl, koth, fish.
- **Grid & physics:** 10×10 tiles, 2 m each, levels 0–2. `setPiece`, `surfaceAt`, `collidersNear`,
  `collide`, `step` (rolling ball). Auto-kerbs are built in `rebuildKerbs`.
- **Each game** has `startX()`, `updateX(dt)` (called from `frame()`), a HUD branch in `renderHud()`, and a
  results branch in `showResults()`. Random arenas come from `randomArenaFor(kind)`.
- **UI:** popups use `sheet(html, wire)`; `toast(msg)` shows big text; `esc()` escapes text for HTML.
  Colors come from CSS variables (`--go`, `--warn`, `--ink`, …).
- **Play Together:** the host streams moving meshes to the other device. Any NEW moving 3D object must be
  registered with `netTrack(mesh, kind, color)`, and the guest needs a matching case in `mirrorMake()`.
  If that's too fiddly for a small idea, reply **later**.

## Style
- Match the surrounding code: short functions, a comment explaining *why*, kid-friendly wording in UI text.
- Keep text plain: no em-dashes in UI copy, and sentence case for buttons ("Play again", not "Play Again").
- Test mentally against the existing flows: home shelf → lobby card → play → results → again/home.
