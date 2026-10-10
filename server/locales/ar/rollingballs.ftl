# Rolling Balls

game-name-rollingballs = الكرات المتدحرجة

# Actions
rb-take = أخذ { $count } { $count ->
    [one] كرة
   *[other] كرات
}
rb-reshuffle-action = إعادة خلط مقدمة الأنبوب ({ $remaining } استخدام متبقٍ)
rb-view-pipe-action = معاينة الأنبوب ({ $remaining } استخدام متبقٍ)
rb-check-pipe-status = عرض حالة الأنبوب
rb-key-reshuffle-pipe = إعادة خلط مقدمة الأنبوب
rb-key-view-pipe = معاينة الأنبوب

# Taking and revealing balls
rb-you-take = تلتزم بأخذ { $count } { $count ->
    [one] كرة
   *[other] كرات
} من مقدمة الأنبوب المكوّن من { $remaining } كرة.
rb-player-takes = يلتزم { $player } بأخذ { $count } { $count ->
    [one] كرة
   *[other] كرات
} من مقدمة الأنبوب المكوّن من { $remaining } كرة.
rb-you-take-brief = تأخذ { $count } { $count ->
    [one] كرة
   *[other] كرات
}.
rb-player-takes-brief = يأخذ { $player } { $count } { $count ->
    [one] كرة
   *[other] كرات
}.
rb-you-forced-take = تبقّت { $count } { $count ->
    [one] كرة فقط
   *[other] كرات فقط
}، أقل من الحد الأدنى للأخذ البالغ { $minimum }، لذا يجب أن تأخذ البقية.
rb-player-forced-takes = تبقّت { $count } { $count ->
    [one] كرة فقط
   *[other] كرات فقط
}، أقل من الحد الأدنى للأخذ البالغ { $minimum }، لذا يجب أن يأخذ { $player } البقية.
rb-you-forced-take-brief = يجب أن تأخذ { $count } { $count ->
    [one] كرة أخيرة
   *[other] كرات أخيرة
}.
rb-player-forced-takes-brief = يجب أن يأخذ { $player } { $count } { $count ->
    [one] كرة أخيرة
   *[other] كرات أخيرة
}.

rb-your-ball-plus = كرتك { $num }: { $description }. زائد { $value } { $value ->
    [one] نقطة
   *[other] نقطة
}.
rb-player-ball-plus = كرة { $player } رقم { $num }: { $description }. زائد { $value } { $value ->
    [one] نقطة
   *[other] نقطة
}.
rb-your-ball-minus = كرتك { $num }: { $description }. ناقص { $value } { $value ->
    [one] نقطة
   *[other] نقطة
}.
rb-player-ball-minus = كرة { $player } رقم { $num }: { $description }. ناقص { $value } { $value ->
    [one] نقطة
   *[other] نقطة
}.
rb-your-ball-zero = كرتك { $num }: { $description }. لا تغيير في النتيجة.
rb-player-ball-zero = كرة { $player } رقم { $num }: { $description }. لا تغيير في النتيجة.

rb-your-draw-summary = لسحبك المكوّن من { $count } كرة قيمة صافية قدرها { $delta } نقطة. أصبحت نتيجتك الآن { $score }، مع بقاء { $remaining } كرة في الأنبوب.
rb-player-draw-summary = لسحب { $player } المكوّن من { $count } كرة قيمة صافية قدرها { $delta } نقطة. أصبحت نتيجة { $player } الآن { $score }، مع بقاء { $remaining } كرة في الأنبوب.
rb-your-draw-summary-brief = الصافي { $delta }؛ نتيجتك { $score }. تبقّت { $remaining } كرة.
rb-player-draw-summary-brief = { $player }: الصافي { $delta }، النتيجة { $score }. تبقّت { $remaining } كرة.
rb-your-score-legacy = أصبحت نتيجتك الآن { $score }، مع بقاء { $remaining } كرة في الأنبوب.
rb-player-score-legacy = أصبحت نتيجة { $player } الآن { $score }، مع بقاء { $remaining } كرة في الأنبوب.

