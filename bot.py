import asyncio
import logging
import sqlite3
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ════════════════════════════════════════════════
#  НАСТРОЙКИ
# ════════════════════════════════════════════════

BOT_TOKEN  = "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"
CHANNEL_ID = "@it_iz_tinder"
ADMIN_ID   = 309001267

# ════════════════════════════════════════════════
#  ВОРОНКА
# ════════════════════════════════════════════════

U = "?utm_source=bot&utm_medium=drip&utm_campaign=free_course&utm_content="

DRIP_MESSAGES = [
    # ───────────────────────────── 1. ПРИВЕТСТВИЕ (0)
    {
        "delay": 0,
        "video_note": "DQACAgIAAxkBAAO0ahVEJrfi2tOpCClQD0xjXYMUviwAApxzAAKBtYFJITnTJiotmZI7BA",
        "text": (
            "<b>😎 Ты попал туда, где твоя жизнь на сайтах знакомств реально изменится.</b>\n\n"
            "Представь: у тебя гора лайков, тебе пишут сами девушки. Ты зовешь их на свидания, "
            "и быстро себе находишь подходящую девушку либо для секса, либо для отношений.\n\n"
            "У меня есть четкая пошаговая система, как это сделать.\n\n"
            "Причем бесплатно!\n\n"
            "Чтобы ты не ныл в подушку от одиночества, а кайфовал от реальных результатов.\n\n"
            "Кстати, ты знал, что необязательно специально заинтересовывать девушек? "
            "За тебя это сделает правильно оформленная анкета. С урока про анкету я и начинаю этот бесплатный курс.\n\n"
            "👇 Жми кнопку ниже. Рекомендую начинать с 1 урока (зря я писал блять что ли?) 👇\n\n"
            "(Если сайт не открывается, включи VPN)"
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("📋 Урок 1 — Анкета",      f"https://dating-it.ru/kurs-anketa/{U}msg1_lesson1"),
            ("💬 Урок 2 — Переписки",   f"https://dating-it.ru/kurs-perepiski/{U}msg1_lesson2"),
            ("☕ Урок 3 — Свидания",    f"https://dating-it.ru/kurs-svidaniya/{U}msg1_lesson3"),
            ("🔥 Урок 4 — Соблазнение", f"https://dating-it.ru/kurs-soblaznenie/{U}msg1_lesson4"),
        ],
    },

    # ───────────────────────────── 2. БОЛЬ + ИСТОРИЯ (+2 дня)
    # БЫЛО: сразу биография «почему я этим занимаюсь».
    # СТАЛО: сначала узнавание боли, потом история как доказательство, что чинится.
    {
        "delay": 172800,
        "photo": "AgACAgIAAxkBAAOyahVAga4yUXrcAZAhMtc7WuPGyaQAAo8daxvpmKhIXOAmh9WAPgcBAAMCAAN5AAM7BA",
        "text": (
            "<b>Знакомо?</b>\n\n"
            "Ты листаешь ленту вечером. Лайкаешь. Мэтчей мало, а те что есть - сливаются на пятом сообщении.\n\n"
            "Или еще хуже: договорились о встрече, ты весь день ждал свидания — а за пару часов «прости, планы поменялись».\n\n"
            "И ты сидишь и не понимаешь: вроде нормальный мужик, работа есть, не урод. А результата ноль. "
            "Зато видишь, как какой-то чувак страшнее тебя идет по улице с симпатичной девочкой.\n\n"
            "<b>Я начинал ровно так же.</b>\n\n"
            "В 2020 меня бросила девушка. После долгих мучений зарегался в тиндере и баду. Иногда даже доходило до свидания.\n\n"
            "Но девушки сливались одна за другой. За первые несколько месяцев практики у меня не было даже поцелуев.\n\n"
            "Потом я включил мозг и начал изучать всю доступную инфу. Тестировал заходы в переписках, флиртовые фишки, "
            "много придумывал сам. И в какой-то момент щелкнуло — я понял, что это просто система, которую можно разобрать по частям.\n\n"
            "Дошел до успеха с девушками, их стало бесчисленное количество в моей жизни (и не только с сайтов знакомств).\n\n"
            "Сейчас у меня <b>600+ учеников и 160+ реальных отзывов.</b> Многие уже нагулялись и ушли в отношения, некоторые женились.\n\n"
            "Я не пропагандирую пикаперский образ жизни. Хочешь трахайся, хочешь живи с одной. Главное чтобы тебе было заебись.\n\n"
            "Подробно про мой путь → https://dating-it.ru/biography/\n"
            "160+ отзывов → https://t.me/it_iz_tinder_otzyv\n"
            "Куча моих переписок и топового контента → https://teletype.in/@it_iz_tinder/spisok-postov"
        ),
        "buttons": [
            ("📚 Все мои материалы со скидкой", f"https://dating-it.ru/complete/{U}msg2_complete"),
            ("✍️ Написать мне лично", "https://t.me/it_iz_tinder_support"),
        ],
        "parse_mode": "HTML",
    },

    # ───────────────────────────── 3. НОВОЕ: ЧЕК-ЛИСТ АНКЕТЫ + МОСТ НА РАЗБОР (+2 дня)
    {
        "delay": 172800,
        "text": (
            "<b>📱 Проверь свою анкету за 30 секунд</b>\n\n"
            "Девушка открывает ленту. На твою анкету у нее — полсекунды. Свайп. Следующий.\n\n"
            "И вот что обидно: чаще всего дело не в лице. Дело в косяках, которые ты сам НЕ ВИДИШЬ.\n\n"
            "Пройдись по чек-листу прямо сейчас:\n\n"
            "1️⃣ Первая фотка — четкая, без очков, без компании друзей, видно лицо\n"
            "2️⃣ Есть хотя бы одна фотка в полный рост\n"
            "3️⃣ Нет селфи в лифте, фоток с рыбой и голого торса в зеркале\n"
            "4️⃣ В описании есть конкретика и зацепки для диалога, а не «ищу простую девушку»\n"
            "5️⃣ Нет негатива и требований («без фото не пишу», «содержанок мимо»)\n\n"
            "Прошел все пять? Красавчик. Но вот подстава: <b>даже с идеальным чек-листом свою анкету "
            "объективно оценить почти невозможно.</b>\n\n"
            "Ты смотришь на свои фотки глазами себя: «ну нормальная же фотка». А девушки смотрят совсем другими глазами. "
            "Я это вижу каждую неделю — парни присылают «идеальные» анкеты, а там 3 отталкивающих косяка в первых двух фотках.\n\n"
            "Если хочешь разобраться сам — вот <a href=\"https://dating-it.ru/kurs-anketa/" + U + "msg3_lesson\">первый урок курса</a>, там подробно.\n\n"
            "А если хочешь, чтобы я лично посмотрел твою анкету глазами девушки и сказал, что менять — жми вторую кнопку. "
            "Это платно, но дешевле, чем еще полгода сидеть без лайков."
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("📋 Урок про анкету (бесплатно)", f"https://dating-it.ru/kurs-anketa/{U}msg3_lesson"),
            ("🔍 Разбор моей анкеты — от 2 500 ₽", f"https://dating-it.ru/razbor-ankety/{U}msg3_service"),
        ],
    },

    # ───────────────────────────── 4. РОМАНТИЧЕСКОЕ РУСЛО (+2 дня)
    {
        "delay": 172800,
        "text": (
            "<b>😎 Как легко перевести общение в романтическое/сексуальное русло?</b>\n\n"
            "Чем дольше ты общаешься с девчонкой на нейтральные темы, тем больше шанс, что у тебя с ней не будет ни секса, ни отношений. "
            "Она думает, что она тебе не интересна, как девушка.\n\n"
            "А если у вас официальное свидание (например, с сайта знакомств), то ты будешь выглядеть странным чуваком, который непонятно зачем ее позвал.\n\n"
            "То ли тебе просто скучно, то ли ищешь просто подругу для общения.\n\n"
            "У девушки в башке диссонанс и она отмораживается от тебя. Второго свидания нет (знакомо, да?).\n\n"
            "Дам три способа наконец вытянуть дружеский диалог в другое русло:\n\n"
            "1⃣ Комплименты с подтекстом\n\n"
            "- \"У тебя красивое платье\" - ХУЙНЯ ⛔\n"
            "- \"Твое платье так облегает, что прям всё видно. Мне нравится\" - ЗАЕБИСЬ ✅\n\n"
            "- \"У тебя классное чувство юмора\" - ХУЙНЯ ⛔\n"
            "- \"Честно говоря меня возбуждают девушки с таким чувством юмора, как у тебя. Ничего не могу с собой поделать\" - ЗАЕБИСЬ ✅\n\n"
            "2⃣ Переворот фрейма\n\n"
            "Делать только если уже есть несколько признаков заинтересованности от девушки, иначе будешь выглядеть глупо! И не забывать подавать с улыбкой.\n\n"
            "(когда вы сидите в заведении)\n"
            "- \"Тут, кстати, чистый туалет. Но это не намек! Не надо меня туда вести насиловать, я еще не готов к такому)\"\n\n"
            "(она тебя дотронулась во время общения)\n"
            "- \"Воу воу осторожнее, я тебя еще мало знаю, не нужно меня лапать\"\n\n"
            "3⃣ Вопросы на тему взаимоотношений М/Ж\n\n"
            "🔹 Какие качества тебе важны в мужчине?\n"
            "🔹 Легко ли ты влюбляешься?\n"
            "🔹 Ты веришь в дружбу между мужчиной и женщиной?\n"
            "🔹 Как думаешь, в мужчине важнее интеллект или внешность?\n\n"
            "Кстати, в более интимные вопросы можно заходить двумя простыми способами.\n\n"
            "Всё, что я описал выше - это флирт. И если у тебя постоянно мысль \"я не умею флиртовать\", то мой большой "
            "\"Учебник по флирту\" создан для тебя. Там гора примеров, формул и шаблонов - и для переписок, и вживую.\n\n"
            "Парням реально это помогает, отзывов дохрена.\n\n"
            "👇 Узнай подробнее по кнопке ниже"
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("📚 Учебник по флирту", f"https://dating-it.ru/uchebnik-po-flirtu/{U}msg4_flirt"),
        ],
    },

    # ───────────────────────────── 5. НОВОЕ: ГДЕ ЛОМАЕТСЯ ПЕРЕПИСКА + МОСТ НА РАЗБОР (+2 дня)
    {
        "delay": 172800,
        "text": (
            "<b>🔍 Это не девушка необщительная, а ты где-то накосячил в переписке</b>\n\n"
            "Каждую неделю мне присылают переписки с одним и тем же вопросом: «что я сделал не так?»\n\n"
            "Отвечала быстро, смеялась, смайлики. Потом пропадает. Или отвечает, но сухо, и позвать на встречу никак не выходит. "
            "Или договорились о свидании, а за день она «заболела» и пропала.\n\n"
            "Парень перечитывает диалог десятый раз и не видит косяка. Друзья говорят - забей хуй.\n\n"
            "<b>А я открываю переписку и за пару минут вижу конкретное сообщение, после которого ее интерес пошел вниз.</b>\n\n"
            "Это огромный опыт. И плюс со стороны видно то, что изнутри не видно НИКОГДА. Ты читаешь свою переписку глазами себя. "
            "А надо — глазами девушки. Или опытного соблазнителя.\n\n"
            "Три самых частых косяка, которые я вижу:\n\n"
            "1️⃣ <b>Завал баланса</b> — отвечаешь мгновенно, пишешь больше нее, закидываешь незаслуженными комплиментами\n"
            "2️⃣ <b>Допрос</b> — хаотичные вопросы вместо диалога, ноль флирта, скукотища\n"
            "3️⃣ <b>Затянутая дружеская волна</b> — чем дольше общаетесь «ни о чем», тем сложнее с нее слезть\n\n"
            "Если хочешь разобрать конкретно СВОЮ переписку — присылай. Я дам голосовой разбор: где именно ты потерял ее интерес, "
            "3 главные ошибки и что писать дальше. Тет-а-тет, без публикации в канале, за 24 часа.\n\n"
            "1 900 ₽. Дешевле, чем повторять косяки раз разом и тратить время на девушек, которые все равно сольются."
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("💬 Разбор моей переписки — 1 900 ₽", f"https://dating-it.ru/razbor-perepiski/{U}msg6_service"),
            ("📗 Методичка по перепискам", f"https://dating-it.ru/metodichka-idealnye-perepiski/{U}msg6_book"),
        ],
    },

    # ───────────────────────────── 6. ЖЕНСКИЕ ПРОВЕРКИ (+2 дня)
    {
        "delay": 172800,
        "text": (
            "<b>👉 Разбор частых женских проверок на свидании</b>\n\n"
            "Проверки - способ протестировать тебя на адекватность, настойчивость, ресурсность и социальный статус.\n\n"
            "Поэтому если ты не умеешь проходить проверки, то твой питон уже заждался твоих удушивающих приемов.\n\n"
            "Главное быть спокойным. Если ты занервничал и сорвался - ты проиграл.\n\n"
            "⬇ Даю несколько примеров женских проверок и их обходов (в скобках альтернативный обход):\n\n"
            "Проверка: \"Сколько ты зарабатываешь?\"\n"
            "Ответ: \"Мне хватает, а вообще это странный вопрос для свидания\" (\"10 тысяч в месяц, сегодня купил дошик, поел и доволен, большего мне и надо\")\n\n"
            "Проверка: \"Ты наверное постоянно так по свиданиям ходишь\"\n"
            "Ответ: \"Нет, у меня нет времени на пустые свидания, поэтому редко хожу\" (\"Да, назначаю по 10 свиданий в день и провожу в виде собеседования. Кстати, следующая!\").\n\n"
            "Проверка: \"Я не поеду к тебе домой, ты просто хочешь меня трахнуть!\"\n"
            "Ответ: \"Для меня общая волна и классное общение на первом месте. Без этого всего секс для меня не интересен. "
            "Поэтому только если мы ОБА этого захотим, то он будет. А так я тебя зову просто пообщаться.\"\n\n"
            "(\"В смысле трахнуть? Я девственник в седьмом поколении. А ты вот похожа на извращенку, поэтому если что я буду держать наготове баллончик. "
            "Не для тебя розочка цвела, поняла?!\")\n\n"
            "Можно проходить проверки логикой, но и вариант переворачивать фрейм, преувеличивать и отшучиваться. "
            "Главное делать это с улыбкой, а не с серьезным ебальником.\n\n"
            "Если ты хочешь больше таких фраз и стратегий - забирай методичку «Идеальные свидания». В ней всё, чтобы ты чувствовал себя на свидании как дома. Жми кнопку 👇"
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("🗓 Идеальные свидания", f"https://dating-it.ru/kurs-idealnye-svidaniya/{U}msg7_book"),
        ],
    },

    # ───────────────────────────── 7. ФИНАЛ: КОМПЛЕКТ (+2 дня)
    # БЫЛО: бандл переписок 5900. СТАЛО: полный комплект 25 000 (экономия 10 800).
    {
        "delay": 172800,
        "text": (
            "<b>Последнее письмо из этой серии. Но не последнее по важности</b>\n\n"
            "За эти дни ты получил от меня 4 урока курса, чек-лист анкеты, приемы перевода общения в романтическое русло, "
            "разбор женских проверок и три главных косяка в переписках.\n\n"
            "Если внедрил — уже должно быть заметно. Если нет — вернись и внедри, это бесплатно и работает.\n\n"
            "Но вот честный момент. Знакомства — это воронка, как в продажах:\n\n"
            "<b>мертвая анкета → нет лайков → нет переписок → нет свиданий → нет секса</b>\n\n"
            "Если где-то узкое место — всё проебывается. Можно идеально научиться переписываться и упереться в то, "
            "что анкета не дает мэтчей. Или довести до свидания и слить, потому что не разобрался в эскалации.\n\n"
            "Поэтому я собрал <b>полный комплект</b>: 9 методичек и учебников, которые я писал 4 года. Плюс три бонуса, "
            "которых нет в отдельной продаже (мастер-класс «Антислив», методичка «Соблазнение у тебя дома» и месяц VIP-канала).\n\n"
            "Закрыт каждый этап: анкета, переписки, флирт, юмор, легкое общение, свидания, секс, психология влечения.\n\n"
            "<s>35 800 ₽</s> по отдельности → <b>25 000 ₽ в комплекте</b>\n"
            "Экономия 10 800 ₽ — это как три методички в подарок.\n\n"
            "👉 https://dating-it.ru/complete/\n\n"
            "Если комплект пока много — возьми одну методичку под свою проблему, это тоже нормальный путь. "
            "Все материалы тут → https://dating-it.ru/about/\n\n"
            "160+ отзывов → https://dating-it.ru/otzivy/"
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("🎁 Полный комплект — 25 000 ₽", f"https://dating-it.ru/complete/{U}msg8_complete"),
            ("📹 Бесплатное видео про воронку", "https://youtu.be/WdaLWGz-CjY"),
            ("⭐ Отзывы", f"https://dating-it.ru/otzivy/{U}msg8_reviews"),
        ],
    },

    # ───────────────────────────── 8. РЕАКТИВАЦИЯ №1 (+21 день)
    {
        "delay": 1814400,
        "text": (
            "👋 <b>Давно не виделись</b>\n\n"
            "Ты читал мой бесплатный курс три недели назад. Хочу спросить прямо, что изменилось?\n\n"
            "Если ответ \"ничего\" - напиши мне, разберемся где затык. https://t.me/it_iz_tinder_support\n\n"
            "Если читал, но не применял - это абсолютли нормал. Большинство парней застревают не на знаниях, а на первом шаге. "
            "Поэтому у меня есть один материал, который конкретно с этим помогает.\n\n"
            "Читаешь за 20 минут, берешь одну технику, пробуешь прям сегодня.\n"
            "👉 <a href=\"https://dating-it.ru/uchebnik-legkoe-obschenie/" + U + "msg9_book\">Учебник по лёгкому общению</a> — "
            "там самый низкий порог входа из всего что у меня есть. Подойдет и для переписок и для живого общения.\n\n"
            "Если уже что-то попробовал и получилось - напиши мне, реально интересно. Такие истории иногда выкладываю в канал (с разрешения).\n\n"
            "С уважением, твой Айтишник"
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("📖 Учебник по лёгкому общению", f"https://dating-it.ru/uchebnik-legkoe-obschenie/{U}msg9_book"),
            ("✍️ Написать Артему", "https://t.me/it_iz_tinder_support"),
        ],
    },

    # ───────────────────────────── 9. НОВОЕ: РЕАКТИВАЦИЯ №2 (+60 дней от предыдущего)
    # Другой угол: не «купи», а «сделай за тебя». Ловит тех, кто не готов разбираться сам.
    {
        "delay": 5184000,
        "text": (
            "<b>Прошло пара месяцев. Как оно?</b>\n\n"
            "Если у тебя за это время что-то поменялось — реально рад, напиши, интересно почитать.\n\n"
            "А если всё там же — скажу честно, без продажи. За 5 лет и 600+ учеников я вижу одну закономерность.\n\n"
            "<b>Есть парни, которые читают материалы и у них щелкает.</b> Пошли внедрять, через месяц скидывают скрины свиданий.\n\n"
            "<b>А есть те, кто всё понял, со всем согласен... и в реальной переписке снова пишет как раньше.</b> "
            "Потому что когда ОНА отвечает что-то неожиданное — теория вылетает из головы.\n\n"
            "Это не тупость и не лень. Навык не ставится чтением. Он ставится, когда кто-то смотрит на твои РЕАЛЬНЫЕ "
            "действия и говорит: «стоп, вот здесь ты сейчас всё сломаешь, пиши вот так».\n\n"
            "В зале это решает тренер. В английском — препод. В знакомствах — обычно никто.\n\n"
            "Если узнал себя, у меня есть форматы, где я смотрю лично:\n\n"
            "▪️ <b>Разбор анкеты</b> — от 2 500 ₽. Скажу, что отталкивает девушек, или соберу анкету за тебя\n"
            "▪️ <b>Разбор переписки</b> — 1 900 ₽. Найду место, где ты теряешь ее интерес\n"
            "▪️ <b>Сопровождение</b> — от 9 000 ₽/мес. Разбираю твои живые диалоги дважды в неделю, веду до свиданий\n\n"
            "Не уверен, что тебе нужно — просто напиши мне, спрошу пару вопросов и скажу честно. "
            "Иногда отвечаю «тебе ничего покупать не надо, поправь вот это».\n\n"
            "С уважением, твой Айтишник"
        ),
        "parse_mode": "HTML",
        "buttons": [
            ("🔍 Разбор анкеты", f"https://dating-it.ru/razbor-ankety/{U}msg10_anketa"),
            ("💬 Разбор переписки", f"https://dating-it.ru/razbor-perepiski/{U}msg10_perepiska"),
            ("✍️ Спросить у Артема", "https://t.me/it_iz_tinder_support"),
        ],
    },
]

