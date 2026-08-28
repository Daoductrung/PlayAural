\*\*Backgammon\*\*

Backgammon es una carrera para exactamente dos jugadores. Cada jugador controla quince fichas en un tablero de veinticuatro puntos numerados. Tu objetivo es llevar todas tus fichas a tu cuadrante final y luego sacar las quince antes que tu oponente.

PlayAural asigna a un jugador el color rojo y al otro el blanco. Los colores mantienen las mismas fichas durante todo el enfrentamiento, pero ambos jugadores escuchan los números de punto desde su propia dirección de avance.

\*\*El tablero\*\*

El tablero es una pista doblada en dos filas. Contiene:

\* \*\*24 puntos:\*\* Los espacios donde descansan las fichas. Desde tu perspectiva, el punto 24 es el más lejano de tu cuadrante final y el punto 1 es el más cercano para sacar fichas.
\* \*\*Tu cuadrante final:\*\* Los puntos 1 al 6. Las quince fichas deben llegar a estos seis puntos antes de que puedas empezar a sacarlas.
\* \*\*La barra:\*\* El divisor en el medio de un tablero físico. Una ficha capturada espera aquí hasta que pueda volver a entrar.
\* \*\*Fuera del tablero:\*\* El destino de las fichas que ya sacaste con éxito.

El tablero accesible es una cuadrícula estable de dos por doce. Tu cuadrante final está abajo a la derecha. La fila inferior va del punto 12 al punto 1, y la fila superior va del punto 13 al punto 24. Tus fichas avanzan de números de punto altos hacia bajos; tu oponente avanza en la dirección contraria.

\*\*Posición inicial\*\*

Cada jugador empieza con la disposición estándar de quince fichas:

\* 2 fichas en su punto 24.
\* 5 fichas en su punto 13.
\* 3 fichas en su punto 8.
\* 5 fichas en su punto 6.

Como los dos lados se mueven en direcciones opuestas, los números de punto de tu oponente son el reverso de los tuyos.

\*\*Empezando una partida\*\*

Cada jugador lanza un dado. Los empates se vuelven a lanzar. El jugador con el número más alto toma el primer turno y usa ambos números de la tirada inicial como los dados de ese turno. Se hace una nueva tirada inicial al comienzo de cada partida dentro de un enfrentamiento.

Después del turno inicial, los jugadores alternan turnos y lanzan dos dados cada vez. En un cliente táctil, toca cualquier punto del tablero para lanzar los dados. En escritorio, presiona Entrar sobre cualquier punto del tablero o presiona R. Lanzar los dados deja tu foco en el tablero donde estaba, así puedes seguir examinando el mismo punto.

\*\*Usando los dados\*\*

Cada dado normalmente mueve una ficha esa cantidad de puntos. Puedes mover dos fichas distintas, o mover una misma ficha dos veces si el punto intermedio está abierto. El orden puede importar: una ruta puede ser legal usando un dado primero y quedar bloqueada usando el otro dado primero.

Debes usar tanto de la tirada como las reglas lo permitan:

\* Si se pueden jugar ambos dados, debes jugar los dos.
\* Si solo se puede jugar un dado, debes jugar el dado más alto cuando el dado más alto tenga un movimiento legal.
\* Si sacas dobles, juegas ese número cuatro veces y debes usar tantos de esos cuatro movimientos como sea posible.
\* Si no se puede jugar ningún dado, el juego anuncia que el turno terminó.

PlayAural evalúa la tirada completa restante, así que rechazará un movimiento que te impediría usar otro dado requerido sin necesidad. El turno termina automáticamente después de que se haya usado cada dado que se podía jugar legalmente.

\*\*Seleccionando y moviendo una ficha\*\*

Activa un punto que contenga una de tus fichas para seleccionarla, luego activa un destino legal. PlayAural elige el dado disponible que corresponda. Activa Deseleccionar para cancelar la selección actual. Si no hay nada seleccionado, Deseleccionar confirma que no hay ninguna ficha seleccionada.

En un cliente táctil, activa Siguiente destino o Destino anterior cuando quieras que PlayAural mueva el foco entre tus opciones legales. Antes de seleccionar una ficha, estas acciones recorren los puntos de origen legales, o los puntos de entrada legales cuando tienes una ficha en la barra. Después de seleccionar una ficha, recorren sus destinos legales. Son los únicos controles de movimiento que cambian tu foco en el tablero intencionalmente.