# Reshuffling
rb-you-reshuffle = تعيد خلط أول { $count } كرة. { $penalty ->
    [0] لا توجد عقوبة
   *[other] تدفع عقوبة قدرها { $penalty } نقطة
}؛ أصبحت نتيجتك الآن { $score }، ولديك { $remaining } إعادة خلط متبقية.
rb-player-reshuffles = يعيد { $player } خلط أول { $count } كرة. { $penalty ->
    [0] لا توجد عقوبة
   *[other] يدفع { $player } عقوبة قدرها { $penalty } نقطة
}؛ أصبحت النتيجة { GENDER_TERM($player_gender, "possessive-determiner") } الآن { $score }، و{ GENDER_TERM($player_gender, "subject-have") } { $remaining } إعادة خلط متبقية.
rb-you-reshuffle-brief = تعيد خلط { $count } كرة؛ العقوبة { $penalty }، النتيجة { $score }، { $remaining } استخدام متبقٍ.
rb-player-reshuffles-brief = يعيد { $player } خلط { $count } كرة؛ العقوبة { $penalty }، النتيجة { $score }، { $remaining } استخدام متبقٍ.

# Pipe preview and status
rb-view-pipe-header = عرض الكرات الـ { $shown } التالية من أصل { $total }. لديك { $remaining } معاينة جديدة متبقية.
rb-view-pipe-ball = { $num }: { $description }. القيمة: { $value } نقطة.
rb-status-pipe = الجولة { $round }. تبقّت { $count } كرة في الأنبوب.
rb-status-take-range = يتطلب كل دور عادي بين { $min } و{ $max } كرة.
rb-status-turn = الدور الحالي: { $player }.
rb-status-resources = لديك { $views } معاينة أنبوب جديدة و{ $reshuffles } إعادة خلط متبقية.

# Start and round flow
rb-pipe-filled = مُلئ الأنبوب بـ { $count } كرة فريدة من: { $packs }.
rb-round-start = تبدأ الجولة { $round } مع بقاء { $count } كرة في الأنبوب.
rb-round-start-brief = الجولة { $round }؛ تبقّت { $count } كرة.

# End of game
rb-pipe-empty = الأنبوب فارغ.
rb-winner = يفوز { $player } بـ { $score } نقطة.
rb-you-win = تفوز بـ { $score } نقطة.
rb-you-tie = تتشارك الفوز مع { $players }؛ أنهى كل منكم على { $score } نقطة.
rb-tie = يتشارك { $players } الفوز بـ { $score } نقطة.
rb-line-format = { $rank }. { $player }: { $points }

# Options
rb-set-min-take = الحد الأدنى للكرات في الدور: { $count }
rb-enter-min-take = أدخل الحد الأدنى للكرات في الدور، من 1 إلى 5:
rb-option-changed-min-take = تم ضبط الحد الأدنى للكرات في الدور على { $count }.
rollingballs-desc-min-take = أقل عدد من الكرات يجب أن يأخذه اللاعب في الدور (الافتراضي 1، المدى 1-5).
rb-set-max-take = الحد الأقصى للكرات في الدور: { $count }
rb-enter-max-take = أدخل الحد الأقصى للكرات في الدور، من 1 إلى 5:
rb-option-changed-max-take = تم ضبط الحد الأقصى للكرات في الدور على { $count }.
rollingballs-desc-max-take = أقصى عدد من الكرات يمكن للاعب أخذه في الدور. لا يمكن أن تبدأ اللعبة إذا كان هذا أقل من الحد الأدنى (الافتراضي 3، المدى 1-5).
rb-set-view-pipe-limit = معاينات الأنبوب الجديدة لكل لاعب: { $count }
rb-enter-view-pipe-limit = أدخل معاينات الأنبوب الجديدة لكل لاعب، من 0 إلى 100؛ 0 يعطّل المعاينات:
rb-option-changed-view-pipe-limit = تم ضبط معاينات الأنبوب الجديدة لكل لاعب على { $count }.
rollingballs-desc-view-pipe-limit = كم كرة قادمة يمكن معاينتها من الأنبوب. اضبط 0 لتعطيل المعاينات (الافتراضي 5، المدى 0-100).
rb-set-reshuffle-limit = إعادات الخلط لكل لاعب: { $count }
rb-enter-reshuffle-limit = أدخل إعادات الخلط لكل لاعب، من 0 إلى 100؛ 0 يعطّل إعادة الخلط:
rb-option-changed-reshuffle-limit = تم ضبط إعادات الخلط لكل لاعب على { $count }.
rollingballs-desc-reshuffle-limit = كم إعادة خلط متاحة قبل نفاد الأنبوب (الافتراضي 3، المدى 0-100).
rb-set-reshuffle-penalty = عقوبة إعادة الخلط: { $points } نقطة
rb-enter-reshuffle-penalty = أدخل عقوبة إعادة الخلط، من 0 إلى 5 نقاط:
rb-option-changed-reshuffle-penalty = تم ضبط عقوبة إعادة الخلط على { $points } نقطة.
rollingballs-desc-reshuffle-penalty = عقوبة النتيجة المطبّقة عند استخدام إعادة خلط. يظهر هذا الخيار فقط عند توفر إعادات الخلط (الافتراضي 1، المدى 0-5).
rb-set-ball-packs = مجموعات الكرات ({ $count } من أصل { $total } مُختارة)
rb-option-changed-ball-packs = تم تغيير اختيار مجموعة الكرات.
rollingballs-desc-ball-packs = اختر مجموعات الكرات المواضيعية المضمّنة في الأنبوب. يجب أن تبقى مجموعة واحدة على الأقل مختارة.

