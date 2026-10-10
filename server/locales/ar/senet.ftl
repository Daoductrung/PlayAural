# Senet localization

game-name-senet = سينت

# Game start
senet-game-started = { $p1 } هو اللاعب 1، { $p2 } هو اللاعب 2. يبدأ { $first } أولًا.

# Throwing sticks
senet-throw-you = ترمي { $result }.{ $bonus ->
    [yes] {" "}رمية إضافية!
   *[no] {""}
}
senet-throw-other = يرمي { $player } { $result }.{ $bonus ->
    [yes] {" "}رمية إضافية!
   *[no] {""}
}

# Movement
senet-move-you = تتحرك من المربع { $from } إلى المربع { $to }.
senet-move-other = يتحرك { $player } من المربع { $from } إلى المربع { $to }.
senet-swap-you = تتبادل مع { $opponent } في المربع { $to }. يعود { $opponent } إلى المربع { $from }.
senet-swap-other = يتبادل { $player } مع { $opponent } في المربع { $to }. يعود { $opponent } إلى المربع { $from }.
senet-bearoff-you = تُخرج قطعة من المربع { $from }. المتبقي { $remaining }.
senet-bearoff-other = يُخرج { $player } قطعة من المربع { $from }. المتبقي { $remaining }.
senet-water-you = هبطت في بيت الماء! أُرسلت القطعة إلى المربع { $dest }.
senet-water-other = هبط { $player } في بيت الماء! أُرسلت القطعة إلى المربع { $dest }.
senet-happiness-you = وصلت إلى بيت السعادة.
senet-happiness-other = وصل { $player } إلى بيت السعادة.
senet-horus-auto-you = تغادر قطعتك بيت حورس لأن صفك الأول خالٍ. المتبقي { $remaining }.
senet-horus-auto-other = تغادر قطعة { $player } بيت حورس لأن صف { GENDER_TERM($player_gender, "possessive-determiner") } الأول خالٍ. المتبقي { $remaining }.

# No moves
senet-no-moves-you = ليست لديك حركات قانونية.
senet-no-moves-other = ليست لدى { $player } حركات قانونية.

# Square labels
senet-sq-empty = { $sq }
senet-sq-own = { $sq }، لك
senet-sq-opponent = { $sq }، { $owner }
senet-sq-empty-special = { $sq }، { $name }
senet-sq-own-special = { $sq }، { $name }، لك
senet-sq-opponent-special = { $sq }، { $name }، { $owner }

# Special square names
senet-house-rebirth = البعث
senet-house-happiness = السعادة
senet-house-water = الماء
senet-house-three-truths = الحقائق الثلاث
senet-house-re-atum = رع-آتوم
senet-house-horus = حورس

# Status
senet-status = { $p1 }: { $off1 } مُخرجة. { $p2 }: { $off2 } مُخرجة.{ $phase ->
    [throwing] {" "}في انتظار الرمي.
   *[moving] {" "}الرمية: { $roll }.
}
senet-sticks = { $result }
senet-sticks-none = لا رمية بعد.

# Win
senet-wins-you = تفوز! جميع قطعك عبرت البيت الأخير.
senet-wins-other = يفوز { $player }! جميع قطع { GENDER_TERM($player_gender, "possessive-determiner") } عبرت البيت الأخير.

# Action labels
senet-check-status = الحالة
senet-check-sticks = العيدان
senet-next-piece = القطعة التالية
senet-previous-piece = القطعة السابقة
senet-score-line = { $player }: { $off } مُخرجة.

# Errors
senet-not-your-piece = ليست قطعتك.
senet-no-piece-there = لا قطعة هناك.
senet-no-moves-from-here = لا حركات قانونية من هذا المربع.
senet-need-throw-first = عليك رمي العيدان قبل اختيار قطعة لتحريكها.
senet-no-movable-pieces = لا يمكن لأي من قطعك التحرك بالرمية الحالية.
senet-error-exactly-two-players = تتطلب سينت لاعبين نشطين اثنين بالضبط. اللاعبون النشطون حاليًا: { $count }.

# Options
senet-option-bot-difficulty = صعوبة الروبوت: { $bot_difficulty }
senet-option-select-bot-difficulty = اختر صعوبة الروبوت
senet-option-changed-bot-difficulty = تم ضبط صعوبة الروبوت على { $bot_difficulty }.
senet-desc-bot-difficulty = يحدد كيفية تحرك روبوتات سينت: العشوائي يلعب بتراخٍ، بينما البسيط يفضّل الحركات التكتيكية الأكثر أمانًا.
senet-difficulty-random = عشوائي
senet-difficulty-simple = بسيط
