game-name-holdem = بوكر تكساس هولدم

holdem-set-starting-chips = الرقاقات الابتدائية: { $count }
holdem-enter-starting-chips = أدخل الرقاقات الابتدائية
holdem-option-changed-starting-chips = تم ضبط الرقاقات الابتدائية على { $count }.
holdem-desc-starting-chips = رصيد كل لاعب الابتدائي في تكساس هولدم، من 100 إلى 1,000,000 رقاقة. الافتراضي: 20,000.

holdem-set-big-blind = الرهان الأعمى الكبير: { $count }
holdem-enter-big-blind = أدخل الرهان الأعمى الكبير
holdem-option-changed-big-blind = تم ضبط الرهان الأعمى الكبير على { $count }.
holdem-desc-big-blind = قيمة الرهان الأعمى الكبير الأساسية. يجب أن تكون أقل من الرصيد الابتدائي (الافتراضي 200، المدى 1-1,000,000 رقاقة).

holdem-set-ante = الرهان المسبق: { $count }
holdem-enter-ante = أدخل الرهان المسبق
holdem-option-changed-ante = تم ضبط الرهان المسبق على { $count }.
holdem-desc-ante = مساهمة إجبارية اختيارية يدفعها كل لاعب نشط عند تفعيل الرهانات المسبقة، من 0 إلى 1,000,000 رقاقة. الافتراضي: 0.

holdem-set-ante-start = يبدأ الرهان المسبق عند المستوى: { $count }
holdem-enter-ante-start = أدخل مستوى الرهان الأعمى لتفعيل الرهان المسبق
holdem-option-changed-ante-start = تم ضبط مستوى بدء الرهان المسبق على { $count }.
holdem-desc-ante-start-level = مستوى الرهان الأعمى الذي تبدأ عنده الرهانات المسبقة. يكون الرهان المسبق الموجب نشطًا من اليد الأولى عندما تكون القيمة 0 (الافتراضي 0، المدى 0-20).

holdem-set-turn-timer = مؤقّت الدور: { $mode }
holdem-select-turn-timer = اختر مؤقّت الدور
holdem-option-changed-turn-timer = تم ضبط مؤقّت الدور على { $mode }.
holdem-desc-turn-timer = حد زمني اختياري لكل قرار في هولدم: 5 أو 10 أو 15 أو 20 أو 30 أو 45 أو 60 أو 90 ثانية، أو غير محدود. الافتراضي: غير محدود.

holdem-set-blind-timer = مؤقّت الرهان الأعمى: { $mode }
holdem-select-blind-timer = اختر مؤقّت الرهان الأعمى
holdem-option-changed-blind-timer = تم ضبط مؤقّت الرهان الأعمى على { $mode }.
holdem-desc-blind-timer = الدقائق بين زيادات الرهان الأعمى: 5 أو 10 أو 15 أو 20 أو 30. الافتراضي: 20 دقيقة.

holdem-set-raise-mode = وضع المزايدة: { $mode }
holdem-select-raise-mode = اختر وضع المزايدة
holdem-option-changed-raise-mode = تم ضبط وضع المزايدة على { $mode }.
holdem-desc-raise-mode = نمط حد المزايدة: بلا حد، أو حد القدر، أو ضعف حد القدر. الافتراضي: بلا حد.

holdem-set-max-raises = الحد الأقصى للمزايدات في كل جولة رهان: { $count }
holdem-enter-max-raises = أدخل الحد الأقصى للمزايدات في كل جولة رهان (0 لغير محدود)
holdem-option-changed-max-raises = تم ضبط الحد الأقصى للمزايدات في كل جولة رهان على { $count }.
holdem-desc-max-raises = الحد الأقصى للمزايدات المسموح بها في جولة رهان واحدة، من 0 إلى 10. اضبط على 0 لإلغاء حد المزايدة. الافتراضي: 0.

holdem-error-big-blind-too-high = يجب أن يكون الرهان الأعمى الكبير ({ $blind } رقاقة) أقل من الرصيد الابتدائي ({ $chips } رقاقة).
holdem-error-ante-too-high = يجب أن يكون الرهان المسبق ({ $ante } رقاقة) أقل من الرصيد الابتدائي ({ $chips } رقاقة).
holdem-error-forced-bets-too-high = مع تفعيل الرهانات المسبقة من المستوى 0، يجب أن يكون مجموع الرهان المسبق والرهان الأعمى الكبير ({ $ante } + { $blind } رقاقة) أقل من الرصيد الابتدائي ({ $chips } رقاقة).

