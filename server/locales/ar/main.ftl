auth-username-password-required = اسم المستخدم وكلمة المرور مطلوبان.
auth-registration-success = تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول ببياناتك.
auth-username-taken = اسم المستخدم مستخدَم بالفعل. يرجى اختيار اسم مستخدم آخر.
auth-username-reserved = هذا الاسم محجوز لدى PlayAural. يرجى اختيار اسم مستخدم آخر.
auth-registration-error = فشل إنشاء الحساب بسبب خطأ في الخادم. يرجى المحاولة مرة أخرى.
auth-error-wrong-password = كلمة المرور غير صحيحة.
auth-error-user-not-found = المستخدم غير موجود.
username-ambiguous = أكثر من حساب قديم يطابق "{ $username }". أدخل التهجئة المسجّلة بالضبط.
auth-kicked-logged-in-elsewhere = تم قطع اتصالك لأنه تم تسجيل الدخول إلى حسابك من جهاز آخر.

chat-global = { $player } يقول في الدردشة العامة: { $message }

admin-smtp-updated-success = تم تحديث إعداد SMTP بنجاح
admin-smtp-settings = إعدادات SMTP
email-reset-subject = رمز إعادة تعيين كلمة مرور PlayAural
email-reset-body = مرحباً { $username },\n\nلقد طلبت إعادة تعيين كلمة المرور لحسابك في PlayAural.\nرمز إعادة التعيين المكوّن من 6 أرقام هو: { $code }\n\nستنتهي صلاحية هذا الرمز خلال 15 دقيقة.\nإذا لم تطلب ذلك، يرجى تجاهل هذا البريد الإلكتروني.
email-reset-body-html = <p>مرحباً { $username },</p>
    <p>لقد تلقينا طلباً لإعادة تعيين كلمة المرور لحسابك في PlayAural.</p>
    <p>رمز الاسترداد المكوّن من 6 أرقام هو:</p>
    <h2>{ $code }</h2>
    <p>ستنتهي صلاحية هذا الرمز خلال 15 دقيقة بالضبط.</p>
    <p>إذا لم تطلب ذلك، يرجى تجاهل هذا البريد الإلكتروني. يبقى حسابك آمناً.</p>
    <p>مع أطيب التحيات,<br>Trung</p>
email-test-subject = اختبار SMTP لـ PlayAural
email-test-body = هذا بريد إلكتروني تجريبي من خادم PlayAural للتحقق من إعدادات SMTP الخاصة بك.
email-test-body-html = <p>مرحباً،</p>
    <p>هذا بريد إلكتروني تجريبي من خادم PlayAural.</p>
    <p>إذا كنت تقرأ هذا، فإن إعدادات SMTP الخاصة بك ترسل رسائل HTML بنجاح.</p>
smtp-test-sending = جارٍ اختبار الاتصال، يرجى الانتظار...
smtp-test-success = تم إرسال البريد التجريبي بنجاح إلى { $email }!
smtp-test-failed = فشل إرسال البريد التجريبي: { $error }
smtp-host = المضيف: { $value }
smtp-port = المنفذ: { $value }
smtp-username = اسم المستخدم: { $value }
smtp-password = كلمة المرور: { $value }
smtp-from-email = البريد المُرسِل: { $value }
smtp-from-name = اسم المُرسِل: { $value }
smtp-encryption = التشفير: { $value }
smtp-test-connection = اختبار الاتصال
smtp-not-set = غير محدّد
smtp-prompt-host = أدخل مضيف SMTP (مثال: smtp.gmail.com):
smtp-prompt-port = أدخل منفذ SMTP (مثال: 587 أو 465):
smtp-prompt-username = أدخل اسم مستخدم SMTP:
smtp-prompt-password = أدخل كلمة مرور SMTP:
smtp-prompt-from-email = أدخل عنوان البريد المُرسِل:
smtp-prompt-from-name = أدخل اسم المُرسِل (مثال: دعم PlayAural):
smtp-prompt-test-email = أدخل عنوان البريد الإلكتروني المستهدف للاختبار:
smtp-enc-none = بدون تشفير
smtp-enc-ssl = استخدام SSL
smtp-enc-tls = تفعيل تشفير TLS تلقائياً (STARTTLS)
smtp-current-enc = * { $value }

play = لعب
view-active-tables = عرض الطاولات النشطة
options = الخيارات
logout = تسجيل الخروج
back = رجوع
go-back = الرجوع
context-menu = قائمة السياق.
no-actions-available = لا توجد إجراءات متاحة.
table-new-host-promoted = { $player } أصبح الآن مضيف الطاولة.
table-new-host-promoted-you = أصبحت الآن مضيف الطاولة.
return-to-table = العودة إلى الطاولة
create-table = إنشاء طاولة جديدة
leave-table = مغادرة الطاولة
start-game = بدء اللعبة
add-bot = إضافة بوت
remove-bot = إزالة بوت
actions-menu = قائمة الإجراءات
save-table = حفظ الطاولة
whose-turn = دور من الآن
whos-at-table = من على الطاولة
check-scores = عرض النتائج
check-scores-detailed = النتائج التفصيلية

game-player-skipped = تم تخطّي { $player }.
game-player-skipped-you = تم تخطّي دورك.

table-created = أنشأ { $host } طاولة { $game } جديدة.
table-created-broadcast = أنشأ { $host } طاولة { $game } جديدة.
table-joined = انضم { $player } إلى الطاولة.
table-joined-you = انضممت إلى الطاولة.
table-left = غادر { $player } الطاولة.
new-host = { $player } أصبح الآن المضيف.
new-host-you = أصبحت الآن المضيف.
waiting-for-players = في انتظار اللاعبين. {$min} كحدّ أدنى، { $max } كحدّ أقصى.
game-starting = اللعبة تبدأ!
table-listing-game-composition-status = { $game } [{ $status }]: طاولة { $host }. { $composition }.
table-composition-human-players = { $count } { $count ->
    [one] لاعب
   *[other] لاعبين
}: { $names }
table-composition-bots = { $count } { $count ->
    [one] بوت
   *[other] بوتات
}
table-composition-spectators = { $count ->
    [one] متفرّج
   *[other] متفرّجون
}: { $names }
table-composition-spectators-more = المتفرّجون: { $names }؛ بالإضافة إلى { $remaining } آخرين
table-composition-spectator-host = { $host } (المضيف)
table-composition-two = { $first }؛ { $second }
table-composition-three = { $first }؛ { $second }؛ { $third }
table-composition-empty = لا مشاركين
table-status-waiting = في الانتظار
table-status-playing = قيد اللعب
table-status-finished = انتهت
table-not-exists = لم تعد الطاولة موجودة.
table-full = الطاولة ممتلئة.
table-closed-disconnect-timeout = أُغلقت الطاولة لأنه لم يعد أي لاعب نشط خلال { $minutes } دقيقة.
player-replaced-by-bot = { $bot } يلعب الآن نيابةً عن { $player }.
player-reclaimed-from-bot = عاد { $player } واستعاد المقعد { GENDER_TERM($player_gender, "possessive-determiner") } من { $bot }.
player-reclaimed-from-bot-you = عدت واستعدت مقعدك من { $bot }.
spectator-joined = انضممتَ إلى طاولة { $host } كمتفرّج.

spectate = المشاهدة
now-playing = { $player } يلعب الآن.
now-playing-you = أنت تلعب الآن.
now-spectating = { $player } يشاهد الآن.
now-spectating-you = أنت تشاهد الآن.
spectator-left = توقف { $player } عن المشاهدة.

welcome = مرحباً بك في PlayAural!
goodbye = إلى اللقاء!

user-online = { $player } أصبح متصلاً.
user-offline = { $player } أصبح غير متصل.
friend-online = صديقك { $player } أصبح الآن متصلاً.
friend-offline = صديقك { $player } أصبح غير متصل.
permission-denied = ليس لديك إذن لتنفيذ هذا الإجراء على مطوّر.
kick-user = طرد مستخدم
kick-broadcast = تم طرد { $target } بواسطة { $actor }.
kick-broadcast-actor = طردت { $target }.
user-not-online = المستخدم { $target } غير متصل.
kick-confirm = هل أنت متأكد أنك تريد طرد { $player }؟
no-users-to-kick = لا يوجد مستخدمون متاحون للطرد.
usage-kick = الاستخدام: /kick <username>
online-users-none = لا يوجد مستخدمون متصلون.
online-users-summary = { $count ->
    [one] { $count } مستخدم متصل. { $groups }
   *[other] { $count } مستخدمون متصلون. { $groups }
}
online-users-group = { $role ->
    [dev] { $count ->
        [one] { $count } مطوّر: { $users }.
       *[other] { $count } مطوّرون: { $users }.
    }
    [admin] { $count ->
        [one] { $count } مسؤول: { $users }.
       *[other] { $count } مسؤولون: { $users }.
    }
   *[user] { $staff_count ->
        [0] { $users }.
       *[other] { $count ->
            [one] { $count } مستخدم: { $users }.
           *[other] { $count } مستخدمون: { $users }.
        }
    }
}
online-users-more = { $count } آخرون
online-user-waiting-approval = في انتظار الموافقة
presence-status-main-menu = القائمة الرئيسية
presence-status-waiting-table = في انتظار على طاولة { $game }
presence-status-playing = يلعب { $game }
presence-status-spectating = يشاهد { $game }
presence-status-watching-table = يراقب طاولة { $game }
presence-status-reviewing-results = يراجع نتائج { $game }
presence-status-spectating-results = يشاهد نتائج { $game }
user-role-dev = مطوّر
user-role-admin = مسؤول
user-role-user = مستخدم
client-type-web = ويب
client-type-python = سطح المكتب
client-type-mobile = الجوال
client-type-with-platform = { $client } ({ $platform })
online-user-full-entry = { $username } ({ $role }، { $client }، { $language }): { $status }
user-not-online-anymore = لم يعد هذا المستخدم متصلاً.
close-menu = إغلاق

language = اللغة
language-option = اللغة: { $language }
language-changed = تم تعيين اللغة إلى { $language }.
language-menu-entry =
    { $official ->
        [true] { $language }. لغة PlayAural رسمية. المترجمون: { $translators }.
       *[false] { $language }. ترجمة مجتمعية. المترجمون: { $translators }.
    }
language-menu-entry-missing-metadata = { $language }. بيانات المترجم غير متوفرة.
language-menu-current-entry = الحالية: { $entry }

option-on = تشغيل
option-off = إيقاف

# Multi-select option sub-menu controls
option-back = رجوع
option-select-all = تحديد الكل
option-deselect-all = إلغاء تحديد الكل
option-selected-count = { $count } محدَّد
option-deselected-count = { $count } غير محدَّد
option-multiselect-group = { $group } (تم تحديد { $count } من { $total })
option-min-selected = يجب أن تحدّد { $count } على الأقل.
option-max-selected = يمكنك تحديد { $count } على الأكثر.

custom-bot-names-option = أسماء بوت مخصّصة: { $status }
option-notify-table-created = التنبيه عند إنشاء طاولة: { $status }
option-notify-user-presence = تنبيهات اتصال/انقطاع المستخدمين: { $status }
option-notify-friend-presence = تنبيهات اتصال/انقطاع الأصدقاء: { $status }
dice-keeping-style-option = نمط الاحتفاظ بالنرد: { $style }
dice-keeping-style-changed = تم تعيين نمط الاحتفاظ بالنرد إلى { $style }.
dice-keeping-style-indexes = مواضع النرد
dice-keeping-style-values = قيم النرد

# Personal options split: general vs game options
general-options = الخيارات العامة
game-options = خيارات اللعبة

# Game Options (declarative preferences with per-game overrides)
pref-category-display = العرض
pref-set-brief-announcements = الإعلانات الموجزة: { $status }
pref-changed-brief-announcements = الإعلانات الموجزة { $status }.
pref-desc-brief-announcements = تقصير إعلانات الحركات والأحداث داخل اللعبة؛ أوقِفها للحصول على تعليق منطوق أكمل.
pref-category-sounds = الأصوات
pref-category-gameplay = طريقة اللعب
pref-category-dice = النرد
pref-default = الافتراضي
pref-per-game-for = { $game }: { $value }
pref-reset-all = إعادة تعيين جميع خيارات اللعبة
pref-reset-category = إعادة تعيين خيارات { $category }
pref-reset-done = تمت إعادة تعيين خيارات اللعبة.
pref-set-play-turn-sound = صوت الدور: { $status }
pref-set-confirm-destructive-actions = تأكيد الإجراءات الخطرة: { $status }
pref-set-allow-custom-bot-names = أسماء بوت مخصّصة: { $status }
pref-set-clear-kept-on-roll = مسح النرد المحتفظ به عند الرمي: { $status }
pref-set-dice-keeping-style = نمط الاحتفاظ بالنرد: { $choice }
pref-changed-play-turn-sound = صوت الدور { $status }.
pref-changed-confirm-destructive-actions = تأكيد الإجراءات الخطرة { $status }.
pref-changed-allow-custom-bot-names = أسماء بوت مخصّصة { $status }.
pref-changed-clear-kept-on-roll = مسح النرد المحتفظ به عند الرمي { $status }.
pref-changed-dice-keeping-style = تم تعيين نمط الاحتفاظ بالنرد إلى { $choice }.
pref-desc-play-turn-sound = تشغيل صوت عندما يحين دورك.
pref-desc-confirm-destructive-actions = طلب التأكيد قبل الإجراءات الخطرة أو التي لا يمكن التراجع عنها، مثل التمرير في Pusoy Dos.
pref-desc-allow-custom-bot-names = يتيح لك تعيين أسماء مخصّصة للبوتات التي تضيفها إلى طاولة.
pref-desc-clear-kept-on-roll = في ألعاب النرد المدعومة مثل Yahtzee، حرّر كل نردة محتفظ بها بعد كل رمية. ستعيد رميتك التالية رمي جميع النرد ما لم تحتفظ ببعضها مجدداً؛ مع قيم النرد، استخدم Shift+1-6 للاحتفاظ بالنرد المطابق.
pref-desc-dice-keeping-style = مواضع النرد: استخدم 1-5، أو 1-6 في Midnight، لتبديل النرد حسب الموضع. قيم النرد: استخدم 1-6 لتحرير نردة محتفظ بها بتلك القيمة وShift+1-6 للاحتفاظ بنردة محرَّرة مطابقة. خلال مرحلة التبادل في Tradeoff، تحتفظ 1-6 بنردة مطابقة وتعلّم Shift+1-6 نردة للتبادل؛ خلال مرحلة الأخذ، تأخذ 1-6 العادية نردة مطابقة من المجموعة.