# ════════════════════════════════════════════════
#  БАЗА ДАННЫХ
# ════════════════════════════════════════════════

def db_init():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY,
            username  TEXT,
            step      INTEGER DEFAULT 0,
            step_at   REAL DEFAULT 0,
            done      INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Добавляем колонки если базы обновляются со старой версии
    for col in [("step", "INTEGER DEFAULT 0"), ("step_at", "REAL DEFAULT 0"), ("done", "INTEGER DEFAULT 0"), ("segment", "TEXT DEFAULT ''")]:
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col[0]} {col[1]}")
        except:
            pass
    conn.commit()
    conn.close()

def db_add_user(user_id: int, username: str):
    conn = sqlite3.connect("users.db")
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username, step, step_at, done) VALUES (?, ?, 0, ?, 0)",
        (user_id, username, time.time())
    )
    conn.commit()
    conn.close()

def db_set_step(user_id: int, step: int):
    conn = sqlite3.connect("users.db")
    conn.execute(
        "UPDATE users SET step=?, step_at=? WHERE user_id=?",
        (step, time.time(), user_id)
    )
    conn.commit()
    conn.close()

def db_set_done(user_id: int):
    conn = sqlite3.connect("users.db")
    conn.execute("UPDATE users SET done=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def db_get_active() -> list[dict]:
    """Возвращает всех пользователей у кого воронка не завершена."""
    conn = sqlite3.connect("users.db")
    rows = conn.execute(
        "SELECT user_id, step, step_at FROM users WHERE done=0"
    ).fetchall()
    conn.close()
    return [{"user_id": r[0], "step": r[1], "step_at": r[2]} for r in rows]

def db_get_all_users() -> list[int]:
    conn = sqlite3.connect("users.db")
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [row[0] for row in rows]

def db_count_users() -> int:
    conn = sqlite3.connect("users.db")
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count

def db_remove_user(user_id: int):
    conn = sqlite3.connect("users.db")
    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# ════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()
active_campaigns: dict[int, asyncio.Task] = {}


def make_kb(buttons: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=url)] for text, url in buttons
    ])

