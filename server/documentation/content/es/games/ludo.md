\*\*Ludo\*\*



Ludo es el juego de carreras de PlayAural basado en el conocido formato de cruz y círculo de cuatro colores. Cada jugador controla cuatro fichas, las saca de la cárcel, las mueve alrededor de la pista exterior compartida, y luego las guía hasta un carril de meta privado. El primer jugador en terminar sus cuatro fichas gana la partida de inmediato.



\*\*Jugabilidad\*\*



Ludo admite de 2 a 4 jugadores. Al inicio de la partida, a cada jugador se le asigna un color en orden de asiento: Rojo, Azul, Verde, y luego Amarillo. Cada jugador empieza con cuatro fichas en su propia cárcel.



En tu turno, primero lanzas el dado.



\* Si ninguna ficha puede moverse con esa tirada, tu turno termina automáticamente después del anuncio de la tirada.

\* Si exactamente una ficha puede moverse, el juego mueve esa ficha automáticamente.

\* Si varias fichas pueden moverse, el juego te pide elegir cuál ficha mover.



La pantalla de puntuación registra cuántas de las cuatro fichas de cada jugador ya han llegado a la meta, pero esto sigue siendo una sola carrera y no una partida de varias rondas. Tan pronto como un jugador lleva sus cuatro fichas a la meta, ese jugador gana.



\*\*Reglas de movimiento\*\*



\* \*\*Salir de la cárcel:\*\* Una ficha solo puede salir de la cárcel con una tirada de 6. Cuando eso pasa, entra al tablero en la casilla de salida de ese color.

\* \*\*Pista exterior:\*\* Una vez que una ficha está en el tablero, se mueve hacia adelante alrededor de la pista compartida de 52 casillas según la tirada del dado. La pista da la vuelta completa, así que las fichas pueden pasar por el lado de salida y continuar hacia la meta.

\* \*\*Entrada a la meta:\*\* Cada color tiene su propio punto de entrada cerca del final de una vuelta completa. Cuando una ficha pasa ese punto de entrada, sale de la pista compartida y entra a su carril de meta privado.

\* \*\*Carril de meta:\*\* El carril de meta tiene 6 casillas de largo. Una ficha solo puede moverse en el carril si la tirada no se pasa del final.

\* \*\*Terminar:\*\* Una ficha que llega al final del carril de meta queda marcada como terminada y ya no se mueve.



\*\*Casillas seguras y pilas\*\*



Ciertas casillas son seguras y no se pueden usar para capturas. En esta implementación, las casillas 9, 22, 35, y 48 siempre son seguras.



El anfitrión también puede activar una opción que hace que las cuatro casillas de salida de color sean seguras. Cuando esa opción está activada, entrar en una casilla de salida está protegido incluso si ya hay una ficha rival ahí.



Las fichas pueden apilarse en la misma casilla. El apilamiento puede pasar con tus propias fichas, con fichas rivales en casillas seguras, o en otras situaciones donde no ocurre ninguna captura.



\*\*Capturas\*\*



Si tu ficha cae en una casilla insegura de la pista exterior ocupada por un oponente, capturas la ficha de ese oponente y la envías de vuelta a la cárcel.



Si esa casilla contiene una pila de fichas de un solo oponente, capturas todas las fichas de ese oponente en la casilla a la vez. Tus propias fichas nunca son capturadas por tu propio movimiento, incluso si caes en una casilla donde ya están apiladas tus propias fichas.



Las capturas no ocurren dentro del carril de meta, ni ocurren en casillas seguras.



\*\*Sacar un 6\*\*



Sacar un 6 normalmente otorga un turno extra después de resolver el movimiento.



Sin embargo, el anfitrión puede limitar cuántos 6 se pueden sacar consecutivamente en la misma secuencia de turno. Por defecto, el límite es 3.



Si se alcanza el límite, la penalización es severa: todos los movimientos hechos durante esa secuencia de turno se deshacen, la cadena de turnos extra termina, y el juego pasa al siguiente jugador. Poner el límite en 0 desactiva por completo esta penalización.



\*\*Puntuación\*\*



Ludo en PlayAural usa una puntuación de carrera sencilla:



\* El primer jugador en terminar sus cuatro fichas gana la partida.

\* Durante el juego, el sistema de puntuación registra cuántas fichas ha llevado a casa cada jugador.

\* No hay puntos de ronda, totales de pips, ni puntuaciones que se acarreen entre carreras en la implementación actual.



\*\*Opciones configurables\*\*



El anfitrión puede ajustar las siguientes opciones antes de que empiece la partida:



\* \*\*Máximo de seises consecutivos:\*\* La cantidad de 6 que un jugador puede sacar seguidos antes de que se aplique la penalización de reversión. Ponerlo en 0 desactiva la penalización (por defecto 3, rango de 0 a 5).

\* \*\*Casillas de salida seguras:\*\* Cuando está activado, todas las casillas de salida de color cuentan como casillas seguras y no se pueden usar para capturas. Por defecto: Activado.



\*\*Atajos de teclado\*\*



\* \*\*R:\*\* Lanzar el dado.

\* \*\*1-4:\*\* Mover la ficha 1 a 4 cuando el juego te pide elegir una ficha.

\* \*\*V:\*\* Leer el estado completo del tablero, incluido el color de cada jugador, la cantidad de fichas terminadas, y la ubicación de cada ficha.

\* \*\*T:\*\* Consultar de quién es el turno.

\* \*\*S:\*\* Consultar la pantalla de puntuación actual.