cancel = إلغاء
enter-bot-name = أدخل اسم البوت
bot-name-invalid-length = يجب أن تتراوح أسماء البوتات بين 3 و30 حرفاً.
bot-name-invalid-characters = يمكن أن تحتوي أسماء البوتات على حروف وأرقام ومسافات فقط.
table-name-already-used = يوجد بالفعل لاعب أو بوت بهذا الاسم على هذه الطاولة.
no-options-available = لا توجد خيارات متاحة.
no-scores-available = لا توجد نتائج متاحة.

option-desc-generic = { $label }. الافتراضي: { $default }.
option-desc-integer = { $label }. أدخل عدداً صحيحاً من { $min } إلى { $max }. الافتراضي: { $default }.
option-desc-number = { $label }. أدخل رقماً من { $min } إلى { $max }. الافتراضي: { $default }.
option-desc-menu = { $label }. اختر واحداً من: { $choices }. الافتراضي: { $default }.
option-desc-bool = { $label }. فعّل هذا العنصر لتشغيل الإعداد أو إيقافه. الافتراضي: { $default }.
option-desc-multiselect = { $label }. المحدَّد الآن: { $selected }. الحد الأدنى للتحديدات: { $min }. الحد الأقصى للتحديدات: { $max }. المحدَّد افتراضياً: { $default }.
option-desc-no-choices = لا توجد خيارات متاحة حالياً
option-desc-none-selected = لا شيء
option-desc-no-maximum = بلا حد أقصى
menu-item-with-hint = { $label }: { $hint }

general-desc-profile = عرض وتعديل تفاصيل ملفك الشخصي العام.
general-desc-friends = إدارة الأصدقاء وطلبات الصداقة والرسائل الخاصة وإجراءات طاولة الأصدقاء.
general-desc-my-stats = مراجعة انتصاراتك وخساراتك وتقييماتك وإحصائيات الألعاب المدعومة.
general-desc-general-options = ضبط اللغة والدردشة العامة والصوت وإمكانية الوصول والتنبيهات وتفضيلات اللعب.
general-desc-game-options = ضبط تفضيلات اللعب التي يمكن تطبيقها بشكل عام أو على الألعاب المدعومة.
general-desc-language = اختر اللغة المستخدمة في قوائم الخادم ورسائله ووثائقه عند توفرها.
general-desc-audio = ضبط الموسيقى والمؤثرات الصوتية والأصوات المحيطة وحجم الدردشة الصوتية وأصوات الكتابة وإعدادات جهاز الإدخال في سطح المكتب.
general-desc-accessibility = ضبط سلوك القراءة والإدخال والعميل المتعلق بإمكانية الوصول المتاح على هذا الجهاز.
general-desc-notifications = اختر تنبيهات الدردشة والحضور وإنشاء الطاولات التي تريد سماعها.
general-desc-music-volume = تغيير حجم الموسيقى الخلفية. تعيينه إلى إيقاف يُسكت الموسيقى.
general-desc-sound-volume = تغيير حجم المؤثرات الصوتية للعبة. تبقى المؤثرات الصوتية عند عشرة بالمئة على الأقل حتى تظل الإشارات المهمة مسموعة.
general-desc-ambience-volume = تغيير حجم الأصوات المحيطة الخلفية. تعيينه إلى إيقاف يُسكت الأصوات المحيطة.
general-desc-voice-volume = تغيير حجم تشغيل الدردشة الصوتية للطاولة.
general-desc-audio-input-device = اختر الميكروفون أو جهاز الإدخال الذي يستخدمه عميل سطح المكتب للدردشة الصوتية.
general-desc-play-typing-sounds = تشغيل أصوات كتابة صغيرة أثناء إدخال النص في حقول التحرير بالعميل.
general-desc-web-speech-settings = تهيئة إخراج الكلام في المتصفح، بما في ذلك وضع ARIA live أو Web Speech وسرعة الكلام والصوت.
general-desc-mobile-speech-settings = تهيئة محرك تحويل النص إلى كلام في الجوال والصوت وسرعة الكلام.
general-desc-invert-multiline-enter = تبديل سلوك الإرسال والسطر الجديد لحقول النص متعددة الأسطر في عميل سطح المكتب.
general-desc-menu-hints = عرض الأوصاف المتاحة مباشرةً في صفوف القائمة. عند الإيقاف، ركّز على عنصر موصوف واضغط F1 في سطح المكتب أو الويب بلوحة مفاتيح فعلية، أو انقر مرة واحدة بثلاثة أصابع في وضع النطق الذاتي بالجوال، لسماعه.
general-desc-mute-global-chat = إيقاف نطق رسائل الدردشة العامة تلقائياً.
general-desc-global-chat-channel = اختر قناة اللغة المستخدمة لإرسال واستقبال الدردشة العامة. القناة مطلوبة حتى عند تفعيل الدردشة العامة.
general-desc-mute-table-chat = إيقاف نطق رسائل دردشة الطاولة تلقائياً.
general-desc-notify-user-presence = الإعلان عند اتصال المستخدمين أو انقطاعهم.
general-desc-notify-friend-presence = الإعلان عند اتصال أصدقائك أو انقطاعهم.
general-desc-notify-table-created = الإعلان عند إنشاء طاولة عامة جديدة.
general-desc-speech-mode = اختر ما إذا كان عميل الويب يرسل الإعلانات إلى قارئ الشاشة عبر ARIA live أو ينطقها باستخدام Web Speech API في المتصفح.
general-desc-speech-rate = تغيير سرعة الكلام في عميل الويب.
general-desc-speech-voice = اختر الصوت المستخدم في Web Speech API بعميل الويب، أو العودة إلى الافتراضي للمتصفح.
general-desc-mobile-tts-engine = اختر محرك تحويل النص إلى كلام في الجوال. يستخدم Android حالياً المحرك المُدار بواسطة النظام.
general-desc-mobile-tts-voice = اختر صوت تحويل النص إلى كلام في الجوال، أو العودة إلى الافتراضي للنظام.
general-desc-mobile-tts-rate = تغيير سرعة تحويل النص إلى كلام في الجوال.

saved-tables = الطاولات المحفوظة
no-saved-tables = ليس لديك طاولات محفوظة.
no-active-tables = لا توجد طاولات نشطة.
no-active-tables-all = لا توجد طاولات نشطة متاحة.
no-active-tables-waiting = لا توجد طاولات في الانتظار متاحة.
no-active-tables-playing = لا توجد طاولات قيد اللعب متاحة.
active-tables-filter = التصفية: { $filter }
filter-name-all = الكل
filter-name-waiting = في الانتظار
filter-name-playing = قيد اللعب
game-category-filter = الفئة: { $category }
game-category-filter-option = { $category } ({ $count })
game-category-all = الكل
game-category-cards = ألعاب الورق
game-category-poker = ألعاب البوكر
game-category-dice = ألعاب النرد
game-category-board = ألعاب الطاولة
game-category-arcade = ألعاب الأركيد
game-category-misc = متنوعة
no-games-in-category = لا توجد ألعاب متاحة في هذه الفئة.
restore-table = استعادة
delete-saved-table = حذف
saved-table-deleted = تم حذف الطاولة المحفوظة.
missing-players = تعذّرت الاستعادة: هؤلاء اللاعبون غير متاحين: { $players }
saved-table-blocked-by-you = تتضمن هذه الطاولة المحفوظة مستخدمين قمت بحظرهم: { $players }. لاستعادتها، افتح "الشخصي والخيارات"، ثم "الأصدقاء"، ثم "المستخدمون المحظورون" وألغِ حظرهم. لا يمكن متابعة الاستعادة إلا إذا أصبح التواصل الاجتماعي المباشر متاحاً للجميع عندئذٍ. تم الاحتفاظ بالحفظ.
saved-table-social-blocked = لا يمكن استعادة هذه الطاولة المحفوظة لأن التواصل الاجتماعي المباشر غير متاح بينك وبين: { $players }. تم الاحتفاظ بالحفظ.
saved-table-social-blocked-mixed = تتضمن هذه الطاولة المحفوظة مستخدمين قمت بحظرهم: { $blocked }. افتح "الشخصي والخيارات"، ثم "الأصدقاء"، ثم "المستخدمون المحظورون" وألغِ حظرهم. التواصل الاجتماعي المباشر غير متاح أيضاً مع: { $unavailable }. تم الاحتفاظ بالحفظ.
saved-table-invalid = لم يعد من الممكن استعادة هذه الطاولة المحفوظة لأن بيانات اللعبة أو اللاعبين المخزّنة غير مكتملة أو غير متوافقة. تم الاحتفاظ بالحفظ.
table-restored = تمت استعادة الطاولة! تم نقل جميع اللاعبين.
table-saved-destroying = تم حفظ الطاولة! العودة إلى القائمة الرئيسية.
game-type-not-found = لم يعد نوع اللعبة موجوداً.

action-not-your-turn = ليس دورك الآن.
action-not-playing = لم تبدأ اللعبة بعد.
action-spectator = لا يمكن للمتفرّجين فعل ذلك.
action-not-host = المضيف وحده من يمكنه فعل ذلك.
action-not-available = هذا الإجراء غير متاح الآن.
action-game-in-progress = لا يمكن فعل ذلك أثناء سير اللعبة.
action-need-more-players = يلزم المزيد من اللاعبين للبدء.
action-table-full = الطاولة ممتلئة.
action-start-needs-more-players = تعذّر البدء. اللاعبون النشطون: { $current }. الحد الأدنى المطلوب: { $minimum }.
action-start-has-too-many-players = تعذّر البدء. اللاعبون النشطون: { $current }. الحد الأقصى المسموح: { $maximum }.
action-start-requires-exact-players = تعذّر البدء. اللاعبون النشطون: { $current }. المطلوب: { $required } بالضبط.
action-start-needs-human-player = لا يمكن البدء بالبوتات فقط. يجب أن يشارك إنسان واحد على الأقل كلاعب. انتقل من متفرّج إلى لاعب؛ وإذا كانت الطاولة ممتلئة، فأزِل بوتاً أولاً.
action-no-bots = لا توجد بوتات لإزالتها.
action-bots-cannot = لا يمكن للبوتات فعل ذلك.
action-role-change-rate-limited = أنت تبدّل بين اللعب والمشاهدة بسرعة كبيرة. حاول مرة أخرى بعد { $seconds ->
    [one] ثانية واحدة
   *[other] { $seconds } ثانية
}.
options-category-audio = الصوت
options-category-accessibility = إمكانية الوصول
options-category-notifications = التنبيهات
music-volume-option = حجم الموسيقى: { $value }%
sound-volume-option = حجم المؤثرات الصوتية: { $value }%
ambience-volume-option = حجم الأصوات المحيطة: { $value }%
voice-volume-option = حجم الدردشة الصوتية: { $value }%
volume-choice-off = إيقاف
volume-choice-percent = { $value }%
volume-choice-current = { $label } (الحالي)
audio-input-device-option = جهاز إدخال الصوت: { $device }
audio-input-device-default = جهاز الإدخال الافتراضي للنظام

mute-global-chat-option = كتم الدردشة العامة: { $status }
global-chat-channel-option = لغة الدردشة العامة: { $channel }
global-chat-channel-none = لم يتم تحديد قناة
global-chat-channel-none-current = لم يتم تحديد قناة (الحالي)
global-chat-channel-name = { $language }
global-chat-channel-recommended = { $language } (موصى به للغة واجهتك)
global-chat-channel-current = { $language } (الحالي)
global-chat-channel-current-recommended = { $language } (الحالي، موصى به للغة واجهتك)
global-chat-channel-selected = تم تعيين لغة الدردشة العامة إلى { $language }. لا تتم مراقبة الدردشة العامة في الوقت الفعلي. إذا استخدم أحدهم ألفاظاً نابية أو أهانك، فاحظره. يرجى الإبلاغ عن الإساءات الجسيمة أو المتكررة للمراجعة لاحقاً.
global-chat-channel-cleared = لم يتم تحديد لغة للدردشة العامة. لن ترسل أو تستقبل رسائل عامة.
mute-table-chat-option = كتم دردشة الطاولة: { $status }
invert-multiline-enter-option = عكس سلوك مفتاح Enter: { $status }
menu-hints-option = تلميحات القائمة: { $status }
menu-hints-changed = تلميحات القائمة الآن { $status }.
play-typing-sounds-option = تشغيل أصوات الكتابة: { $status }
invalid-volume = حجم غير صالح.

