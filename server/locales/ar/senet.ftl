# Senet localization

game-name-senet = سينيت
# Game start
senet-game-started = { $p1 } هو اللاعب 1، { $p2 } هو اللاعب 2. { $first } يذهب أولا.
# Throwing sticks
senet-throw-you =
    ترمي { $result }.{ $bonus ->
        [yes] { " " }رمي المكافأة!
       *[no] { "" }
    }
senet-throw-other =
    { $player } رميات { $result }.{ $bonus ->
        [yes] { " " }رمي المكافأة!
       *[no] { "" }
    }
# Movement
senet-move-you = تنتقل من المربع { $from } إلى المربع { $to }.
senet-move-other = { $player } يتحرك من المربع { $from } إلى المربع { $to }.
senet-swap-you = يمكنك التبديل مع { $opponent } على الساحة { $to }. { $opponent } يعود إلى الساحة { $from }.
senet-swap-other = { $player } مقايضات مع { $opponent } على الساحة { $to }. { $opponent } يعود إلى المربع { $from }.
senet-bearoff-you = أنت تتحمل من المربع { $from }. { $remaining } متبقي.
senet-bearoff-other = { $player } يخرج من المربع { $from }. { $remaining } متبقي.
senet-water-you = لقد هبطت في بيت الماء! القطعة المرسلة إلى المربع { $dest }.
senet-water-other = { $player } هبطت في بيت الماء! القطعة المرسلة إلى المربع { $dest }.
senet-happiness-you = وصلت إلى دار السعادة.
senet-happiness-other = { $player } وصلت إلى دار السعادة .
senet-horus-auto-you = قطعتك تغادر بيت حورس لأن صفك الأول واضح. { $remaining } متبقي.
senet-horus-auto-other = { $player }قطعة تغادر بيت حورس لأن صفهم الأول واضح. { $remaining } متبقي.
# No moves
senet-no-moves-you = ليس لديك أي تحركات قانونية.
senet-no-moves-other = { $player } ليس لديه تحركات قانونية.
# Square labels
senet-sq-empty = { $sq }
senet-sq-own = { $sq }، لك
senet-sq-opponent = { $sq }, { $owner }
senet-sq-empty-special = { $sq }, { $name }
senet-sq-own-special = { $sq }, { $name }، لك
senet-sq-opponent-special = { $sq }, { $name }, { $owner }
# Special square names
senet-house-rebirth = ولادة جديدة
senet-house-happiness = السعادة
senet-house-water = ماء
senet-house-three-truths = ثلاث حقائق
senet-house-re-atum = ري أتوم
senet-house-horus = حورس
# Status
senet-status =
    { $p1 }: { $off1 } عن. { $p2 }: { $off2 } عن.{ $phase ->
        [throwing] { " " }في انتظار رمي.
       *[moving] { " " }لفة: { $roll }.
    }
senet-sticks = { $result }
senet-sticks-none = لا رمي بعد.
# Win
senet-wins-you = فزت! لقد عبرت جميع القطع الخاصة بك المنزل النهائي.
senet-wins-other = { $player } يفوز! لقد عبرت جميع قطعهم المنزل النهائي.
# Action labels
senet-check-status = الحالة
senet-check-sticks = العصي
senet-next-piece = القطعة التالية
senet-previous-piece = القطعة السابقة
senet-score-line = { $player }: { $off } عن.
# Errors
senet-not-your-piece = ليس قطعتك.
senet-no-piece-there = لا قطعة هناك.
senet-no-moves-from-here = لا توجد تحركات قانونية من هذه الساحة.
senet-need-throw-first = تحتاج إلى رمي العصي قبل اختيار قطعة لتحريكها.
senet-no-movable-pieces = لا يمكن لأي من قطعك أن تتحرك بالرمية الحالية.
senet-error-exactly-two-players = يتطلب Senet لاعبين نشطين بالضبط. اللاعبون النشطون الحاليون: { $count }.
# Options
senet-option-bot-difficulty = صعوبة البوت: { $bot_difficulty }
senet-option-select-bot-difficulty = حدد صعوبة الروبوت
senet-option-changed-bot-difficulty = تم ضبط صعوبة الروبوت على { $bot_difficulty }.
senet-desc-bot-difficulty = يختار كيفية تحرك روبوتات Senet: يلعب بشكل عشوائي بشكل غير محكم، بينما يفضل Simple الحركات التكتيكية الأكثر أمانًا.
senet-difficulty-random = عشوائي
senet-difficulty-simple = بسيط
