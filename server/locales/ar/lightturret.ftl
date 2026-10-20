game-name-lightturret = البرج الضوئي

lightturret-intro = يبدأ البرج الضوئي بسعة طاقة { $power } و{ $rounds } جولات كاملة. أطلق النار لاكتساب الضوء وضعف عدده من العملات. يحدث التحميل الزائد للبرج فقط عندما يتجاوز الضوء الطاقة. تكلّف ترقية النواة { $cost } عملة وقد تأتي بنتائج عكسية.
lightturret-intro-brief = البرج الضوئي: طاقة { $power }، { $rounds } جولة، الترقيات { $cost } عملة.
lightturret-round-start = تبدأ الجولة { $round } من { $total } بـ { $alive } { $alive ->
    [one] برج مدفعي نشط
    [two] برجين مدفعيين نشطين
    [few] أبراج مدفعية نشطة
    [many] برجًا مدفعيًا نشطًا
   *[other] برج مدفعي نشط
}.
lightturret-round-start-brief = الجولة { $round }/{ $total }. النشطة: { $alive }.

lightturret-shoot = إطلاق نار البرج
lightturret-shoot-safe-label = إطلاق نار البرج؛ { $headroom } سعة آمنة
lightturret-shoot-risk-label = إطلاق نار البرج؛ { $risk }% خطر تحميل زائد
lightturret-upgrade = ترقية النواة
lightturret-upgrade-label = ترقية النواة؛ تكلّف { $cost } عملة، لديك { $coins }
lightturret-check-stats = عرض حالة البرج

lightturret-you-shoot = تطلق النار وتكسب { $gain } ضوءًا بالإضافة إلى { $coins } عملة. برجك عند { $light } من { $power } طاقة، مع { $headroom } سعة آمنة و{ $total_coins } عملة.
lightturret-player-shoots = يطلق { $player } النار ويكسب { $gain } ضوءًا بالإضافة إلى { $coins } عملة. برج { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } عند { $light } من { $power } طاقة، مع { $headroom } سعة آمنة و{ $total_coins } عملة.
lightturret-you-shoot-brief = تطلق النار: ‎+{ $gain } ضوء، ‎+{ $coins } عملة. الضوء { $light }/{ $power}؛ العملات { $total_coins }.
lightturret-player-shoots-brief = يطلق { $player } النار: ‎+{ $gain } ضوء، ‎+{ $coins } عملة. الضوء { $light }/{ $power}؛ العملات { $total_coins }.

lightturret-you-shoot-overload = تطلق النار وتكسب { $gain } ضوءًا بالإضافة إلى { $coins } عملة، لتصل إلى { $light } ضوء مقابل { $power } طاقة. تتجاوز السعة بمقدار { $overload } ويتم إقصاؤك مع بقاء { $total_coins } عملة.
lightturret-player-shoots-overload = يطلق { $player } النار ويكسب { $gain } ضوءًا بالإضافة إلى { $coins } عملة، ليصل إلى { $light } ضوء مقابل { $power } طاقة. يرفع التحميل الزائد { GENDER_TERM($player_gender, "object") } بمقدار { $overload } فوق السعة ويقصي { GENDER_TERM($player_gender, "object") } مع بقاء { $total_coins } عملة.
lightturret-you-shoot-overload-brief = تحميل زائد لديك: ‎+{ $gain } ضوء، { $light }/{ $power}، تجاوز بمقدار { $overload}. أُقصيت.
lightturret-player-shoots-overload-brief = تحميل زائد لـ { $player }: ‎+{ $gain } ضوء، { $light }/{ $power}، تجاوز بمقدار { $overload}. أُقصي.

lightturret-you-upgrade = تنفق { $cost } عملة وترقّي النواة بمقدار { $gain } طاقة. برجك الآن عند { $light } ضوء، { $power } طاقة، { $headroom } سعة آمنة، و{ $coins } عملة.
lightturret-player-upgrades = ينفق { $player } { $cost } عملة ويرقّي النواة بمقدار { $gain } طاقة. برج { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } الآن عند { $light } ضوء، { $power } طاقة، { $headroom } سعة آمنة، و{ $coins } عملة.
lightturret-you-upgrade-brief = ترقية: ‎+{ $gain } طاقة. الضوء { $light }/{ $power}؛ العملات { $coins }.
lightturret-player-upgrades-brief = يرقّي { $player }: ‎+{ $gain } طاقة. الضوء { $light }/{ $power}؛ العملات { $coins }.

lightturret-you-upgrade-accident = تنفق { $cost } عملة، لكن النواة تأتي بنتيجة عكسية وتضيف { $gain } ضوءًا. برجك عند { $light } من { $power } طاقة، مع { $headroom } سعة آمنة و{ $coins } عملة.
lightturret-player-upgrades-accident = ينفق { $player } { $cost } عملة، لكن النواة تأتي بنتيجة عكسية وتضيف { $gain } ضوءًا. برج { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } عند { $light } من { $power } طاقة، مع { $headroom } سعة آمنة و{ $coins } عملة.
lightturret-you-upgrade-accident-brief = ترقيتك جاءت بنتيجة عكسية: ‎+{ $gain } ضوء. الضوء { $light }/{ $power}؛ العملات { $coins }.
lightturret-player-upgrades-accident-brief = ترقية { $player } جاءت بنتيجة عكسية: ‎+{ $gain } ضوء. الضوء { $light }/{ $power}؛ العملات { $coins }.