dice-not-rolled = لم ترمِ النرد بعد.
dice-no-dice = لا يوجد نرد متاح.
table-no-players = لا يوجد لاعبون.
table-players-one = { $count } لاعب: { $players }.
table-players-many = { $count } لاعبين: { $players }.
table-spectators = المتفرّجون: { $spectators }.
table-host-suffix = (المضيف)
table-voice-chat-suffix = (في الدردشة الصوتية)
table-members-summary-compact = ملخص الطاولة: { $composition }.
table-summary-human-players = { $count } { $count ->
    [one] لاعب بشري
   *[other] لاعبين بشريين
}
table-summary-bots = { $count } { $count ->
    [one] بوت
   *[other] بوتات
}
table-summary-spectators = { $count } { $count ->
    [one] متفرّج
   *[other] متفرّجين
}
table-members-empty = لا يوجد أعضاء طاولة مدرجون حالياً. استخدم "رجوع" للعودة وتحديث عرض الطاولة.
table-member-entry = { $player }: { $status }
table-member-status-host = المضيف
table-member-status-player = لاعب
table-member-status-spectator = متفرّج
table-member-status-bot = بوت
table-member-status-online = متصل
table-member-status-offline = غير متصل
table-member-status-voice-chat = في الدردشة الصوتية
table-member-status-bot-takeover = بوت يلعب في المقعد { GENDER_TERM($member_gender, "possessive-determiner") }: { $bot }
table-member-no-actions = لا توجد إجراءات متاحة لـ { $player }.
table-member-left = لم يعد هذا الشخص على هذه الطاولة.
table-member-bot-left = لم يعد هذا البوت على هذه الطاولة.
game-over = انتهت اللعبة
game-final-scores = النتائج النهائية
game-points = { $count } { $count ->
    [one] نقطة
   *[other] نقاط
}

leaderboards = لوحات الصدارة
leaderboard-no-data = لا توجد بيانات لوحة صدارة لهذه اللعبة بعد.

leaderboard-type-wins = متصدّرو الانتصارات
leaderboard-type-rating = تقييم المهارة
leaderboard-type-total-score = إجمالي النتيجة
leaderboard-type-high-score = أعلى نتيجة
leaderboard-type-games-played = الألعاب الملعوبة
leaderboard-type-avg-points-per-turn = متوسط النقاط لكل دور
leaderboard-type-best-single-turn = أفضل دور منفرد
leaderboard-type-score-per-round = النتيجة لكل جولة
leaderboard-type-most-enemies-defeated = أكثر الأعداء المهزومين
leaderboard-type-deepest-wave-reached = أعمق موجة تم بلوغها


leaderboard-wins-entry = { $rank }: { $player }، { $wins } { $wins ->
    [one] انتصار
   *[other] انتصارات
} { $losses } { $losses ->
    [one] خسارة
   *[other] خسائر
}، { $percentage }% نسبة الفوز
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value } لعبة
leaderboard-avg-entry = { $rank }. { $player }: { $value }
leaderboard-no-player-stats = لم تلعب هذه اللعبة بعد.

leaderboard-no-ratings = لا توجد بيانات تقييم لهذه اللعبة بعد.
leaderboard-rating-entry = { $rank }. { $player }: تقييم { $rating }
leaderboard-no-player-rating = ليس لديك تقييم لهذه اللعبة بعد.

my-stats = إحصائياتي
my-stats-select-game = اختر لعبة لعرض إحصائياتك
my-stats-no-data = لم تلعب هذه اللعبة بعد.
my-stats-no-games = لم تلعب أي ألعاب بعد.
my-stats-header = { $game } - إحصائياتك
my-stats-wins = الانتصارات: { $value }
my-stats-losses = الخسائر: { $value }
my-stats-winrate = نسبة الفوز: { $value }%
my-stats-games-played = الألعاب الملعوبة: { $value }
my-stats-total-score = إجمالي النتيجة: { $value }
my-stats-high-score = أعلى نتيجة: { $value }
my-stats-rating = تقييم المهارة: { $value }
my-stats-no-rating = لا يوجد تقييم مهارة بعد
my-stats-custom = { $name }: { $value }
my-stats-avg-per-turn = متوسط النقاط لكل دور: { $value }
my-stats-best-turn = أفضل دور منفرد: { $value }
my-stats-score-per-round = النتيجة لكل جولة: { $value }
my-stats-most-enemies-defeated = أكثر الأعداء المهزومين: { $value }
my-stats-deepest-wave-reached = أعمق موجة تم بلوغها: { $value }

confirm-leave-game = هل أنت متأكد أنك تريد مغادرة الطاولة؟
confirm-yes = نعم
confirm-no = لا

administration = الإدارة

admin-moderation = إشراف الدردشة
admin-moderation-global-chat-toggle = الدردشة العامة: { $status }
admin-moderation-global-chat-toggle-description = تشغيل أو إيقاف إرسال الرسائل لكل قناة لغة عامة. يبقى هذا الإعداد بعد إعادة تشغيل الخادم.
admin-moderation-global-chat-status-description = الحالة الحالية على مستوى الخادم. يمكن للمطوّر وحده تغيير هذا الإعداد.
admin-moderation-global-chat-update-failed = تعذّر حفظ إعداد الدردشة العامة، لذا لم يتم إجراء أي تغيير. يرجى المحاولة مرة أخرى.
global-chat-availability-enabled = تم تفعيل الدردشة العامة بواسطة المطوّر. حدّد قناة لغة قبل إرسال أو استقبال الرسائل العامة.
global-chat-availability-disabled = تم تعطيل الدردشة العامة مؤقتاً بواسطة المطوّر.
admin-moderation-section-reports = البلاغات
admin-moderation-open-reports = البلاغات المفتوحة: { $count }
admin-moderation-closed-reports = البلاغات المغلقة: { $count }
admin-moderation-all-reports = جميع البلاغات المحتفظ بها: { $count }
admin-moderation-section-messages = سجل الرسائل العامة
admin-moderation-browse-messages = تصفّح وفلترة جميع الرسائل العامة
admin-moderation-find-history = البحث في سجل الدردشة العامة باسم مستخدم مطابق تماماً
admin-moderation-retained-summary = الأدلة المحتفظ بها: { $messages } رسالة عامة و{ $closed } بلاغاً مغلقاً.
admin-moderation-section-retention = الحذف الدائم
admin-moderation-clear-history = مسح جميع رسائل الدردشة العامة المحتفظ بها ({ $count })
admin-moderation-clear-closed-reports = مسح جميع البلاغات المغلقة ({ $count })
admin-moderation-open-report-list = البلاغات المفتوحة، الأحدث أولاً
admin-moderation-closed-report-list = البلاغات المغلقة، الأحدث أولاً
admin-moderation-all-report-list = جميع البلاغات المحتفظ بها، الأحدث أولاً
admin-moderation-report-row = بلاغ رقم { $id }، مُقدَّم { $time }. المستخدم المُبلَّغ عنه: { $target }، المعرّف { $target_id }. السبب: { $reason }. المُبلِّغ: { $reporter }. الحالة: { $status }.
admin-moderation-no-reports = لا توجد بلاغات تطابق هذا العرض.
admin-moderation-value-unknown = غير معروف
admin-moderation-status-open = مفتوح
admin-moderation-status-reviewed = تمت المراجعة
admin-moderation-status-dismissed = مرفوض
admin-moderation-status-actioned = تم تسجيل إجراء
admin-moderation-status-unknown = غير معروف
admin-moderation-report-unavailable = لم يعد هذا البلاغ موجوداً. ربما قام مطوّر آخر بمسحه.
admin-moderation-report-id = معرّف البلاغ: { $id }
admin-moderation-report-time = وقت التقديم: { $time }
admin-moderation-report-status = الحالة: { $status }
admin-moderation-report-origin = المصدر: { $origin }
admin-moderation-origin-manual = مُقدَّم من مستخدم
admin-moderation-origin-automatic = مُنشأ تلقائياً بواسطة النظام
admin-moderation-report-reporter = المُبلِّغ: { $username }. معرّف الحساب: { $uuid }
admin-moderation-report-target = المستخدم المُبلَّغ عنه: { $username }. معرّف الحساب: { $uuid }
admin-moderation-report-reason = السبب: { $reason }
admin-moderation-report-channel = قناة سياق الدردشة العامة: { $channel }
admin-moderation-report-scope = تم الاكتشاف في: { $scope }
admin-moderation-scope-global = الدردشة العامة
admin-moderation-scope-table = دردشة الطاولة
admin-moderation-detection-rate-limited = رسائل أُرسلت بسرعة كبيرة
admin-moderation-detection-repeated-message = رسائل متطابقة متكررة
admin-moderation-automatic-evidence = مُنشأ تلقائياً بواسطة النظام للمراجعة اليدوية فقط؛ لم يتم تطبيق أي عقوبة. في { $scope }، لاحظ الكاشف { $incidents } حادثة إزعاج منفصلة ورفض { $rejected } محاولة خلال نافذة مراقبة مدتها { $window }. تم قبول { $accepted } رسالة حديثة. الاكتشاف: { $detection }. آخر رسالة مرفوضة: { $sample }
admin-moderation-automatic-evidence-unavailable = أُنشئ هذا البلاغ تلقائياً بواسطة النظام للمراجعة اليدوية فقط، ولم يتم تطبيق أي عقوبة. أدلة الاكتشاف المنظّمة الخاصة به غير متوفرة أو من إصدار غير مدعوم.
admin-moderation-report-anchor = معرّف رسالة ربط السياق المحفوظة: { $id }
admin-moderation-report-anchor-unavailable = لا تتوفر رسالة ربط سياق محفوظة. قد لا يكون الحساب المُبلَّغ عنه قد أرسل رسالة محتفظاً بها في هذه القناة، أو ربما تم مسح سجل الدردشة.
admin-moderation-report-details = تفاصيل إضافية: { $details }
admin-moderation-report-review = تمت المراجعة بواسطة { $reviewer }، معرّف الحساب { $reviewer_id }، في { $time }.
admin-moderation-view-context = عرض المحادثة حول وقت البلاغ
admin-moderation-view-target-history = عرض جميع الرسائل العامة المحتفظ بها من معرّف الحساب المُبلَّغ عنه
admin-moderation-mark-reviewed = وضع علامة "تمت المراجعة" دون تسجيل عقوبة
admin-moderation-dismiss-report = رفض البلاغ
admin-moderation-mark-actioned = وضع علامة "تم تسجيل إجراء". هذا لا يطبّق عقوبة.
admin-moderation-context-heading = سياق البلاغ رقم { $id }، مُقدَّم { $time }. القناة: { $channel }. الرسائل مرتبة زمنياً؛ ورسائل المستخدم المُبلَّغ عنه محدَّدة صراحةً.
admin-moderation-context-message = { $username }: { $message } الرسالة رقم { $id }، أُرسلت { $time }. معرّف الحساب: { $uuid }. اللغة: { $channel }.
admin-moderation-context-target-message = المستخدم المُبلَّغ عنه { $username }: { $message } الرسالة رقم { $id }، أُرسلت { $time }. معرّف الحساب: { $uuid }. اللغة: { $channel }.
admin-moderation-context-anchor-message = رسالة مرتبطة للمستخدم المُبلَّغ عنه من { $username }: { $message } الرسالة رقم { $id }، أُرسلت { $time }. معرّف الحساب: { $uuid }. اللغة: { $channel }.
admin-moderation-context-empty = لم تتبقَّ رسائل عامة محتفظ بها حول وقت هذا البلاغ.
admin-moderation-copy-page = { $count ->
    [one] نسخ الرسالة في هذه الصفحة (1)
   *[other] نسخ الرسائل في هذه الصفحة ({ $count })
}
admin-moderation-copy-page-success = { $count ->
    [one] تم نسخ رسالة واحدة من هذه الصفحة إلى الحافظة.
   *[other] تم نسخ { $count } رسالة من هذه الصفحة إلى الحافظة.
}
admin-moderation-copy-page-failed = تعذّر نسخ هذه الصفحة إلى الحافظة. تحقّق من إذن الحافظة وحاول مرة أخرى.
admin-moderation-history-prompt = أدخل اسم المستخدم المطابق تماماً الذي تريد العثور على سجل دردشته العامة المحتفظ به. ستُدرج معرّفات الحسابات التاريخية التي تحمل اسم المستخدم نفسه بشكل منفصل.
admin-moderation-sender-results-heading = هويات المرسِلين المحتفظ بها المطابقة لاسم المستخدم المطابق تماماً "{ $username }".
admin-moderation-sender-result = { $username }، معرّف الحساب { $uuid }. { $count } رسالة من { $first } إلى { $last }.
admin-moderation-no-sender-history = لا يوجد سجل دردشة عامة محتفظ به يطابق اسم المستخدم المطابق تماماً "{ $username }".
admin-moderation-history-heading = سجل الدردشة العامة المحتفظ به لـ { $username }، معرّف الحساب { $uuid }: { $count } رسالة، الأحدث أولاً.
admin-moderation-history-message = { $username }: { $message } الرسالة رقم { $id }، أُرسلت { $time }. اللغة: { $channel }.
admin-moderation-history-empty = لم تتبقَّ رسائل عامة محتفظ بها لمعرّف الحساب هذا.
admin-moderation-message-list-heading = سجل الرسائل العامة. { $count } رسالة مطابقة. الترتيب: { $sort }. اللغة: { $channel }. الفترة: { $period }. جميع الأوقات بتوقيت UTC.
admin-moderation-message-row = { $username }: { $message } الرسالة رقم { $id }، أُرسلت { $time }. معرّف الحساب: { $uuid }. اللغة: { $channel }.
admin-moderation-message-list-empty = لا توجد رسائل عامة محتفظ بها تطابق هذه الفلاتر.
admin-moderation-message-filter-sort = ترتيب الفرز: { $sort }
admin-moderation-message-filter-language = اللغة: { $channel }
admin-moderation-message-filter-period = الفترة الزمنية: { $period }
admin-moderation-message-filter-reset = إعادة تعيين جميع فلاتر الرسائل
admin-moderation-message-sort-newest = الأحدث أولاً
admin-moderation-message-sort-oldest = الأقدم أولاً
admin-moderation-message-language-all = جميع اللغات
admin-moderation-message-period-all = كل الأوقات
admin-moderation-message-period-today = اليوم
admin-moderation-message-period-yesterday = أمس
admin-moderation-message-period-last-7-days = آخر 7 أيام
admin-moderation-message-period-last-30-days = آخر 30 يوماً
admin-moderation-message-period-current-month = الشهر التقويمي الحالي
admin-moderation-message-period-previous-month = الشهر التقويمي السابق
admin-moderation-message-language-menu = فلترة الرسائل حسب اللغة. الفلتر الحالي هو { $channel }.
admin-moderation-message-period-menu = فلترة الرسائل حسب الفترة الزمنية بتوقيت UTC. الفلتر الحالي هو { $period }.
admin-moderation-message-filter-current = { $value } (الحالي)
admin-moderation-clear-history-confirm = حذف جميع رسائل الدردشة العامة المحتفظ بها البالغ عددها { $count } نهائياً؟ لا يمكن التراجع عن ذلك. ستبقى { $open } بلاغاً مفتوحاً، لكن ستُزال روابط الرسائل المحفوظة وسياق المحادثة الخاص بها.
admin-moderation-clear-closed-confirm = حذف جميع البلاغات المغلقة البالغ عددها { $count } نهائياً؟ ستبقى البلاغات المفتوحة وسجل الدردشة العامة. لا يمكن التراجع عن ذلك.
admin-moderation-report-already-closed = تم إغلاق هذا البلاغ بالفعل بواسطة إجراء مراجعة آخر. تمت إعادة تحميل السجل الحالي.
admin-moderation-report-status-updated = تم الآن وضع علامة { $status } على البلاغ رقم { $id }. لم يتم تطبيق أي عقوبة تلقائية.
admin-new-manual-report = بلاغ إشراف جديد رقم { $id }: أبلغ { $reporter } عن { $target }.
admin-new-automatic-report = بلاغ إزعاج جديد من النظام رقم { $id } يتطلب مراجعة يدوية: { $target }.
admin-moderation-history-cleared = تم حذف { $count } رسالة دردشة عامة محتفظ بها نهائياً. تبقى البلاغات الموجودة دون روابط رسائل. إذا لم تتبقَّ أي رسائل، فسيُعاد ترقيم الرسائل بدءاً من 1.
admin-moderation-closed-reports-cleared = تم حذف { $count } بلاغ مغلق نهائياً. تبقى البلاغات المفتوحة. إذا لم تتبقَّ أي بلاغات، فسيُعاد ترقيم البلاغات بدءاً من 1.

