game-name-citadels = Ciudadelas

citadels-character-1 = Asesino
citadels-character-2 = Ladrón
citadels-character-3 = Mago
citadels-character-4 = Rey
citadels-character-5 = Obispo
citadels-character-6 = Comerciante
citadels-character-7 = Arquitecto
citadels-character-8 = Condotiero
citadels-character-9 = Reina

citadels-district-type-noble = Noble
citadels-district-type-religious = Religiosa
citadels-district-type-trade = Comercial
citadels-district-type-military = Militar
citadels-district-type-unique = Única

citadels-district-temple = Templo
citadels-district-church = Iglesia
citadels-district-monastery = Monasterio
citadels-district-cathedral = Catedral
citadels-district-manor = Mansión
citadels-district-castle = Castillo
citadels-district-palace = Palacio
citadels-district-tavern = Taberna
citadels-district-market = Mercado
citadels-district-trading_post = Puesto Comercial
citadels-district-docks = Muelles
citadels-district-harbor = Puerto
citadels-district-town_hall = Ayuntamiento
citadels-district-watchtower = Atalaya
citadels-district-prison = Prisión
citadels-district-barracks = Cuartel
citadels-district-fortress = Fortaleza
citadels-district-dragon_gate = Puerta del Dragón
citadels-district-factory = Fábrica
citadels-district-haunted_quarter = Barrio Encantado
citadels-district-imperial_treasury = Tesoro Imperial
citadels-district-keep = Torreón
citadels-district-laboratory = Laboratorio
citadels-district-library = Biblioteca
citadels-district-map_room = Sala de Mapas
citadels-district-quarry = Cantera
citadels-district-school_of_magic = Escuela de Magia
citadels-district-smithy = Herrería
citadels-district-statue = Estatua
citadels-district-thieves_den = Guarida de Ladrones
citadels-district-wishing_well = Pozo de los Deseos

