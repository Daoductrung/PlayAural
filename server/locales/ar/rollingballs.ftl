# Rolling Balls

game-name-rollingballs = الكرات المتدحرجة
# Actions
rb-take =
    خذ { $count } { $count ->
        [one] الكرة
       *[other] كرات
    }
rb-reshuffle-action = قم بتعديل الجزء الأمامي من الأنبوب ({ $remaining } يستخدم المتبقي)
rb-view-pipe-action = معاينة الأنبوب ({ $remaining } الاستخدامات المتبقية)
rb-check-pipe-status = التحقق من حالة الأنابيب
rb-key-reshuffle-pipe = تعديل الجزء الأمامي من الأنبوب
rb-key-view-pipe = معاينة الأنبوب
# Taking and revealing balls
rb-you-take =
    تلتزم بأخذ { $count } { $count ->
        [one] الكرة
       *[other] كرات
    } من أمام { $remaining }- أنبوب الكرة.
rb-player-takes =
    { $player } يلتزم بأخذ { $count } { $count ->
        [one] الكرة
       *[other] كرات
    } من أمام { $remaining }- أنبوب الكرة.
rb-you-take-brief =
    تأخذ { $count } { $count ->
        [one] الكرة
       *[other] كرات
    }.
rb-player-takes-brief =
    { $player } يأخذ { $count } { $count ->
        [one] الكرة
       *[other] كرات
    }.
rb-you-forced-take =
    فقط { $count } { $count ->
        [one] تبقى الكرة
       *[other] تبقى الكرات
    }، أقل من الحد الأدنى لـ { $minimum }، لذلك عليك أن تأخذ الباقي.
rb-player-forced-takes =
    فقط { $count } { $count ->
        [one] تبقى الكرة
       *[other] تبقى الكرات
    }، أقل من الحد الأدنى لـ { $minimum }، إذن { $player } يجب أن تأخذ الباقي.
rb-you-forced-take-brief =
    يجب أن تأخذ النهائي { $count } { $count ->
        [one] الكرة
       *[other] كرات
    }.
rb-player-forced-takes-brief =
    { $player } يجب أن تأخذ النهائي { $count } { $count ->
        [one] الكرة
       *[other] كرات
    }.
rb-your-ball-plus =
    كرتك { $num }: { $description }. زائد { $value } { $value ->
        [one] نقطة
       *[other] النقاط
    }.
rb-player-ball-plus =
    { $player }الكرة { $num }: { $description }. زائد { $value } { $value ->
        [one] نقطة
       *[other] النقاط
    }.
rb-your-ball-minus =
    كرتك { $num }: { $description }. ناقص { $value } { $value ->
        [one] نقطة
       *[other] النقاط
    }.
rb-player-ball-minus =
    { $player }الكرة { $num }: { $description }. ناقص { $value } { $value ->
        [one] نقطة
       *[other] النقاط
    }.
rb-your-ball-zero = كرتك { $num }: { $description }. لا تغيير النتيجة.
rb-player-ball-zero = { $player }الكرة { $num }: { $description }. لا تغيير النتيجة.
rb-your-draw-summary =  { $count }الخاص بك - سحب الكرة له قيمة صافية قدرها { $delta } نقاط. درجاتك الآن { $score }مع { $remaining } الكرات المتبقية في الأنبوب.
rb-player-draw-summary = { $player } { $count }-سحب الكرة له قيمة صافية قدرها { $delta } نقاط. { $player }النتيجة الآن { $score }مع { $remaining } الكرات المتبقية في الأنبوب.
rb-your-draw-summary-brief = نت { $delta }; درجاتك هي { $score }. { $remaining } تبقى الكرات.
rb-player-draw-summary-brief = { $player }: صافي { $delta }، النتيجة { $score }. { $remaining } تبقى الكرات.
rb-your-score-legacy = درجاتك الآن { $score }مع { $remaining } الكرات المتبقية في الأنبوب.
rb-player-score-legacy = { $player }النتيجة الآن { $score }مع { $remaining } الكرات المتبقية في الأنبوب.
# Reshuffling
rb-you-reshuffle =
    قمت بتعديل الأول { $count } كرات. { $penalty ->
        [0] ليس هناك عقوبة
       *[other] أنت تدفع { $penalty }-نقطة جزاء
    }; درجاتك الآن { $score }، ولديك { $remaining } تعديلات وزارية اليسار.
rb-player-reshuffles =
    { $player } يعيد الترتيب الأول { $count } كرات. { $penalty ->
        [0] ليس هناك عقوبة
       *[other] { $player } يدفع { $penalty }-نقطة جزاء
    }; درجاتهم الآن { $score }، ولديهم { $remaining } تعديلات وزارية اليسار.
