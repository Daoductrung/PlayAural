game-name-lastoutpost = Último Bastión
lo-root-vitals = Salud { $hp }/{ $maximum }; PA { $ap }; { $item }.
lo-root-spectator = Observando Último Bastión.
lo-menu-attack = Atacar
lo-menu-move = Moverse
lo-menu-equipment = Armas y recarga
lo-menu-support = Ayuda y carga
lo-menu-interact = Objetivos y entorno
lo-menu-supplies = Suministros y mejoras
lo-menu-back = Volver al menú principal
lo-menu-available = { $menu }; Disponible
lo-menu-equipment-state = { lo-menu-equipment }: { $weapon }; en el cargador { $loaded }, reserva { $reserve }.
lo-shop-balance = Créditos: { $credits }.
lo-shop-done = Cerrar tienda
lo-help-shop-done = Cierra la tienda sin terminar tu turno. E o X también la cierran.
lo-key-finish-or-end = Confirmar preparación, cerrar tienda o terminar turno
lo-menu-close-information = Cierra primero el panel de información.
lo-help-menu-attack = Elige un objetivo para el arma, el cuchillo o la granada.
lo-help-menu-move = Rutas abiertas, costos de movimiento y ocupantes del destino.
lo-help-menu-equipment = Recarga o cambia de arma. Cambiar de arma no cuesta PA.
lo-help-menu-support = { $party_size ->
    [1] Cúrate o suelta la carga.
   *[other] Cura, reanima o transfiere la carga.
    }
lo-help-menu-interact = Restaura la energía y la radio, abre puertas o repara barricadas.
lo-help-menu-supplies = Compra suministros y mejoras. Las compras mantienen la tienda abierta. X vuelve atrás.
lo-help-menu-back = Vuelve al botón de tu categoría en el menú principal.
lo-empty-attack = No hay objetivos disponibles.
lo-empty-move = No hay rutas abiertas.
lo-empty-equipment = No hay acciones de arma disponibles.
lo-empty-preparation = No disponible durante la preparación.
lo-empty-support = No hay acciones de ayuda ni de carga disponibles.
lo-empty-interact = No hay interacciones disponibles.
lo-empty-supplies = No hay suministros disponibles aquí.
lo-move-location = { $zone }. { $description }
lo-destination = { $party_size ->
    [1] { $zone }; { $ap } PA. Enemigos: { $inside } dentro, { $outside } fuera. { $barricade }
   *[other] { $zone }; { $ap } PA. Zombis: { $inside } dentro, { $outside } fuera. Escuadrón: { $survivors }. { $barricade }
    }
lo-destination-survivor = { $name } ({ $condition })
lo-destination-barricade = Entrada enemiga; resistencia de la barricada { $strength }.
lo-enemies = Inspector de enemigos
lo-help-enemies = Primero los objetivos al alcance, luego los enemigos más lejanos y los refuerzos. Para atacar sigues necesitando tu turno, PA y munición.
lo-enemies-context = Objetivos desde { $zone }.
lo-enemies-spectator-context = Vista general desde { $zone }.
lo-enemies-empty = No hay enemigos en el mapa.
lo-enemy-detail = { $pack }. Salud por enemigo: { $health }. { $distance } { $access }
lo-enemy-distance = Distancia por ruta: { $count ->
    [one] { $count } conexión.
   *[other] { $count } conexiones.
    }
lo-enemy-unreachable = No hay ruta abierta.
lo-enemy-barricade = Tras una barricada de resistencia { $strength }; los ataques quedan bloqueados.
lo-enemy-reach = Al alcance: { $actions }.
lo-enemy-reposition = Fuera de alcance con tu equipo actual.
lo-enemy-observe = Vista de espectador.
lo-health = Comprobar salud
lo-help-health = Salud actual y estado de rescate.
lo-health-report = Salud { $hp }/{ $maximum }. { $condition }.
lo-health-upright = De pie
lo-health-downed = { $party_size ->
    [1] En el suelo
   *[other] En el suelo; fases de horda para el rescate: { $phases }
    }
lo-health-awaiting-recovery = A la espera de la recuperación de la oleada
lo-slot-primary = Equipar arma principal
lo-slot-sidearm = Equipar pistola
lo-error-slot-empty = No tienes un arma principal equipada.
lo-error-preparation = Las acciones de combate no están disponibles durante la preparación.
lo-option-voices = Diálogos de los personajes: { $enabled }
lo-change-voices = Diálogos de los personajes: { $enabled }.
lo-desc-voices = Diálogos de los personajes en inglés, con lenguaje fuerte. Los informes tácticos usan el idioma que hayas elegido.
lo-you = Tú
lo-team = { $party_size ->
    [1] Superviviente
   *[other] Equipo
    }
lo-none = Ninguno
lo-yes = Sí
lo-no = No
lo-inside = dentro
lo-outside = fuera de la barricada
lo-message = { $text }
lo-term-none = { lo-none }
lo-term-courtyard = Patio
lo-term-gatehouse = Caseta de guardia
lo-term-workshop = Taller
lo-term-infirmary = Enfermería
lo-term-loading = Muelle de carga
lo-term-generator = Sala del generador
lo-term-pump = Sala de bombas
lo-term-roof = Azotea de radio
lo-term-walker = { $count ->
    [one] caminante
   *[other] caminantes
    }
