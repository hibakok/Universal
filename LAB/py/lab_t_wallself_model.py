"""lab_t_wallself_model.py — модель класса эквивалентности каркаса (T-E6-49d).

Предсказание поведения прохода 0+1 каркаса wall.wall по строкам
оракула _lex (E6.4d-3/2): какие источники сравнимы с оракулом parse
(ошибка на той же строке / приём), какие — вне класса. Детали класса
и правило cerr — в docstring _expect_line; патологические kw-формы —
_kw_falls. Вызывается из lab_t_wallself.run (T-E6-49d).
"""
import lab_l2
import lab_l2_err
import lab_l2_lex


def _kw_falls(toks, no):
    """Принял ли бы p1_namestmt каркаса строку «KW ...» (kw-имя как
    обычное имя; S008/S009/S00A/S00F — E6.4d-3/3): форма вызова
    '(' арги ')' или присваивания '=' выр с пустым хвостом.
    Разбор — класс P оракула (грамматика выражений/аргументов у
    каркаса та же — стен-режим зеркалит wall.exe); astore-форма
    («[») на kw-имени всегда ERR (astore_chk: неизвестное)."""
    p = lab_l2_lex.P(no, toks[1:])
    try:
        k, v = p.peek()
        if (k, v) == ("sym", "("):
            p.pop()
            p.args()
            p.at_end()
            return True
        if (k, v) == ("sym", "="):
            p.pop()
            p.expr()
            p.at_end()
            return True
        return False
    except lab_l2_err.WallError:
        return False


