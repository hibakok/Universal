"""lab_up.py — оракул контейнера .UP (SPEC/13 v1/v2).

Вход:  байты контейнера .UP (parse_up) либо (memsize, код, данные)
       (make_up).
Выход: parse_up -> (memsize, код, данные); make_up -> байты .UP;
       отказы — UpError с причиной SPEC/13 п. 4.
Функция: эталонная семантика контейнера программ UNIVM: заголовок
         24 Б + код (+ секция данных с v2). Выделен из lab_vm.py по
         лимиту 500 строк (E7.4-1; прецедент lab_t_kernel_corpus.py);
         импортируется лабораторией как независимый свидетель SPEC/13
         (ядро E7.2/E7.4-2 обязано повторять порядок отказов).

Правила v2 (E7.4-1, SPEC/13 п. 2.1):
  - поле @20 — смещение данных (в v1 было резервом 0);
  - dataoff = 0 — данных нет: файл кончается кодом (v1-эквивалент);
  - dataoff = 24+codesize — данные сразу за кодом до конца файла,
    datalen >= 1, инициализация RAM[0:datalen] (остальное — нули);
  - v1-файлы валидны навсегда: версия — часть файла (читатель
    принимает обе); иное значение версии — отказ VER.
"""
MEM_MAX = 67108864            # 64 МиБ — предел memsize (SPEC/13 п. 3)
CODE_MAX = 67108864           # 64 МиБ — предел codesize


class UpError(Exception):
    """Отказ разбора контейнера .UP (причина — SPEC/13 п. 4)."""

    def __init__(self, reason):
        super().__init__("ERR=%s" % reason)
        self.reason = reason


def make_up(memsize, code, data=b""):
    """(memsize, код[, данные]) -> байты .UP: без данных — v1 (как
    раньше, байт-в-байт), с данными — v2 (dataoff = 24+codesize).
    Отказы — UpError: MEM/CODE0/LEN/DATA (SPEC/13 п. 4)."""
    if not (0 <= memsize <= MEM_MAX):
        raise UpError("MEM")
    if not (1 <= len(code) <= CODE_MAX):
        raise UpError("CODE0" if not code else "LEN")
    if len(data) > memsize:
        raise UpError("DATA")           # инициализация не влезает в RAM
    head = (b"UP01" + (2 if data else 1).to_bytes(4, "little")
            + memsize.to_bytes(8, "little")
            + len(code).to_bytes(4, "little")
            + (24 + len(code) if data else 0).to_bytes(4, "little"))
    return head + code + data


def parse_up(data):
    """Байты .UP -> (memsize, код, данные); отказы — UpError в порядке
    SPEC/13 п. 4: SIG -> VER -> MEM -> CODE0 -> LEN (обрезка/лишние
    байты) -> RES (поле dataoff) -> DATA (длиннее RAM)."""
    if len(data) < 24 or data[:4] != b"UP01":
        raise UpError("SIG")
    ver = int.from_bytes(data[4:8], "little")
    if ver not in (1, 2):
        raise UpError("VER")
    memsize = int.from_bytes(data[8:16], "little")
    if memsize > MEM_MAX:
        raise UpError("MEM")
    codesize = int.from_bytes(data[16:20], "little")
    if codesize == 0:
        raise UpError("CODE0")
    off = int.from_bytes(data[20:24], "little")
    if ver == 1:
        if len(data) != 24 + codesize:
            raise UpError("LEN")
        if off != 0:
            raise UpError("RES")
        return memsize, data[24:], b""
    # v2: off — смещение данных (0 — данных нет)
    if len(data) < 24 + codesize:
        raise UpError("LEN")            # код обрезан
    if off not in (0, 24 + codesize):
        raise UpError("RES")            # мусор в поле смещения
    if off == 0:
        if len(data) != 24 + codesize:
            raise UpError("LEN")        # лишние байты при данных «нет»
        return memsize, data[24:], b""
    if len(data) == off:
        raise UpError("RES")            # данные заявлены, байтов нет
    datalen = len(data) - off
    if datalen > memsize:
        raise UpError("DATA")           # инициализация не влезает в RAM
    return memsize, data[24:off], data[off:]