lo-term-hound = { $count ->
    [one] sabueso
   *[other] sabuesos
    }
lo-term-brute = { $count ->
    [one] bruto
   *[other] brutos
    }
lo-term-pistol = Pistola M1911
lo-term-rifle = Fusil AK
lo-term-shotgun = Escopeta
lo-term-marksman = Fusil de precisión
lo-term-knife = Cuchillo
lo-term-medkit = Botiquín
lo-term-grenade = Granada
lo-term-endurance = Aguante
lo-term-medic = Médico de campo
lo-term-quickhands = Manos rápidas
lo-term-combat = Fase de los supervivientes
lo-term-resolving = Acción en curso
lo-term-reloading = Recargando
lo-term-prep = Preparación
lo-term-finished = Finalizada
lo-term-dempsey = Dempsey
lo-term-nikolai = Nikolai
lo-term-takeo = Takeo
lo-term-richtofen = Richtofen
lo-term-victory = { $party_size ->
    [1] Sobrevivió
   *[other] El escuadrón sobrevivió
    }
lo-term-objectives = Radio o energía sin completar
lo-term-overwhelmed = { $party_size ->
    [1] La horda te superó
   *[other] La horda superó al equipo
    }
lo-term-overrun = Se alcanzó el límite de tiempo de la oleada
lo-turn-resolving = { lo-error-resolving }
lo-turn-prep = { $survivor_count ->
    [1] Preparación. Confirma tu preparación para iniciar la siguiente oleada.
   *[other] Preparación. La siguiente oleada empieza cuando todos hayan confirmado su preparación.
    }
lo-map = Mapa y grupos enemigos
lo-forecast = Pronóstico de la próxima horda
lo-inventory = Equipo y suministros
lo-help-map = Rutas, barricadas, grupos enemigos y calendario de llegadas. El audio mira al norte.
lo-help-forecast = La próxima fase de horda si nadie actúa más.
lo-help-inventory = Tus créditos, armas y suministros, además de las piezas para reparaciones y objetivos.
lo-header = Oleada { $wave }; ciclo { $cycle }/{ $limit }. { $phase }. { $zone }. Salud { $hp }; PA { $ap }; créditos { $credits }; piezas { $parts }.
lo-spectator-header = Observando. Oleada { $wave }; ciclo { $cycle }. { $phase }; piezas { $parts }.
lo-objectives = Objetivos
lo-survivor = { $name } ({ $character }): { $zone }; salud { $hp }/{ $maximum }; PA { $ap }. { $condition }; preparación { $ready }; protección { $guard }.
lo-zone = { $zone }: { $description } Rutas abiertas: { $links }. Enemigos: { $enemies }. { $barrier } Espacios de contacto cuerpo a cuerpo: { $frontage }.
lo-pack = { $count } { $kind }, { $zone }, { $side }; salud combinada { $hp }
lo-incoming = { $zone }: { $count ->
    [one] 1 refuerzo
   *[other] { $count } refuerzos
    } tras la fase de horda { $cycle }; primera acción en la fase { $first }.
lo-forecast-caveat = Supone que no hay más acciones. Los brutos ocupan dos espacios de contacto; los demás enemigos, uno. Los enemigos amontonados siguen disputando los objetivos. Leer no consume tiempo.
lo-weapon-status = { $name }, { $weapon }: en el cargador { $ammo }, reserva { $reserve }; daño { $damage } por objetivo, máximo de objetivos { $targets }; alcance de { $minimum } a { $maximum }; equipada: { $equipped }.
lo-kit-status = { $name }: créditos { $credits }; botiquines { $medkits }, granadas { $grenades }; ventajas { $perks }.
lo-action-label = { $action }: { $detail } ({ $ap } PA)
lo-action-label-simple = { $action } ({ $ap } PA)
lo-reload-detail = { $weapon }; cargador { $loaded }/{ $capacity }, reserva { $reserve }
lo-attack-detail = { $weapon }, { $ammo } en el cargador; { $target }
lo-price = { $item }, { $cost } créditos
lo-ammo-price = { $item }, { $amount ->
    [one] 1 bala
   *[other] { $amount } balas
    } de reserva por { $cost } créditos
lo-parts-price = { $item }, { $cost } piezas
lo-work-price = { $item }, { $done } de { $total } unidades de trabajo, { $cost } piezas por pagar
lo-verb-fire = Disparar
lo-verb-knife = Atacar con cuchillo
lo-verb-reload = Recargar
lo-verb-grenade = Lanzar granada
lo-verb-heal = Usar botiquín
lo-verb-revive = Reanimar
lo-verb-open = Abrir puerta
lo-verb-repair = Reparar barricada
lo-verb-work = Reparar equipo
lo-verb-ammo = Comprar munición
lo-verb-buy = Comprar equipo
lo-verb-perk = Comprar ventaja
lo-verb-upgrade = Mejorar arma principal
lo-verb-equip = Equipar
lo-verb-ready = Confirmar preparación para la siguiente oleada
lo-verb-end = Terminar turno
lo-help-fire = Impacta primero al enemigo más herido del grupo. Las escopetas alcanzan hasta a dos. Las barricadas protegen a los enemigos de fuera hasta que son destruidas.
lo-help-knife = 1 de daño; 1 PA; misma zona. Sin munición.
lo-help-move = 1 PA por conexión; 2 al salir de una zona con enemigos. Llevar carga suma 1 PA.
lo-help-reload = 1 PA; al terminar pasa la munición de reserva al arma. Puedes seguir caminando. Manos rápidas anula el costo en PA de la primera recarga de cada oleada.
lo-help-grenade = { $party_size ->
    [1] 3 de daño a hasta cuatro enemigos; 1 PA. Tu zona o una zona adyacente visible. Solo alcanza a los enemigos dentro del perímetro.
   *[other] 3 de daño a hasta cuatro enemigos; 1 PA. Tu zona o una zona adyacente visible. Solo alcanza a los enemigos dentro del perímetro; sin fuego amigo.
    }