rb-you-reshuffle-brief = قمت بتعديل وزاري { $count } كرات. ضربة جزاء { $penalty }، النتيجة { $score }, { $remaining } يستخدم اليسار.
rb-player-reshuffles-brief = { $player } تعديلات { $count } كرات. ضربة جزاء { $penalty }، النتيجة { $score }, { $remaining } يستخدم اليسار.
# Pipe preview and status
rb-view-pipe-header = عرض التالي { $shown } من { $total } كرات. لديك { $remaining } المعاينات الجديدة المتبقية.
rb-view-pipe-ball = { $num }: { $description }. القيمة: { $value } نقاط.
rb-status-pipe = جولة { $round }. { $count } تبقى الكرات في الأنبوب.
rb-status-take-range = كل دورة عادية تتطلب ما بين { $min } و { $max } كرات.
rb-status-turn = المنعطف الحالي: { $player }.
rb-status-resources = لديك { $views } معاينات الأنابيب الجديدة و { $reshuffles } التعديلات المتبقية.
# Start and round flow
rb-pipe-filled = تم ملء الأنبوب بـ { $count } كرات فريدة من: { $packs }.
rb-round-start = جولة { $round } يبدأ بـ { $count } الكرات المتبقية في الأنبوب.
rb-round-start-brief = جولة { $round }; { $count } تبقى الكرات.
# End of game
rb-pipe-empty = الأنبوب فارغ.
rb-winner = { $player } يفوز مع { $score } نقاط.
rb-you-win = تربح مع { $score } نقاط.
rb-you-tie = أنت تشارك الفوز مع { $players }; انتهى كل منكم من { $score } نقاط.
rb-tie = { $players } شارك الفوز مع { $score } نقاط.
rb-line-format = { $rank }. { $player }: { $points }
# Options
rb-set-min-take = الحد الأدنى من الكرات لكل دور: { $count }
rb-enter-min-take = أدخل الحد الأدنى من الكرات في كل دور، من 1 إلى 5:
rb-option-changed-min-take = الحد الأدنى من الكرات في كل دورة مضبوطة على { $count }.
rollingballs-desc-min-take = الحد الأدنى لعدد الكرات التي يجب على اللاعب أن يأخذها في الدور (الافتراضي 1، النطاق 1-5).
rb-set-max-take = الحد الأقصى للكرات في كل دورة: { $count }
rb-enter-max-take = أدخل الحد الأقصى للكرات في كل دور، من 1 إلى 5:
rb-option-changed-max-take = تم ضبط الحد الأقصى للكرات في كل دورة على { $count }.
rollingballs-desc-max-take = الحد الأقصى لعدد الكرات التي يمكن للاعب أن يأخذها في الدور. لا يمكن أن تبدأ اللعبة إذا كان هذا أقل من الحد الأدنى (الافتراضي 3، النطاق 1-5).
rb-set-view-pipe-limit = معاينات الأنابيب الجديدة لكل لاعب: { $count }
rb-enter-view-pipe-limit = أدخل معاينات الأنابيب الجديدة لكل لاعب، من 0 إلى 100؛ 0 تعطيل المعاينات:
rb-option-changed-view-pipe-limit = تم ضبط معاينات الأنابيب الجديدة لكل لاعب على { $count }.
rollingballs-desc-view-pipe-limit = كم عدد الكرات القادمة التي يمكن معاينتها من الأنبوب. اضبط 0 لتعطيل المعاينات (الافتراضي 5، النطاق 0-100).
rb-set-reshuffle-limit = التعديلات لكل لاعب: { $count }
rb-enter-reshuffle-limit = أدخل التعديلات لكل لاعب، من 0 إلى 100؛ 0 تعطيل التعديل:
rb-option-changed-reshuffle-limit = تم ضبط التعديلات لكل لاعب على { $count }.
rollingballs-desc-reshuffle-limit = كم عدد التعديلات المتاحة قبل نفاد الأنبوب (الافتراضي 3، النطاق 0-100).
rb-set-reshuffle-penalty = عقوبة التعديل: { $points } النقاط
rb-enter-reshuffle-penalty = أدخل عقوبة التعديل الوزاري من 0 إلى 5 نقاط:
rb-option-changed-reshuffle-penalty = تم ضبط عقوبة التعديل الوزاري على { $points } نقاط.
rollingballs-desc-reshuffle-penalty = يتم تطبيق عقوبة النتيجة عند استخدام التعديل الوزاري. يظهر هذا الخيار فقط عند توفر التعديلات (الافتراضي 1، النطاق 0-5).
rb-set-ball-packs = مجموعات الكرات ({ $count } من { $total } مختارة)
rb-option-changed-ball-packs = تم تغيير اختيار مجموعة الكرة.
rollingballs-desc-ball-packs = اختر مجموعات الكرات ذات السمات المضمنة في الأنبوب. يجب أن تظل حزمة واحدة على الأقل محددة.
# Contextual disabled reasons and setup validation
rb-draw-resolving = انتظر حتى { $player }تنتهي عملية سحب الكرة الحالية قبل بدء إجراء أنبوب آخر.
rb-take-not-your-turn = لا يمكنك أن تأخذ { $count } الكرات الآن لأنه { $player }دور.
rb-take-outside-range = لقد حاولت أن تأخذ { $count } الكرات ولكن هذه اللعبة تسمح { $min } إلى { $max } لكل دورة عادية.
rb-not-enough-balls = لقد حاولت أن تأخذ { $count } كرات ولكن فقط { $remaining } تبقى في الأنبوب.
rb-reshuffle-not-your-turn = لا يمكنك التعديل الآن لأنه { $player }دور.
rb-no-reshuffles-left = لقد استخدمت كل { $limit } من التعديلات الخاصة بك لهذه اللعبة.
rb-already-reshuffled = لقد قمت بالفعل بتعديل وزارتك خلال هذا المنعطف. خذ الكرات لإنهاء الدور.
rb-not-enough-balls-to-reshuffle = يحتاج التعديل على الأقل { $required } كرات ولكن فقط { $remaining } يبقى. خذ الكرات بدلا من ذلك.
rb-no-views-left = لقد تغير الأنبوب، واستخدمت كل شيء { $limit } من معايناتك الجديدة. لا يزال بإمكانك إعادة فتح معاينة لم تتغير قبل أن يتحرك الأنبوب.
rb-error-min-take-invalid = الحد الأدنى هو { $count }; يجب أن يكون من { $min } إلى { $max }.
rb-error-max-take-invalid = الحد الأقصى هو { $count }; يجب أن يكون من { $min } إلى { $max }.
rb-error-take-range-conflict = الحد الأدنى هو { $min }، فوق الحد الأقصى { $max }. خفض الحد الأدنى أو رفع الحد الأقصى قبل البدء.
rb-error-view-limit-invalid = حد المعاينة هو { $count }; يجب أن يكون من { $min } إلى { $max }.
rb-error-reshuffle-limit-invalid = حد التعديل هو { $count }; يجب أن يكون من { $min } إلى { $max }.
rb-error-reshuffle-penalty-invalid = عقوبة التعديل هي { $points }; يجب أن يكون من { $min } إلى { $max } نقاط.
rb-error-no-ball-packs = حدد مجموعة كرة واحدة على الأقل قبل البدء في دحرجة الكرات.
rb-error-invalid-ball-packs =
    يحتوي التحديد على { $count } كرة غير متاحة { $count ->
        [one] مجموعة
       *[other] مجموعات
    }. قم بإزالة المجموعات غير المتوفرة قبل البدء.