# Contextual disabled reasons and setup validation
rb-draw-resolving = انتظر حتى ينتهي سحب الكرة الحالي لـ { $player } قبل بدء إجراء أنبوب آخر.
rb-take-not-your-turn = لا يمكنك أخذ { $count } كرة الآن لأنه دور { $player }.
rb-take-outside-range = حاولت أخذ { $count } كرة، لكن هذه اللعبة تسمح بين { $min } و{ $max } لكل دور عادي.
rb-not-enough-balls = حاولت أخذ { $count } كرة، لكن تبقّت { $remaining } فقط في الأنبوب.
rb-reshuffle-not-your-turn = لا يمكنك إعادة الخلط الآن لأنه دور { $player }.
rb-no-reshuffles-left = لقد استخدمت كل إعادات الخلط البالغة { $limit } لهذه اللعبة.
rb-already-reshuffled = لقد أعدت الخلط بالفعل في هذا الدور. خذ كرات لإنهاء الدور.
rb-not-enough-balls-to-reshuffle = تحتاج إعادة الخلط إلى { $required } كرة على الأقل، لكن تبقّت { $remaining } فقط. خذ كرات بدلاً من ذلك.
rb-no-views-left = تغيّر الأنبوب، وقد استخدمت كل معايناتك الجديدة البالغة { $limit }. لا يزال بإمكانك إعادة فتح معاينة لم تتغير قبل أن يتحرك الأنبوب.
rb-error-min-take-invalid = الحد الأدنى للأخذ هو { $count }؛ يجب أن يكون من { $min } إلى { $max }.
rb-error-max-take-invalid = الحد الأقصى للأخذ هو { $count }؛ يجب أن يكون من { $min } إلى { $max }.
rb-error-take-range-conflict = الحد الأدنى للأخذ هو { $min }، أعلى من الحد الأقصى البالغ { $max }. اخفض الحد الأدنى أو ارفع الحد الأقصى قبل البدء.
rb-error-view-limit-invalid = حد المعاينة هو { $count }؛ يجب أن يكون من { $min } إلى { $max }.
rb-error-reshuffle-limit-invalid = حد إعادة الخلط هو { $count }؛ يجب أن يكون من { $min } إلى { $max }.
rb-error-reshuffle-penalty-invalid = عقوبة إعادة الخلط هي { $points }؛ يجب أن تكون من { $min } إلى { $max } نقطة.
rb-error-no-ball-packs = اختر مجموعة كرات واحدة على الأقل قبل بدء الكرات المتدحرجة.
rb-error-invalid-ball-packs = يحتوي الاختيار على { $count } { $count ->
    [one] مجموعة كرات غير متاحة
   *[other] مجموعات كرات غير متاحة
}. أزل المجموعات غير المتاحة قبل البدء.

# Ball sets
rb-pack-international = حول العالم
rb-pack-vietnam = رحلة عبر فيتنام

