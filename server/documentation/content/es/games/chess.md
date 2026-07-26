\*\*Ajedrez\*\*

El ajedrez es un duelo de cálculo, tiempo y planificación a largo plazo en un campo de batalla de 8 por 8. Dos jugadores comandan ejércitos opuestos, cada uno intentando abrirse paso en la posición, defender a su rey, y dar jaque mate antes de que el otro bando lo logre.

\*\*Jugabilidad\*\*

Cada bando empieza con dieciséis piezas. Las blancas mueven primero, y luego los jugadores alternan turnos por el resto de la partida.

El tablero es una cuadrícula de 8 por 8. En tu turno, eliges una de tus propias piezas y luego eliges una casilla de destino legal.

También puedes escribir una jugada directamente. La entrada acepta formatos comunes de ajedrez, incluida la notación de coordenadas como `e2e4`, la notación algebraica como `Cf3` o `Tae1`, el enroque como `O-O` u `O-O-O`, y la coronación como `e8=D`.

\* Los peones avanzan hacia adelante, capturan en diagonal, y pueden avanzar dos casillas desde su fila inicial.
\* Los caballos se mueven en forma de L y pueden saltar sobre otras piezas.
\* Los alfiles se mueven en diagonal a través de cualquier cantidad de casillas libres.
\* Las torres se mueven en horizontal o vertical a través de cualquier cantidad de casillas libres.
\* Las damas combinan el movimiento de torre y alfil.
\* Los reyes se mueven una casilla en cualquier dirección.

Nunca puedes hacer una jugada que deje a tu propio rey en jaque. Si tu rey está bajo ataque, debes responder a esa amenaza de inmediato, moviendo al rey, bloqueando la línea de ataque, o capturando a la pieza atacante.

Si hay un reloj activado, solo corre el reloj del jugador activo. Después de completar una jugada legal, se añade al tiempo restante de ese jugador cualquier incremento del control de tiempo seleccionado. Si hay una oferta de tablas o una solicitud de deshacer esperando respuesta, el reloj se pausa hasta que esa respuesta se resuelva.

\*\*Mecánicas especiales\*\*

\* \*\*Enroque:\*\* El enroque es legal si el rey y la torre involucrados no se han movido, las casillas entre ellos están vacías, el rey no está actualmente en jaque, y el rey no pasa por ni termina en jaque.
\* \*\*Al paso:\*\* Si un peón rival avanza dos casillas en una sola jugada y termina junto a tu peón, puedes capturarlo de inmediato como si se hubiera movido solo una casilla.
\* \*\*Coronación:\*\* Cuando un peón llega a la última fila, debe coronarse como dama, torre, alfil o caballo.
\* \*\*Jaque mate:\*\* La partida termina de inmediato cuando un jugador está en jaque y no tiene ninguna jugada legal.
\* \*\*Ahogado:\*\* La partida termina en tablas si el bando en turno no está en jaque pero no tiene ninguna jugada legal.
\* \*\*Material insuficiente:\*\* La partida termina en tablas automáticamente si ningún bando tiene suficiente material para forzar el jaque mate.
\* \*\*Tiempo agotado:\*\* Si el reloj de un jugador llega a cero, ese jugador pierde por tiempo, a menos que el oponente no tenga suficiente material para dar jaque mate en ningún momento, en cuyo caso la partida termina en tablas.

\*\*Tablas, reclamos y acuerdos\*\*

El ajedrez incluye varias formas de terminar una partida en tablas.

\* \*\*Triple repetición:\*\* Si la misma posición ocurre tres veces con el mismo bando en turno y los mismos derechos, la partida puede terminar en tablas.
\* \*\*Repetición quíntuple:\*\* Si la misma posición ocurre cinco veces, la partida termina en tablas automáticamente.
\* \*\*Regla de las cincuenta jugadas:\*\* Si cada jugador ha hecho cincuenta jugadas consecutivas sin ningún movimiento de peón ni captura, la partida puede terminar en tablas.
\* \*\*Regla de las setenta y cinco jugadas:\*\* Si cada jugador ha hecho setenta y cinco jugadas consecutivas sin ningún movimiento de peón ni captura, la partida termina en tablas automáticamente, a menos que la última jugada haya dado jaque mate.
\* \*\*Oferta de tablas:\*\* Si las ofertas de tablas están activadas para la mesa, un jugador puede ofrecer tablas después de que ambos jugadores hayan hecho al menos una jugada, y el oponente puede aceptar o rechazar.
\* \*\*Solicitud de deshacer:\*\* Si las solicitudes de deshacer están activadas para la mesa, un jugador puede pedir deshacer la última jugada, y el oponente puede aceptar o rechazar.

El anfitrión decide si la triple repetición y la regla de las cincuenta jugadas se manejan automáticamente o deben ser reclamadas por el jugador en turno. La repetición quíntuple y la regla de las setenta y cinco jugadas siempre son automáticas.

\*\*Opciones configurables\*\*

\* \*\*Control de tiempo:\*\* Elige el preajuste de reloj para ambos jugadores (por defecto `Sin tiempo`, opciones: `Bala 1+0`, `Bala 2+1`, `Blitz 3+0`, `Blitz 3+2`, `Blitz 5+0`, `Rápidas 10+0`, `Rápidas 10+5`, `Clásicas 30+0`).
\* \*\*Manejo de tablas:\*\* Elige si la triple repetición y la regla de las cincuenta jugadas son automáticas o deben reclamarse. La repetición quíntuple y la regla de las setenta y cinco jugadas siempre son automáticas (por defecto `Automático`, opciones: `Automático` o `Requiere reclamo`).
\* \*\*Permitir ofrecer tablas:\*\* Si los jugadores pueden ofrecer tablas durante la partida (por defecto `Activado`).
\* \*\*Permitir solicitudes de deshacer:\*\* Si los jugadores pueden pedirle a su oponente deshacer jugadas (por defecto `Desactivado`).

\*\*Atajos de teclado\*\*

\* \*\*Entrar:\*\* Selecciona la casilla resaltada del tablero.
\* \*\*V:\*\* Leer el tablero.
\* \*\*C:\*\* Consultar el estado actual de la partida.
\* \*\*M:\*\* Escribir una jugada directamente.
\* \*\*F:\*\* Voltear la orientación del tablero.
\* \*\*Mayús+T:\*\* Consultar ambos relojes.
\* \*\*Mayús+C:\*\* Reclamar tablas cuando la posición actual califica.
\* \*\*Mayús+D:\*\* Ofrecer tablas.
\* \*\*Mayús+U:\*\* Solicitar deshacer.
\* \*\*Y:\*\* Aceptar una oferta de tablas o solicitud de deshacer.
\* \*\*N:\*\* Rechazar una oferta de tablas o solicitud de deshacer.