lightturret-you-upgrade-overload = تنفق { $cost } عملة، لكن النواة تأتي بنتيجة عكسية وتضيف { $gain } ضوءًا. تصل إلى { $light } ضوء مقابل { $power } طاقة، وتتجاوز السعة بمقدار { $overload }، ويتم إقصاؤك مع بقاء { $coins } عملة.
lightturret-player-upgrades-overload = ينفق { $player } { $cost } عملة، لكن النواة تأتي بنتيجة عكسية وتضيف { $gain } ضوءًا. ترفع النتيجة العكسية { GENDER_TERM($player_gender, "object") } إلى { $light } ضوء مقابل { $power } طاقة، { $overload } فوق السعة، وتقصي { GENDER_TERM($player_gender, "object") } مع بقاء { $coins } عملة.
lightturret-you-upgrade-overload-brief = تحميل زائد من الترقية: ‎+{ $gain } ضوء، { $light }/{ $power}، تجاوز بمقدار { $overload}. أُقصيت.
lightturret-player-upgrades-overload-brief = تحميل زائد من ترقية { $player }: ‎+{ $gain } ضوء، { $light }/{ $power}، تجاوز بمقدار { $overload}. أُقصي.

lightturret-action-resolving = إجراء برجك قيد التنفيذ بالفعل. انتظر حتى ينتهي صوته ونتيجته.
lightturret-not-enough-coins = تحتاج إلى { $need } عملة لترقية النواة، لكن لديك { $have }.
lightturret-you-are-eliminated = تعرّض برجك لتحميل زائد وتم إقصاؤك، لذا لا يمكنك القيام بإجراء آخر.
lightturret-confirm-risky-shot = الإطلاق الآن يحمل خطر تحميل زائد بنسبة { $risk }% عند { $light } ضوء و{ $power } طاقة. أطلق النار مجددًا خلال { $seconds } ثانية للتأكيد.

lightturret-status-round = الجولة { $round } من { $total }. الأبراج النشطة: { $alive }.
lightturret-stats-alive = { $player}: { $light } ضوء، { $power } طاقة، { $headroom } سعة آمنة، { $coins } عملة، خطر التحميل الزائد للطلقة التالية { $risk }%.
lightturret-stats-eliminated = { $player}: أُقصي عند { $light } ضوء مقابل { $power } طاقة.

lightturret-end-max-rounds = اكتملت جميع الجولات الـ { $total }. مجاميع الضوء النهائية تحدد الفائز.
lightturret-end-max-rounds-brief = اكتملت { $total } جولة.
lightturret-end-all-eliminated = تعرّضت جميع الأبراج لتحميل زائد خلال الجولة { $round }. مجاميع الضوء النهائية تحدد الفائز.
lightturret-end-all-eliminated-brief = تعرّضت جميع الأبراج لتحميل زائد في الجولة { $round }.

lightturret-you-win = تفوز بـ { $light } ضوء و{ $power } طاقة. { $survived ->
    [true] نجا برجك.
   *[false] مجموع ضوئك النهائي في الصدارة رغم التحميل الزائد.
}
lightturret-player-wins = يفوز { $player } بـ { $light } ضوء و{ $power } طاقة. { $survived ->
    [true] نجا برج { GENDER_TERM($player_gender, "possessive-determiner-capitalized") }.
   *[false] مجموع ضوء { GENDER_TERM($player_gender, "possessive-determiner-capitalized") } النهائي في الصدارة رغم التحميل الزائد.
}
lightturret-you-win-brief = تفوز: { $light } ضوء.
lightturret-player-wins-brief = يفوز { $player }: { $light } ضوء.
lightturret-you-tie = تتعادل على المركز الأول مع { $players } عند { $light } ضوء.
lightturret-players-tie = يتعادل { $players } على المركز الأول عند { $light } ضوء.
lightturret-you-tie-brief = تتعادل مع { $players}: { $light } ضوء.
lightturret-players-tie-brief = تعادل: { $players}، { $light } ضوء.

lightturret-set-starting-power = الطاقة الابتدائية: { $power }
lightturret-enter-starting-power = أدخل الطاقة الابتدائية:
lightturret-option-changed-power = تم ضبط الطاقة الابتدائية على { $power }.
lightturret-desc-starting-power = سعة التحميل الزائد الأولية لكل برج. الضوء المساوي للطاقة آمن؛ فقط الضوء الذي يفوق الطاقة يسبب التحميل الزائد (الافتراضي 10، النطاق 5-30).
lightturret-set-max-rounds = أقصى عدد للجولات: { $rounds }
lightturret-enter-max-rounds = أدخل أقصى عدد للجولات:
lightturret-option-changed-rounds = تم ضبط أقصى عدد للجولات على { $rounds }.
lightturret-desc-max-rounds = عدد الجولات الكاملة. يحصل كل برج نشط على دور واحد في الجولة الأخيرة (الافتراضي 50، النطاق 10-200).
lightturret-error-starting-power-invalid = يجب أن تكون الطاقة الابتدائية بين { $min } و{ $max }؛ القيمة الحالية هي { $power }.
lightturret-error-max-rounds-invalid = يجب أن يكون أقصى عدد للجولات بين { $min } و{ $max }؛ القيمة الحالية هي { $rounds }.

lightturret-status-survived = نشط
lightturret-status-eliminated = مُقصى
lightturret-end-winner = الفائز: { $player } بـ { $light } ضوء.
lightturret-end-tie = تعادل على المركز الأول: { $players } بـ { $light } ضوء.
lightturret-line-format = { $rank }. { $player}: { $light } ضوء، { $power } طاقة، { $coins } عملة، { $status }
