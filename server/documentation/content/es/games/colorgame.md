\*\*Juego de Colores\*\*

Juego de Colores es la adaptación de PlayAural del tradicional juego filipino de apuestas de dados de color \*perya\*. Todos apuestan a uno o más colores, se lanzan tres dados de color juntos, y cada apuesta de color se paga estrictamente según cuántos dados mostraron ese mismo color.

\*\*Jugabilidad\*\*

\* El tablero tiene \*\*6 colores para apostar\*\*: rojo, azul, amarillo, verde, blanco, y naranja.
\* Cada ronda usa \*\*3 dados de color\*\*.
\* Cada dado contiene los mismos 6 colores, así que un color puede aparecer \*\*0, 1, 2, o 3 veces\*\* en una ronda.
\* Al inicio de la partida, cada jugador recibe fichas \*\*iniciales\*\* según la configuración del anfitrión.
\* Una ronda abre con una \*\*fase de apuestas compartida\*\*. No es un turno estricto de un solo jugador. Todos los jugadores activos pueden colocar o cambiar apuestas durante la misma ventana de temporizador.
\* Un \*\*jugador activo\*\* es un jugador cuyas fichas todavía pueden cubrir la Apuesta mínima de la mesa.
\* Durante las apuestas, puedes poner fichas en \*\*un color\*\* o repartir tu total entre \*\*varios colores\*\*.
\* Cada apuesta de color se trata de forma independiente. No estás eligiendo un color ganador general para toda la ronda.
\* Seleccionar un color abre un \*\*menú de apuesta rápida\*\*. Ofrece montos preestablecidos legales según tus fichas restantes y el límite de ronda de la mesa, incluido el 25 por ciento, 50 por ciento, y el monto más grande permitido actualmente.
\* Elige \*\*Ingresar monto personalizado\*\* cuando necesites una cantidad exacta. Ingresar 0 borra ese color.
\* Elegir \*\*All-in\*\* usa toda la capacidad de apuesta que todavía queda disponible para ese color en la ronda actual. El límite de Apuesta total máxima por ronda del anfitrión sigue aplicando, así que esta elección nunca se salta el límite de la mesa.
\* Cuando estés satisfecho con tus apuestas, usa \*\*Bloquear apuestas\*\*.
\* Si todos los jugadores activos bloquean sus apuestas antes de que se acabe el temporizador, los dados se lanzan de inmediato.
\* Si el temporizador se acaba primero, cada jugador activo restante queda bloqueado automáticamente con su hoja de apuestas actual, incluida la posibilidad de bloquear \*\*sin ninguna apuesta\*\*.
\* Después de que se resuelve la tirada, las fichas se actualizan, se anuncia la clasificación, y comienza una nueva ronda de apuestas a menos que la partida haya terminado.

\*\*Mecánicas especiales\*\*

\* \*\*Fase de apuestas compartida:\*\* todos los jugadores activos pueden actuar durante la misma ventana de apuestas.
\* \*\*Apuestas bloqueadas:\*\* una vez que bloqueas tus apuestas de la ronda, no las puedes editar de nuevo hasta la siguiente ronda.
\* \*\*Quedarse fuera:\*\* puedes bloquear una hoja de apuestas vacía. En ese caso, ni ganas ni pierdes fichas en esa ronda.
\* \*\*Jugadores por debajo del mínimo:\*\* si tus fichas caen por debajo de la Apuesta mínima de la mesa, permaneces en la clasificación pero quedas fuera de las apuestas porque no es posible ninguna apuesta legal.
\* \*\*Temporizador de ronda:\*\* el temporizador no descarta tus apuestas actuales. Simplemente bloquea lo que ya tengas cuando se acabe el tiempo.
\* \*\*Confirmar acciones arriesgadas:\*\* cuando tu preferencia personal está activada, All-in y bloquear una hoja de apuestas vacía requieren la misma elección una segunda vez dentro de 10 segundos.
\* \*\*Anuncios breves:\*\* cuando está activado en tus Opciones de juego personales, los mensajes de ronda, tirada, bloqueo, y pago usan una redacción compacta centrada en datos.

\*\*Puntuación\*\*

Juego de Colores trata fundamentalmente sobre la \*\*gestión de fichas\*\*.

\* Tu valor competitivo principal son tus \*\*fichas\*\* actuales.
\* La clasificación también registra:
\* \*\*Rondas ganadoras:\*\* cuántas rondas terminaron con una ganancia neta positiva
\* \*\*Mayor victoria:\*\* tu mayor ganancia individual en una sola ronda

\*\*Lógica de pago\*\*

El código usa exactamente este modelo de pago para \*\*cada apuesta de color individual\*\*:

\* \*\*0 coincidencias:\*\* el cambio neto es \*\*-apuesta\*\*
\* \*\*1 coincidencia:\*\* el cambio neto es \*\*+apuesta\*\*
\* \*\*2 coincidencias:\*\* el cambio neto es \*\*+2 × apuesta\*\*
\* \*\*3 coincidencias:\*\* el cambio neto es \*\*+3 × apuesta\*\*

Esto corresponde a la estructura tradicional \*\*1:1, 2:1, 3:1\*\* del Juego de Colores.

Ejemplo:

\* Colocas 5 fichas en rojo y 3 fichas en azul.
\* Los dados salen rojo, rojo, verde.
\* Tu apuesta en rojo coincidió con \*\*2 dados\*\*, así que su resultado neto es \*\*+10\*\*.
\* Tu apuesta en azul coincidió con \*\*0 dados\*\*, así que su resultado neto es \*\*-3\*\*.
\* Tu resultado neto total de la ronda es entonces \*\*+7 fichas\*\*.

\*\*Ganar la partida\*\*

El juego admite dos condiciones de victoria:

\* \*\*Último jugador en pie\*\*
\* \*\*Fichas más altas al límite de ronda\*\*

Ambos modos también comparten una regla práctica de fin anticipado:

\* Si solo queda \*\*un jugador capaz de cumplir la apuesta mínima\*\*, la partida termina de inmediato, incluso si todavía no se ha llegado al límite de ronda.

Eso significa que el comportamiento exacto es:

\* \*\*Último jugador en pie:\*\*
\* Si solo un jugador todavía tiene fichas, ese jugador gana de inmediato.
\* Si se llega primero al límite de ronda, gana el jugador con las fichas más altas.
\* \*\*Fichas más altas al límite de ronda:\*\*
\* El enfoque previsto son las fichas al final del límite.
\* Si solo un jugador todavía tiene fichas antes del límite, la partida termina porque ningún otro jugador puede colocar otra apuesta ni cambiar la clasificación.

Si los jugadores están empatados en el primer lugar, la clasificación se desempata exactamente en este orden:

\* fichas más altas
\* más rondas ganadoras
\* mayor victoria en una sola ronda
\* si sigue empatado, el resultado permanece empatado

\*\*Opciones configurables\*\*

\* \*\*Fichas iniciales:\*\* Cada jugador empieza la partida con esta cantidad de fichas (por defecto \*\*100\*\*, rango válido \*\*10 a 1000\*\*).

\* \*\*Apuesta mínima:\*\* Cada apuesta de color distinta de cero debe ser al menos esta cantidad (por defecto \*\*1\*\*, rango válido \*\*1 a 100\*\*).

\* \*\*Apuesta total máxima por ronda:\*\* El límite real por ronda de un jugador es el menor entre sus fichas actuales y el valor de esta opción. La validación adicional requiere que sea:
\* al menos la Apuesta mínima
\* no mayor que las Fichas iniciales
\* Por defecto \*\*20\*\*, rango válido en el control de opciones \*\*1 a 1000\*\*.

\* \*\*Temporizador de apuestas:\*\* El temporizador compartido para la fase de apuestas de cada ronda (por defecto \*\*15 segundos\*\*, rango válido \*\*5 a 60 segundos\*\*).

\* \*\*Límite de rondas:\*\* Una vez completada esta cantidad de rondas, la partida termina y la clasificación se finaliza (por defecto \*\*20\*\*, rango válido \*\*1 a 100\*\*).

\* \*\*Condición de victoria:\*\* Determina cómo se decide al ganador (por defecto \*\*Último jugador en pie\*\*, opciones: \*\*Último jugador en pie\*\* o \*\*Fichas más altas al límite de ronda\*\*).

\*\*Atajos de teclado\*\*

\* \*\*R:\*\* Abrir el menú de apuesta rápida en rojo.
\* \*\*U:\*\* Abrir el menú de apuesta rápida en azul.
\* \*\*Y:\*\* Abrir el menú de apuesta rápida en amarillo.
\* \*\*G:\*\* Abrir el menú de apuesta rápida en verde.
\* \*\*W:\*\* Abrir el menú de apuesta rápida en blanco.
\* \*\*O:\*\* Abrir el menú de apuesta rápida en naranja.
\* \*\*C:\*\* Borrar tus apuestas actuales.
\* \*\*Espacio:\*\* Bloquear tus apuestas de la ronda actual.
\* \*\*E:\*\* Escuchar la fase actual, el temporizador, las fichas, el estado de bloqueo, y el líder.
\* \*\*V:\*\* Escuchar la hoja de apuestas actual de cada jugador.
\* \*\*D:\*\* Escuchar la tirada anterior y el resultado de cada jugador en esa tirada.
\* \*\*T:\*\* Escuchar el aviso de la fase actual.
\* \*\*S:\*\* Escuchar la clasificación.
\* \*\*Ctrl+U:\*\* Escuchar quién está en la mesa.