admin-database-management = إدارة قاعدة البيانات
admin-database-management-summary = صيانة قاعدة بيانات للمطوّرين فقط. التحليل للقراءة فقط. يؤدي النسخ الاحتياطي والتنظيف والضغط إلى إيقاف اللعب وتغييرات الحسابات مؤقتاً عبر الخادم.
admin-database-backup = نسخ قاعدة البيانات احتياطياً
admin-database-backup-confirm = نسخ قاعدة البيانات احتياطياً الآن؟ سيتوقف اللعب وتغييرات الحسابات مؤقتاً بينما ينشئ SQLite لقطة استرداد ويتحقق منها. سيُحتفظ بالنسخة الاحتياطية في دليل النسخ الاحتياطي للخادم حتى يزيلها مشغّل.
admin-database-backup-success = اكتمل النسخ الاحتياطي لقاعدة البيانات: { $filename } ({ $size }).
admin-database-backup-failed = فشل النسخ الاحتياطي لقاعدة البيانات. لم يتم نشر أي نسخة احتياطية جزئية. راجع سجل الخادم للتفاصيل.
admin-database-size-bytes = { $value ->
    [one] بايت واحد
   *[other] { NUMBER($value, maximumFractionDigits: 0) } بايت
}
admin-database-size-kib = { NUMBER($value, maximumFractionDigits: 1) } كيبيبايت
admin-database-size-mib = { NUMBER($value, maximumFractionDigits: 1) } ميبيبايت
admin-database-size-gib = { NUMBER($value, maximumFractionDigits: 1) } جيبيبايت
admin-database-storage-analyze = تحليل مرشّحات التنظيف
admin-database-storage-analysis-summary = حجم قاعدة البيانات: { $size }. مساحة SQLite القابلة لإعادة الاستخدام: { $reusable }. سجلات قاعدة البيانات المؤهلة: { $records }.
admin-database-storage-analysis-failed = فشل تحليل التخزين دون تغيير أي بيانات. راجع سجل الخادم للتفاصيل.
admin-database-storage-refresh-analysis = تحديث تحليل التخزين
admin-database-storage-cleanup = تشغيل تنظيف التخزين
admin-database-storage-cleanup-confirm = تشغيل تنظيف التخزين الآمن الآن؟ سيتوقف اللعب وتغييرات الحسابات مؤقتاً بينما ينشئ الخادم نسخة احتياطية للأمان ويتحقق منها، ويزيل فقط السجلات المؤقتة أو اليتيمة المدرجة، ويتحقق من النتيجة. لن يتم ضغط ملف قاعدة البيانات.
admin-database-storage-cleanup-not-needed = تنظيف التخزين غير مطلوب. لم يُعثر على سجلات قاعدة بيانات مؤهلة أو ملفات نسخ احتياطي مؤقتة مهجورة.
admin-database-storage-cleanup-success = اكتمل تنظيف التخزين. سجلات قاعدة البيانات المُزالة: { $records }. ملفات النسخ الاحتياطي المؤقتة المهجورة المُزالة: { $files } ({ $file_size }). مساحة SQLite القابلة لإعادة الاستخدام: { $reusable }. شغّل الضغط بشكل منفصل لتقليل حجم ملف قاعدة البيانات. نسخة الأمان الاحتياطية: { $filename }.
admin-database-storage-cleanup-failed = فشل تنظيف التخزين. تم الاحتفاظ بأي نسخة احتياطية للأمان مكتملة. راجع سجل الخادم قبل المحاولة مرة أخرى.
admin-database-storage-no-record-candidates = لا توجد سجلات قاعدة بيانات مؤهلة حالياً للتنظيف الآمن.
admin-database-storage-temporary-files = ملفات النسخ الاحتياطي المؤقتة المهجورة لـ PlayAural: { $count } ({ $size }).
admin-database-storage-invalid-timestamps = تحذير أمان: { $count } سجل يحتوي على طوابع زمنية احتفاظ غير صالحة. لن يصنّفها التنظيف أبداً على أنها منتهية الصلاحية بتخمين عمرها؛ راجعها يدوياً.
admin-database-storage-exclusions = مستثناة دائماً من التنظيف التلقائي: الطاولات المحفوظة، ونتائج الألعاب، وسجل الدردشة العامة، وبلاغات الإشراف، وحسابات المستخدمين، وعمليات الحظر الصالحة، والبيانات النشطة، وإحصائيات الألعاب المسجّلة، وبيانات التوافق، والنسخ الاحتياطية الصالحة، والسجلات. لا تُزال الطاولات المحفوظة إلا بإجراء صريح من المالك أو المطوّر.
admin-database-storage-category-row = { $category }: { $count }
admin-database-storage-category-expired-table-checkpoints = نقاط تحقّق الطاولات المؤقتة المنتهية الصلاحية
admin-database-storage-category-expired-password-reset-tokens = رموز إعادة تعيين كلمة المرور المنتهية الصلاحية
admin-database-storage-category-expired-bans = سجلات الحظر المحتفظ بها لأكثر من { $days } يوماً بعد انتهاء الصلاحية
admin-database-storage-category-stale-pending-friend-requests = طلبات الصداقة المعلّقة الأقدم من { $days } يوماً
admin-database-storage-category-orphaned-friendships = سجلات الصداقة اليتيمة
admin-database-storage-category-orphaned-user-blocks = سجلات حظر المستخدمين اليتيمة
admin-database-storage-category-stale-user-notifications = تنبيهات المستخدمين الأقدم من { $days } يوماً
admin-database-storage-category-orphaned-user-notifications = سجلات تنبيهات المستخدمين اليتيمة
admin-database-storage-category-expired-mutes = سجلات الكتم المنتهية الصلاحية
admin-database-storage-category-orphaned-mutes = سجلات الكتم اليتيمة
admin-database-compact = ضغط قاعدة البيانات واستعادة المساحة غير المستخدمة
admin-database-compact-confirm = ضغط قاعدة البيانات الآن؟ سيتوقف اللعب وتغييرات الحسابات مؤقتاً. ستُنشأ نسخة احتياطية للأمان مُتحقَّق منها قبل أن يعيد SQLite بناء قاعدة البيانات الحية. تتطلب هذه العملية مساحة قرص مؤقتة كبيرة ويُفضّل تشغيلها خلال فترة هدوء.
admin-database-compact-success = اكتمل ضغط قاعدة البيانات. تغيّر حجم الملف من { $before } إلى { $after }؛ تم استعادة { $reclaimed }. نسخة الأمان الاحتياطية: { $filename }.
admin-database-compact-failed = فشل ضغط قاعدة البيانات. لم تُغيَّر قاعدة البيانات الحية عمداً، وتم الاحتفاظ بأي نسخة احتياطية للأمان مكتملة. راجع سجل الخادم للتفاصيل.
admin-database-maintenance-busy = توجد عملية خادم حصرية أخرى نشطة بالفعل. انتظر انتهاءها قبل بدء صيانة قاعدة البيانات.
database-maintenance-operation-backup = النسخ الاحتياطي لقاعدة البيانات
database-maintenance-operation-cleanup = تنظيف التخزين
database-maintenance-operation-compaction = ضغط قاعدة البيانات
database-maintenance-not-active = صيانة قاعدة البيانات غير نشطة حالياً.
database-maintenance-input-blocked = عملية { $operation } للخادم قيد التنفيذ. تم إيقاف اللعب وتسجيل الدخول وإنشاء الحسابات وتغييرات الحسابات مؤقتاً. تبقى قائمتك الحالية متاحة، لكن لن تُنفَّذ الإجراءات حتى تنتهي الصيانة.
database-maintenance-auth-blocked = صيانة قاعدة بيانات الخادم قيد التنفيذ. تسجيل الدخول وإنشاء الحسابات وتغييرات كلمة المرور غير متاحة مؤقتاً. يرجى المحاولة مرة أخرى بعد انتهاء الصيانة.
database-maintenance-backup-started = يقوم المطوّر بإنشاء نسخة احتياطية لقاعدة بيانات الخادم. تم إيقاف اللعب وتغييرات الحسابات مؤقتاً؛ تبقى القوائم الحالية مرئية. سيتم إعلامك عند استئناف الخدمة العادية.
database-maintenance-backup-completed = اكتمل النسخ الاحتياطي لقاعدة بيانات الخادم. يُستأنف الآن اللعب والوصول إلى الحسابات بشكل عادي.
database-maintenance-backup-failed = تعذّر إكمال النسخ الاحتياطي لقاعدة بيانات الخادم. لم يتم نشر أي نسخة احتياطية جزئية. يُستأنف الآن اللعب والوصول إلى الحسابات بشكل عادي.
database-maintenance-cleanup-started = يقوم المطوّر بتنفيذ تنظيف تخزين الخادم. تم إيقاف اللعب وتغييرات الحسابات مؤقتاً، لكن تبقى القوائم الحالية مرئية. تُنشأ أولاً نسخة احتياطية للأمان مُتحقَّق منها. سيتم إعلامك عند استئناف الخدمة العادية.
database-maintenance-cleanup-completed = اكتمل تنظيف تخزين الخادم والتحقق من قاعدة البيانات. يُستأنف الآن اللعب والوصول إلى الحسابات بشكل عادي.
database-maintenance-cleanup-failed = تعذّر إكمال تنظيف تخزين الخادم بأمان. يُستأنف الآن اللعب والوصول إلى الحسابات بشكل عادي.
database-maintenance-compaction-started = يقوم المطوّر بضغط قاعدة بيانات الخادم. تم إيقاف اللعب وتغييرات الحسابات مؤقتاً؛ تبقى القوائم الحالية مرئية. سيتم إعلامك عند استئناف الخدمة العادية.
database-maintenance-compaction-completed = اكتمل ضغط قاعدة بيانات الخادم. يُستأنف الآن اللعب والوصول إلى الحسابات بشكل عادي.
database-maintenance-compaction-failed = تعذّر إكمال ضغط قاعدة بيانات الخادم. يُستأنف اللعب والوصول إلى الحسابات بشكل عادي دون تطبيق الضغط.
database-maintenance-reopen-failed = خطأ حرج في صيانة قاعدة البيانات: تعذّرت إعادة فتح قاعدة البيانات الحية بأمان، لذا يبقى الخادم مجمّداً. يرجى انتظار المطوّر لاستعادة الخدمة.