La acción Movimientos legales abre una lista en vivo de cada movimiento permitido por la tirada completa restante. Los números de punto en esa lista usan tu perspectiva. Deshacer revierte el último submovimiento del turno actual, incluida la restauración de una ficha del oponente si ese movimiento la capturó. Una vez que el turno termina, sus movimientos ya no se pueden deshacer.

Puedes caer en:

\* Un punto vacío.
\* Un punto ocupado por cualquier cantidad de tus propias fichas.
\* Un punto ocupado por exactamente una ficha del oponente.

Un punto con dos o más fichas del oponente está cerrado, así que no puedes caer ahí.

\*\*Fichas sueltas, capturas y la barra\*\*

Una sola ficha parada sola en un punto se llama ficha suelta. Cuando una ficha del oponente cae en ese punto, la ficha suelta es capturada y se mueve a la barra.

Si tienes una o más fichas en la barra, debes hacerlas entrar todas antes de mover cualquier ficha que ya esté en el tablero. Para entrar, activa un destino abierto en el cuadrante final de tu oponente. El dado determina el punto de entrada: un 1 entra en el punto 1 del oponente desde su perspectiva, un 6 en su punto 6, y así sucesivamente. PlayAural anuncia estos destinos usando tus propios números de punto.

Un punto de entrada está abierto si está vacío, contiene tus propias fichas, o contiene una sola ficha suelta del oponente. Si hay varias fichas en la barra, debes hacer entrar tantas como los dados lo permitan. Después de que la última entra, cualquier dado sin usar puede mover esa misma ficha de nuevo o mover otra ficha. Si toda entrada permitida por los dados restantes está cerrada, no puedes moverte y pierdes el resto del turno.

\*\*Sacando fichas\*\*

Solo puedes empezar a sacar fichas cuando las quince están en tu cuadrante final y ninguna está en la barra.

\* Usa un dado igual al número de punto de una ficha para sacarla exactamente.
\* Un dado mayor que el punto ocupado más alto puede sacar una ficha de ese punto ocupado más alto.
\* No puedes usar un dado más grande de lo necesario en una ficha de un punto más bajo mientras te queden fichas en un punto más alto.

Si sacar la ficha del tablero es su único destino legal, activa su punto una vez. Si la ficha podría tanto moverse dentro del tablero como salir, actívala una vez para seleccionarla y activa el mismo punto de nuevo para sacarla. Esto deja disponible el destino dentro del tablero cuando ese movimiento es estratégicamente mejor.

Si una activación repetida no puede sacar la ficha, PlayAural explica por qué y cancela la selección. Si una de tus fichas restantes es capturada, debes hacerla entrar de nuevo y devolverla a tu cuadrante final antes de que puedas seguir sacando fichas.

\*\*Ganando una partida\*\*

El primer jugador en sacar sus quince fichas gana la partida. El resultado básico se multiplica entonces por el cubo de doblaje, si el cubo está en uso:

\* \*\*Victoria normal, 1 vez el cubo:\*\* El perdedor sacó al menos una ficha.
\* \*\*Gammon, 2 veces el cubo:\*\* El perdedor no sacó ninguna ficha.
\* \*\*Backgammon, 3 veces el cubo:\*\* El perdedor no sacó ninguna ficha y todavía tiene una ficha en la barra o en el cuadrante final del ganador.

En un enfrentamiento, el resultado se suma al puntaje del ganador. El primer jugador en alcanzar o superar el puntaje objetivo gana el enfrentamiento.

\*\*El cubo de doblaje\*\*

Los enfrentamientos de más de un punto usan un cubo de doblaje, que empieza centrado en 1. Al inicio de tu turno, antes de lanzar los dados, puedes ofrecer doblar el valor de la partida actual.

El turno inicial no se puede doblar porque sus dados ya se lanzaron para decidir quién empieza.

El oponente debe elegir una de estas respuestas:

\* \*\*Aceptar:\*\* El valor del cubo se duplica. El jugador que acepta toma posesión del cubo y es el único que puede ofrecer el próximo doblaje.
\* \*\*Rechazar:\*\* La partida actual termina de inmediato. El jugador que ofreció el doblaje gana el valor del cubo previo al aumento propuesto.

Rechazar puede requerir una segunda confirmación cuando la confirmación de acciones riesgosas está activada. Un jugador no puede ofrecer un doblaje cuando el oponente es dueño del cubo, después de haber lanzado los dados, durante una partida Crawford, o cuando aumentar el cubo no puede mejorar el resultado de ese jugador en el enfrentamiento porque el valor actual ya alcanza para ganarlo. Las partidas de un solo punto no usan el cubo.

\*\*La regla Crawford\*\*