# Around the World: -5
rb-ball-paris-pickpocket = سرقة جواز السفر والمحفظة في الخارج
rb-ball-lost-luggage-in-london = زيارة طبية طارئة في الخارج
rb-ball-tokyo-train-delay = تفويت آخر رحلة ربط دولية
rb-ball-sahara-sandstorm = إجلاء بسبب طقس قاسٍ
rb-ball-passport-lost-before-flight = فقدان جواز السفر قبل المغادرة
# Around the World: -4
rb-ball-venice-flood = فيضان يغلق مكان إقامتك
rb-ball-new-york-traffic = إلغاء رحلة ليلية
rb-ball-amazon-mosquito-swarm = إرسال أمتعة أساسية إلى بلد خاطئ
rb-ball-berlin-club-rejected = حجز الفندق مفقود عند الوصول
rb-ball-hotel-booking-vanished = طريق جبلي مغلق لعدة أيام
# Around the World: -3
rb-ball-spilled-coffee-in-rome = تحطم الهاتف أثناء التنقل
rb-ball-sydney-sunburn = إنهاك حراري يلغي رحلة يومية
rb-ball-istanbul-bazaar-scam = فشل حجز جولة مدفوعة مسبقاً
rb-ball-moscow-blizzard = عاصفة ثلجية تحبس قطارك
rb-ball-dubai-heatwave = تعطل مركبة مستأجرة
# Around the World: -2
rb-ball-mexico-city-smog = جودة هواء رديئة تغيّر المسار
rb-ball-cairo-camel-spit = دوار الحركة في رحلة طويلة
rb-ball-athens-ruins-trip = التواء الكاحل في جولة سيراً
rb-ball-rio-carnival-hangover = النوم أكثر من اللازم وتفويت جولة الصباح
rb-ball-bali-belly = اضطراب في المعدة يكلفك فترة بعد الظهر
# Around the World: -1
rb-ball-swiss-alps-avalanche = مسار خلّاب مغلق للسلامة
rb-ball-amsterdam-bicycle-crash = إطار دراجة مثقوب
rb-ball-bangkok-tuk-tuk-breakdown = توقف التوك توك في الزحام
rb-ball-iceland-volcano-ash = تنبيه طقس يؤخر الرحلة
rb-ball-cape-town-wind = رياح قوية تغلق نقطة المشاهدة
# Around the World: 0
rb-ball-neutral-passport = ختم جديد في جواز السفر
rb-ball-airport-layover = توقف هادئ في المطار
rb-ball-hotel-lobby = الانتظار في بهو الفندق
rb-ball-tourist-map = فرد خريطة المدينة
rb-ball-souvenir-magnet = اختيار مغناطيس تذكاري
# Around the World: +1
rb-ball-free-museum-day = دخول مجاني للمتحف
rb-ball-street-food-snack = وجبة طعام شارع ممتازة
rb-ball-post-card-home = إرسال بطاقة بريدية إلى الوطن
rb-ball-friendly-local = إرشادات مفيدة من أحد السكان
rb-ball-sunny-day = طقس مثالي للاستكشاف
# Around the World: +2
rb-ball-eiffel-tower-view = أفق باريس من برج إيفل
rb-ball-taj-mahal-sunrise = شروق الشمس عند تاج محل
rb-ball-great-wall-hike = نزهة على سور الصين العظيم
rb-ball-machu-picchu-climb = صباح في ماتشو بيتشو
rb-ball-kyoto-cherry-blossoms = أزهار الكرز في كيوتو
# Around the World: +3
rb-ball-colosseum-tour = زيارة مرشدة للكولوسيوم
rb-ball-pyramids-exploration = استكشاف مجمع أهرامات الجيزة
rb-ball-santorini-sunset = غروب الشمس فوق سانتوريني
rb-ball-aurora-borealis = الأضواء الشمالية في الأعلى
rb-ball-safari-lion-sighting = مشاهدة حياة برية مسؤولة في رحلة سفاري
# Around the World: +4
rb-ball-bora-bora-villa = إقامة على البحيرة في بورا بورا
rb-ball-maldives-scuba = غوص في الشعاب المرجانية في المالديف
rb-ball-niagara-falls-boat = رحلة بالقارب عند شلالات نياغارا
rb-ball-grand-canyon-heli = جولة طيران فوق جراند كانيون
rb-ball-serengeti-migration = الهجرة الكبرى في سيرينغيتي
# Around the World: +5
rb-ball-first-class-upgrade = ترقية مفاجئة إلى الدرجة الأولى
rb-ball-lottery-in-macau = الفوز بتذكرة قطار لمدة عام
rb-ball-private-jet = رحلة جزيرة تحدث مرة في العمر
rb-ball-royal-palace-invite = زيارة متحف خاصة بعد ساعات العمل
rb-ball-world-tour-ticket = تذكرة حول العالم