account-approval = الموافقة على الحساب
no-pending-accounts = لا توجد حسابات معلّقة.
approve-account = الموافقة
decline-account = رفض
account-approved = تمت الموافقة على حساب { $player }.
account-declined = تم رفض حساب { $player } وحذفه.

waiting-for-approval = حسابك في انتظار موافقة مسؤول. يرجى الانتظار...
account-approved-welcome = تمت الموافقة على حسابك! مرحباً بك في PlayAural!
account-declined-goodbye = تم رفض طلب حسابك.

account-action = تم اتخاذ إجراء بشأن الحساب

promote-admin = ترقية إلى مسؤول
demote-admin = خفض رتبة مسؤول
ban-user = حظر مستخدم
unban-user = إلغاء حظر مستخدم
no-users-to-promote = لا يوجد مستخدمون متاحون للترقية.
no-admins-to-demote = لا يوجد مسؤولون متاحون لخفض الرتبة.
admin-search-users = البحث باسم المستخدم
admin-search-users-current = البحث باسم المستخدم. البحث الحالي: { $query }.
admin-search-prompt = أدخل اسم مستخدم كاملاً أو جزءاً منه للبحث. اتركه فارغاً لتصفّح جميع النتائج صفحةً صفحة.
menu-page-summary = عرض { $start }-{ $end } من { $total } إدخالاً. الصفحة { $page } من { $pages }.
menu-page-summary-query = البحث "{ $query }": عرض { $start }-{ $end } من { $total } إدخالاً. الصفحة { $page } من { $pages }.
menu-page-refresh = تحديث القائمة
menu-list-refreshed = تم تحديث القائمة.
menu-page-first = الصفحة الأولى
menu-page-previous = الصفحة السابقة
menu-page-next = الصفحة التالية
menu-page-last = الصفحة الأخيرة
admin-search-no-results = لم يُعثر على مستخدمين مطابقين. استخدم "البحث باسم المستخدم" لتجربة مصطلح مختلف.
confirm-promote = هل أنت متأكد أنك تريد ترقية { $player } إلى مسؤول؟
confirm-demote = هل أنت متأكد أنك تريد خفض رتبة { $player } من مسؤول؟
admin-role-target-changed = لم يعد { $player } يحمل الرتبة المتوقعة. حدّث القائمة وحاول مرة أخرى.
broadcast-to-all = الإعلان لجميع المستخدمين
broadcast-to-admins = الإعلان للمسؤولين فقط
broadcast-to-nobody = صامت (بدون إعلان)
promote-announcement = تمت ترقية { $player } إلى مسؤول!
promote-announcement-you = تمت ترقيتك إلى مسؤول!
promote-announcement-actor = رقّيت { $player } إلى مسؤول!
demote-announcement = تم خفض رتبة { $player } من مسؤول.
demote-announcement-you = تم خفض رتبتك من مسؤول.
demote-announcement-actor = خفضت رتبة { $player } من مسؤول.
not-admin-anymore = لم تعد مسؤولاً ولا يمكنك تنفيذ هذا الإجراء.
dev-only-action = هذا الإجراء مقتصر على المطوّرين فقط.

ban-duration-1h = ساعة واحدة
ban-duration-6h = 6 ساعات
ban-duration-12h = 12 ساعة
ban-duration-1d = يوم واحد
ban-duration-3d = 3 أيام
ban-duration-1w = أسبوع واحد
ban-duration-1m = شهر واحد
ban-duration-permanent = دائم

reason-spam = إزعاج
reason-harassment = تحرّش
reason-cheating = غش
reason-inappropriate = سلوك غير لائق
reason-custom = أخرى / مخصّص

no-users-to-ban = لا يوجد مستخدمون متاحون للحظر.
no-banned-users = لا يوجد مستخدمون محظورون حالياً.
admin-active-ban-entry = { $username }. انتهاء الحظر: { $expires }. السبب: { $reason }. صادر عن: { $admin }.
admin-active-mute-entry = { $username }. انتهاء الكتم: { $expires }. السبب: { $reason }. صادر عن: { $admin }.
admin-penalty-expiry-permanent = دائم
admin-penalty-expiry-unknown = انتهاء غير معروف
admin-penalty-expiry-expired = منتهٍ بالفعل
admin-penalty-expiry-timed = { $date } (متبقٍّ { $remaining })
admin-penalty-reason-unknown = سبب غير محدّد
admin-penalty-admin-unknown = مسؤول غير معروف
admin-penalty-remaining-days = { $count ->
    [one] يوم واحد
   *[other] { $count } يوم
}
admin-penalty-remaining-hours = { $count ->
    [one] ساعة واحدة
   *[other] { $count } ساعة
}
admin-penalty-remaining-minutes = { $count ->
    [one] دقيقة واحدة
   *[other] { $count } دقيقة
}
admin-penalty-remaining-less-minute = أقل من دقيقة واحدة

ban-broadcast = تم حظر { $target } بواسطة { $actor } بسبب { $reason }. المدة: { $duration }.
ban-broadcast-actor = حظرت { $target } بسبب { $reason }. المدة: { $duration }.
unban-broadcast = تم إلغاء حظر { $target } بواسطة { $actor }.
unban-broadcast-actor = ألغيت حظر { $target }.
unban-broadcast-target = ألغى { $actor } حظرك.

banned-menu-title = الحساب محظور
banned-reason = السبب: { $reason }
banned-expires = ينتهي: { $expires }
banned-permanent = ينتهي: دائم
disconnect = قطع الاتصال


mute-user = كتم مستخدم
unmute-user = إلغاء كتم مستخدم
no-users-to-mute = لا يوجد مستخدمون متاحون للكتم.
no-muted-users = لا يوجد مستخدمون مكتومون حالياً.
mute-duration-5m = 5 دقائق
mute-duration-15m = 15 دقيقة
mute-duration-30m = 30 دقيقة
mute-duration-1h = ساعة واحدة
mute-duration-6h = 6 ساعات
mute-duration-1d = يوم واحد
mute-duration-permanent = دائم
mute-broadcast = تم كتم { $target } بواسطة { $actor } بسبب { $reason }. المدة: { $duration }.
mute-broadcast-actor = كتمت { $target } بسبب { $reason }. المدة: { $duration }.
unmute-broadcast = تم إلغاء كتم { $target } بواسطة { $actor }.
unmute-broadcast-actor = ألغيت كتم { $target }.
you-have-been-muted = لقد تم كتمك. السبب: { $reason }. المدة: { $duration }.
you-have-been-unmuted = لقد تم إلغاء كتمك. يمكنك الدردشة مرة أخرى.
muted-remaining-seconds = أنت مكتوم. متبقٍّ { $seconds } ثانية.
muted-remaining-minutes = أنت مكتوم. متبقٍّ { $minutes } دقيقة.
muted-permanent = أنت مكتوم بشكل دائم. تواصل مع مسؤول لمزيد من المعلومات.
chat-rate-limited = تمهّل! أنت ترسل الرسائل بسرعة كبيرة.
chat-repeated-message = يرجى عدم تكرار الرسالة نفسها.
chat-global-disabled-send = الدردشة العامة معطّلة في خياراتك. أعد تفعيل الدردشة العامة قبل إرسال رسائل عامة.
chat-global-channel-required-send = حدّد لغة للدردشة العامة قبل إرسال الرسائل. لا تتم مراقبة الدردشة العامة في الوقت الفعلي. إذا استخدم أحدهم ألفاظاً نابية أو أهانك، فاحظره. يرجى الإبلاغ عن الإساءات الجسيمة أو المتكررة للمراجعة لاحقاً.
chat-global-log-unavailable = الدردشة العامة غير متاحة مؤقتاً لأن هذه الرسالة تعذّر حفظها بأمان. يرجى المحاولة لاحقاً.
chat-table-disabled-send = دردشة الطاولة معطّلة في خياراتك. أعد تفعيل دردشة الطاولة قبل إرسال رسائل الطاولة.
chat-global-temporarily-disabled-send = تم تعطيل الدردشة العامة مؤقتاً بواسطة المطوّر.
chat-invalid-channel = قناة الدردشة تلك غير متاحة.
communication-channel-table = دردشة الطاولة
communication-channel-global = الدردشة العامة
communication-channel-team = دردشة الفريق
communication-channel-selected = تم اختيار { $channel }.
communication-channel-stale = لم تعد قناة التواصل هذه متاحة. تم تحديث اختيارك للقناة.
communication-text-restricted = لا يمكنك إرسال رسائل في هذه القناة الآن.
communication-chat-message = { $player } في { $channel }: { $message }
communication-chat-message-you = أنت في { $channel }: { $message }
communication-voice-room-label = صوت { $channel }
communication-voice-restricted = لا يمكن استخدام ميكروفونك في هذه القناة الآن.
communication-voice-not-connected = يجب الاتصال بالدردشة الصوتية قبل أن تتمكن من استخدام الميكروفون.
chat-invalid-message = تعذّر إرسال تلك الرسالة لأن تنسيقها غير صالح.
chat-message-too-long = تلك الرسالة طويلة جداً. يمكن أن تحتوي الرسائل على { $limit } حرفاً كحدّ أقصى.

report-user = الإبلاغ عن مستخدم
enter-report-username = أدخل اسم المستخدم المراد الإبلاغ عنه.
report-error-self = لا يمكنك الإبلاغ عن حسابك الخاص.
report-select-reason = الإبلاغ عن { $username }: حدّد السبب الذي يصف السلوك على أفضل وجه.
report-reason-spam = إزعاج أو تشويش متكرر
report-reason-harassment = تحرّش أو إهانات شخصية
report-reason-hateful-content = محتوى يحضّ على الكراهية
report-reason-sexual-content = محتوى جنسي
report-reason-threats = تهديدات بالأذى
report-reason-personal-information = مشاركة معلومات شخصية
report-reason-other = سوء سلوك جسيم آخر
report-channel-unspecified = لم يتم تحديد قناة دردشة عامة
report-confirm-summary = الإبلاغ عن { $username } بسبب { $reason }. قناة السياق: { $channel }. سيُحفظ البلاغ للمراجعة اليدوية. لن يتم إعلام المستخدم أو معاقبته تلقائياً.
report-submit = إرسال البلاغ
report-change-reason = تغيير السبب
report-submitted = تم حفظ بلاغك عن { $username } مع وقت تقديمه الدقيق للمراجعة اليدوية. لم يتم إعلام المستخدم. يمكنك أيضاً حظر { GENDER_TERM($username_gender, "object") } لإيقاف التواصل المباشر وإخفاء الرسائل العامة { GENDER_TERM($username_gender, "possessive-determiner") }.
report-target-cooldown = لقد أبلغت مؤخراً عن { $username }. أضف بلاغاً آخر فقط بعد { $duration }؛ استخدم "حظر" الآن إذا كنت لا تريد تلقّي الرسائل { GENDER_TERM($username_gender, "possessive-determiner") }.
report-rate-limited = لقد قدّمت عدة بلاغات مؤخراً. حاول مرة أخرى بعد { $duration }.
report-failed = تعذّر حفظ البلاغ بأمان. يرجى المحاولة لاحقاً.

broadcast-announcement = إعلان عام
admin-broadcast-prompt = أدخل الرسالة لبثّها لجميع المستخدمين المتصلين. (سترسل إلى الجميع!)
admin-broadcast-sent = تم إرسال البث إلى { $count } مستخدم.

manage-motd = إدارة رسالة اليوم
create-update-motd = إنشاء/تحديث رسالة اليوم
view-motd = عرض رسالة اليوم النشطة
delete-motd = حذف رسالة اليوم
motd-version-prompt = أدخل رقم إصدار رسالة اليوم الجديد (يجب أن يكون > 0):
invalid-motd-version = إصدار رسالة اليوم غير صالح. يجب أن يكون رقماً موجباً.
motd-created = تم إنشاء رسالة اليوم الإصدار { $version } بنجاح.
motd-deleted = تم حذف رسالة اليوم.
motd-delete-empty = لا توجد رسالة يوم نشطة لحذفها.
motd-not-exists = لا توجد رسالة يوم نشطة.
motd-announcement = رسالة اليوم
motd-broadcast = رسالة اليوم الجديدة: { $message }
error-no-languages = خطأ: لم يُعثر على لغات.
ok = موافق

