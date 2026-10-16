# Nine game messages

# Game name and description
game-name-nine = التسعة
nine-description = لعبة ورق روسية شهيرة يبني فيها اللاعبون متتاليات حسب نوع الورق.

# Player count validation
nine-error-invalid-player-count = تستخدم لعبة التسعة مجموعة أوراق من 36 بطاقة وتتسع لـ 3 أو 4 أو 6 لاعبين بالضبط.
nine-error-starting-nine-missing = لم يُعثر على تسعة الماس في أي يد. لا يمكن متابعة اللعبة.

# Dealing messages
nine-player-nine-deal = توزيع { $cards } بطاقة لكل لاعب.

# Game start
nine-you-start-player-announcement = لديك تسعة الماس وتبدأ اللعبة.
nine-player-start-player-announcement = { $player } لديه تسعة الماس ويبدأ اللعبة.
nine-you-start-player-announcement-brief = تبدأ بتسعة الماس.
nine-player-start-player-announcement-brief = { $player } يبدأ بتسعة الماس.

# Turn actions
nine-you-plays-starting-nine = تلعب { $card } لفتح الطاولة.
nine-player-plays-starting-nine = { $player } يلعب { $card } لفتح الطاولة.
nine-you-plays-starting-nine-brief = تلعب { $card }.
nine-player-plays-starting-nine-brief = { $player }: { $card }.

nine-you-plays-nine-suit = تلعب { $card } لبدء متتالية { $suit }.
nine-player-plays-nine-suit = { $player } يلعب { $card } لبدء متتالية { $suit }.
nine-you-plays-nine-suit-brief = تبدأ { $suit } بـ { $card }.
nine-player-plays-nine-suit-brief = { $player } يبدأ { $suit } بـ { $card }.

nine-you-extend-sequence = تمدّد متتالية { $suit } بـ { $card }.
nine-player-extend-sequence = { $player } يمدّد متتالية { $suit } بـ { $card }.
nine-you-extend-sequence-brief = تلعب { $card } على { $suit }.
nine-player-extend-sequence-brief = { $player }: { $card } على { $suit }.

nine-you-skips-turn = ليس لديك بطاقة قانونية للعب، لذا يُتخطّى دورك.
nine-player-skips-turn = { $player } ليس لديه بطاقة قانونية للعب، لذا يُتخطّى دور { GENDER_TERM($player_gender, "possessive-determiner") }.
nine-you-skips-turn-brief = تتخطّى؛ لا بطاقة قانونية.
nine-player-skips-turn-brief = { $player } يتخطّى؛ لا بطاقة قانونية.

# Reasons for not being able to play a card
nine-reason-not-your-turn = ليس دورك.
nine-reason-card-slot-gone = لم تعد تلك البطاقة في يدك. تم تحديث قائمة يدك.
nine-reason-must-play-starting-nine = يجب أن تكون أول لعبة هي { $starting_card }. لا يمكن لعب { $card } حتى تُفتح الطاولة.
nine-reason-nine-already-started = لا يمكن لعب { $card } لأن متتالية { $suit } مفتوحة بالفعل.
nine-reason-cannot-extend = لا يمكن لـ { $card } تمديد متتالية { $suit }. العب البطاقة الأدنى التالية أو الأعلى التالية عند أحد طرفَي تلك المتتالية.
nine-reason-unopened-suit = لا يمكن لعب { $card } لأن متتالية { $suit } لم تُفتح بعد. ابدأ ذلك النوع بالتسعة الخاصة به أولًا.
nine-reason-must-skip = ليس لديك بطاقة قانونية للعب؛ سيُتخطّى دورك تلقائيًا.
# Winning
nine-you-wins-game = لم يتبقَّ لديك أي بطاقات وتفوز باللعبة!
nine-player-wins-game = لم يتبقَّ لدى { $player } أي بطاقات ويفوز باللعبة!
nine-you-wins-game-brief = أنت تفوز!
nine-player-wins-game-brief = { $player } يفوز!
nine-player-game-ended = انتهت لعبة التسعة.
nine-you-game-ended = انتهت لعبة التسعة.

nine-you-win = أنت تفوز!
nine-you-lose = أنت تخسر!
nine-final-score = البطاقات المتبقية: { $score }

# Status
nine-status = { $name }: { $cards_left } بطاقة متبقية.
nine-status-sequence = متتالية { $suit }: { $sequence }.
nine-status-no-sequence = لم تبدأ متتالية { $suit } بعد.
nine-sequence-range = { $low } إلى { $high }
nine-none = لا شيء
nine-action-check-sequences = عرض المتتاليات
nine-action-check-hand-counts = عرض عدد البطاقات في الأيدي
nine-status-player-hand-count = { $player }: { $count } بطاقة