lo-help-heal = 1 botiquín y 1 PA; restablece hasta 3 de salud a un superviviente de pie en tu zona.
lo-help-revive = Reanima con 2 de salud; 2 PA, o 1 con Médico de campo. Misma zona. Sin turno extra.
lo-help-revive-preview = { lo-help-revive } Si no hay más acciones, { $target } tendría { $health } de salud tras la próxima fase de horda.
lo-gate-link = { $origin } a { $destination }
lo-gate-service = Puerta de servicio
lo-gate-shortcut = Atajo de la enfermería
lo-gate-roof = Puerta de acceso a la radio
lo-gate-crossing = Cruce de carga
lo-gate-bulkhead = Mamparo estanco
lo-gate-status = { $gate }: abierta { $opened }; { $cost } piezas; requiere energía { $power }. Rutas: { $routes }. Espacios de contacto tras abrirla: { $frontages }.
lo-help-open-routes = { $cost } piezas; 1 PA; tu zona debe estar despejada. Abre { $routes } de forma permanente para ambos bandos. Requiere energía: { $power }. Espacios de contacto después: { $frontages }.
lo-frontage-site = { $zone }, { $count } espacios de contacto
lo-gate-opened-routes = Nuevas rutas para ambos bandos: { $routes }.
lo-defense-until-clear = Sigue defendiendo { $zone } hasta que termine la oleada; los enemigos aún pueden dañar el repetidor.
lo-help-repair = 1 pieza y 1 PA; restablece 2 de resistencia de la barricada, hasta 4. Una vez por ciclo; zona despejada.
lo-help-work = 1 PA por unidad de trabajo. La primera unidad paga el costo de piezas indicado. Requiere zona despejada; la radio necesita energía.
lo-help-ammo = Capacidad de reserva: tres cargadores. En combate, compra en una estación de munición despejada. En la preparación, compra en cualquier parte.
lo-help-buy = Solo en la preparación. Las armas principales sustituyen a la actual. La primera compra incluye munición; volver a comprarla conserva la munición anterior. Sin reembolso.
lo-help-perk = Requiere energía; máximo dos ventajas. Aguante: +2 de salud. Médico de campo: reanimar por 1 PA. Manos rápidas: la primera recarga de cada oleada no cuesta PA.
lo-help-upgrade = Requiere energía; 500 créditos por tipo de arma. Daño: AK 4, escopeta 6, fusil de precisión 9.
lo-help-equip = Cambia de arma; no cuesta PA.
lo-help-ready = { $survivor_count ->
    [1] Inicia la siguiente oleada.
   *[other] Alterna tu preparación. Cuando todos confirmen, empieza la siguiente oleada. Cancela tu preparación para volver a comprar.
    }
lo-help-end = { $party_size ->
    [1] Descarta los PA restantes. Los enemigos actúan después.
   *[other] Descarta los PA restantes. Los enemigos actúan cuando el escuadrón termina.
    }
lo-error-unavailable = No disponible en esta fase.
lo-error-stale = Esa opción ya no está disponible.
lo-error-turn = { action-not-your-turn }
lo-error-down = Estás en el suelo.
lo-error-ready = Cancela tu preparación antes de comprar.
lo-error-ap = No tienes suficientes PA.
lo-error-range = Objetivo fuera del alcance de tiro o de la línea de visión.
lo-error-ammo = No hay suficiente munición cargada.
lo-error-grenade = No tienes granadas.
lo-error-medkit = No tienes botiquines.
lo-error-engaged = Despeja primero los enemigos de esta zona.
lo-error-complete = Este objetivo ya está completado.
lo-error-power = Restaura primero la energía.
lo-error-parts = No hay suficientes piezas.
lo-error-credits = No tienes suficientes créditos.
lo-error-equipped = Esta arma ya está equipada.
lo-error-resolving = La acción actual se está resolviendo.
lo-event-wave = Oleada { $amount }; { $count } enemigos. { $deployment }.
lo-deployment-now = { $count } fuera ahora
lo-deployment-later = { $count ->
    [one] 1 llega tras la fase de horda { $cycle }
   *[other] { $count } llegan tras la fase de horda { $cycle }
    }
lo-event-final_warning = Última oleada. Trabajo de infraestructura pendiente: { $amount }; piezas por pagar: { $count }. Termina la infraestructura y la misión antes de que acabe la oleada.
lo-event-clear = { $party_size ->
    [1] Oleada { $amount } superada. +{ $count } créditos; +3 piezas. Recuperas { $healing } de salud, o vuelves con { $recovery } de salud si habías caído. Hasta { $ammo } de munición de reserva para la pistola. Preparación.
   *[other] Oleada { $amount } superada. Cada superviviente gana { $count } créditos y hasta { $ammo } de munición de reserva para la pistola. Los supervivientes de pie recuperan { $healing } de salud; los que habían caído vuelven con { $recovery } de salud. Equipo: +3 piezas. Preparación.
    }