admin-localized-text-subject-motd = رسالة اليوم
admin-localized-text-subject-power = سبب طاقة الخادم
admin-localized-text-subject-ban = سبب حظر مخصّص
admin-localized-text-subject-mute = سبب كتم مخصّص
admin-localized-text-instructions = حرّر ترجمات { $subject }. اللغات الرسمية مطلوبة. اللغات المجتمعية اختيارية وتستخدم { $fallback } عند تركها فارغة.
admin-localized-text-motd-version = إصدار رسالة اليوم: { $version }
admin-localized-text-official-heading = اللغات الرسمية، مطلوبة
admin-localized-text-community-heading = اللغات المجتمعية، اختيارية
admin-localized-text-field = { $language }: { $status }
admin-localized-text-required-set = مُدخَل، مطلوب
admin-localized-text-required-missing = غير مُدخَل، مطلوب
admin-localized-text-optional-set = مُدخَل، اختياري
admin-localized-text-optional-fallback = غير مُدخَل، اختياري، يستخدم البديل
admin-localized-text-prompt = أدخل { $subject } بـ { $language }. الحد الأقصى { $max } حرفاً.
admin-localized-text-too-long = تلك الترجمة طويلة جداً. الحد الأقصى هو { $max } حرفاً.
admin-localized-text-missing-required = أدخل جميع الترجمات المطلوبة أولاً. المفقود: { $languages }.
admin-localized-text-publish-motd = نشر رسالة اليوم
admin-localized-text-continue = متابعة
admin-localized-text-apply-ban = تطبيق الحظر
admin-localized-text-apply-mute = تطبيق الكتم

unknown-player = لاعب غير معروف
unknown-user = مستخدم غير معروف
user-account-unavailable = لم يعد حساب هذا المستخدم متاحاً.

logout-confirm-title = هل أنت متأكد أنك تريد تسجيل الخروج والخروج من اللعبة؟
logout-confirm-yes = نعم، تسجيل الخروج
logout-confirm-no = لا، البقاء

system-name = النظام
server-restarting = سيُعاد تشغيل الخادم خلال { $seconds } ثانية...
server-shutting-down = سيتم إيقاف الخادم خلال { $seconds } ثانية...
server-shutting-down-now = يتم إيقاف الخادم الآن. إلى اللقاء!
server-power-management = إدارة طاقة الخادم
server-power-reboot = إعادة تشغيل الخادم
server-power-shutdown = إيقاف الخادم
server-power-cancel = إلغاء إجراء الطاقة المجدول
server-power-active-status = { $action } مجدول. السبب: { $reason }.
server-power-action-reboot = إعادة التشغيل
server-power-action-shutdown = الإيقاف
server-power-delay-30s = خلال 30 ثانية
server-power-delay-1m = خلال دقيقة واحدة
server-power-delay-5m = خلال 5 دقائق
server-power-delay-10m = خلال 10 دقائق
server-power-delay-30m = خلال 30 دقيقة
server-power-delay-1h = خلال ساعة واحدة
server-power-delay-2h = خلال ساعتين
server-power-delay-custom = تأخير مخصّص بالدقائق
server-power-custom-delay-prompt = أدخل التأخير بالدقائق، من 1 إلى { $max }:
server-power-invalid-custom-delay = تأخير غير صالح. أدخل عدداً صحيحاً من الدقائق من 1 إلى { $max }.
server-power-reason-update = تحديث
server-power-reason-maintenance = صيانة
server-power-reason-security = أمان
server-power-reason-technical = مشكلة تقنية
server-power-reason-custom = سبب مخصّص
server-power-reason-unspecified = سبب غير محدّد
server-power-confirm-summary = أكّد { $action } الخادم خلال { $duration }. السبب: { $reason }.
server-power-scheduled = تمت جدولة { $action } الخادم خلال { $duration }.
server-power-already-scheduled = يوجد إجراء طاقة خادم مجدول بالفعل. ألغِه قبل جدولة إجراء آخر.
server-power-cancel-none = لا يوجد إجراء طاقة خادم مجدول حالياً.
server-power-cancelled = تم إلغاء إجراء طاقة الخادم المجدول.
server-power-cancelled-broadcast = ألغى { $admin } { $action } الخادم المجدول.
server-power-cancelled-broadcast-you = ألغيت { $action } الخادم المجدول.
server-power-command-removed = تمت إزالة أمري الدردشة /reboot و/stop. استخدم "الإدارة"، "إدارة طاقة الخادم" بدلاً من ذلك.
server-power-finalizing-input-blocked = ينهي الخادم عملية إعادة تشغيل أو إيقاف. يرجى انتظار قطع اتصال العميل.
server-power-maintenance-active = لا يمكن جدولة عملية طاقة خادم أثناء نشاط صيانة قاعدة البيانات. انتظر انتهاء الصيانة وحاول مرة أخرى.
server-power-finalize-failed = تعذّر إنهاء { $action } الخادم المجدول بأمان. سيبقى الخادم متصلاً؛ يرجى التواصل مع مسؤول.
server-power-reboot-warning = إعادة تشغيل الخادم خلال { $duration }. السبب: { $reason }. لا تقطع الاتصال يدوياً؛ سيعيد عميلك الاتصال تلقائياً، وسيتم الحفاظ على الطاولات النشطة.
server-power-shutdown-warning = إيقاف الخادم خلال { $duration }. السبب: { $reason }. سيصبح الخادم غير متصل؛ احفظ أي ألعاب تريد الاحتفاظ بها قبل الإيقاف.
server-power-reboot-now = يُعاد تشغيل الخادم الآن. السبب: { $reason }. لا تقطع الاتصال يدوياً؛ سيعيد عميلك الاتصال تلقائياً، وسيتم الحفاظ على الطاولات النشطة.
server-power-shutdown-now = يتم إيقاف الخادم الآن. السبب: { $reason }. سيصبح الخادم غير متصل.
server-power-restore-waiting = تمت استعادة هذه الطاولة بعد إعادة تشغيل مخطّطة. الانتظار حتى { $seconds } ثانية لإعادة اتصال اللاعبين الآخرين قبل استبدال المقاعد المفقودة ببوتات.
server-power-restore-input-blocked = لا تزال هذه الطاولة تتعافى من إعادة التشغيل المخطّطة. تم إيقاف اللعب مؤقتاً حتى { $seconds } ثانية إضافية في انتظار { $players }؛ يرجى المحاولة مرة أخرى بعد انتهاء فترة السماح.
server-power-restore-missing-players-fallback = اللاعبون المتبقّون
server-power-restore-complete = أعاد جميع اللاعبين النشطين الاتصال بعد إعادة التشغيل المخطّطة. استؤنفت اللعبة.
server-power-restore-complete-with-bots = انتهت فترة سماح إعادة الاتصال بعد إعادة التشغيل المخطّطة. تم استبدال المقاعد المفقودة ببوتات، وتُستأنف اللعبة.
duration-seconds = { $count ->
    [one] ثانية واحدة
   *[other] { $count } ثانية
}
duration-minutes = { $count ->
    [one] دقيقة واحدة
   *[other] { $count } دقيقة
}
duration-hours = { $count ->
    [one] ساعة واحدة
   *[other] { $count } ساعة
}
duration-minutes-seconds = { $minutes } دقيقة و{ $seconds } ثانية
duration-hours-minutes = { $hours } ساعة و{ $minutes } دقيقة
server-error-changing-language = تعذّر تغيير اللغة. تبقى واجهتك السابقة نشطة.
default-save-name = { $game } - { $date }

speech-settings = إعدادات الكلام
speech-mode-option = وضع الكلام: { $status }
speech-rate-option = سرعة الكلام: { $value }%
speech-voice-option = الصوت: { $voice }
select-voice = اختيار الصوت
invalid-rate = سرعة كلام غير صالحة. استخدم قيمة بين 50 و300.
mode-aria = Aria-live
mode-web-speech = Web Speech API
default-voice = الصوت الافتراضي
mobile-speech-settings = إعدادات الكلام في الجوال
mobile-tts-engine-option = محرك تحويل النص إلى كلام: { $engine }
mobile-tts-engine-system = الافتراضي للنظام
mobile-tts-engine-system-selected = محرك تحويل النص إلى كلام الافتراضي للنظام
mobile-tts-engine-api-note = يُدار اختيار محرك Android بواسطة إعدادات النظام في هذا الإصدار.
mobile-tts-voice-option = صوت الجوال: { $voice }
mobile-tts-rate-option = سرعة الكلام في الجوال: { $value }%
mobile-tts-enter-rate = أدخل سرعة الكلام في الجوال (50-200)
mobile-tts-invalid-rate = سرعة كلام جوال غير صالحة. استخدم قيمة بين 50 و200.

player-kicked-offline = تم طرد اللاعب { $player } (غير متصل).
game-paused-host-disconnect = توقفت اللعبة مؤقتاً. في انتظار إعادة اتصال { $player }...
game-resumed = أعاد { $player } الاتصال. استؤنفت اللعبة!
game-resumed-you = أعدت الاتصال. استؤنفت اللعبة!

auth-error-username-length = يجب أن يتراوح اسم المستخدم بين 3 و30 حرفاً.
auth-error-username-invalid-chars = يمكن أن يحتوي اسم المستخدم على حروف وأرقام ومسافات فقط (بدون مسافات متتالية، وبدون أحرف خاصة).
auth-error-password-weak = يجب أن تتكون كلمة المرور من 8 أحرف على الأقل وأن تحتوي على حروف وأرقام معاً.

personal-and-options = الشخصي والخيارات
profile = الملف الشخصي
friends = الأصدقاء
profile-registration-date = تاريخ التسجيل: { $date }
profile-date-unknown = غير معروف
profile-username = اسم المستخدم: { $username }
profile-email = البريد الإلكتروني: { $email }
admin-view-email = عرض المسؤول - البريد الإلكتروني: { $email }
profile-gender = الجنس: { $gender }
profile-bio = النبذة: { $bio }
profile-bio-empty = غير محدّد
profile-email-empty = غير محدّد

gender-male = ذكر
gender-female = أنثى
gender-non-binary = غير ثنائي
gender-not-set = غير محدّد

# Shared grammatical forms for account gender. Games may override any form by
# defining <context>-gender-term-<form> and passing that context to GENDER_TERM.
gender-term-subject =
    { $gender ->
        [male] هو
        [female] هي
       *[other] هو
    }
gender-term-subject-capitalized =
    { $gender ->
        [male] هو
        [female] هي
       *[other] هو
    }
gender-term-subject-be =
    { $gender ->
        [male] هو
        [female] هي
       *[other] هو
    }
gender-term-subject-be-capitalized =
    { $gender ->
        [male] هو
        [female] هي
       *[other] هو
    }
gender-term-subject-have =
    { $gender ->
        [male] لديه
        [female] لديها
       *[other] لديه
    }
gender-term-subject-have-capitalized =
    { $gender ->
        [male] لديه
        [female] لديها
       *[other] لديه
    }
gender-term-object =
    { $gender ->
        [male] إياه
        [female] إياها
       *[other] إياه
    }
gender-term-possessive-determiner =
    { $gender ->
        [male] الخاص به
        [female] الخاص بها
       *[other] الخاص بهم
    }
gender-term-possessive-determiner-capitalized =
    { $gender ->
        [male] الخاص به
        [female] الخاص بها
       *[other] الخاص بهم
    }
gender-term-possessive-pronoun =
    { $gender ->
        [male] له
        [female] لها
       *[other] لهم
    }
gender-term-reflexive =
    { $gender ->
        [male] نفسه
        [female] نفسها
       *[other] نفسه
    }

action-set-edit = تعيين / تحرير
action-delete = حذف
bio-already-empty = النبذة فارغة بالفعل.
bio-deleted = تم حذف النبذة.
bio-updated = تم تحديث النبذة.

enter-email = أدخل عنوان بريد إلكتروني جديد:
email-updated = تم تحديث عنوان البريد الإلكتروني.
enter-bio = أدخل نبذتك:

gender-updated = تم تحديث الجنس.
no-changes-made = لم يتم إجراء أي تغييرات.
confirm-email-change = هل أنت متأكد أنك تريد تغيير بريدك الإلكتروني إلى { $email }؟

mandatory-email-notice = يجب تعيين بريد إلكتروني لمواصلة المشاركة. بريدك الإلكتروني خاص ولا يعرفه سواك.
error-email-empty = البريد الإلكتروني إلزامي ولا يمكن أن يكون فارغاً.
error-email-invalid = تنسيق البريد الإلكتروني غير صالح. يرجى تقديم عنوان بريد إلكتروني صالح.
reg-error-email = البريد الإلكتروني مطلوب لإنشاء حساب.

error-email-taken = هذا البريد الإلكتروني مستخدَم بالفعل من حساب آخر.

error-bio-length = يجب ألا تتجاوز النبذة 250 حرفاً.
error-captcha-failed = فشل التحقق. يرجى المحاولة مرة أخرى.
error-rate-limit-login = عدد كبير جداً من محاولات تسجيل الدخول الفاشلة. يرجى المحاولة مرة أخرى بعد 15 دقيقة.
error-rate-limit-register = لقد بلغت الحد الأقصى لعدد عمليات إنشاء الحسابات لهذا اليوم.
auth-error-rate-limit = { error-rate-limit-login }

friends-my-friends = أصدقائي
friends-pending-requests = الطلبات المعلّقة ({ $count })
friends-no-pending-requests = الطلبات المعلّقة
friends-sent-requests = { $count ->
    [0] الطلبات المرسَلة
   *[other] الطلبات المرسَلة ({ $count })
}
friends-send-request = إرسال طلب صداقة
friends-block-user = حظر مستخدم
enter-block-username = أدخل اسم مستخدم الشخص الذي تريد حظره:
friends-blocked-users = { $count ->
    [0] المستخدمون المحظورون
   *[other] المستخدمون المحظورون ({ $count })
}
friends-blocked-empty = لم تحظر أحداً.
friends-list-empty = ليس لديك أصدقاء بعد.
friend-status-offline = غير متصل
friend-status-offline-last-online = غير متصل، آخر ظهور { $relative_time }
friend-list-entry = { $username } ({ $status })

