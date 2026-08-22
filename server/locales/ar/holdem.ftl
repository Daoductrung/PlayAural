game-name-holdem = بوكر تكساس هولدم
holdem-set-starting-chips = رقائق البداية: { $count }
holdem-enter-starting-chips = أدخل رقائق البداية
holdem-option-changed-starting-chips = تم ضبط شرائح البداية على { $count }.
holdem-desc-starting-chips = مجموع رقائق Texas Hold'em الافتتاحي لكل لاعب، من 100 إلى 1,000,000 رقاقة. الافتراضي: 20000.
holdem-set-big-blind = أعمى كبير: { $count }
holdem-enter-big-blind = أدخل الرهان المبدئي الكبير
holdem-option-changed-big-blind = تم تعيين الرهان المبدئي الكبير على { $count }.
holdem-desc-big-blind = قاعدة مبلغ أعمى كبير. يجب أن يكون أقل من مكدس البداية (الافتراضي 200، النطاق من 1 إلى 1,000,000 شريحة).
holdem-set-ante = أنتي : { $count }
holdem-enter-ante = أدخل الرهان
holdem-option-changed-ante = تم ضبط الرهان على { $count }.
holdem-desc-ante = مساهمة إجبارية اختيارية ينشرها كل لاعب نشط بمجرد تنشيط الرهانات المسبقة، من 0 إلى 1,000,000 رقاقة. الافتراضي: 0.
holdem-set-ante-start = الرهان المسبق يبدأ عند المستوى: { $count }
holdem-enter-ante-start = أدخل المستوى الأعمى لتمكين الرهان المسبق
holdem-option-changed-ante-start = تم ضبط مستوى البداية المسبق على { $count }.
holdem-desc-ante-start-level = المستوى الأعمى حيث تبدأ الرهانات المسبقة. يتم تنشيط الرهان الإيجابي من توزيع الورق الأول عندما يكون هذا 0 (الافتراضي 0، النطاق 0-20).
holdem-set-turn-timer = مؤقت الدوران: { $mode }
holdem-select-turn-timer = حدد مؤقت الدوران
holdem-option-changed-turn-timer = قم بضبط المؤقت على { $mode }.
holdem-desc-turn-timer = حد زمني اختياري لكل قرار في Hold'em: 5، 10، 15، 20، 30، 45، 60، أو 90 ثانية، أو غير محدود. الافتراضي: غير محدود.
holdem-set-blind-timer = الموقت الأعمى: { $mode }
holdem-select-blind-timer = حدد الموقت الأعمى
holdem-option-changed-blind-timer = تم ضبط المؤقت الأعمى على { $mode }.
holdem-desc-blind-timer = الدقائق بين الزيادات العمياء: 5، 10، 15، 20، أو 30. الافتراضي: 20 دقيقة.
holdem-set-raise-mode = وضع الرفع: { $mode }
holdem-select-raise-mode = حدد وضع الرفع
holdem-option-changed-raise-mode = تم ضبط وضع الرفع على { $mode }.
holdem-desc-raise-mode = رفع نمط الحد: لا يوجد حد، حد الرهان، أو حد الرهان المزدوج. الافتراضي: لا يوجد حد.
holdem-set-max-raises = الحد الأقصى للزيادة في كل جولة مراهنة: { $count }
holdem-enter-max-raises = أدخل الحد الأقصى للزيادة في كل جولة مراهنة (0 لعدد غير محدود)
holdem-option-changed-max-raises = تم ضبط الحد الأقصى للزيادات في كل جولة مراهنة على { $count }.
holdem-desc-max-raises = الحد الأقصى للزيادات المسموح بها في جولة الرهان الواحدة، من 0 إلى 10. قم بتعيين 0 لعدم وجود سقف للزيادة. الافتراضي: 0.
holdem-error-big-blind-too-high = يجب أن تكون الرهان المبدئي الكبير ({ $blind } الرقائق) أقل من مجموع رقائق البداية ({ $chips } الرقائق).
holdem-error-ante-too-high = يجب أن يكون الرهان المسبق ({ $ante } الرقائق) أقل من مجموعة البداية ({ $chips } الرقائق).
holdem-error-forced-bets-too-high = مع تنشيط الرهان المسبق من المستوى 0، يجب أن يكون الرهان المسبق بالإضافة إلى الرهان المبدئي الكبير ({ $ante } + { $blind } الرقائق) أقل من مجموعة البداية ({ $chips } الرقائق).
holdem-antes-posted = يتم نشر النمل. الوعاء يحتوي الآن على { $amount } رقائق.
holdem-you-post-small-blind = قمت بنشر الرهان المبدئي الصغير ({ $sb } الرقائق). { $bb_player } ينشر الرهان المبدئي الكبير ({ $bb } الرقائق).
holdem-you-post-big-blind = { $sb_player } ينشر الرهان المبدئي الصغير ({ $sb } الرقائق). قمت بنشر الرهان المبدئي الكبير ({ $bb } الرقائق).
holdem-players-post-blinds = { $sb_player } ينشر الرهان المبدئي الصغير ({ $sb } الرقائق). { $bb_player } ينشر الرهان المبدئي الكبير ({ $bb } الرقائق).
holdem-raise-invalid = أدخل رقمًا صحيحًا أكبر من 0 للمبلغ المراد رفعه.
holdem-raise-cap-reached = الحد { $count } لقد تم بالفعل الوصول إلى الزيادات في جولة الرهان هذه. يمكنك الاتصال أو الطي.
holdem-raise-over-stack = لقد حاولت رفع بواسطة { $requested } رقائق، ولكن لديك فقط { $chips } الرقائق المتبقية. أدخل زيادة أقل أو اختر الكل في.
holdem-raise-too-small = لقد حاولت رفع بواسطة { $requested } رقائق. الحد الأدنى للزيادة هو { $minimum } رقائق.
holdem-raise-over-limit =
    لقد حاولت رفع بواسطة { $requested } رقائق. تحت { $mode ->
        [pot_limit] حد الوعاء
        [double_pot] حد الوعاء المزدوج
       *[other] وضع الرفع المحدد
    }، أكبر زيادة متاحة بعد الاتصال هي { $maximum } رقائق.