lo-event-fire = { $actor } disparó { $item } hacia { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife = { $actor } atacó con cuchillo en { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade = { $actor } detonó una granada en { $zone }. { $hits }. { lo-combat-kills }
lo-event-move = { $actor } se movió de { $origin } a { $zone }.
lo-event-reload = { $actor } cargó { $amount ->
    [one] 1 bala
   *[other] { $amount } balas
    } en { $item }.
lo-reload-start = { $actor } está recargando.
lo-reload-start-personal = Recargando.
lo-error-reloading = { lo-reload-start-personal }
lo-event-heal = { $actor } curó a { $target }; salud actual { $amount }.
lo-event-revive = { $actor } reanimó a { $target } con { $amount } de salud.
lo-event-open = { $actor } abrió { $item }; piezas restantes: { $amount }. { $routes }
lo-event-repair = { $actor } reparó la barricada de { $zone } hasta una resistencia de { $amount }.
lo-event-work = { $count ->
    [1] { $actor } restauró { $item } en { $zone }.
   *[0] { $actor } avanzó en { $item }, en { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo = { $actor } compró { $amount ->
    [one] 1 bala
   *[other] { $amount } balas
    } para { $item } por { $count } créditos.
lo-event-buy = { $actor } compró { $item }; créditos restantes: { $amount }.
lo-event-perk = { $actor } adquirió { $item }.
lo-event-upgrade = { $actor } mejoró { $item }.
lo-event-equip = { $actor } equipó { $item }.
lo-event-ready = { $actor }: { $amount ->
    [1] preparación confirmada para la siguiente oleada.
   *[0] preparación cancelada.
    }
lo-event-end = { $actor } terminó su turno.
lo-event-barrier = { $zone }: { $count ->
    [one] 1 golpe
   *[other] { $count } golpes
    } de { $item } contra la barricada; resistencia actual { $amount }.
lo-event-enter = { $count ->
    [one] Entra { $count } { $item } en { $zone }.
   *[other] Entran { $count } { $item } en { $zone }.
    }
lo-event-approach = { $count ->
    [one] { $count } { $item } se mueve de { $origin } a { $zone }.
   *[other] { $count } { $item } se mueven de { $origin } a { $zone }.
    }
lo-event-hurt = { $target }: { $count ->
    [one] 1 ataque
   *[other] { $count } ataques
    } de { $item }, { $amount } de daño total en { $zone }.
lo-event-down = { $target } ha caído en { $zone }. Puede reanimarse durante las próximas dos fases de horda.
lo-event-incapacitated = { $target } queda fuera de combate hasta la siguiente oleada.
lo-event-recovery = { $target }: última recuperación de emergencia. Salud { $amount }; en el próximo turno, { $count } PA. La carga se queda donde cayó.
lo-event-arrivals = { $count ->
    [one] Hay 1 refuerzo fuera. Actúa en la próxima fase de horda.
   *[other] Hay { $count } refuerzos fuera. Actúan en la próxima fase de horda.
    }
lo-event-finish = { $item }. Oleadas superadas: { $amount } de { $waves }.
lo-result-cycles = Fases de horda: { $count }.
lo-error-magazine-full = El cargador equipado ya está lleno.
lo-error-reserve-empty = No queda munición de reserva.
lo-error-barrier-full = Esta barricada ya tiene toda su resistencia.
lo-error-already-repaired = Esta barricada ya se reparó en este ciclo.
lo-error-weapon-owned = Ya llevas esta arma principal.
lo-error-kit-capacity = Has alcanzado la capacidad de botiquines.
lo-error-grenade-capacity = Has alcanzado la capacidad de granadas.
lo-error-ammo-capacity = Has alcanzado la capacidad de munición de reserva.
lo-error-perk-owned = Ya tienes esta ventaja.
lo-error-perk-capacity = Has alcanzado el límite de ventajas.
lo-error-no-primary = Compra primero un arma principal.
lo-error-upgraded = Esta arma ya está mejorada.
lo-event-heal-self = { $actor } usó un botiquín; salud actual { $amount }.
lo-event-heal-self-personal = Te curaste; salud actual { $amount }.
lo-event-heal-target = { $actor } te curó; salud actual { $amount }.
lo-event-revive-target = { $actor } te reanimó con { $amount } de salud. Actúas en el próximo ciclo.
lo-event-hurt-personal = Recibiste { $count ->
    [one] 1 ataque
   *[other] { $count } ataques
    } de { $item }, { $amount } de daño total en { $zone }.
lo-event-down-personal = Has caído en { $zone }. Tu equipo tiene las próximas dos fases de horda para reanimarte.
lo-event-down-solo-recovery = { $target } cayó en { $zone }. Recuperación de emergencia: { $recovery_seconds } segundos después de esta fase de horda.
lo-event-down-solo-recovery-personal = Caíste en { $zone }. Recuperación de emergencia: { $recovery_seconds } segundos después de esta fase de horda.
lo-event-down-solo-final = { $target } cayó en { $zone }. No quedan supervivientes ni recuperaciones.
lo-event-down-solo-final-personal = Caíste en { $zone }. No quedan supervivientes ni recuperaciones.
lo-event-incapacitated-personal = Quedas fuera de combate hasta la siguiente oleada.
lo-event-recovery-personal = Usaste tu última recuperación de emergencia. Salud { $amount }; en el próximo turno, { $count } PA. La carga se queda donde caíste.
lo-event-fire-personal = Disparaste { $item } hacia { $zone }. { $hits }. { lo-combat-kills }
lo-event-knife-personal = Atacaste con cuchillo en { $zone }. { $hits }. { lo-combat-kills }
lo-event-grenade-personal = Lanzaste una granada hacia { $zone }. { $hits }. { lo-combat-kills }
lo-event-move-personal = Te moviste de { $origin } a { $zone }.
lo-event-reload-personal = Cargaste { $amount ->
    [one] 1 bala
   *[other] { $amount } balas
    } en { $item }.
lo-event-heal-personal = Curaste a { $target }; salud actual { $amount }.
lo-event-revive-personal = Reanimaste a { $target } con { $amount } de salud.
lo-event-open-personal = Abriste { $item }; piezas restantes: { $amount }. { $routes }
lo-event-repair-personal = Reparaste la barricada de { $zone } hasta una resistencia de { $amount }.
lo-event-work-personal = { $count ->
    [1] Restauraste { $item } en { $zone }.
   *[0] Avanzaste en { $item }, en { $zone }: { $amount }/{ $total }.
    }
lo-event-ammo-personal = Compraste { $amount ->
    [one] 1 bala
   *[other] { $amount } balas
    } para { $item } por { $count } créditos.
lo-event-buy-personal = Compraste { $item }; créditos restantes: { $amount }.
lo-event-perk-personal = Adquiriste { $item }.
lo-event-upgrade-personal = Mejoraste { $item }.
lo-event-equip-personal = Equipaste { $item }.
lo-event-ready-personal = { $amount ->
    [1] Preparación confirmada para la siguiente oleada.
   *[0] Preparación cancelada.
    }
lo-event-end-personal = Terminaste tu turno.
lo-term-horde = enemigos
lo-help-move-destination = { $description } { lo-help-move }
lo-zone-description-courtyard = Un hormigón agrietado rodea un asta de bandera vacía bajo el cielo abierto. El Taller queda al oeste y la Enfermería al este; al sur, la Caseta de guardia da a la oscuridad que se extiende más allá del perímetro.
lo-zone-description-gatehouse = Al sur del Patio, el techo de la caseta de guardia se ha derrumbado y deja las tablas astilladas expuestas a la noche. La silla vacía del guardia mira hacia la entrada exterior, donde la valla del perímetro se encuentra con el camino.
lo-zone-description-workshop = Manchas de aceite se extienden bajo bancos de trabajo abandonados, y el óxido surca las paredes de chapa. El casillero de munición está contra el muro del fondo; una puerta de servicio conduce hacia el generador.
lo-zone-description-infirmary = Estrechas camillas alinean una sala de madera al este del Patio. De un carrito volcado cuelgan vendas polvorientas, y una luz pálida se refleja en el cristal de la ventana. Un pasaje lateral lleva hacia la Sala de bombas.
lo-zone-description-loading = Una cubierta de acero oxidado pasa junto a pilas de palés vacíos bajo el cielo abierto. El Taller queda al sur; al este, un pasaje se interna en la humedad de la Sala de bombas.
lo-zone-description-generator = Un generador achaparrado llena una cámara de hormigón más allá de la puerta de servicio del Taller. Gruesos cables cruzan el suelo metálico hacia un cuadro de mandos marcado por el uso. Aquí hay que restaurar la energía del puesto.
lo-zone-description-pump = Una capa de agua poco profunda cubre el suelo bajo gruesas tuberías y válvulas corroídas. Una marca de marea mancha las paredes de hormigón. Aquí confluyen el pasaje de la Enfermería y la ruta desde el Muelle de carga.
lo-zone-description-roof = Una antena se inclina sobre una azotea de hormigón desnudo, con los cables tensores estirados contra el cielo. La radio está en un armario impermeable maltrecho. Puertas de acceso con energía protegen los accesos desde abajo.
lo-option-map = Mapa: { $value }
lo-prompt-map = Elige un mapa
lo-change-map = Mapa configurado en { $value }.
lo-desc-map = Puesto Abandonado: una guarnición maltrecha en torno a un patio abierto. Estación de Maniobras: vías desiertas bajo un estrecho paso elevado. Planta Inundada: salas de maquinaria anegadas, divididas por pesadas compuertas.
lo-option-mode = Modo: { $value }
lo-prompt-mode = Elige un modo
lo-change-mode = Modo configurado en { $value }.
lo-desc-mode = Operaciones: misiones e infraestructura. Asedio: defiende la integridad del repetidor. Salvamento: recupera cargamento. Extracción clásica: ocho oleadas, energía, radio y un último abastecimiento.
lo-extraction-route = Oleada { $wave }: lleva suministros de { $pickup } a { $destination } con un plazo en fases de horda de { $deadline }. Despeja las zonas de recogida y de entrega. Con carga: +1 PA por movimiento, solo pistola.
lo-option-difficulty = Dificultad: { $value }
lo-prompt-difficulty = Elige la dificultad
lo-change-difficulty = Dificultad configurada en { $value }.
lo-desc-difficulty = Recluta: más recuperación y suministros. Estándar: hordas más fuertes y condiciones cambiantes. Veterano: presión máxima, ingresos escasos, sin curación gratuita entre oleadas ni munición gratuita de pistola.
lo-error-scenario = Mapa, modo o dificultad no compatibles. Revisa las opciones de la sala de espera.
lo-event-start = { $map }. { $mode }, { $difficulty }. { $waves } oleadas. Inicio en { $spawn }.
lo-scenario-status = { $map }; { $mode }; { $difficulty }. { $condition }.
lo-mission-status-retrieve = Recupera la carga en { $cargo }; portador: { $carrier }; entrégala en { $destination }. Fases de horda restantes: { $remaining }.
lo-mission-status-relay = Terminales del repetidor: { $zone } y { $destination }. Fases de horda restantes: { $remaining }.
lo-mission-status-hold = Defiende { $zone }: { $progress } de { $total } fases de defensa. Fases de horda restantes: { $remaining }.
lo-mission-help-retrieve = 1 PA para recoger, entregar, pasar o soltar la carga. Se requiere zona despejada, salvo para soltarla. Con carga: +1 PA por movimiento, solo pistola. Si caes, la carga se suelta; su plazo sigue corriendo.
lo-mission-help-relay = { $survivor_count ->
    [1] 1 PA por terminal en una zona despejada. Activa ambos puntos; las activaciones se conservan entre ciclos. Ambos puntos deben quedar despejados tras la horda.
   *[other] 1 PA por terminal en una zona despejada. Dos supervivientes activan puntos distintos en el mismo ciclo y luego permanecen de pie allí durante la horda. Ambos puntos deben quedar despejados al final.
    }
lo-mission-help-hold = Mantén a un superviviente de pie en el punto, sin enemigos dentro, al final de dos fases de horda. Un punto vacío o disputado pierde un avance. En Asedio, protege el repetidor hasta que termine la oleada; incumplir el plazo cuesta integridad.
lo-terminal-status = { $zone }: activada por { $actor }.
lo-verb-mission = Interacción de misión
lo-verb-handoff = Pasar la carga
lo-verb-drop = Soltar la carga
lo-verb-guard = Protegerse
lo-help-mission = 1 PA; realiza la tarea marcada en una zona despejada.
lo-help-handoff = 1 PA; transfiere la carga a un compañero de pie en la misma zona despejada.
lo-help-drop = 1 PA; suelta la carga aquí. Restablece el movimiento normal y el disparo con el arma principal.
lo-help-guard = 1 PA; intercepta el próximo ataque local y reduce su daño en uno. Caduca en el próximo ciclo; no se acumula ni atrae a enemigos lejanos.
lo-error-guarded = Ya te has protegido.
lo-error-carrying = La carga impide disparar el arma principal. Usa tu pistola o suelta la carga.
lo-error-terminal = Esta terminal ya está activa.
lo-error-relay-partner = Otro superviviente debe activar la otra terminal.
lo-task-activate = Activa esta terminal del repetidor; punto asociado: { $zone }
lo-task-pickup = Recoge la carga para { $zone }
lo-task-deliver = Entrega la carga en { $zone }
lo-event-mission_complete = { $party_size ->
    [1] Misión completada: { $item } ({ $sites }). +{ $count } créditos; +1 pieza. { $defense }
   *[other] Misión completada: { $item } ({ $sites }). Cada superviviente +{ $count } créditos; el equipo +1 pieza. { $defense }
    }
lo-event-mission_failed = Misión fallida: { $item }. Misiones fallidas: { $amount }.
lo-event-mission_clock = { $item }: fases de horda restantes: { $amount }.
lo-event-mission_pressure = { $count ->
    [one] El ruido de la misión atrajo a 1 caminante fuera de { $zone }. Se activa en la próxima fase de horda.
   *[other] El ruido de la misión atrajo a { $count } caminantes fuera de { $zone }. Se activan en la próxima fase de horda.
    }
lo-event-hold_progress = Defensa en { $zone }: { $amount } de { $count } fases aseguradas.
lo-event-core_damage = El repetidor de { $zone } pierde { $amount } de integridad; integridad restante: { $count }.
lo-event-relay_reset = Repetidores: { $item }.
lo-event-cargo_lost = La carga se soltó en { $zone }.
lo-event-condition = { $item }. Primeros refuerzos tras la fase de horda { $amount }.
lo-term-outpost = Puesto Abandonado
lo-term-switchyard = Estación de Maniobras
lo-term-floodworks = Planta Inundada
lo-term-operations = Operaciones
lo-term-siege = Asedio
lo-term-salvage = Salvamento
lo-term-classic = Extracción clásica
lo-term-recruit = Recluta
lo-term-standard = Estándar
lo-term-veteran = Veterano
lo-term-retrieve = Recuperación de carga
lo-term-relay = Repetidor coordinado
lo-term-hold = Defensa de sector
lo-term-mission_quota = No se cumplió el requisito de misiones
lo-term-core_lost = Repetidor destruido
lo-term-latched = las terminales activadas siguen listas
lo-term-reset = activa de nuevo ambas terminales en el mismo ciclo
lo-term-condition-normal = Condiciones despejadas
lo-term-condition-rush = Refuerzos tempranos
lo-term-condition-fog = Niebla: las armas de fuego solo alcanzan una conexión
lo-term-condition-battering = Horda embestidora: un punto extra de daño a las barricadas
lo-term-condition-shortage = Escasez de suministros: los cargadores de reserva cuestan 90 créditos
lo-term-depot = Estación de pasajeros
lo-term-west_tracks = Vías oeste
lo-term-east_tracks = Vías este
lo-term-signal_box = Caseta de señales
lo-term-freight = Patio de carga
lo-term-maintenance = Cobertizo de mantenimiento
lo-term-switchgear = Sala de interruptores
lo-term-overpass = Paso elevado
lo-term-tower = Torre de radio
lo-term-tunnel = Túnel ferroviario
lo-term-quay = Muelle de desembarco
lo-term-foyer = Vestíbulo de entrada
lo-term-canal = Canal de drenaje
lo-term-filter = Lechos filtrantes
lo-term-control = Sala de control
lo-term-laboratory = Laboratorio
lo-term-archive = Archivo de suministros
lo-term-turbine = Sala de turbinas
lo-term-skybridge = Pasarela de radio
lo-term-clinic = Clínica
lo-event-guard = { $actor } se protegió: el próximo golpe recibido causa un punto menos de daño.
lo-event-guard-personal = Te protegiste: el próximo golpe recibido causa un punto menos de daño.
lo-event-cargo_pickup = { $actor } recoge la carga en { $zone } para { $origin }.
lo-event-cargo_pickup-personal = Recoges la carga en { $zone } para { $origin }.
lo-event-cargo_deliver = { $actor } entrega la carga en { $zone }.
lo-event-cargo_deliver-personal = Entregas la carga en { $zone }.
lo-event-cargo_drop = { $actor } suelta la carga en { $zone }.
lo-event-cargo_drop-personal = Sueltas la carga en { $zone }.
lo-event-cargo_handoff = { $actor } pasa la carga a { $target } en { $zone }.
lo-event-cargo_handoff-personal = Pasas la carga a { $target } en { $zone }.
lo-event-relay_armed = { $actor } activa la terminal de { $zone }; terminales armadas: { $amount }.
lo-event-relay_armed-personal = Activas la terminal de { $zone }; terminales armadas: { $amount }.
lo-event-cargo_handoff-target = { $actor } te pasa la carga en { $zone }.
lo-zone-description-depot = Filas de bancos vacíos dan a un panel de salidas detenido en trenes cancelados. El polvo apaga el suelo de hormigón. Las puertas de ambos extremos del vestíbulo salen a las vías del oeste y del este.
lo-zone-description-west_tracks = Una pasarela de acero sigue los rieles oxidados bajo lámparas de señales apagadas. Los postes de la valla marcan el borde del patio; más allá de la estación, la Caseta de señales se alza por el lado norte.
lo-zone-description-east_tracks = Vagones vacíos se alinean junto a una franja de cubierta de acero combada. Los rieles se pierden en la oscuridad más allá del perímetro; el Patio de carga se abre hacia el norte.
lo-zone-description-signal_box = Palancas amontonadas llenan una cabina de madera sobre un diagrama de vías desvaído. Las ventanas dan a los rieles del oeste. Hay pasajes hacia el Cobertizo de mantenimiento y hacia las escaleras del Paso elevado.
lo-zone-description-freight = Contenedores de carga se ciernen sobre un patio de planchas de acero abolladas. De un bastidor de carga cuelgan cadenas sueltas. La puerta del cruce guarda el acceso al Paso elevado; otra ruta entra en el Túnel ferroviario.
lo-zone-description-maintenance = Ruedas desmontadas y herramientas grasientas se alinean en un cobertizo de chapa ondulada. Un casillero de munición está sobre el suelo de hormigón manchado, junto a la puerta de servicio de la Sala de interruptores.
lo-zone-description-switchgear = Hileras de pesados interruptores llenan una sala de hormigón al otro lado de la puerta de servicio. Gruesos cables desaparecen bajo las placas metálicas del suelo, y las etiquetas de advertencia se despegan de los armarios. Aquí hay que restaurar la energía del patio.
lo-zone-description-overpass = Una rejilla de acero abierta salva las vías, con solo un estrecho pasamanos frente al vacío. La Caseta de señales y el Patio de carga quedan abajo; la Torre de radio se alza al frente, hacia el norte.
lo-zone-description-tower = Un escritorio de radio y una silla de madera gastada llenan la cabina sobre las vías. Las ventanas dan al patio por todos lados. Hace falta energía para abrir las puertas de acceso de abajo.
lo-zone-description-tunnel = Los rieles desaparecen en un túnel de hormigón marcado por el hollín y las filtraciones. El Patio de carga queda a tu espalda; un pasaje lateral asciende hacia la puerta de acceso de la Torre de radio.
lo-zone-description-quay = Tablones de desembarco combados sobresalen sobre el agua negra, con las amarras sueltas colgando. Aquí termina el perímetro sur. Más adelante, la entrada de hormigón de la planta se abre al Vestíbulo de entrada.
lo-zone-description-foyer = Manchas de agua trepan por las paredes de hormigón bajo un plano de evacuación desvaído. Esta entrada angosta se bifurca hacia el Canal de drenaje, al oeste, y el Archivo de suministros, al este.
lo-zone-description-canal = Un agua poco profunda corre entre altas orillas de hormigón y arrastra restos de maleza desde más allá del perímetro. El canal gira al norte hacia los Lechos filtrantes; el vestíbulo queda al este.
lo-zone-description-filter = El agua de la inundación lame filas de lechos filtrantes obstruidos bajo paredes de metal oxidado. La puerta de servicio conduce hacia las turbinas; un pesado mamparo separa esta sala de la Sala de control.
lo-zone-description-control = Una larga hilera de indicadores y pantallas rotas domina un suelo metálico. El Laboratorio se abre al este, el mamparo de los filtros al oeste; el acceso norte sube hacia la Pasarela de radio.
lo-zone-description-laboratory = Frascos de muestras empañados abarrotan los bancos, y el vidrio roto brilla sobre el hormigón. Las puertas conectan el Archivo de suministros, la Sala de control y la Clínica; todas las rutas atraviesan esta sala de trabajo abandonada.
lo-zone-description-archive = Libros de registro hinchados de agua se hunden en estantes de madera junto a cajas de suministros selladas. El casillero de munición ocupa el rincón más seco. El vestíbulo queda al oeste y el Laboratorio al norte.
lo-zone-description-turbine = Enormes carcasas de turbinas llenan una nave metálica cavernosa al otro lado de la puerta de servicio. Placas de mantenimiento forman el suelo entre ellas. Los controles de energía están bajo la ruta que sube a la Pasarela de radio.
lo-zone-description-skybridge = Un estrecho puente de acero cuelga sobre las salas norte de la planta, expuesto al viento. Un armario de radio se alza bajo una antena; aquí convergen los accesos desde la Sala de control, la Clínica y las turbinas.
lo-zone-description-clinic = Cortinas de privacidad desvaídas dividen una sala de hormigón flanqueada de camillas de exploración. La humedad se ha colado bajo los armarios de medicinas. El Laboratorio queda al sur; otro acceso sube hacia la Pasarela de radio.
lo-event-mission_start-retrieve = Carga: de { $zone } a { $origin }. Plazo en fases de horda: { $amount }.
lo-event-mission_start-relay = Repetidores: { $zone } y { $origin }. Plazo en fases de horda: { $amount }.
lo-event-mission_start-hold = Defiende { $zone }. Plazo en fases de horda: { $amount }.
lo-error-visibility = La niebla bloquea los disparos a más de una conexión.
lo-help-weapon = Daño { $damage }; mejorada { $upgraded }; objetivos { $targets }; alcance { $minimum }–{ $maximum }; cargador { $magazine }; { $rounds } balas por disparo; { $price } créditos. Sustituye al arma principal; sin reembolso.
lo-error-barricade = La barricada bloquea este ataque.
lo-combat-hit = { $enemy }: { $damage } de daño
lo-combat-outside = { $zone }, { lo-outside }
lo-objective-generator = Energía
lo-objective-radio = Radio
lo-combat-kills = { $count ->
    [0] { "" }
    [one] 1 eliminación.
   *[other] { $count } eliminaciones.
    }
lo-shop-ready = Terminar de comprar y confirmar preparación
lo-help-shop-ready = E cierra la tienda y confirma tu preparación. X vuelve atrás sin confirmarla.
lo-already-ready = { $party_size ->
    [1] Preparación ya confirmada.
   *[other] Preparación confirmada. Esperando al escuadrón.
    }
lo-help-teammates = { $party_size ->
    [1] Tu posición, salud y personaje.
   *[other] Posiciones, salud, plazos de rescate y personajes del escuadrón.
    }
lo-help-objectives = Requisitos de victoria, progreso de la infraestructura y misión activa.
lo-teammates = { $party_size ->
    [1] Personaje
   *[other] Compañeros
    }
lo-required = Obligatorio
lo-optional = Opcional
lo-complete = Completado
lo-incomplete = Incompleto
lo-objective-waves = Obligatorio: supera todas las oleadas. { $completed }/{ $total } superadas.
lo-objective-missions = Obligatorio: completa { $total } misiones. { $completed } completadas; { $failed } fallidas.
lo-objective-bonus-missions = Misiones: { $completed } completadas; { $failed } fallidas.
lo-objective-integrity = Obligatorio: mantén el repetidor intacto. Integridad { $current }/{ $total }.
lo-objective-project = { $project }, { $zone }: { $requirement }. { $state }; trabajo { $progress }/{ $total }. Pendiente: { $remaining } de trabajo, { $cost } piezas, además de las puertas de acceso sin abrir.
lo-mission-idle = No hay ninguna misión activa.
lo-verb-unready = Cancelar preparación

lo-health-recovering = En el suelo; recuperación de emergencia { $recovery_seconds } segundos después de la horda
lo-inventory-parts = { $party_size ->
    [1] Piezas: { $parts }.
   *[other] Piezas compartidas: { $parts }.
    }
lo-board-lineup = { $count ->
    [1] Un superviviente
   *[other] { $count } supervivientes: humanos { $humans }, bots { $bots }
    }
lo-board-original = Sin toma de control por bots
lo-board-takeover = Con toma de control por bots
leaderboard-lo-clear-entry = { $rank }. { $player }: { $value } fases de horda.
lo-personal-record = { $name }: { $value } fases de horda.
lo-record-unranked = Sin clasificación: cambió la alineación inicial.