holdem-antes-posted = تم دفع الرهانات المسبقة. يحتوي القدر الآن على { $amount } رقاقة.
holdem-you-post-small-blind = تدفع الرهان الأعمى الصغير ({ $sb } رقاقة). { $bb_player } يدفع الرهان الأعمى الكبير ({ $bb } رقاقة).
holdem-you-post-big-blind = { $sb_player } يدفع الرهان الأعمى الصغير ({ $sb } رقاقة). تدفع الرهان الأعمى الكبير ({ $bb } رقاقة).
holdem-players-post-blinds = { $sb_player } يدفع الرهان الأعمى الصغير ({ $sb } رقاقة). { $bb_player } يدفع الرهان الأعمى الكبير ({ $bb } رقاقة).

holdem-raise-invalid = أدخل عددًا صحيحًا أكبر من 0 لمبلغ المزايدة.
holdem-raise-cap-reached = تم بلوغ حد { $count } مزايدة في جولة الرهان هذه بالفعل. يمكنك المجاراة أو الانسحاب.
holdem-raise-over-stack = حاولت المزايدة بمقدار { $requested } رقاقة، لكن لديك { $chips } رقاقة فقط متبقية. أدخل مزايدة أصغر أو اختر المراهنة بكل الرقاقات.
holdem-raise-too-small = حاولت المزايدة بمقدار { $requested } رقاقة. الحد الأدنى للمزايدة هو { $minimum } رقاقة.
holdem-raise-over-limit = حاولت المزايدة بمقدار { $requested } رقاقة. ضمن { $mode ->
    [pot_limit] حد القدر
    [double_pot] ضعف حد القدر
   *[other] وضع المزايدة المختار
}، أكبر مزايدة متاحة بعد المجاراة هي { $maximum } رقاقة.
holdem-all-in-over-limit = لا يمكنك المراهنة بكل رقاقاتك المتبقية البالغة { $stack } رقاقة لأن { $mode ->
    [pot_limit] حد القدر
    [double_pot] ضعف حد القدر
   *[other] وضع المزايدة المختار
} يسمح حاليًا بمزايدة لا تتجاوز { $maximum } رقاقة بعد المجاراة. استخدم المزايدة لإدخال مبلغ مسموح.
holdem-all-in-raise-cap-reached = لا يمكنك المراهنة بكل الرقاقات كمزايدة كاملة لأنه تم بلوغ حد { $count } مزايدة بالفعل. يمكنك المجاراة أو الانسحاب.
holdem-all-in-unavailable-raise-cap = المراهنة بكل الرقاقات غير متاحة لأنها ستكون مزايدة كاملة بعد بلوغ حد المزايدة. يمكنك المجاراة أو الانسحاب.
holdem-all-in-unavailable-limit = المراهنة بكل الرقاقات غير متاحة لأن رصيدك يتجاوز حد الرهان الحالي. استخدم المزايدة لإدخال مبلغ مسموح.
holdem-raise-unavailable-cap = المزايدة غير متاحة لأن جولة الرهان هذه بلغت حد المزايدة.
holdem-raise-unavailable-limit = المزايدة الكاملة غير متاحة برصيدك وحد الرهان الحالي. يمكنك المجاراة أو الانسحاب أو المراهنة بكل الرقاقات عندما يكون ذلك مسموحًا.

holdem-current-bet = الرهان الحالي على الطاولة هو { $amount } رقاقة.
holdem-raise-range = الحد الأدنى للمزايدة هو { $minimum } رقاقة. يمكنك المزايدة بما يصل إلى { $maximum } رقاقة بعد المجاراة.
holdem-no-full-raise-available = تحتاج { $to_call } رقاقة للمجاراة ولديك { $chips } رقاقة متبقية، لذا لا يمكنك إجراء مزايدة كاملة. يمكنك المجاراة بكل رقاقاتك أو الانسحاب.
holdem-button-unavailable = لا يوجد موضع للزر في اليد الحالية بعد.
holdem-position-unavailable = أنت لست نشطًا في اليد الحالية، لذا ليس لديك موضع رهان.
holdem-reveal-no-live-hand = لا يمكنك كشف البطاقتين المخفيتين إلا عند الوصول إلى المواجهة بيد حية.
holdem-private-hand-unavailable = نفدت رقاقاتك ولم تعد لديك يد حية لقراءتها.

holdem-winner-chips = { $rank }. { $player }: { $chips } { $chips ->
    [one] رقاقة
    [two] رقاقتان
    [few] رقاقات
    [many] رقاقة
   *[other] رقاقة
}
