game-name-ludo = Ludo

ludo-roll-die = Lanzar dado
ludo-move-token = Mover ficha
ludo-move-token-n = Mover ficha { $token }
ludo-check-board = Ver estado del tablero
ludo-select-token = Selecciona la ficha para mover:

ludo-roll = { $player } saca un { $roll }.
ludo-you-roll = Sacas un { $roll }.
ludo-no-moves = { $player } no tiene movimientos válidos.
ludo-you-no-moves = No tienes movimientos válidos.
ludo-error-roll-pending-move = Ya lanzaste y tienes un movimiento válido. Mueve una de tus fichas disponibles antes de volver a lanzar.
ludo-you-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] Tú: ficha { $token } sale +{ $spaces } a { $position }, segura.
           *[no] Tú: ficha { $token } sale +{ $spaces } a { $position }.
        }
       *[no] { $safe ->
            [yes] Sacas la ficha { $token } a la posición { $position }, que es una casilla segura.
           *[no] Sacas la ficha { $token } a la posición { $position }.
        }
    }
ludo-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }): ficha { $token } sale +{ $spaces } a { $position }, segura.
           *[no] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }): ficha { $token } sale +{ $spaces } a { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }) saca la ficha { $token } a la posición { $position }, que es una casilla segura.
           *[no] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }) saca la ficha { $token } a la posición { $position }.
        }
    }
ludo-you-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] Tú: ficha { $token } +{ $spaces } a { $position }, segura.
           *[no] Tú: ficha { $token } +{ $spaces } a { $position }.
        }
       *[no] { $safe ->
            [yes] Mueves la ficha { $token } a la posición { $position }, que es una casilla segura.
           *[no] Mueves la ficha { $token } a la posición { $position }.
        }
    }
ludo-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }): ficha { $token } +{ $spaces } a { $position }, segura.
           *[no] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }): ficha { $token } +{ $spaces } a { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }) mueve la ficha { $token } a la posición { $position }, que es una casilla segura.
           *[no] { $player } ({ $color ->
                [red] Rojo
                [blue] Azul
                [green] Verde
                [yellow] Amarillo
               *[other] { $color }
            }) mueve la ficha { $token } a la posición { $position }.
        }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] Tú: ficha { $token } +{ $spaces } a la meta { $position }/{ $total }.
       *[no] Mueves la ficha { $token } a tu columna final ({ $position }/{ $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $color }
        }): ficha { $token } +{ $spaces } a la meta { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
            *[other] { $color }
        }) mueve la ficha { $token } a su columna final ({ $position }/{ $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] Tú: ficha { $token } en casa ({ $finished }/4).
       *[no] Tu ficha { $token } llega a casa. ({ $finished }/4 terminadas)
    }
ludo-home-finish =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $color }
        }): ficha { $token } en casa ({ $finished }/4).
       *[no] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
            *[other] { $color }
        }) ficha { $token } llega a casa. ({ $finished }/4 terminadas)
    }
ludo-you-move-home =
    { $brief ->
        [yes] Tú: ficha { $token } +{ $spaces } a la meta { $position }/{ $total }.
       *[no] Mueves la ficha { $token } en tu columna final ({ $position }/{ $total }).
    }
ludo-move-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $color }
        }): ficha { $token } +{ $spaces } a la meta { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $color }
        }) mueve la ficha { $token } en su columna final ({ $position }/{ $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes] Tú: capturas { $count } de { $captured_player } ({ $captured_color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $captured_color }
        }) de vuelta a la cárcel.
       *[no] Capturas { $count ->
            [one] 1 ficha
           *[other] { $count } fichas
        } de { $captured_player } ({ $captured_color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
            *[other] { $captured_color }
        }) y { $count ->
            [one] la
           *[other] las
        } envías de vuelta a la cárcel.
    }
ludo-your-token-captured =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $color }
        }): { $count ->
            [one] tu ficha
           *[other] tus { $count } fichas
        } de vuelta a la cárcel.
       *[no] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
            *[other] { $color }
        }) captura { $count ->
            [one] tu ficha
           *[other] { $count } de tus fichas
        } y { $count ->
            [one] la
           *[other] las
        } envía de vuelta a la cárcel.
    }
ludo-captures =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $color }
        }): captura { $count } de { $captured_player } ({ $captured_color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
           *[other] { $captured_color }
        }) de vuelta a la cárcel.
       *[no] { $player } ({ $color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
            *[other] { $color }
        }) captura { $count ->
            [one] 1 ficha
           *[other] { $count } fichas
        } de { $captured_player } ({ $captured_color ->
            [red] Rojo
            [blue] Azul
            [green] Verde
            [yellow] Amarillo
            *[other] { $captured_color }
        }). Enviada de vuelta a la cárcel.
    }
ludo-extra-turn = { $player } sacó un 6. Turno extra.
ludo-you-extra-turn = Sacaste un 6. Turno extra.
ludo-you-too-many-sixes = Sacaste { $count } seises seguidos. Los movimientos de esta secuencia de turno se deshacen, y tu turno termina.
ludo-too-many-sixes = { $player } sacó { $count } seises seguidos. Movimientos deshechos. El turno termina.
ludo-you-winner = ¡Ganas! Tus 4 fichas están en casa.
ludo-winner = ¡{ $player } ({ $color ->
    [red] Rojo
    [blue] Azul
    [green] Verde
    [yellow] Amarillo
    *[other] { $color }
}) gana! Sus 4 fichas están en casa.
ludo-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 ficha en casa
   *[other] { $count } fichas en casa
}

ludo-board-player = { $player } ({ $color ->
    [red] Rojo
    [blue] Azul
    [green] Verde
    [yellow] Amarillo
    *[other] { $color }
}): { $finished }/4 terminadas
ludo-token-yard = Ficha { $token } (en la cárcel)
ludo-token-track =
    { $safe ->
        [yes] Ficha { $token } (posición { $position }, casilla segura)
       *[no] Ficha { $token } (posición { $position })
    }
ludo-token-home = Ficha { $token } (columna final { $position }/{ $total })
ludo-token-finished = Ficha { $token } (terminada)
ludo-last-roll = Última tirada: { $roll }

ludo-set-max-sixes = Máximo de seises consecutivos: { $max_consecutive_sixes }
ludo-enter-max-sixes = Ingresa el máximo de seises consecutivos
ludo-option-changed-max-sixes = Máximo de seises consecutivos establecido en { $max_consecutive_sixes }.
ludo-desc-max-consecutive-sixes = Cuántos seises consecutivos puede sacar un jugador antes de que se penalice o pase el turno (por defecto 3, rango 0-5).
ludo-set-safe-start-squares = Casillas de salida seguras: { $enabled }
ludo-option-changed-safe-start-squares = Casillas de salida seguras establecidas en { $enabled }.
ludo-desc-safe-start-squares = Controla si la casilla de salida de cada jugador se trata como una casilla segura.
