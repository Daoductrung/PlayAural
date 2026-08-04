game-name-leftrightcenter = Izquierda Centro Derecha

lrc-roll = Lanzar { $count } { $count ->
    [one] dado
   *[other] dados
}
lrc-roll-label = Lanzar dados

lrc-face-left = Izquierda
lrc-face-center = Centro
lrc-face-right = Derecha
lrc-face-dot = Punto

lrc-you-roll = Sacas { $results }.
lrc-player-rolls = { $player } saca { $results }.
lrc-you-roll-brief = Tú: { $results }.
lrc-player-rolls-brief = { $player }: { $results }.

lrc-you-pass-left = Pasas { $count } { $count ->
    [one] ficha
   *[other] fichas
} a la izquierda, a { $target }. Te quedan { $remaining }; { $target } ahora tiene { $target_total }.
lrc-player-passes-left = { $player } pasa { $count } { $count ->
    [one] ficha
   *[other] fichas
} a la izquierda, a { $target }. A { $player } le quedan { $remaining }; { $target } ahora tiene { $target_total }.
lrc-you-pass-left-brief = Tú, izquierda a { $target }: { $count }. Restantes: { $remaining }.
lrc-player-passes-left-brief = { $player }, izquierda a { $target }: { $count }. Restantes: { $remaining }.

lrc-you-pass-right = Pasas { $count } { $count ->
    [one] ficha
   *[other] fichas
} a la derecha, a { $target }. Te quedan { $remaining }; { $target } ahora tiene { $target_total }.
lrc-player-passes-right = { $player } pasa { $count } { $count ->
    [one] ficha
   *[other] fichas
} a la derecha, a { $target }. A { $player } le quedan { $remaining }; { $target } ahora tiene { $target_total }.
lrc-you-pass-right-brief = Tú, derecha a { $target }: { $count }. Restantes: { $remaining }.
lrc-player-passes-right-brief = { $player }, derecha a { $target }: { $count }. Restantes: { $remaining }.

lrc-you-pass-center = Pones { $count } { $count ->
    [one] ficha
   *[other] fichas
} en el centro. Te quedan { $remaining }; el centro ahora tiene { $center }.
lrc-player-passes-center = { $player } pone { $count } { $count ->
    [one] ficha
   *[other] fichas
} en el centro. A { $player } le quedan { $remaining }; el centro ahora tiene { $center }.
lrc-you-pass-center-brief = Tú, centro: { $count }. Restantes: { $remaining }. Total del centro: { $center }.
lrc-player-passes-center-brief = { $player }, centro: { $count }. Restantes: { $remaining }. Total del centro: { $center }.

lrc-you-keep-all = Todos tus dados son puntos, así que conservas las { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-player-keeps-all = Todos los dados de { $player } son puntos, así que conserva las { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-you-keep-all-brief = Tú: sin traspasos; { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-player-keeps-all-brief = { $player }: sin traspasos; { $count } { $count ->
    [one] ficha
   *[other] fichas
}.

lrc-you-skip-no-chips = No tienes fichas, así que se salta tu turno. Sigues en la partida y puedes recibir fichas de cualquiera de tus vecinos.
lrc-player-skips-no-chips = { $player } no tiene fichas, así que se salta su turno. Sigue en la partida y puede recibir fichas de cualquiera de sus vecinos.
lrc-you-skip-no-chips-brief = Tú: sin fichas; turno saltado.
lrc-player-skips-no-chips-brief = { $player }: sin fichas; turno saltado.

lrc-you-win = Eres el último jugador con fichas y ganas con { $count } restantes. Te llevas las { $center } { $center ->
    [one] ficha
   *[other] fichas
} del centro.
lrc-player-wins = { $player } es el último jugador con fichas y gana con { $count } restantes. Se lleva las { $center } { $center ->
    [one] ficha
   *[other] fichas
} del centro.
lrc-you-win-brief = Ganas. Tus fichas: { $count }. Centro: { $center }.
lrc-player-wins-brief = { $player } gana. Fichas: { $count }. Centro: { $center }.

lrc-roll-already-resolving = Tu tirada ya se está resolviendo. Espera a que terminen los traspasos de fichas.
lrc-no-chips-to-roll = No tienes fichas para lanzar. Tu turno se saltará automáticamente.

lrc-center-pot = Bote del centro: { $count } { $count ->
    [one] ficha
   *[other] fichas
}.
lrc-check-center = Ver bote del centro
lrc-check-last-roll = Ver última tirada
lrc-last-roll-none = Aún no se ha lanzado ningún dado.
lrc-last-roll-you = Tu última tirada fue { $results }.
lrc-last-roll-player = La última tirada de { $player } fue { $results }.

lrc-set-starting-chips = Fichas iniciales: { $count }
lrc-enter-starting-chips = Ingresa las fichas iniciales:
lrc-option-changed-starting-chips = Fichas iniciales establecidas en { $count }.
leftrightcenter-desc-starting-chips = Con cuántas fichas empieza cada jugador de Izquierda Centro Derecha (por defecto 3, rango 1-10).
lrc-error-starting-chips-invalid = Las fichas iniciales deben estar entre { $min } y { $max }; el valor actual es { $count }.

lrc-line-format = { $player }: { $chips } { $chips ->
    [one] ficha
   *[other] fichas
}