def kb_subscribe():
    channel = CHANNEL_ID.lstrip("@")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{channel}")],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
    ])

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

async def run_drip(user_id: int, start_step: int = 0, first_delay: float = 0):
    """
    Запускает воронку с нужного шага.
    first_delay — сколько секунд осталось ждать до следующего шага (при восстановлении).
    """
    try:
        for i in range(start_step, len(DRIP_MESSAGES)):
            msg = DRIP_MESSAGES[i]

            if i == start_step and first_delay > 0:
                await asyncio.sleep(first_delay)
            elif i > start_step:
                await asyncio.sleep(msg["delay"])

            try:
                kb = make_kb(msg["buttons"])
                parse_mode = msg.get("parse_mode")
                if msg.get("video_note"):
                    await bot.send_video_note(user_id, msg["video_note"])
                if msg.get("photo"):
                    await bot.send_photo(user_id, msg["photo"])
                await bot.send_message(user_id, msg["text"], reply_markup=kb, parse_mode=parse_mode)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if "bot was blocked" in str(e) or "user is deactivated" in str(e) or "chat not found" in str(e):
                    db_remove_user(user_id)
                    return
                # Не роняем всю кампанию из-за одного письма — логируем и идём дальше
                logging.error(f"Drip [{user_id}] письмо {i+1}: {e}")
            db_set_step(user_id, i + 1)
            logging.info(f"Drip [{user_id}]: отправлено {i+1}/{len(DRIP_MESSAGES)}")

        db_set_done(user_id)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Drip [{user_id}]: ошибка — {e}")
        # Если пользователь заблокировал бота — удаляем
        if "bot was blocked" in str(e) or "user is deactivated" in str(e):
            db_remove_user(user_id)
    finally:
        active_campaigns.pop(user_id, None)