citadels-game-start = Comenzó Ciudadelas.
citadels-selection-start-you = Ronda { $round }. Eliges un personaje primero.
citadels-selection-start = Ronda { $round }. { $player } elige un personaje primero.
citadels-selection-prompt = Elige un personaje ahora.
citadels-you-chose-character = Elegiste un personaje.
citadels-character-chosen = { $player } eligió un personaje.
citadels-select-character-line = { $brief ->
    [yes] { $character }
   *[no] Rango { $rank }: { $character }
}
citadels-turn-phase-start = Comienza el llamado de personajes.
citadels-no-characters = No hay { $characters }.
citadels-list-pair = { $first } o { $last }
citadels-list-series = { $head }, o { $last }
citadels-you-character-revealed = { $brief ->
    [yes] Revelas al { $character }.
   *[no] Revelas el rango { $rank }, { $character }.
}
citadels-character-revealed = { $brief ->
    [yes] { $player } revela al { $character }.
   *[no] { $player } revela el rango { $rank }, { $character }.
}
citadels-you-took-crown = Tomas la corona y elegirás primero la próxima ronda.
citadels-crown-taken = { $player } toma la corona.
citadels-you-king-heir = Revelas al Rey al final de la ronda y tomas la corona.
citadels-king-heir = { $player } revela al Rey al final de la ronda y toma la corona.
citadels-you-assassin-targeted = { $brief ->
    [yes] Nombras al { $character } para el asesinato.
   *[no] Nombras el rango { $rank }, { $character }, para el asesinato.
}
citadels-assassin-targeted = { $brief ->
    [yes] { $player }, el Asesino, nombra al { $character }.
   *[no] { $player }, el Asesino, nombra el rango { $rank }, { $character }.
}
citadels-character-killed-skip = { $brief ->
    [yes] El { $character } fue asesinado y pierde su turno.
   *[no] El rango { $rank }, { $character }, fue asesinado y pierde su turno.
}
citadels-you-character-killed-skip = { $brief ->
    [yes] Fuiste asesinado siendo el { $character } y pierdes este turno.
   *[no] Fuiste asesinado en el rango { $rank }, { $character }, y pierdes este turno.
}
citadels-you-thief-targeted = { $brief ->
    [yes] Robarás al { $character } cuando se revele ese personaje.
   *[no] Robarás el rango { $rank }, { $character }, cuando se revele ese personaje.
}
citadels-thief-targeted = { $brief ->
    [yes] { $player }, el Ladrón, marca al { $character } para el robo.
   *[no] { $player }, el Ladrón, marca el rango { $rank }, { $character }, para el robo.
}
citadels-you-thief-found-nothing = Tu robo no encuentra oro para robar.
citadels-thief-found-nothing = { $player }, el Ladrón, no encuentra oro para robar.
citadels-you-thief-stole-gold = Robas { $amount } de oro como el Ladrón.
citadels-thief-stole-gold = { $player }, el Ladrón, roba { $amount } de oro.
citadels-you-took-gold = Tomas { $amount } de oro.
citadels-player-took-gold = { $player } toma { $amount } de oro.
citadels-you-drew-options = Robas cartas de distrito y debes quedarte con una.
citadels-player-drew-options = { $player } roba cartas de distrito y debe quedarse con una.
citadels-player-kept-card = { $player } se queda con una carta de distrito.
citadels-you-kept-card = Te quedas con { $district }.
citadels-you-income-collected = Recolectas { $amount } de oro como el { $character }.
citadels-income-collected = { $player } recolecta { $amount } de oro como el { $character }.
citadels-you-architect-bonus = Robas { $count } cartas extra como el Arquitecto.
citadels-architect-bonus = { $player } roba { $count } cartas extra.
citadels-you-magician-swapped = Intercambias tu mano con { $target }.
citadels-magician-swapped = { $player } intercambia su mano con { $target }.
citadels-you-magician-redrew = Vuelves a robar { $count } cartas.
citadels-magician-redrew = { $player } vuelve a robar { $count } cartas.
citadels-you-laboratory-used = Usas el Laboratorio y ganas { $amount } de oro.
citadels-laboratory-used = { $player } usa el Laboratorio y gana { $amount } de oro.
citadels-you-smithy-used = Usas la Herrería y robas { $count } cartas.
citadels-smithy-used = { $player } usa la Herrería y roba { $count } cartas.
citadels-you-library-draw = Usas la Biblioteca y te quedas con las { $count } cartas robadas.
citadels-library-draw = { $player } usa la Biblioteca y se queda con las { $count } cartas robadas.
citadels-you-built-district = Construyes { $district } y pagas { $gold } de oro.
citadels-district-built = { $player } construye { $district } y paga { $gold } de oro.
citadels-thieves-den-payment = Descartas { $cards } para ayudar a pagar la Guarida de Ladrones.
citadels-you-city-completed = Completas tu ciudad con { $count } distritos.
citadels-city-completed = { $player } completa una ciudad con { $count } distritos.
citadels-you-queen-bonus = Ganas { $amount } de oro extra de la Reina.
citadels-queen-bonus = { $player } gana { $amount } de oro extra de la Reina.
citadels-you-warlord-destroyed = Destruyes { $district } de { $target }.
citadels-warlord-destroyed = { $player } destruye { $district } de { $target }.

citadels-take-gold = Tomar 2 de oro
citadels-draw-cards = Robar cartas de distrito
citadels-collect-income = Recolectar ingreso de personaje
citadels-magician-swap = Intercambiar manos
citadels-magician-redraw = Volver a robar cartas
citadels-use-laboratory = Usar Laboratorio
citadels-use-smithy = Usar Herrería
citadels-warlord-destroy = Destruir un distrito
citadels-confirm-redraw = Confirmar nuevo robo
citadels-build-thieves-den = Construir Guarida de Ladrones
citadels-end-turn = Terminar turno
citadels-read-status = Leer resumen de estado
citadels-read-status-detailed = Leer estado detallado
citadels-read-character = Leer personaje
citadels-read-hand = Leer mano
citadels-read-cities = Leer ciudades
citadels-read-discards = Leer descartes

citadels-assassinate-target-line = { $brief ->
    [yes] Asesinar al { $character }
   *[no] Asesinar rango { $rank }: { $character }
}
citadels-thief-target-line = { $brief ->
    [yes] Robar al { $character }
   *[no] Robar rango { $rank }: { $character }
}
citadels-magician-swap-line = Intercambiar con { $player } ({ $cards } cartas)
citadels-warlord-target-line = Destruir { $district } de { $player } por { $cost } de oro
citadels-build-card-line = Construir { $district } ({ $cost } de oro)
citadels-build-card-disabled-line = No se puede construir { $district } ({ $cost } de oro): { $reason }
citadels-district-line = { $district }, costo { $cost }, { $type }. { $description }
citadels-district-menu-line = { $district }, costo { $cost }, { $type }
citadels-toggle-selected = Seleccionado: { $district }, costo { $cost }
citadels-toggle-not-selected = No seleccionado: { $district }, costo { $cost }