holdem-all-in-over-limit =
    لا يمكنك المشاركة بكل ما تبقى لديك من { $stack } رقائق لأن { $mode ->
        [pot_limit] حد الوعاء
        [double_pot] حد الوعاء المزدوج
       *[other] وضع الرفع المحدد
    } يسمح حاليا برفع الحد الأقصى { $maximum } رقائق بعد الاتصال. استخدم رفع لإدخال المبلغ المسموح به.
holdem-all-in-raise-cap-reached = لا يمكنك إضافة كل شيء كزيادة كاملة لأن الحد { $count } لقد تم بالفعل الوصول إلى الزيادات. يمكنك الاتصال أو الطي.
holdem-all-in-unavailable-raise-cap = كل ما في الأمر غير متاح لأنه سيكون بمثابة زيادة كاملة بعد الوصول إلى حد الزيادة. يمكنك الاتصال أو الطي.
holdem-all-in-unavailable-limit = الكل غير متاح لأن مجموعتك تتجاوز حد الرهان الحالي. استخدم رفع لإدخال المبلغ المسموح به.
holdem-raise-unavailable-cap = الزيادة غير متاحة لأن جولة الرهان هذه قد وصلت إلى حد الزيادة.
holdem-raise-unavailable-limit = الزيادة الكاملة غير متاحة مع مجموعتك وحد الرهان الحالي. يمكنك الاتصال أو طي أو استخدام الكل عندما يكون ذلك قانونيًا.
holdem-current-bet = رهان الجدول الحالي هو { $amount } رقائق.
holdem-raise-range = الحد الأدنى للزيادة هو { $minimum } رقائق. يمكنك زيادة ما يصل إلى { $maximum } رقائق بعد الاتصال.
holdem-no-full-raise-available = تحتاج { $to_call } رقائق للاتصال بها { $chips } الرقائق المتبقية، لذلك لا يمكنك الحصول على زيادة كاملة. يمكنك استدعاء الكل أو طيه.
holdem-button-unavailable = لا يوجد موضع زر للعقرب الحالي حتى الآن.
holdem-position-unavailable = أنت غير نشط في توزيع الورق الحالي، لذا ليس لديك مركز مراهنة.
holdem-reveal-no-live-hand = لا يمكنك الكشف عن البطاقات المقلوبة إلا عندما تصل إلى المواجهة بتوزيع ورق مباشر.
holdem-private-hand-unavailable = لقد نفدت رقائقك ولم يعد لديك يد حية للقراءة.
holdem-winner-chips =
    { $rank }. { $player }: { $chips } { $chips ->
        [one] شريحة
       *[other] رقائق
    }