view-profile = عرض الملف الشخصي
block-user = حظر مستخدم
unblock-user = إلغاء حظر مستخدم
join-table = الانضمام إلى الطاولة
remove-friend = إزالة صديق
friend-remove-confirm = إزالة { $username } من قائمة أصدقائك؟
friend-remove-not-friends = لم يعد { $username } في قائمة أصدقائك.
already-in-table = أنت بالفعل في هذه الطاولة.
friend-removed-success = تمت إزالة { $username } من قائمة أصدقائك.
friend-removed-notify = أزالك { $username } من قائمة الأصدقاء { GENDER_TERM($username_gender, "possessive-determiner") }.

no-pending-requests = لا توجد طلبات معلّقة.
no-sent-requests = ليس لديك طلبات مرسَلة معلّقة.
friend-request-to = تم إرسال طلب صداقة إلى { $username }
accept = قبول
decline = رفض
friend-accepted-success = أنت الآن صديق لـ { $username }.
friend-accepted-notify = قبل { $username } طلب صداقتك!
request-not-found = لم يعد طلب الصداقة موجوداً.
friend-declined-success = تم رفض طلب الصداقة.
friend-declined-notify = رفض { $username } طلب صداقتك.
friend-request-manage-sent = إدارة طلب الصداقة المرسَل
friend-request-accept-action = قبول طلب الصداقة
friend-request-cancel-action = إلغاء طلب الصداقة
friend-request-cancel-confirm = إلغاء طلب الصداقة المعلّق الخاص بك إلى { $username }؟
friend-request-cancelled = تم إلغاء طلب صداقتك إلى { $username }.
friend-request-cancel-unavailable = لم يعد طلب الصداقة هذا معلّقاً، لذا لم يتم إلغاؤه.

relative-time-just-now = الآن
relative-time-minutes-ago = { $count ->
    [one] قبل دقيقة واحدة
   *[other] قبل { $count } دقيقة
}
relative-time-hours-ago = { $count ->
    [one] قبل ساعة واحدة
   *[other] قبل { $count } ساعة
}
relative-time-days-ago = { $count ->
    [one] قبل يوم واحد
   *[other] قبل { $count } يوم
}
relative-time-weeks-ago = { $count ->
    [one] قبل أسبوع واحد
   *[other] قبل { $count } أسبوع
}
relative-time-months-ago = { $count ->
    [one] قبل شهر واحد
   *[other] قبل { $count } شهر
}
relative-time-years-ago = { $count ->
    [one] قبل سنة واحدة
   *[other] قبل { $count } سنة
}

enter-friend-username = أدخل اسم مستخدم الشخص الذي تريد مصادقته:
friend-error-self = لا يمكنك إرسال طلب صداقة إلى نفسك.
friend-error-already-friends = أنت بالفعل صديق لهذا المستخدم.
friend-error-duplicate = لديك بالفعل طلب صداقة معلّق إلى هذا المستخدم.
friend-error-blocked-by-you = لقد حظرت { $username }. ألغِ حظر { GENDER_TERM($username_gender, "object") } قبل إرسال طلب صداقة.
friend-error-blocked = طلبات الصداقة غير متاحة بينك وبين { $username }.
friend-request-sent = تم إرسال طلب صداقة إلى { $username }.
friend-request-received = لقد تلقيت طلب صداقة جديداً من { $username }.

block-confirm = حظر { $username }؟ يؤدي هذا إلى إزالة أي صداقة وطلبات صداقة معلّقة بينكما. لن يتمكن أي منكما من إرسال طلبات صداقة أو رسائل خاصة أو دعوات طاولة إلى الآخر، وستُخفى رسائل الدردشة العادية في كلا الاتجاهين. وحتى إلغاء الحظر، لا يمكن لأي من المستخدمين الدخول حديثاً إلى طاولة يستضيفها الآخر أو استعادة طاولة محفوظة تحتوي على كليهما. لا يؤدي الحظر إلى إزالة أي منكما من طاولة مشتركة، أو منع استرداد مقعد محجوز، أو كتم الدردشة الصوتية للطاولة.
block-success = لقد حظرت { $username }. أصبح التواصل الاجتماعي المباشر غير متاح بينكما؛ وتُخفى رسائل الدردشة العادية { GENDER_TERM($username_gender, "possessive-determiner") }، ولا يمكن لأي منكما الدخول حديثاً إلى طاولة يستضيفها الآخر أو استعادة طاولة محفوظة تحتوي على كليهما.
block-error-self = لا يمكنك حظر نفسك.
block-already-active = لقد حظرت { $username } بالفعل.
block-no-longer-active = لم يعد هذا الحظر نشطاً.
unblock-success = لقد ألغيت حظر { $username }. لم تتم استعادة الصداقات والطلبات السابقة.

friends-grouped-requests = لديك طلبات صداقة معلّقة من: { $usernames }
friends-grouped-accepted = تم قبول طلبات صداقتك بواسطة: { $usernames }
friends-grouped-declined = تم رفض طلبات صداقتك بواسطة: { $usernames }
friends-grouped-removed = تمت إزالتك من قائمة الأصدقاء بواسطة: { $usernames }
friends-and-others = { $names } و{ $count } { $count ->
    [one] آخر
   *[other] آخرين
}

send-private-message = إرسال رسالة خاصة
enter-pm-message = أدخل رسالتك لـ { $username }:
pm-error-not-friends = يمكنك إرسال رسائل خاصة إلى الأصدقاء فقط.
pm-error-blocked = الرسائل الخاصة غير متاحة بينك وبين هذا المستخدم.
pm-error-offline = { $username } غير متصل حالياً.
pm-error-self = لا يمكنك إرسال رسالة خاصة إلى نفسك.
pm-error-message-required = أدخل رسالة خاصة. عند استخدام الدردشة، ضمّن اسم مستخدم، على سبيل المثال: @User مرحباً.
pm-sent-content = أنت إلى { $username }: { $message }
pm-received = رسالة خاصة من { $username }: { $message }

host-management = إدارة المضيف
table-spectator-suffix = (متفرّج)
host-management-set-private = جعل الطاولة خاصة
host-management-set-public = جعل الطاولة عامة
host-management-invite = دعوة صديق
host-management-voice = إدارة الدردشة الصوتية
host-management-switch-game = التبديل إلى لعبة أخرى
host-management-pass-host = تمرير دور المضيف إلى لاعب آخر
host-management-kick = طرد لاعب
host-management-kick-ban = طرد وحظر لاعب
host-management-player-substitution = استبدال لاعب
host-management-restart-game = إعادة بدء اللعبة
host-management-table-now-private = أصبحت هذه الطاولة خاصة الآن. يمكن للمستخدمين المدعوّين فقط الانضمام.
host-management-table-now-public = أصبحت هذه الطاولة عامة الآن.
host-game-switch-current = اللعبة الحالية: { $game }. تحتوي هذه الطاولة على { $seats } { $seats ->
    [one] مقعد نشط
   *[other] مقاعد نشطة
}. تُدرج فقط الألعاب التي يمكنها استيعاب كل مقعد نشط.
host-game-switch-no-compatible-games = لا توجد لعبة أخرى يمكنها حالياً استيعاب كل { $seats } { $seats ->
    [one] مقعد نشط
   *[other] مقاعد نشطة
}.
host-game-switch-confirm = تبديل هذه الطاولة من { $old_game } إلى { $new_game }؟ سينتقل كل من لا يزال حاضراً إلى ردهة الانتظار الجديدة بالدور نفسه لعباً أو مشاهدةً، وستبقى البوتات. سيتم تجاهل المباراة الحالية أو إعداد الردهة والخيارات والفرق وحالة الاستعداد. ستبقى ملكية الطاولة وخصوصيتها وعمليات الحظر والدردشة الصوتية متصلة. سيتم إلغاء الدعوات المعلّقة للعبة القديمة.
host-game-switch-target-unavailable = لم تعد تلك اللعبة متاحة كهدف للتبديل. لم تتغير أي حالة للطاولة.
host-game-switch-roster-invalid = لم تعد عضوية هذه الطاولة الحية تطابق قائمة لاعبي لعبتها، لذا تم منع تبديل الألعاب لمنع إسقاط أي شخص. عد إلى الطاولة وحاول مرة أخرى بعد تحديث القائمة.
host-game-switch-too-many-seats = لا يمكن التبديل إلى { $game }: فهي تدعم { $max } { $max ->
    [one] مقعد نشط
   *[other] مقاعد نشطة
} كحدّ أقصى، لكن هذه الطاولة تحتاج حالياً إلى { $seats }.
host-game-switch-failed = تعذّر تبديل اللعبة بأمان. تُركت الطاولة واللعبة الحاليتان دون تغيير.
host-game-switch-you = لقد بدّلت هذه الطاولة من { $old_game } إلى { $new_game }. الجميع الآن في ردهة الانتظار الجديدة؛ تبقى الدردشة الصوتية للطاولة متصلة.
host-game-switch-player = بدّل { $player } هذه الطاولة من { $old_game } إلى { $new_game }. الجميع الآن في ردهة الانتظار الجديدة؛ تبقى الدردشة الصوتية للطاولة متصلة.
host-restart-confirm = إعادة بدء اللعبة الحالية وإعادة هذه الطاولة إلى غرفة الانتظار؟ سيبقى اللاعبون الحاليون والدردشة الصوتية متصلين، لكن سيتم إلغاء المباراة الحالية.
host-restart-broadcast = أعاد { $player } بدء اللعبة. عادت الطاولة إلى غرفة الانتظار.
host-restart-you = أعدت بدء اللعبة. عادت الطاولة إلى غرفة الانتظار.
host-restart-not-playing = لا توجد لعبة نشطة لإعادة بدئها.
player-substitution-offer-action = استبدال متفرّج في هذا المقعد
player-substitution-seat-bot = مقعد بوت: { $bot }
player-substitution-seat-replacement = { $bot }، يلعب في المقعد المحجوز لـ { $player }
player-substitution-seat-self = مقعدك: { $player }
player-substitution-seat-player = مقعد لاعب: { $player }
player-substitution-no-seats = (لا توجد مقاعد لاعبين نشطة متاحة)
player-substitution-seat-unavailable = لم يعد مقعد اللاعب ذاك متاحاً للاستبدال. لم يتغير أي دور.
player-substitution-no-spectators = (لا يوجد متفرّجون مؤهّلون متاحون)
player-substitution-spectator-unavailable = لم يعد ذلك المتفرّج متاحاً للاستبدال. لم يتغير أي دور.
player-substitution-user-busy = { $player } يكمل إدخالاً آخر أو عرض حالة. حاول مرة أخرى عندما لا يعود العرض مفتوحاً { GENDER_TERM($player_gender, "possessive-pronoun") }.
player-substitution-game-busy = تكمل اللعبة اختياراً متزامناً أو استرداد طاولة يقفل مؤقتاً استبدالات اللاعبين. حاول مرة أخرى بعد انتهائه.
player-substitution-offer-sent = تم عرض مقعد { $seat } على { $player }. يجب أن يقبل { GENDER_TERM($player_gender, "subject-capitalized") } قبل أن تتغير السيطرة.
player-substitution-self-offer-sent = تم عرض مقعدك على { $player }. إذا قَبِل { GENDER_TERM($player_gender, "subject") } العرض، فستصبح متفرّجاً وتبقى مضيف الطاولة؛ وستُسجَّل النتيجة النهائية للمقعد { GENDER_TERM($player_gender, "possessive-pronoun") }.
player-substitution-self-incoming-consent-sent = طلبتَ من { $player } أن يمنحك المقعد { GENDER_TERM($player_gender, "possessive-determiner") }. إذا قَبِل { GENDER_TERM($player_gender, "subject") } هذا الطلب، فستتولى السيطرة فوراً لأن اختيارك لنفسك أكّد موافقتك بالفعل.
player-substitution-outgoing-consent-sent = طلبتَ من { $player } أن يمنح المقعد { GENDER_TERM($player_gender, "possessive-determiner") } لـ { $substitute }. إذا قَبِل { GENDER_TERM($player_gender, "subject") } هذا الطلب، فيجب أن يقبل { $substitute } أيضاً قبل أن تتغير السيطرة.
player-substitution-offer-pending = { $player } لديه بالفعل طلب استبدال في انتظار الرد.
player-substitution-seat-offer-pending = مقعد { $seat } لديه بالفعل طلب استبدال في انتظار الرد.
player-substitution-self-seat-offer-pending = مقعدك لديه بالفعل طلب استبدال في انتظار الرد.
player-substitution-request-outgoing = يريد { $host } أن يحل { $player } محلّك في مقعدك الحالي. إذا قبلت، فستصبح متفرّجاً وسيتلقى { GENDER_TERM($player_gender, "subject") } حالة لعبتك الدقيقة ومعلوماتك الخاصة ووقت دورك المتبقي ونسبة النتيجة النهائية. لن يُعاد تعيين أي مؤقّت.
player-substitution-request-outgoing-host-incoming = يريد { $host } أن يحل محلّك في مقعدك الحالي. إذا قبلت، فستصبح متفرّجاً وسيتلقى { GENDER_TERM($host_gender, "subject") } حالة لعبتك الدقيقة ومعلوماتك الخاصة ووقت دورك المتبقي ونسبة النتيجة النهائية. لن يُعاد تعيين أي مؤقّت.
player-substitution-request-player = يعرض عليك { $host } مقعد { $player } بالموافقة { GENDER_TERM($player_gender, "possessive-determiner") }. إذا قبلت، فسترث حالة اللعبة الدقيقة للمقعد ومعلوماته الخاصة ووقت الدور المتبقي ونسبة النتيجة النهائية؛ لن يُعاد تعيين أي مؤقّت، وسيصبح { GENDER_TERM($player_gender, "subject") } متفرّجاً.
player-substitution-request-host-seat = يعرض عليك { $host } المقعد { GENDER_TERM($host_gender, "possessive-determiner") }. إذا قبلت، فسترث حالة اللعبة الدقيقة للمقعد ومعلوماته الخاصة ووقت الدور المتبقي ونسبة النتيجة النهائية؛ لن يُعاد تعيين أي مؤقّت، وسيصبح { GENDER_TERM($host_gender, "subject") } متفرّجاً مع بقائه مضيف الطاولة.
player-substitution-request-bot = يعرض عليك { $host } المقعد الذي يتحكم فيه حالياً { $bot }. إذا قبلت، فسترث حالة اللعبة الدقيقة له ومعلوماته الخاصة ووقت الدور المتبقي ونسبة النتيجة النهائية؛ لن يُعاد تعيين أي مؤقّت.
player-substitution-request-replacement = يعرض عليك { $host } المقعد المحجوز لـ { $player }، الذي يتحكم فيه حالياً { $bot }. إذا قبلت، فسترث حالة اللعبة الدقيقة له ومعلوماته الخاصة ووقت الدور المتبقي ونسبة النتيجة النهائية؛ لن يُعاد تعيين أي مؤقّت، ولن يعود { GENDER_TERM($player_gender, "subject") } قادراً على استرداد هذا المقعد.
player-substitution-decline = رفض الاستبدال
player-substitution-accept = قبول الاستبدال
player-substitution-offer-expired = انتهت صلاحية طلب الاستبدال. لم يتغير أي دور.
player-substitution-offer-expired-host = { $player } لم يرد قبل انتهاء صلاحية طلب الاستبدال. لم يتغير أي دور.
player-substitution-offer-declined = رفض { $player } طلب الاستبدال. لم يتغير أي دور.
player-substitution-no-longer-available = لم يعد طلب الاستبدال ذاك متاحاً. لم يتغير أي دور.
player-substitution-awaiting-incoming = { $player } يمكنه الآن قبول الاستبدال أو رفضه. لم يتغير أي دور بعد.
player-substitution-complete-player-you = لقد تولّيت السيطرة على مقعد { $player } السابق. { GENDER_TERM($player_gender, "subject-be-capitalized") } الآن متفرّج.
player-substitution-complete-outgoing-you = تولّى { $player } السيطرة على مقعدك السابق. أنت الآن متفرّج.
player-substitution-complete-player = تولّى { $player } السيطرة على مقعد { $outgoing } السابق. { GENDER_TERM($outgoing_gender, "subject-be-capitalized") } الآن متفرّج.
player-substitution-complete-host-player-you = لقد تولّيت السيطرة على مقعد { $player } السابق. { GENDER_TERM($player_gender, "subject-be-capitalized") } الآن متفرّج، ويبقى دور مضيف الطاولة { GENDER_TERM($player_gender, "possessive-pronoun") }.
player-substitution-complete-outgoing-host-you = تولّى { $player } السيطرة على مقعدك السابق. أنت الآن متفرّج وتبقى مضيف الطاولة.
player-substitution-complete-host = تولّى { $player } السيطرة على مقعد { $outgoing } السابق. { GENDER_TERM($outgoing_gender, "subject-be-capitalized") } الآن متفرّج ويبقى مضيف الطاولة.
player-substitution-complete-bot-you = لقد تولّيت السيطرة على مقعد { $bot }.
player-substitution-complete-bot = تولّى { $player } السيطرة على مقعد { $bot }.
player-substitution-complete-replacement-you = لقد تولّيت السيطرة على المقعد المحجوز لـ { $replaced_player } من { $bot }. انتهى الحجز السابق.
player-substitution-complete-replacement = تولّى { $player } السيطرة على المقعد المحجوز لـ { $replaced_player } من { $bot }. انتهى الحجز السابق.
host-invite-no-friends = (لا يوجد أصدقاء متاحون للدعوة)
host-invite-sent = تم إرسال دعوة إلى { $player }.
host-invite-friend-unavailable = لم يعد ذلك الصديق متاحاً للدعوة.
host-invite-already-pending = توجد دعوة معلّقة بالفعل لذلك الصديق.
host-invite-friend-busy = ذلك الصديق موجود بالفعل في لعبة.
host-invite-pair-cooldown = يرجى الانتظار { $seconds ->
    [one] ثانية واحدة
   *[other] { $seconds } ثانية
} قبل دعوة ذلك الصديق مرة أخرى.
host-invite-rate-limited = أنت ترسل دعوات الطاولة بسرعة كبيرة. حاول مرة أخرى بعد { $seconds ->
    [one] ثانية واحدة
   *[other] { $seconds } ثانية
}.
host-invite-declined = رفض { $player } دعوة طاولتك.
table-invite-received = دعاك { $host } إلى طاولة { $game } { GENDER_TERM($host_gender, "possessive-determiner") }.
table-invite-queued = دعاك { $host } إلى طاولة { $game } { GENDER_TERM($host_gender, "possessive-determiner") }. أنهِ إدخالك الحالي للرد.
table-invite-expired = انتهت صلاحية دعوة الطاولة.
table-invite-no-longer-available = لم تعد دعوة الطاولة تلك متاحة.
invite-accept = قبول الدعوة
invite-decline = رفض الدعوة
host-management-no-longer-host = لم تعد مضيف هذه الطاولة.
host-pass-no-candidates = (لا يوجد لاعبون متاحون لتمرير دور المضيف إليهم)
host-pass-no-longer-host = مرّرت دور المضيف إلى لاعب آخر. لم تعد مضيف هذه الطاولة.
host-passed = { $player } أصبح الآن المضيف.
host-passed-you = أصبحت الآن المضيف.
host-pass-failed = فشل نقل دور المضيف. ربما غادر اللاعب.
host-kick-no-candidates = (لا يوجد لاعبون متاحون للطرد)
host-kick-invalid-target = هدف طرد غير صالح.
host-kick-broadcast = تم طرد { $player } من الطاولة.
host-kick-ban-broadcast = تم طرد وحظر { $player } من الطاولة.
host-kick-confirm = طردت { $player } من الطاولة.
host-kick-ban-confirm = طردت { $player } من الطاولة وحظرته.
host-kick-you = تم طردك من الطاولة بواسطة { $host }.
host-kick-ban-you = تم طردك وحظرك من الطاولة بواسطة { $host }.
table-you-are-banned = أنت محظور من هذه الطاولة.
table-private-invite-only = هذه الطاولة خاصة. يجب أن تتلقى دعوة من المضيف للانضمام.
table-join-social-blocked = لا يمكنك دخول هذه الطاولة لأن التواصل الاجتماعي المباشر غير متاح بينك وبين مضيفها. لا يزال بإمكانك استرداد مقعد محجوز لك بالفعل.

