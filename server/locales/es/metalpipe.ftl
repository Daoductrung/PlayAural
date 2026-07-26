# Metal Pipe game messages

game-name-metalpipe = Tubo de Metal

metalpipe-mode-single = Golpe único
metalpipe-mode-multiple = Golpes múltiples
metalpipe-self-bonk-allowed = autogolpes permitidos
metalpipe-self-bonk-blocked = autogolpes bloqueados

metalpipe-game-start = Tubo de Metal comienza en modo { $mode }. El tubo lo elige todo automáticamente.
metalpipe-game-start-brief = Tubo de Metal: { $mode }.

metalpipe-you-hit-other = Blandes el tubo de metal y golpeas a { $bonked }. { $bonked } queda eliminado.
metalpipe-player-hits-you = { $bonker } blande el tubo de metal y te golpea. Quedas eliminado.
metalpipe-player-hits-other = { $bonker } blande el tubo de metal y golpea a { $bonked }. { $bonked } queda eliminado.
metalpipe-you-hit-self = De alguna forma te golpeas a ti mismo con el tubo de metal y quedas eliminado.
metalpipe-player-hits-self = De alguna forma { $bonker } se golpea a sí mismo con el tubo de metal y queda eliminado.

metalpipe-you-hit-other-brief = Golpeas a { $bonked }. { $bonked } fuera.
metalpipe-player-hits-you-brief = { $bonker } te golpea. Quedas fuera.
metalpipe-player-hits-other-brief = { $bonker } golpea a { $bonked }. { $bonked } fuera.
metalpipe-you-hit-self-brief = Te autogolpeas. Fuera.
metalpipe-player-hits-self-brief = { $bonker } se autogolpea. Fuera.

metalpipe-you-win = Ganas. El tubo de metal ha hablado.
metalpipe-you-win-with-others = Ganas junto con { $players }. El tubo de metal ha hablado.
metalpipe-players-win = { $players } ganan. El tubo de metal ha hablado.
metalpipe-you-win-brief = Ganas.
metalpipe-you-win-with-others-brief = Tú y { $players } ganan.
metalpipe-players-win-brief = Ganadores: { $players }.
metalpipe-no-winner = El tubo de metal no deja ganador.
metalpipe-no-winner-brief = Sin ganador.

metalpipe-check-status = Ver estado del tubo
metalpipe-status-mode = Modo: { $mode }; { $self_bonk }.
metalpipe-status-progress = Golpes resueltos: { $count }. Jugadores en pie: { $alive } de { $total }.
metalpipe-status-awaiting = El tubo aún no ha caído.
metalpipe-status-last-other = Último golpe: { $bonker } golpeó a { $bonked }.
metalpipe-status-last-self = Último golpe: { $bonker } se golpeó a sí mismo.
metalpipe-status-player = { $player}: { $status }.
metalpipe-status-alive = En pie
metalpipe-status-eliminated = Eliminado
metalpipe-no-turn-automatic = Tubo de Metal se está resolviendo automáticamente. Quedan { $alive } jugadores en pie, y ningún jugador tiene un turno manual.

metalpipe-final-results = Resultados de Tubo de Metal
metalpipe-end-winner = Ganador: { $player }.
metalpipe-end-winners = Ganadores: { $players }.
metalpipe-line-format = { $player}: { $status }

metalpipe-set-multiple-bonks = Golpes múltiples: { $enabled }
metalpipe-option-changed-multiple-bonks = Golpes múltiples establecido en { $enabled }.
metalpipe-desc-multiple-bonks = Cuando está activado, el tubo sigue eligiendo golpeadores y objetivos hasta que quede un solo jugador (desactivado por defecto).
metalpipe-set-allow-self-bonk = Permitir autogolpe: { $enabled }
metalpipe-option-changed-allow-self-bonk = Permitir autogolpe establecido en { $enabled }.
metalpipe-desc-allow-self-bonk = Cuando está activado, el golpeador elegido al azar también puede ser el objetivo (activado por defecto).