# Journey Through Vietnam: -5
rb-ball-stolen-motorbike = سرقة جواز السفر والمحفظة أثناء الرحلة
rb-ball-flooded-street-saigon = فيضان يفرض انتقالاً طارئاً
rb-ball-food-poisoning-bun-mam = حالة طبية طارئة تقطع الرحلة
rb-ball-fake-taxi-scam = عطل في النقل يسبب تفويت رحلة طيران
rb-ball-passport-lost-at-airport = فقدان جواز السفر في المطار
# Journey Through Vietnam: -4
rb-ball-typhoon-in-central-vietnam = إجلاء بسبب إعصار على الساحل الأوسط
rb-ball-lost-wallet-ben-thanh = فقدان أمتعة أساسية أثناء النقل
rb-ball-traffic-jam-hanoi = إلغاء قطار ليلي
rb-ball-pickpocketed-in-bui-vien = سرقة الهاتف في حي مزدحم
rb-ball-mountain-road-landslide = ممر جبلي مغلق بسبب انهيار أرضي
# Journey Through Vietnam: -3
rb-ball-spilled-pho = تلف الكاميرا في مطر مفاجئ
rb-ball-overcharged-for-coffee = خلط في حجز الفندق
rb-ball-sunburn-in-mui-ne = إنهاك حراري في موي ني
rb-ball-missed-train-to-sapa = تفويت القطار الليلي إلى لاو كاي
rb-ball-loud-karaoke-next-door = ليلة بلا نوم قبل مغادرة مبكرة
# Journey Through Vietnam: -2
rb-ball-broken-flip-flop = انقطاع حزام الصندل في جولة سيراً
rb-ball-sudden-downpour = هطول مطر استوائي مفاجئ
rb-ball-dog-chased-you = محطة حافلة خاطئة بعيدة عن الفندق
rb-ball-bitten-by-mosquitoes = أمسية من لدغات البعوض
rb-ball-out-of-gas = نفاد وقود الدراجة النارية
# Journey Through Vietnam: -1
rb-ball-spicy-chili-bite = فلفل حار بشكل غير متوقع
rb-ball-delayed-flight = تأخير قصير لرحلة داخلية
rb-ball-wifi-disconnected = إشارة ضعيفة في الجبال
rb-ball-forgot-umbrella = ترك معطف المطر في الفندق
rb-ball-minor-scratch = منعطف خاطئ في الحي القديم
# Journey Through Vietnam: 0
rb-ball-plastic-stool = مقعد على كرسي رصيف
rb-ball-iced-tea-tra-da = كأس من الشاي المثلج (ترا دا)
rb-ball-waiting-for-green-light = الانتظار خلال ضوء أحمر طويل
rb-ball-bamboo-hat = تجربة قبعة النون لا
rb-ball-motorbike-helmet = تثبيت خوذة الدراجة النارية
# Journey Through Vietnam: +1
rb-ball-tasty-banh-mi = بان مي مقرمش على الإفطار
rb-ball-free-sugar-cane-juice = عصير قصب سكر طازج
rb-ball-friendly-street-vendor = ترحيب حار من بائع في السوق
rb-ball-cool-breeze = نسيم بارد بعد المطر
rb-ball-found-10k-vnd = رحلة حافلة محلية بسعر زهيد
# Journey Through Vietnam: +2
rb-ball-delicious-pho-bowl = وعاء فو عطري
rb-ball-egg-coffee-in-hanoi = قهوة البيض في هانوي
rb-ball-boat-ride-in-ninh-binh = رحلة بزورق سامبان عبر مجمع ترانغ آن الطبيعي
rb-ball-lantern-festival-hoian = أمسية مضاءة بالفوانيس في بلدة هوي آن القديمة
rb-ball-motorbike-road-trip = رحلة بقارب في بستان دلتا ميكونغ
# Journey Through Vietnam: +3
rb-ball-ha-long-bay-cruise = رحلة بحرية عبر خليج ها لونغ - أرخبيل كات با
rb-ball-golden-bridge-bana-hills = الجسر الذهبي فوق تلال با نا
rb-ball-phu-quoc-sunset = غروب الشمس على فو كووك
rb-ball-sapa-terraced-fields = الحقول المدرجة حول سا با
rb-ball-phong-nha-cave-exploration = رحلة كهوف في فونغ نها - كي بانغ
# Journey Through Vietnam: +4
rb-ball-tet-holiday-lucky-money = لمّ شمل التيت ونقود الحظ
rb-ball-vip-ticket-to-concert = شروق الشمس على مسار ها جيانغ
rb-ball-luxury-resort-stay = زيارة حفظ مجتمعي في كون داو
rb-ball-business-class-flight = مقصورة خلّابة على قطار إعادة التوحيد
rb-ball-won-lottery-vietlott = ليلة مهرجان بين معالم هوي
# Journey Through Vietnam: +5
rb-ball-billionaire-inheritance = بعثة سون دونغ
rb-ball-found-gold-treasure = ورشة ثقافية خاصة مع حرفيين مهرة
rb-ball-free-house-in-district-1 = رحلة قطار لمدة شهر عبر فيتنام
rb-ball-national-hero-award = ضيف شرف في مهرجان قروي
rb-ball-ultimate-happiness = رحلة الأحلام من ها جيانغ إلى كا ماو
