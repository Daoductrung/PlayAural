# ThÃ´ng bÃ¡o trÃ² chÆ¡i Farkle

# ThÃ´ng tin game
game-name-farkle = Farkle

# HÃ nh Äá»ng - Gieo vÃ  Chá»t
farkle-roll = Gieo { $count } { $count ->
    [one] viÃªn
   *[other] viÃªn
}
farkle-bank = Chá»t { $points } Äiá»m

# HÃ nh Äá»ng chá»n tá» há»£p Äiá»m (khá»p vá»i báº£n v10)
farkle-take-single-one = Láº¥y con 1 láº» ÄÆ°á»£c { $points } Äiá»m
farkle-take-single-five = Láº¥y con 5 láº» ÄÆ°á»£c { $points } Äiá»m
farkle-take-three-kind = Láº¥y bá» ba con { $number } ÄÆ°á»£c { $points } Äiá»m
farkle-take-four-kind = Láº¥y tá»© quÃ½ { $number } ÄÆ°á»£c { $points } Äiá»m
farkle-take-five-kind = Láº¥y ngÅ© quÃ½ { $number } ÄÆ°á»£c { $points } Äiá»m
farkle-take-six-kind = Láº¥y lá»¥c quÃ½ { $number } ÄÆ°á»£c { $points } Äiá»m
farkle-take-small-straight = Láº¥y Sáº£nh nhá» ÄÆ°á»£c { $points } Äiá»m
farkle-take-large-straight = Láº¥y Sáº£nh lá»n ÄÆ°á»£c { $points } Äiá»m
farkle-take-three-pairs = Láº¥y 3 ÄÃ´i ÄÆ°á»£c { $points } Äiá»m
farkle-take-double-triplets = Láº¥y 2 bá» ba ÄÆ°á»£c { $points } Äiá»m
farkle-take-full-house = Láº¥y CÃ¹ lÅ© ÄÆ°á»£c { $points } Äiá»m

# Sá»± kiá»n trong game
farkle-rolls = { $player } gieo { $count } { $count ->
    [one] viÃªn
   *[other] viÃªn
}...
farkle-roll-result = { $dice }
farkle-farkle = CHÃY ÄIá»M! { $player } máº¥t { $points } Äiá»m
farkle-takes-combo = { $player } láº¥y { $combo } ÄÆ°á»£c { $points } Äiá»m
farkle-you-take-combo = Báº¡n láº¥y { $combo } ÄÆ°á»£c { $points } Äiá»m
farkle-hot-dice = Än trá»n! (Hot dice)
farkle-banks = { $player } chá»t { $points } Äiá»m, tá»ng cá»ng cÃ³ { $total }
farkle-winner = { $player } tháº¯ng vá»i { $score } Äiá»m!
farkle-winners-tie = HÃ²a nhau rá»i! Nhá»¯ng ngÆ°á»i tháº¯ng: { $players }

# Kiá»m tra Äiá»m lÆ°á»£t nÃ y
farkle-turn-score = LÆ°á»£t nÃ y { $player } Äang cÃ³ { $points } Äiá»m.
farkle-no-turn = Hiá»n khÃ´ng cÃ³ ai Äang chÆ¡i lÆ°á»£t cá»§a mÃ¬nh.

# TÃ¹y chá»n riÃªng cho Farkle
farkle-set-target-score = Äiá»m má»¥c tiÃªu: { $score }
farkle-enter-target-score = Nháº­p Äiá»m má»¥c tiÃªu (500-5000):
farkle-option-changed-target = Äiá»m má»¥c tiÃªu ÄÃ£ Äáº·t lÃ  { $score }.

# LÃ½ do hÃ nh Äá»ng bá» vÃ´ hiá»u hÃ³a
farkle-must-take-combo = Báº¡n pháº£i chá»n tá» há»£p Än Äiá»m trÆ°á»c.
farkle-cannot-bank = Báº¡n khÃ´ng thá» chá»t Äiá»m lÃºc nÃ y.

# TÃªn tá» há»£p (dÃ¹ng cho thÃ´ng bÃ¡o)
farkle-combo-single-1 = Con 1 láº»
farkle-combo-single-5 = Con 5 láº»
farkle-combo-three-kind = Bá» ba con { $number }
farkle-combo-four-kind = Tá»© quÃ½ { $number }
farkle-combo-five-kind = NgÅ© quÃ½ { $number }
farkle-combo-six-kind = Lá»¥c quÃ½ { $number }
farkle-combo-small-straight = Sáº£nh nhá»
farkle-combo-large-straight = Sáº£nh lá»n
farkle-combo-three-pairs = 3 ÄÃ´i
farkle-combo-double-triplets = 2 bá» ba
farkle-combo-full-house = CÃ¹ lÅ©

# Ð?nh d?ng
farkle-line-format = {  }. {  }: {  }
farkle-combo-fallback = {  } du?c {  } di?m