voice-room-table-label = الدردشة الصوتية لطاولة { $game }
voice-unavailable = الدردشة الصوتية غير متاحة الآن.
voice-invalid-context = طلب غرفة الصوت ذاك غير صالح.
voice-not-at-table = لم تنضم إلى طاولة بعد. انضم إلى طاولة قبل بدء الدردشة الصوتية.
voice-not-in-context = يجب أن تكون على تلك الطاولة قبل الانضمام إلى دردشتها الصوتية.
voice-rate-limited = تمهّل. الدردشة الصوتية تتغير بسرعة كبيرة الآن.
voice-muted-seconds = أنت مكتوم ولا يمكنك الانضمام إلى الدردشة الصوتية. متبقٍّ { $seconds } ثانية.
voice-muted-minutes = أنت مكتوم ولا يمكنك الانضمام إلى الدردشة الصوتية. متبقٍّ { $minutes } دقيقة.
voice-muted-permanent = أنت مكتوم ولا يمكنك الانضمام إلى الدردشة الصوتية.
voice-status-connected = { $player } اتصل بالدردشة الصوتية للطاولة.
voice-status-connected-you = اتصلت بالدردشة الصوتية للطاولة.
voice-status-disconnected = { $player } انقطع عن الدردشة الصوتية.
voice-status-disconnected-you = انقطعت عن الدردشة الصوتية.
voice-status-connection-lost = { $player } فقد الاتصال وتمت إزالته من الدردشة الصوتية.
voice-status-connection-lost-you = فقدت الاتصال وتمت إزالتك من الدردشة الصوتية.
voice-status-left-table = { $player } غادر الطاولة وغادر الدردشة الصوتية.
voice-status-left-table-you = غادرت الطاولة وغادرت الدردشة الصوتية.
voice-member-status-connected = متصل بالدردشة الصوتية
voice-member-status-not-connected = غير متصل بالدردشة الصوتية
voice-member-status-host-muted = الميكروفون معطّل بواسطة المضيف
voice-member-status-host-unmuted = مسموح له باستخدام الميكروفون
voice-member-entry = { $player }: { $status }
voice-host-management-no-members = لا يوجد أعضاء طاولة آخرون للإشراف عليهم.
voice-host-target-summary = حالة الصوت لـ { $player }: { $voice_status }؛ { $moderation_status }.
voice-host-mute-action = تعطيل ميكروفون { $player }
voice-host-unmute-action = السماح لـ { $player } باستخدام ميكروفونه
voice-host-cannot-mute-self = لا يمكنك تعطيل ميكروفونك الخاص كمضيف.
voice-host-moderation-rate-limited = إشراف الصوت يتغير بسرعة كبيرة. حاول مرة أخرى بعد { $seconds } ثانية.
voice-host-muted-actor = لقد عطّلت ميكروفون { $player } لهذه الطاولة. لا يزال بإمكانه الاستماع، لكن لا يمكنه بثّ صوت الميكروفون.
voice-host-muted-target = عطّل { $host } ميكروفونك لهذه الطاولة. لا يزال بإمكانك الاستماع، لكن لا يمكنك تشغيل ميكروفونك.
voice-host-muted-observer = عطّل { $host } ميكروفون { $player } لهذه الطاولة.
voice-host-unmuted-actor = سمحت لـ { $player } باستخدام ميكروفونه مرة أخرى. يبقى ميكروفونه مغلقاً حتى يشغّله صراحةً.
voice-host-unmuted-target = سمح لك { $host } باستخدام ميكروفونك مرة أخرى. يبقى ميكروفونك مغلقاً حتى تشغّله صراحةً.
voice-host-unmuted-observer = سمح { $host } لـ { $player } باستخدام ميكروفونه مرة أخرى.
voice-host-unmuted-self = سمحت لنفسك باستخدام الميكروفون مرة أخرى. يبقى مغلقاً حتى تشغّله صراحةً.
voice-personal-settings-action = الإعدادات الصوتية الشخصية
voice-personal-settings-summary = الإعدادات الصوتية الشخصية لـ { $player }: الحجم { $volume } بالمئة؛ { $mute_status }؛ { $connection_status }.
voice-personal-status-muted = مكتوم محلياً
voice-personal-status-unmuted = غير مكتوم محلياً
voice-personal-mute-action = كتم { $player } بالنسبة لي
voice-personal-unmute-action = إلغاء كتم { $player } بالنسبة لي
voice-personal-volume-action = تغيير الحجم الشخصي، حالياً { $volume } بالمئة
voice-personal-volume-choice = { $volume } بالمئة
voice-personal-reset-action = إعادة تعيين الإعدادات الصوتية الشخصية
voice-personal-muted = لقد كتمت { $player } محلياً. أنت وحدك من سيتوقف عن سماعه.
voice-personal-unmuted = لقد ألغيت كتم { $player } محلياً.
voice-personal-volume-set = لقد عيّنت حجم صوت { $player } الشخصي إلى { $volume } بالمئة.
voice-personal-reset = لقد أعدت تعيين إعداداتك الصوتية الشخصية لـ { $player }.
voice-member-left = لم يعد عضو الطاولة ذاك على هذه الطاولة. لم تتغير إعدادات صوت الطاولة المحتفظ بها الخاصة به.
voice-settings-limit-reached = بلغت هذه الطاولة الحد الأقصى الآمن لإعدادات الصوت. لم يتغير أي إعداد.
voice-settings-invalid = إعداد الصوت ذاك غير صالح. لم يتغير أي إعداد.
voice-invalid-participant = مشارك الصوت ذاك غير صالح.
voice-moderation-provider-failed = تعذّر تطبيق إشراف الصوت الآن. لم يتغير أي إعداد؛ يرجى المحاولة مرة أخرى.

error-smtp-not-configured = استرداد كلمة المرور معطّل حالياً بواسطة المسؤول.
error-email-not-found = لم يُعثر على حساب بعنوان البريد الإلكتروني ذاك.
success-reset-email-sent = تم إرسال رمز إعادة التعيين إلى عنوان بريدك الإلكتروني.
error-smtp-send-failed = فشل إرسال بريد إعادة التعيين. يرجى المحاولة لاحقاً.
error-invalid-reset-code = رمز إعادة تعيين غير صالح أو منتهي الصلاحية.
success-password-reset = تمت إعادة تعيين كلمة مرورك بنجاح. يمكنك الآن تسجيل الدخول.