def start_drip(user_id: int, username: str):
    db_add_user(user_id, username)
    if user_id not in active_campaigns:
        task = asyncio.create_task(run_drip(user_id, start_step=0, first_delay=0))
        active_campaigns[user_id] = task

async def restore_campaigns():
    """При старте бота восстанавливает незавершённые кампании."""
    active = db_get_active()
    restored = 0
    for row in active:
        user_id = row["user_id"]
        step    = row["step"]
        step_at = row["step_at"]

        if step >= len(DRIP_MESSAGES):
            db_set_done(user_id)
            continue

        if user_id in active_campaigns:
            continue

        # Считаем сколько секунд осталось до следующего шага
        next_delay = DRIP_MESSAGES[step]["delay"]
        elapsed    = time.time() - step_at
        remaining  = max(0, next_delay - elapsed)

        task = asyncio.create_task(run_drip(user_id, start_step=step, first_delay=remaining))
        active_campaigns[user_id] = task
        restored += 1

    if restored:
        logging.info(f"Восстановлено кампаний: {restored}")


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id  = message.from_user.id
    username = message.from_user.username or ""
    if await is_subscribed(user_id):
        await message.answer("✅ Подписка подтверждена! Запускаем курс...")
        start_drip(user_id, username)
    else:
        await message.answer(
            "👋 Привет! Подпишитесь на канал, чтобы получить бесплатный курс.",
            reply_markup=kb_subscribe()
        )