# Ball sets
rb-pack-all = جميع مجموعات الكرات مختلطة
rb-pack-international = حول العالم
rb-pack-vietnam = رحلة عبر فيتنام
# Around the World: -5
rb-ball-paris-pickpocket = جواز السفر والمحفظة مسروقين بالخارج
rb-ball-lost-luggage-in-london = زيارة طبية طارئة للخارج
rb-ball-tokyo-train-delay = فات آخر اتصال دولي
rb-ball-sahara-sandstorm = إخلاء بسبب الأحوال الجوية القاسية
rb-ball-passport-lost-before-flight = فقدان جواز السفر قبل المغادرة
# Around the World: -4
rb-ball-venice-flood = الفيضان يغلق مكان إقامتك
rb-ball-new-york-traffic = إلغاء الرحلة بين عشية وضحاها
rb-ball-amazon-mosquito-swarm = تم إرسال الأمتعة الأساسية إلى البلد الخطأ
rb-ball-berlin-club-rejected = حجز الفندق مفقود عند تسجيل الوصول
rb-ball-hotel-booking-vanished = الطريق الجبلي مغلق لعدة أيام
# Around the World: -3
rb-ball-spilled-coffee-in-rome = الهاتف متصدع أثناء النقل
rb-ball-sydney-sunburn = الإرهاق الحراري يلغي رحلة ليوم واحد
rb-ball-istanbul-bazaar-scam = يقع حجز الرحلات المدفوعة مسبقًا عبر
rb-ball-moscow-blizzard = عاصفة ثلجية تقطع قطارك
rb-ball-dubai-heatwave = تعطل السيارة المستأجرة
# Around the World: -2
rb-ball-mexico-city-smog = سوء نوعية الهواء يغير مسار الرحلة
rb-ball-cairo-camel-spit = دوار الحركة في رحلة طويلة
rb-ball-athens-ruins-trip = التواء في الكاحل في جولة سيرا على الأقدام
rb-ball-rio-carnival-hangover = نامت وتغيبت عن الجولة الصباحية
rb-ball-bali-belly = اضطراب في المعدة يكلف فترة ما بعد الظهر
# Around the World: -1
rb-ball-swiss-alps-avalanche = ممر ذو مناظر خلابة مغلق من أجل السلامة
rb-ball-amsterdam-bicycle-crash = إطار دراجة مسطح
rb-ball-bangkok-tuk-tuk-breakdown = أكشاك التوك توك في حركة المرور
rb-ball-iceland-volcano-ash = تنبيه جوي يؤخر الرحلة
rb-ball-cape-town-wind = الرياح القوية تغلق وجهة النظر
# Around the World: 0
rb-ball-neutral-passport = ختم جواز سفر جديد
rb-ball-airport-layover = توقف هادئ في المطار
rb-ball-hotel-lobby = الانتظار في بهو الفندق
rb-ball-tourist-map = طي خريطة المدينة
rb-ball-souvenir-magnet = اختيار مغناطيس تذكاري
# Around the World: +1
rb-ball-free-museum-day = دخول مجاني للمتحف
rb-ball-street-food-snack = وجبة خفيفة ممتازة لطعام الشارع
rb-ball-post-card-home = تم إرسال البطاقة البريدية إلى المنزل
rb-ball-friendly-local = توجيهات مفيدة من
rb-ball-sunny-day = محلي الطقس المثالي للاستكشاف
# Around the World: +2
rb-ball-eiffel-tower-view = أفق باريس من برج إيفل
rb-ball-taj-mahal-sunrise = شروق الشمس في تاج محل
rb-ball-great-wall-hike = تنزه على سور الصين العظيم
rb-ball-machu-picchu-climb = الصباح في ماتشو بيتشو
rb-ball-kyoto-cherry-blossoms = أزهار الكرز في كيوتو
# Around the World: +3
rb-ball-colosseum-tour = زيارة إرشادية إلى الكولوسيوم
rb-ball-pyramids-exploration = استكشاف مجمع أهرامات الجيزة
rb-ball-santorini-sunset = غروب الشمس فوق سانتوريني
rb-ball-aurora-borealis = الأضواء الشمالية في سماء المنطقة
rb-ball-safari-lion-sighting = رؤية مسؤولة للحياة البرية في رحلات السفاري
# Around the World: +4
rb-ball-bora-bora-villa = إقامة في البحيرة في بورا بورا
rb-ball-maldives-scuba = الغوص في الشعاب المرجانية في جزر المالديف
rb-ball-niagara-falls-boat = رحلة بالقارب في شلالات نياجرا
rb-ball-grand-canyon-heli = جولة سياحية في جراند كانيون
rb-ball-serengeti-migration = الهجرة الكبرى في سيرينجيتي
# Around the World: +5
rb-ball-first-class-upgrade = مفاجأة ترقية درجة أولى
rb-ball-lottery-in-macau = تم الفوز بتذكرة قطار لمدة عام
rb-ball-private-jet = رحلة الجزيرة مرة واحدة في العمر
rb-ball-royal-palace-invite = زيارة المتحف الخاص بعد ساعات العمل
rb-ball-world-tour-ticket = تذكرة جولة حول العالم
# Journey Through Vietnam: -5
rb-ball-stolen-motorbike = جواز السفر والمحفظة مسروقين أثناء الرحلة
rb-ball-flooded-street-saigon = الفيضانات تفرض عملية نقل طارئة
rb-ball-food-poisoning-bun-mam = الطوارئ الطبية تعطل الرحلة
rb-ball-fake-taxi-scam = تعطل النقل يتسبب في تفويت رحلة
rb-ball-passport-lost-at-airport = فقدان جواز السفر في المطار
# Journey Through Vietnam: -4
rb-ball-typhoon-in-central-vietnam = إخلاء الإعصار بالسواحل الوسطى
rb-ball-lost-wallet-ben-thanh = الأمتعة الأساسية المفقودة أثناء النقل
rb-ball-traffic-jam-hanoi = إلغاء القطار الليلي
rb-ball-pickpocketed-in-bui-vien = سرقة هاتف في منطقة مزدحمة
rb-ball-mountain-road-landslide = إغلاق ممر جبلي بسبب انهيار أرضي
# Journey Through Vietnam: -3
rb-ball-spilled-pho = الكاميرا تضررت بسبب المطر المفاجئ
rb-ball-overcharged-for-coffee = الخلط بين حجز الفنادق
rb-ball-sunburn-in-mui-ne = الإنهاك الحراري في موي ني
rb-ball-missed-train-to-sapa = فاتني القطار المسائي المتجه إلى لاو كاي
rb-ball-loud-karaoke-next-door = ليلة بلا نوم قبل المغادرة المبكرة
# Journey Through Vietnam: -2
rb-ball-broken-flip-flop = حزام الصندل يستقر في جولة سيرا على الأقدام
rb-ball-sudden-downpour = هطول أمطار استوائية مفاجئة
rb-ball-dog-chased-you = موقف حافلات خاطئ بعيد عن الفندق
rb-ball-bitten-by-mosquitoes = مساء لدغات البعوض
rb-ball-out-of-gas = دراجة نارية نفاد الوقود
# Journey Through Vietnam: -1
rb-ball-spicy-chili-bite = فلفل حار شرس بشكل غير متوقع
rb-ball-delayed-flight = تأخير قصير للرحلة الداخلية
rb-ball-wifi-disconnected = إشارة ضعيفة في الجبال
rb-ball-forgot-umbrella = معطف واق من المطر ترك في الفندق
rb-ball-minor-scratch = منعطف خاطئ في الحي القديم
# Journey Through Vietnam: 0
rb-ball-plastic-stool = مقعد على كرسي الرصيف
rb-ball-iced-tea-tra-da = كأس ترا دا
rb-ball-waiting-for-green-light = الانتظار عبر الضوء الأحمر الطويل
rb-ball-bamboo-hat = محاولة على غير لا
rb-ball-motorbike-helmet = ربط خوذة الدراجة النارية
# Journey Through Vietnam: +1
rb-ball-tasty-banh-mi = كريسب بانه مي على الفطور
rb-ball-free-sugar-cane-juice = عصير قصب السكر الطازج
rb-ball-friendly-street-vendor = ترحيب حار من بائع في السوق
rb-ball-cool-breeze = نسيم بارد بعد المطر
rb-ball-found-10k-vnd = رحلة حافلة محلية رخيصة
# Journey Through Vietnam: +2
rb-ball-delicious-pho-bowl = وعاء معطر من فو
rb-ball-egg-coffee-in-hanoi = قهوة البيض في هانوي
rb-ball-boat-ride-in-ninh-binh = رحلة سامبان عبر مجمع ترانج آن للمناظر الطبيعية
rb-ball-lantern-festival-hoian = أمسية مضاءة بالفوانيس في مدينة هوي آن القديمة
rb-ball-motorbike-road-trip = ركوب قارب البستان في دلتا نهر ميكونغ
# Journey Through Vietnam: +3
rb-ball-ha-long-bay-cruise = رحلة بحرية عبر خليج ها لونج - أرخبيل كات با
rb-ball-golden-bridge-bana-hills = الجسر الذهبي فوق با نا هيلز
rb-ball-phu-quoc-sunset = غروب الشمس في فو كووك
rb-ball-sapa-terraced-fields = الحقول المدرجات حول سا با
rb-ball-phong-nha-cave-exploration = رحلة الكهف في فونج نها - كي بانج
# Journey Through Vietnam: +4
rb-ball-tet-holiday-lucky-money = لم شمل تيت والمال المحظوظ
rb-ball-vip-ticket-to-concert = شروق الشمس على حلقة ها جيانج
rb-ball-luxury-resort-stay = زيارة الحفاظ على المجتمع في كون داو
rb-ball-business-class-flight = رصيف ذو مناظر خلابة على قطار Reunification Express
rb-ball-won-lottery-vietlott = ليلة المهرجان بين آثار هوى
# Journey Through Vietnam: +5
rb-ball-billionaire-inheritance = رحلة سون دونغ
rb-ball-found-gold-treasure = ورشة ثقافية خاصة مع كبار الحرفيين
rb-ball-free-house-in-district-1 = رحلة بالسكك الحديدية لمدة شهر عبر فيتنام
rb-ball-national-hero-award = ضيف شرف في مهرجان القرية
rb-ball-ultimate-happiness = رحلة الأحلام من Ha Giang إلى Ca Mau
