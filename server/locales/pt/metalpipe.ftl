# Metal Pipe game messages

game-name-metalpipe = Cano de Metal

metalpipe-mode-single = Uma batida
metalpipe-mode-multiple = Múltiplas batidas
metalpipe-self-bonk-allowed = auto-batidas permitidas
metalpipe-self-bonk-blocked = auto-batidas bloqueadas

metalpipe-game-start = Metal Pipe começa no modo { $mode }. O cano escolherá tudo automaticamente.
metalpipe-game-start-brief = Cano de Metal: { $mode }.

metalpipe-you-hit-other = Você balança o cano de metal e acerta { $bonked }. { $bonked } foi eliminado.
metalpipe-player-hits-you = { $bonker } balança o cano de metal e acerta você. Você foi eliminado.
metalpipe-player-hits-other = { $bonker } balança o cano de metal e acerta { $bonked }. { $bonked } foi eliminado.
metalpipe-you-hit-self = Você de alguma forma acerta a si mesmo com o cano de metal e é eliminado.
metalpipe-player-hits-self = { $bonker } de alguma forma acerta a si mesmo com o cano de metal e é eliminado.

metalpipe-you-hit-other-brief = Você acerta { $bonked }. { $bonked } eliminado.
metalpipe-player-hits-you-brief = { $bonker } acerta você. Você está fora.
metalpipe-player-hits-other-brief = { $bonker } acerta { $bonked }. { $bonked } eliminado.
metalpipe-you-hit-self-brief = Auto-batida. Fora.
metalpipe-player-hits-self-brief = { $bonker } se auto-acerta. Fora.

metalpipe-you-win = Você venceu. O cano de metal falou.
metalpipe-you-win-with-others = Você venceu junto com { $players }. O cano de metal falou.
metalpipe-players-win = { $players } venceram. O cano de metal falou.
metalpipe-you-win-brief = Você venceu.
metalpipe-you-win-with-others-brief = Você e { $players } venceram.
metalpipe-players-win-brief = Vencedores: { $players }.
metalpipe-no-winner = O cano de metal não deixa nenhum vencedor.
metalpipe-no-winner-brief = Sem vencedor.

metalpipe-check-status = Ver status do cano
metalpipe-status-mode = Modo: { $mode }; { $self_bonk }.
metalpipe-status-progress = Batidas resolvidas: { $count }. Jogadores ainda de pé: { $alive } de { $total }.
metalpipe-status-awaiting = O cano ainda não caiu.
metalpipe-status-last-other = Última batida: { $bonker } acertou { $bonked }.
metalpipe-status-last-self = Última batida: { $bonker } acertou a si mesmo.
metalpipe-status-player = { $player}: { $status }.
metalpipe-status-alive = De pé
metalpipe-status-eliminated = Eliminado
metalpipe-no-turn-automatic = Metal Pipe está se resolvendo automaticamente. Há { $alive } jogadores ainda de pé, e nenhum jogador tem um turno manual.

metalpipe-final-results = Resultados do Metal Pipe
metalpipe-end-winner = Vencedor: { $player }.
metalpipe-end-winners = Vencedores: { $players }.
metalpipe-line-format = { $player}: { $status }

metalpipe-set-multiple-bonks = Múltiplas batidas: { $enabled }
metalpipe-option-changed-multiple-bonks = Múltiplas batidas definidas para { $enabled }.
metalpipe-desc-multiple-bonks = Quando ativado, o cano continua escolhendo quem bate e os alvos até que apenas um jogador permaneça (padrão desativado).
metalpipe-set-allow-self-bonk = Permitir auto-batida: { $enabled }
metalpipe-option-changed-allow-self-bonk = Permitir auto-batida definido para { $enabled }.
metalpipe-desc-allow-self-bonk = Quando ativado, quem bate (escolhido aleatoriamente) também pode se tornar o alvo (padrão ativado).