@dp.callback_query(F.data == "check_sub")
async def callback_check(callback: types.CallbackQuery):
    await callback.answer()
    user_id  = callback.from_user.id
    username = callback.from_user.username or ""
    if await is_subscribed(user_id):
        await callback.message.edit_text("🎉 Подписка подтверждена! Запускаем курс.")
        start_drip(user_id, username)
    else:
        await callback.message.edit_text(
            "❌ Подписка не найдена. Попробуйте снова.",
            reply_markup=kb_subscribe()
        )

@dp.message(Command("preview"))
async def cmd_preview(message: types.Message):
    """Прислать всю воронку подряд как её видит пользователь: /preview"""
    if message.from_user.id != ADMIN_ID:
        return

    total_days = sum(m["delay"] for m in DRIP_MESSAGES) // 86400
    await message.answer(
        f"👀 <b>Полный прогон воронки</b>\n"
        f"Писем: {len(DRIP_MESSAGES)} · вся цепочка растянута на {total_days} дней\n\n"
        f"Дальше письма идут ровно так, как их видит подписчик.",
        parse_mode="HTML"
    )
    await asyncio.sleep(1.5)

    for i, msg in enumerate(DRIP_MESSAGES):
        d = msg["delay"]
        if d == 0:
            when = "сразу после подписки"
        elif d % 86400 == 0:
            when = f"через {d // 86400} дн. после предыдущего"
        else:
            when = f"через {d // 3600} ч. после предыдущего"

        # Разделитель-заголовок отдельным сообщением, чтобы не портить вёрстку письма
        await message.answer(
            f"━━━━━━━━━━━━━━━\n"
            f"✉️ <b>ПИСЬМО {i + 1} из {len(DRIP_MESSAGES)}</b> · {when}\n"
            f"━━━━━━━━━━━━━━━",
            parse_mode="HTML"
        )
        await asyncio.sleep(0.8)

        try:
            kb = make_kb(msg["buttons"])
            if msg.get("video_note"):
                await bot.send_video_note(message.from_user.id, msg["video_note"])
                await asyncio.sleep(0.5)
            if msg.get("photo"):
                await bot.send_photo(message.from_user.id, msg["photo"])
                await asyncio.sleep(0.5)
            await bot.send_message(
                message.from_user.id, msg["text"],
                reply_markup=kb, parse_mode=msg.get("parse_mode")
            )
        except Exception as e:
            await message.answer(f"⚠️ Письмо {i + 1} не отправилось: {e}")

        await asyncio.sleep(1.2)

    await message.answer(
        f"✅ <b>Конец воронки.</b>\n\n"
        f"Всего писем: {len(DRIP_MESSAGES)}\n"
        f"Активная фаза: {sum(m['delay'] for m in DRIP_MESSAGES[:7]) // 86400} дней\n"
        f"Реактивации: +21 и +60 дней\n\n"
        f"Проверить одно письмо: /test N",
        parse_mode="HTML"
    )