def _expect_line(s):
    """(код, строка) — исход ожидания: (6, L) — ERR=FORMAT AT=L;
    (0, None) — успех (код 0, пустой stdout/.b2); None — источник вне
    класса эквивалентности каркаса (пропуск).

    Класс E6.4d-3/2 (S006 var + S004 заголовки + S007 end + S00B
    return + S00C setb + S00D namestmt; выражения стат-режимом):
    моделирование прохода 1 каркаса по строкам оракула _lex
    (состояние fcur/seenfunc/fdepth; строки с токенами):
    1) _lex отказал — ошибка лексера (ловится проходом 0 каркаса);
    2) не-имя первым токеном — каркас ERR=FORMAT на строке; сравнимо,
       если оракул parse падает на той же строке;
    3) func — заголовок (в ЛЮБОМ состоянии — quirk wall.exe: плечо
       kw==3 раньше fcur; вложенная func — оракул падает на строке,
       инструменты принимают — вне класса); ошибка заголовка у обоих
       на строке заголовка; корректный заголовок — fcur=1/seenfunc=1/
       fdepth+1;
    4) в теле (fcur): end — закрытие (fdepth-1, fcur=0; лишние токены
       или лишний end — ошибка на строке); var — локаль (S006):
       ошибки имени/[n]/at_end/дубликата/глобали — на строке у обоих;
       return/setb/имя-стат (S00B/S00C/S00D) — ошибки фронтенда на
       строке у обоих (perr == строка — сравнимо); приняты обеими
       сторонами — продолжение; ошибка ТОЛЬКО прохода 2 (cerr ==
       строка: неизвестное имя в выражении и т.п.) — каркас даст 0,
       wall.exe 6 — вне класса; kw else/if/while/break/continue и
       str/ext — строки этих статов у каркаса идут в namestmt
       (плечи — E6.4d-3/3): при perr == строка патологические формы
       «KW = выр» / «KW(арг)» namestmt принимает (оракул
       отвергает) — вне класса (_kw_falls), прочее — ERR=FORMAT
       строки у обоих — сравнимо; при perr != строка (корректный
       стат) namestmt отвергает — вне класса;
    5) между func (seenfunc) — только func (заголовок), прочее —
       ERR=FORMAT на строке у обоих (плече hdrfail — как wall.exe:
       kw-статы действуют только при fcur != 0);
    6) до первой func — объявления S003 (как E6.4d-2/3);
    7) пост-проверки: незакрытый func — set_lastline (последняя
       непустая); ровно одна main без параметров — КОД 0 (выход .b2
       пуст — эмитция прохода 2 позже; и ТОЛЬКО если полный конвейер
       оракула тоже проходит — cerr is None: иначе wall.exe даст 6,
       а каркас 0 — вне класса); main с параметрами — ошибка
       в строке заголовка main; не одна main — последняя непустая.
    Сравнимо = модель совпадает с ожиданием оракула parse (строка
    ошибки или приём). Инструмент wall.exe — третья сторона (проверя-
    ется прогоном)."""
    try:
        lines = lab_l2_lex._lex(s)
    except lab_l2_err.WallError as e:
        return (6, e.line)
    try:
        lab_l2.parse(s)
        perr = None
    except lab_l2_err.WallError as e:
        perr = e.line
    try:
        lab_l2.compile_wall(s)
        cerr = None
    except lab_l2_err.WallError as e:
        cerr = e.line
    fcur = seen = fdepth = 0
    for no, toks, _t in lines:
        if not toks:
            continue
        k, v = toks[0]
        if k != "id":
            return (6, no) if perr == no else None
        if v == "func":
            if fcur:
                # вложенная func — quirk wall.exe: инструменты приняли
                # бы заголовок (проверено: каркас == wall.exe), оракул
                # падает на этой строке — вне класса
                return None
            if perr == no:
                return (6, no)
            fcur = 1
            seen = 1
            fdepth += 1
            continue
        if fcur:
            if v == "end":
                if perr == no:
                    return (6, no)
                fdepth -= 1
                fcur = 0
                continue
            if v == "var":
                # S006 (E6.4d-3/1): ошибки имени/[n]/at_end/дубликата/
                # глобали — на строке у обеих сторон (порядок совпа-
                # дает); принято — локаль в окне, продолжение
                if perr == no:
                    return (6, no)
                continue
            if v in ("else", "if", "while", "break", "continue",
                     "str", "ext"):
                # плечи S008/S009/S00A/S00F — E6.4d-3/3; str/ext в
                # теле — оракул «объявление после func»; каркас гонит
                # их через namestmt
                if perr == no:
                    if _kw_falls(toks, no):
                        return None
                    return (6, no)
                # корректный стат (или корректное «KW(арг)»-имя) —
                # namestmt обычно отвергает — вне класса
                return None
            # return/setb/имя-стат (S00B/S00C/S00D): perr == строка —
            # обе стороны отвергают; cerr == строка — только проход 2
            if perr == no:
                return (6, no)
            if cerr == no:
                return None
            continue
        if seen:
            return (6, no) if perr == no else None
        if perr == no:
            return (6, no)
    if fdepth or fcur:
        last = lab_l2_lex.last_line(lines)
        return (6, last) if perr == last else None
    # все func закрыты (тела пустые): пост-проверка main по заголовкам
    mains = mline = mpar = 0
    inf = 0
    for no, toks, _t in lines:
        if not toks:
            continue
        k, v = toks[0]
        if k == "id" and v == "func":
            inf = 1
            nm = toks[1][1] if len(toks) > 1 and toks[1][0] == "id" \
                else None
            np_ = 0
            if ("sym", "(") in toks:
                i = toks.index(("sym", "("))
                if not (i + 1 < len(toks) and toks[i + 1] == ("sym", ")")):
                    np_ = sum(1 for t in toks[i + 1:] if t[0] == "id")
            if nm == "main":
                mains += 1
                mline = no
                mpar = np_
        elif k == "id" and v == "end" and inf:
            inf = 0
    if mains == 1 and mpar == 0:
        if perr is None and cerr is None:
            return (0, None)
        return None
    if mains == 1 and mpar != 0:
        return (6, mline) if perr == mline else None
    last = lab_l2_lex.last_line(lines)
    return (6, last) if perr == last else None
