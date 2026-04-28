game-round-start = بدأت الجولة { $round }.
game-round-end = انتهت الجولة { $round }.
game-turn-start = دور اللاعب { $player }.
game-no-turn = لا يوجد دور نشط حالياً.

game-score-line = { $player }: { $score } { $score ->
    [one] نقطة واحدة
    [two] نقطتين
    [few] نقاط
   *[other] نقطة
    }
game-score-line-target = { $player }: { $score }/{ $target } { $score ->
    [one] نقطة
   *[other] نقطة
    }
game-points = { $count } { $count ->
    [one] نقطة واحدة
    [two] نقطتين
    [few] نقاط
   *[other] نقطة
    }
game-final-scores-header = النتائج النهائية:

game-winner = الفائز هو { $player }!
game-winner-score = فاز { $player } برصيد { $score } { $score ->
    [one] نقطة واحدة
    [two] نقطتين
    [few] نقاط
   *[other] نقطة
    }!
game-tiebreaker = تعادل! جولة كسر التعادل!
game-tiebreaker-players = تعادل بين { $players }! جولة كسر التعادل!
game-eliminated = تم إقصاء { $player } برصيد { $score } { $score ->
    [one] نقطة
   *[other] نقطة
    }.

game-set-target-score = الهدف: { $score }
game-enter-target-score = أدخل النتيجة المستهدفة:
game-option-changed-target = تم تحديد الهدف عند { $score } نقطة.

game-set-team-mode = نمط الفريق: { $mode }
game-select-team-mode = اختر نمط الفريق
game-option-changed-team = تم تغيير نمط الفريق إلى { $mode }.
game-team-mode-individual = فردي
game-team-mode-x-teams-of-y = { $num_teams } فرق (كل فريق { $team_size } لاعبين)
game-team-name = فريق { $index }

option-on = مفعل
option-off = معطل

status-box-closed = تم إغلاق نافذة الحالة.

game-leave = مغادرة اللعبة

round-timer-paused = تم إيقاف اللعبة مؤقتاً بواسطة { $player } (اضغط p للاستئناف).
round-timer-resumed = تم استئناف مؤقت الجولة.
round-timer-countdown = الجولة القادمة ستبدأ خلال { $seconds } ثانية...

dice-keeping = الاحتفاظ بـ { $value }.
dice-rerolling = إعادة رمي { $value }.
dice-locked = حجر النرد هذا مقفل ولا يمكن تغييره.
dice-status-label-locked = { $value } (مقفل)
dice-status-label-kept = { $value } (محتفظ به)

game-deal-counter = توزيع { $current } من أصل { $total }.
game-you-deal = أنت من يوزع الأوراق.
game-player-deals = يقوم { $player } بتوزيع الأوراق.

card-name = { $rank } of { $suit }
no-cards = لا توجد أوراق متاحة.

suit-diamonds = Diamonds
suit-clubs = Clubs
suit-hearts = Hearts
suit-spades = Spades

rank-ace = Ace
rank-two = 2
rank-three = 3
rank-four = 4
rank-five = 5
rank-six = 6
rank-seven = 7
rank-eight = 8
rank-nine = 9
rank-ten = 10
rank-jack = Jack
rank-queen = Queen
rank-king = King

rank-ace-plural = Aces
rank-two-plural = Twos
rank-three-plural = Threes
rank-four-plural = Fours
rank-five-plural = Fives
rank-six-plural = Sixes
rank-seven-plural = Sevens
rank-eight-plural = Eights
rank-nine-plural = Nines
rank-ten-plural = Tens
rank-jack-plural = Jacks
rank-queen-plural = Queens
rank-king-plural = Kings

poker-high-card-with = أعلى ورقة { $high }، مع { $rest }
poker-high-card = أعلى ورقة { $high }
poker-pair-with = زوج من { $pair }، مع { $rest }
poker-pair = زوج من { $pair }
poker-two-pair-with = زوجين { $high } و { $low }، مع { $kicker }
poker-two-pair = زوجين { $high } و { $low }
poker-trips-with = ثلاثة من نوع { $trips }، مع { $rest }
poker-trips = ثلاثة من نوع { $trips }
poker-straight-high = متسلسلة (ستريت) أعلاها { $high }
poker-flush-high-with = لون موحد (فلاش) أعلاه { $high }، مع { $rest }
poker-full-house = فول هاوس ({ $trips } على { $pair })
poker-quads-with = أربعة من نوع { $quads }، مع { $kicker }
poker-quads = أربعة من نوع { $quads }
poker-straight-flush-high = ستريت فلاش أعلاه { $high }
poker-unknown-hand = يد غير معروفة

game-error-invalid-team-mode = نمط الفريق المختار غير متوافق مع عدد اللاعبين الحالي.

documentation-menu = الوثائق والتعليمات
introduction = مقدمة
community-rules = قوانين المجتمع
global-keys = مفاتيح التحكم العامة
game-rules = قوانين الألعاب
changelog = سجل التغييرات
donation = دعم المشروع
contact = اتصل بنا
document-not-found = عذراً، لم يتم العثور على الوثيقة المطلوبة.
help = المساعدة

# Game Info (Ctrl+I)
game-info = معلومات اللعبة
game-info-header = تفاصيل المباراة الحالية
game-info-name = اللعبة: {$game}
game-info-players = عدد اللاعبين: {$count}
game-info-host = المضيف: {$host}
game-info-status = الحالة: {$status}
game-info-status-waiting = في الردهة (انتظار اللاعبين)
game-info-status-playing = جولة نشطة
game-info-options-header = إعدادات المباراة:
game-info-no-options = لا توجد خيارات مخصصة لهذه اللعبة.

# How to Play (Ctrl+F1)
how-to-play = طريقة اللعب
game-rules-not-available = قوانين لعبة {$game} غير متوفرة حالياً.