@dp.message(F.text.lower().in_({"стоп", "stop", "отписаться", "отписка", "хватит", "не пиши", "отстань", "достаточно", "всё", "все"}))
async def cmd_unsubscribe(message: types.Message):
    user_id = message.from_user.id
    # Отменяем активную кампанию если есть
    if user_id in active_campaigns:
        active_campaigns[user_id].cancel()
        active_campaigns.pop(user_id, None)
    # Помечаем done=1 в базе
    db_set_done(user_id)
    await message.answer(
        "Окей, больше не пишу 🤝\n\n"
        "Если что — канал всегда тут: @it_iz_tinder"
    )

@dp.message(Command("getid"))
async def cmd_getid(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Отправь мне фото, видео или кружочек — отвечу его file_id")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    file_id = message.photo[-1].file_id
    await message.answer(f"📸 file_id фото:\n{file_id}")

@dp.message(F.video_note)
async def handle_video_note(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    file_id = message.video_note.file_id
    await message.answer(f"🎥 file_id кружочка:\n{file_id}")

@dp.message(F.video)
async def handle_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    file_id = message.video.file_id
    await message.answer(f"🎬 file_id видео:\n{file_id}")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.removeprefix("/broadcast").strip()
    if not text:
        await message.answer("Напиши: /broadcast Текст сообщения")
        return
    users = db_get_all_users()
    if not users:
        await message.answer("📭 Пока нет пользователей.")
        return
    sent = 0
    status = await message.answer(f"📤 Отправляю {len(users)} пользователям...")
    for uid in users:
        try:
            await bot.send_message(uid, text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            if "bot was blocked" in str(e) or "user is deactivated" in str(e):
                db_remove_user(uid)
    await status.edit_text(f"✅ Готово! Отправлено: {sent} из {len(users)}")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("users.db")
    rows  = conn.execute("SELECT step, COUNT(*) FROM users GROUP BY step ORDER BY step").fetchall()
    done  = conn.execute("SELECT COUNT(*) FROM users WHERE done=1").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    day   = conn.execute("SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now', '-1 day')").fetchone()[0]
    week  = conn.execute("SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now', '-7 day')").fetchone()[0]
    conn.close()

    lines = [
        "📊 <b>Статистика воронки</b>",
        f"👥 Всего в базе: {total}",
        f"🆕 За сутки: {day} · за неделю: {week}",
        f"✅ Прошли воронку до конца: {done}",
        f"⚡ Активных кампаний: {len(active_campaigns)}",
        "",
        "<b>Кто на каком письме:</b>",
    ]
    mx = max([c for _, c in rows], default=1)
    for step, cnt in rows:
        bar = "▓" * max(1, round(cnt / mx * 12))
        label = "не начал" if step == 0 else f"получил {step} из {len(DRIP_MESSAGES)}"
        lines.append(f"  {label}: <b>{cnt}</b> {bar}")
    await message.answer("\n".join(lines), parse_mode="HTML")

@dp.message(Command("test"))
async def cmd_test(message: types.Message):
    """Прислать одно письмо воронки для проверки: /test 3"""
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer(f"Напиши: /test N  (от 1 до {len(DRIP_MESSAGES)})")
        return
    i = int(parts[1]) - 1
    if not (0 <= i < len(DRIP_MESSAGES)):
        await message.answer(f"Нет такого письма. Всего их {len(DRIP_MESSAGES)}")
        return
    msg = DRIP_MESSAGES[i]
    kb = make_kb(msg["buttons"])
    if msg.get("video_note"):
        await bot.send_video_note(message.from_user.id, msg["video_note"])
    if msg.get("photo"):
        await bot.send_photo(message.from_user.id, msg["photo"])
    await bot.send_message(message.from_user.id, msg["text"],
                           reply_markup=kb, parse_mode=msg.get("parse_mode"))
    d = msg["delay"]
    await message.answer(f"☝️ Письмо {i+1} из {len(DRIP_MESSAGES)} · задержка перед ним: {d//86400} дн.")

async def daily_stats():
    """Отправляет статистику за сутки каждый день в 12:00 по Москве."""
    import datetime
    while True:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        next_noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now >= next_noon:
            next_noon += datetime.timedelta(days=1)
        wait_seconds = (next_noon - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        conn = sqlite3.connect("users.db")
        count = conn.execute(
            "SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now', '-1 day')"
        ).fetchone()[0]
        conn.close()

        if count > 0:
            await bot.send_message(
                ADMIN_ID,
                f"📊 Статистика за последние 24 часа:\n"
                f"👥 Новых пользователей: {count}\n"
                f"📦 Всего в базе: {db_count_users()}"
            )

async def main():
    db_init()
    await restore_campaigns()
    asyncio.create_task(daily_stats())
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