Cuando cualquiera de los dos jugadores empieza por primera vez una partida a exactamente un punto de ganar el enfrentamiento, esa partida es la partida Crawford. El cubo de doblaje se desactiva para esa única partida. Si el enfrentamiento continúa, el cubo vuelve a estar disponible en cada partida posterior. PlayAural aplica esta regla automáticamente.

\*\*Opciones personalizables\*\*

\* \*\*Duración del enfrentamiento:\*\* El puntaje objetivo del enfrentamiento, de 1 a 25. El valor por defecto es 1. Una duración de 1 juega una sola partida sin cubo de doblaje.
\* \*\*Dificultad del bot:\*\* Simple, el valor por defecto, prefiere movimientos tácticos útiles. Aleatorio elige entre los movimientos legales sin esa preferencia táctica.

\*\*Opciones personales de partida\*\*

\* \*\*Anuncios breves:\*\* Usa mensajes de movimiento de ficha más cortos, conservando quién mueve, el origen, el destino, y si una ficha fue capturada, entró desde la barra, o fue sacada del tablero.
\* \*\*Confirmar acciones riesgosas:\*\* Requiere activar Rechazar una segunda vez dentro de 10 segundos antes de conceder una partida en respuesta a un doblaje.

\*\*Acciones de información\*\*

\* \*\*Estado:\*\* Informa las fichas de cada jugador en la barra, fuera del cuadrante final, y ya sacadas.
\* \*\*Cuenta de pips:\*\* Informa la distancia total que a cada lado le queda por recorrer para llevar sus fichas a casa y sacarlas. Un conteo más bajo suele ser mejor en una carrera pura, pero no mide las posibilidades de bloqueo o captura.
\* \*\*Dados:\*\* Informa los dados sin usar del turno actual.
\* \*\*Movimientos legales:\*\* Abre una lista en vivo de los movimientos permitidos por los dados restantes.
\* \*\*Cubo:\*\* Informa el valor del cubo, su dueño, y si un doblaje es posible en este momento.
\* \*\*Consultar puntajes:\*\* Lee el puntaje actual del enfrentamiento. Puntajes detallados abre un panel de puntaje en vivo.
\* \*\*Ver de quién es el turno\*\* y \*\*Quién está en la mesa:\*\* Informan el jugador activo y la lista de la mesa.

Las acciones de información más usadas están disponibles directamente en los clientes táctiles. Las demás acciones permanecen en el menú de Acciones.

\*\*Atajos de teclado\*\*

\* \*\*Entrar sobre un punto del tablero:\*\* Lanza los dados antes de mover, selecciona una ficha, o elige un destino.
\* \*\*R:\*\* Lanza los dados al inicio de tu turno.
\* \*\*Ctrl+Retroceso:\*\* Deselecciona la ficha actual.
\* \*\*Ctrl+Abajo o Ctrl+Derecha:\*\* Recorre hacia adelante los puntos de origen legales, o los destinos legales después de seleccionar una ficha. Las fichas sueltas del oponente se ofrecen primero.
\* \*\*Ctrl+Arriba o Ctrl+Izquierda:\*\* Recorre hacia atrás las mismas opciones.
\* \*\*Shift+D:\*\* Ofrece un doblaje antes de lanzar los dados.
\* \*\*Y:\*\* Acepta un doblaje ofrecido.
\* \*\*N:\*\* Rechaza un doblaje ofrecido.
\* \*\*U:\*\* Deshace el último submovimiento del turno actual.
\* \*\*E:\*\* Lee el estado de las fichas.
\* \*\*P:\*\* Lee ambas cuentas de pips.
\* \*\*D:\*\* Lee el cubo de doblaje.
\* \*\*S:\*\* Lee el puntaje del enfrentamiento.
\* \*\*Shift+S:\*\* Abre los puntajes detallados.
\* \*\*C:\*\* Lee los dados restantes.
\* \*\*M:\*\* Abre Movimientos legales.

\*\*Estrategia para principiantes\*\*

Trata de no dejar fichas sueltas al alcance fácil del oponente. Dos o más fichas en un mismo punto lo hacen seguro para que nadie caiga ahí. Los bloqueos son especialmente valiosos cuando retrasan una ficha del oponente que intenta salir de tu cuadrante final.

Cuando tengas una ficha en la barra, primero fíjate en qué puntos de entrada están abiertos. En una carrera donde ya no es posible ningún contacto, usa la cuenta de pips para comparar quién va adelante. Al sacar fichas, considera toda la tirada antes de elegir la primera ficha, porque un orden puede usar más dados que otro.