citadels-build-error = No puedes construir { $district }: { $reason }
citadels-build-error-card-missing = Esa carta de distrito ya no está en tu mano.
citadels-build-reason-need-resource = Debes tomar oro o robar cartas de distrito antes de construir.
citadels-build-reason-limit = Ya construiste el { $limit } { $limit ->
    [one] distrito permitido
   *[other] distritos permitidos
} este turno.
citadels-build-reason-duplicate = Tu ciudad ya contiene { $district }, y no tienes la Cantera para permitir distritos duplicados.
citadels-build-reason-gold = Necesitas { $needed } más de oro.
citadels-build-reason-thieves-den-payment = Incluso después de descartar todas las demás cartas de tu mano, todavía necesitas { $needed } más de oro en valor de pago.

citadels-district-effect-none = Sin habilidad especial.
citadels-district-effect-dragon_gate = Fin de la partida: ganas 2 puntos extra.
citadels-district-effect-factory = Tus otros distritos únicos cuestan 1 menos al construir.
citadels-district-effect-haunted_quarter = Fin de la partida: puede contar como noble, religiosa, comercial, militar o única para el bono de cinco colores.
citadels-district-effect-imperial_treasury = Fin de la partida: ganas 1 punto por cada oro que aún tengas.
citadels-district-effect-keep = El Condotiero no puede destruir este distrito.
citadels-district-effect-laboratory = Una vez por turno, descarta una carta de tu mano para ganar 2 de oro.
citadels-district-effect-library = Cuando robes cartas de distrito, te quedas con ambas cartas robadas.
citadels-district-effect-map_room = Fin de la partida: ganas 1 punto por cada carta en tu mano.
citadels-district-effect-quarry = Puedes construir distritos duplicados en tu ciudad.
citadels-district-effect-school_of_magic = Durante el ingreso del Rey, el Obispo, el Comerciante o el Condotiero, este distrito cuenta como el tipo que elijas.
citadels-district-effect-smithy = Una vez por turno después de tomar recursos, paga 2 de oro para robar 3 cartas.
citadels-district-effect-statue = Fin de la partida: ganas 5 puntos si tienes la corona.
citadels-district-effect-thieves_den = Al construir este distrito, puedes descartar cartas de tu mano para pagar 1 de oro por cada carta descartada.
citadels-district-effect-wishing_well = Fin de la partida: ganas 1 punto por cada distrito único en tu ciudad, incluido este.

citadels-hand-header = Tu mano tiene { $count } cartas.
citadels-hand-empty = Tu mano está vacía.
citadels-cities-header = Ciudades en la mesa
citadels-city-empty = sin distritos
citadels-city-line = { $player }: { $count } distritos, { $gold } de oro, { $score } puntos. { $districts }
citadels-character-none = Actualmente no tienes ningún personaje. Tienes { $gold } de oro.
citadels-character-line = { $brief ->
    [yes] { $character }. Tienes { $gold } de oro.
   *[no] Rango { $rank }: { $character }. Tienes { $gold } de oro.
}
citadels-discards-none = ninguno
citadels-faceup-discards-line = Personajes descartados boca arriba: { $characters }

citadels-status-header = Estado de Ciudadelas
citadels-status-crown = Poseedor de la corona: { $player }
citadels-status-selection = Selección de personajes. { $player } está eligiendo.
citadels-status-rank-resolution = { $brief ->
    [yes] Llamando al { $character }.
   *[no] Llamando al rango { $rank }: { $character }.
}
citadels-status-turn = { $brief ->
    [yes] { $player } está tomando su turno como el { $character }.
   *[no] { $player } está tomando su turno en el rango { $rank }, { $character }.
}
citadels-status-turn-progress = Construidos { $builds } de { $limit } distritos permitidos este turno.
citadels-status-killed = { $brief ->
    [yes] Asesinado: { $character }.
   *[no] Rango asesinado: { $rank }, { $character }.
}
citadels-status-killed-none = Ningún personaje ha sido asesinado esta ronda.
citadels-status-robbed = { $brief ->
    [yes] Robado: { $character }.
   *[no] Rango robado: { $rank }, { $character }.
}
citadels-status-robbed-none = Ningún personaje ha sido marcado para robo esta ronda.
citadels-status-first-completed = Primera ciudad completada: { $player }

citadels-standings-header = Clasificación actual
citadels-standing-line = Rango { $rank }: { $player }, { $score } puntos, { $gold } de oro, { $districts } distritos, { $cards } cartas en mano.
citadels-end-line = Rango { $rank }: { $player }, { $score } puntos, { $gold } de oro, { $districts } distritos.
