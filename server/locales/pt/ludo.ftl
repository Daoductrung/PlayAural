game-name-ludo = Ludo

ludo-roll-die = Rolar dado
ludo-move-token = Mover peão
ludo-move-token-n = Mover peão { $token }
ludo-check-board = Ver status do tabuleiro
ludo-select-token = Selecionar peão para mover:

ludo-roll = { $player } tirou { $roll }.
ludo-you-roll = Você tirou { $roll }.
ludo-no-moves = { $player } não tem lances válidos.
ludo-you-no-moves = Você não tem lances válidos.
ludo-error-roll-pending-move = Você já rolou o dado e tem um lance válido. Mova um dos seus peões disponíveis antes de rolar novamente.
ludo-you-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] Você: peão { $token } saiu +{ $spaces } para { $position }, seguro.
           *[no] Você: peão { $token } saiu +{ $spaces } para { $position }.
        }
       *[no] { $safe ->
            [yes] Você coloca o peão { $token } na posição { $position }, que é uma casa segura.
           *[no] Você coloca o peão { $token } na posição { $position }.
        }
    }
ludo-enter-board =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }): peão { $token } saiu +{ $spaces } para { $position }, seguro.
           *[no] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }): peão { $token } saiu +{ $spaces } para { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }) coloca o peão { $token } na posição { $position }, que é uma casa segura.
           *[no] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }) coloca o peão { $token } na posição { $position }.
        }
    }
ludo-you-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] Você: peão { $token } +{ $spaces } para { $position }, seguro.
           *[no] Você: peão { $token } +{ $spaces } para { $position }.
        }
       *[no] { $safe ->
            [yes] Você move o peão { $token } para a posição { $position }, que é uma casa segura.
           *[no] Você move o peão { $token } para a posição { $position }.
        }
    }
ludo-move-track =
    { $brief ->
        [yes] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }): peão { $token } +{ $spaces } para { $position }, seguro.
           *[no] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }): peão { $token } +{ $spaces } para { $position }.
        }
       *[no] { $safe ->
            [yes] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }) move o peão { $token } para a posição { $position }, que é uma casa segura.
           *[no] { $player } ({ $color ->
                [red] Vermelho
                [blue] Azul
                [green] Verde
                [yellow] Amarelo
               *[other] { $color }
            }) move o peão { $token } para a posição { $position }.
        }
    }
ludo-you-enter-home =
    { $brief ->
        [yes] Você: peão { $token } +{ $spaces } para casa { $position }/{ $total }.
       *[no] Você move o peão { $token } para sua coluna final ({ $position }/{ $total }).
    }
ludo-enter-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $color }
        }): peão { $token } +{ $spaces } para casa { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
            *[other] { $color }
        }) move o peão { $token } para a coluna final ({ $position }/{ $total }).
    }
ludo-you-home-finish =
    { $brief ->
        [yes] Você: peão { $token } chegou ({ $finished }/4).
       *[no] Seu peão { $token } chega ao destino. ({ $finished }/4 concluídos)
    }
ludo-home-finish =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $color }
        }): peão { $token } chegou ({ $finished }/4).
       *[no] O peão { $token } de { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
            *[other] { $color }
        }) chega ao destino. ({ $finished }/4 concluídos)
    }
ludo-you-move-home =
    { $brief ->
        [yes] Você: peão { $token } +{ $spaces } para casa { $position }/{ $total }.
       *[no] Você move o peão { $token } na sua coluna final ({ $position }/{ $total }).
    }
ludo-move-home =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $color }
        }): peão { $token } +{ $spaces } para casa { $position }/{ $total }.
       *[no] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $color }
        }) move o peão { $token } na coluna final ({ $position }/{ $total }).
    }
ludo-you-capture =
    { $brief ->
        [yes] Você: captura { $count } de { $captured_player } ({ $captured_color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $captured_color }
        }) para a base.
       *[no] Você captura { $count ->
            [one] 1 peão
           *[other] { $count } peões
        } de { $captured_player } ({ $captured_color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
            *[other] { $captured_color }
        }) e envia { $count ->
            [one] ele
           *[other] eles
        } de volta para a base.
    }
ludo-your-token-captured =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $color }
        }): { $count ->
            [one] seu peão
           *[other] seus { $count } peões
        } para a base.
       *[no] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
            *[other] { $color }
        }) captura { $count ->
            [one] seu peão
           *[other] { $count } dos seus peões
        } e envia { $count ->
            [one] ele
           *[other] eles
        } de volta para a base.
    }
ludo-captures =
    { $brief ->
        [yes] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $color }
        }): captura { $count } de { $captured_player } ({ $captured_color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
           *[other] { $captured_color }
        }) para a base.
       *[no] { $player } ({ $color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
            *[other] { $color }
        }) captura { $count ->
            [one] 1 peão
           *[other] { $count } peões
        } de { $captured_player } ({ $captured_color ->
            [red] Vermelho
            [blue] Azul
            [green] Verde
            [yellow] Amarelo
            *[other] { $captured_color }
        }). Enviado de volta para a base.
    }
ludo-extra-turn = { $player } tirou 6. Turno extra.
ludo-you-extra-turn = Você tirou 6. Turno extra.
ludo-you-too-many-sixes = Você tirou { $count } 6s seguidos. Seus lances desta sequência de turnos foram desfeitos e seu turno termina.
ludo-too-many-sixes = { $player } tirou { $count } 6s seguidos. Lances desfeitos. O turno termina.
ludo-you-winner = Você venceu! Todos os 4 peões estão em casa.
ludo-winner = { $player } ({ $color ->
    [red] Vermelho
    [blue] Azul
    [green] Verde
    [yellow] Amarelo
    *[other] { $color }
}) venceu! Todos os 4 peões estão em casa.
ludo-end-score-line = { $index }. { $player }: { $count ->
    [one] 1 peão em casa
   *[other] { $count } peões em casa
}

ludo-board-player = { $player } ({ $color ->
    [red] Vermelho
    [blue] Azul
    [green] Verde
    [yellow] Amarelo
    *[other] { $color }
}): { $finished }/4 concluídos
ludo-token-yard = Peão { $token } (base)
ludo-token-track =
    { $safe ->
        [yes] Peão { $token } (posição { $position }, casa segura)
       *[no] Peão { $token } (posição { $position })
    }
ludo-token-home = Peão { $token } (coluna final { $position }/{ $total })
ludo-token-finished = Peão { $token } (concluído)
ludo-last-roll = Último resultado: { $roll }

ludo-set-max-sixes = Máximo de 6s consecutivos: { $max_consecutive_sixes }
ludo-enter-max-sixes = Digitar máximo de 6s consecutivos
ludo-option-changed-max-sixes = Máximo de 6s consecutivos definido para { $max_consecutive_sixes }.
ludo-desc-max-consecutive-sixes = Quantos 6s consecutivos um jogador pode tirar antes que o turno seja penalizado ou passado (padrão 3, intervalo de 0 a 5).
ludo-set-safe-start-squares = Casas iniciais seguras: { $enabled }
ludo-option-changed-safe-start-squares = Casas iniciais seguras definidas para { $enabled }.
ludo-desc-safe-start-squares = Controla se a casa inicial de cada jogador é tratada como uma casa segura.
