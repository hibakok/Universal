"""lab_brick.py — оракул формата BRICK v1 (SPEC/08): исходник -> тело.

Вход:  текст BRICK (str/bytes).
Выход: bytes тела секции; ValueError при ошибке формата (в сообщении —
       номер строки, как в ERR=FORMAT AT=...).
Функция: независимая от brick.exe сборка: два пассажа, метки, слоты
         $имя/$имя:1, директивы H/DB/DZ/DBZ/DD/DQ, предопределённая
         метка base; файловая длина фиксируется на первом DBZ
         (зеркалит реализацию K1-A010: заморозка при r15==0).

Семантика слотов: слот $имя размером s на позиции p получает значение
L(имя) − (p + s), знаковое; для s=1 — проверка диапазона −128..127.
Значение $имя в DD/DQ = RVA метки = L(имя) + 0x1000.
"""
HEXD = "0123456789ABCDEF"
BASE_LABEL = -0x1000          # предопределённая метка base (RVA 0)


class BrickError(ValueError):
    pass


def _err(lineno):
    raise BrickError("FORMAT AT=%04X" % lineno)


class _Parser:
    """Пословный разбор одной строки (курсор по байтам)."""

    def __init__(self, buf, pos):
        self.b = buf
        self.p = pos

    def peek(self):
        return self.b[self.p] if self.p < len(self.b) else 0

    def adv(self):
        self.p += 1

    def skip_seps(self):
        while self.peek() in (0x20, 0x09):
            self.adv()

    def at_eol(self):
        c = self.peek()
        return c in (0, 0x0A, 0x0D, 0x3B)

    def hexval(self, maxd=8):
        """1..maxd ЗАГЛАВНЫХ hex-цифр -> значение | None."""
        start = self.p
        v = 0
        n = 0
        while True:
            c = self.peek()
            if 0x30 <= c <= 0x39:
                d = c - 0x30
            elif 0x41 <= c <= 0x46:
                d = c - 0x37
            else:
                break
            if n == maxd:
                break
            v = (v << 4) | d
            n += 1
            self.adv()
        if n == 0:
            return None
        if self.peek() in (0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36,
                           0x37, 0x38, 0x39, 0x41, 0x42, 0x43, 0x44,
                           0x45, 0x46):
            return None                 # цифр больше максимума
        return v

    def hexbyte(self):
        """Ровно 2 ЗАГЛАВНЫЕ цифры -> байт | None (зеркало read_hex_byte)."""
        c1 = self._digit()
        if c1 is None:
            return None
        c2 = self._digit()
        if c2 is None:
            return None
        return (c1 << 4) | c2

    def _digit(self):
        c = self.peek()
        if 0x30 <= c <= 0x39:
            d = c - 0x30
        elif 0x41 <= c <= 0x46:
            d = c - 0x37
        else:
            return None
        self.adv()
        return d

    def name(self):
        """[a-z0-9_]+ -> (адрес, длина) | None; предел 63."""
        start = self.p
        while True:
            c = self.peek()
            if (0x61 <= c <= 0x7A) or (0x30 <= c <= 0x39) or c == 0x5F:
                self.adv()
            else:
                break
        n = self.p - start
        if n == 0 or n > 63:
            return None, n
        return start, n


def assemble(text):
    """BRICK v1 -> тело секции (bytes)."""
    if isinstance(text, str):
        text = text.encode("latin1")
    buf = text + b"\x00"
    labels = {"base": BASE_LABEL}
    # пасс 1: длины и метки; пасс 2: материализация
    for pas in (1, 2):
        out, cursor, filelen = bytearray(0x20010), 0, 0
        lineno, p = 1, 0
        while True:
            c = buf[p]
            if c == 0:
                break
            if c == 0x0A:
                p += 1
                lineno += 1
                continue
            if c == 0x0D:
                p += 1
                continue
            if c == 0x3B:                      # ';' комментарий
                while buf[p] not in (0, 0x0A):
                    p += 1
                continue
            if c == 0x3A:                      # ':' метка
                p += 1
                ps = _Parser(buf, p)
                addr, n = ps.name()
                if addr is None:
                    _err(lineno)
                p = ps.p
                _expect_eol(buf, p, lineno)
                if pas == 1:
                    name = buf[addr:addr + n].decode()
                    if name in labels:
                        _err(lineno)           # дубликат (вкл. base)
                    if len(labels) >= 512:
                        _err(lineno)           # переполнение labtab (SPEC/08:
                        # меток <= 512, ВКЛ. предопределённую base; поймано
                        # расхождение оракула с brick.exe — E6.4c-3/1)
                    labels[name] = cursor
                while buf[p] not in (0, 0x0A):
                    p += 1
                continue
            if c == 0x48:                      # 'H'
                p += 1
                cursor = _line_h(buf, p, pas, cursor, labels, out,
                                 lineno)
                while buf[p] not in (0, 0x0A):
                    p += 1
                continue
            if c == 0x44:                      # 'D' — данные
                p += 1
                kind, cursor, filelen = _line_d(buf, p, pas, cursor,
                                                filelen, labels, out,
                                                lineno)
                while buf[p] not in (0, 0x0A):
                    p += 1
                continue
            _err(lineno)                       # неизвестная строка
        if pas == 1:
            virtual_end = cursor
        else:
            if cursor != virtual_end:
                raise BrickError("внутренняя: длины пассажей "
                                 "разошлись")
    # файловая длина: frozen на первом DBZ (иначе — виртуальный конец)
    return bytes(out[:filelen if filelen else virtual_end])


def _expect_eol(buf, p, lineno):
    ps = _Parser(buf, p)
    ps.skip_seps()
    if not ps.at_eol():
        _err(lineno)


def _line_h(buf, p, pas, cursor, labels, out, lineno):
    ps = _Parser(buf, p)
    while True:
        ps.skip_seps()
        if ps.at_eol():
            break
        if ps.peek() == 0x24:                  # '$' — слот
            ps.adv()
            addr, n = ps.name()
            if addr is None:
                _err(lineno)
            slot = 4
            if ps.peek() == 0x3A:              # ':'
                ps.adv()
                if ps.peek() != 0x31:          # '1'
                    _err(lineno)
                ps.adv()
                slot = 1
            if not ps.at_eol():                # за слотом — только хвост
                ps.skip_seps()                 # expect_eol вызывающего
                if not ps.at_eol():
                    _err(lineno)
            name = buf[addr:addr + n].decode()
            if pas == 2:
                if name not in labels:
                    _err(lineno)
                disp = labels[name] - (cursor + slot)
                if slot == 1 and not (-128 <= disp <= 127):
                    _err(lineno)
                if slot == 1:
                    out[cursor] = disp & 0xFF
                else:
                    out[cursor:cursor + 4] = (disp & 0xFFFFFFFF)\
                        .to_bytes(4, "little")
            cursor += slot
            break
        v = ps.hexbyte()
        if v is None:
            _err(lineno)
        out[cursor] = v
        cursor += 1
    return cursor


def _line_d(buf, p, pas, cursor, filelen, labels, out, lineno):
    """DB/DBZ/DZ/DD/DQ. -> (вид, курсор, файловая_длина)."""
    ps = _Parser(buf, p)
    c = ps.peek()
    if c == 0x42:                              # 'B'
        ps.adv()
        if ps.peek() == 0x5A:                  # 'Z' — DBZ
            ps.adv()
            ps.skip_seps()
            v = ps.hexval()
            if v is None:
                _err(lineno)
            _expect_eol(buf, ps.p, lineno)
            if filelen == 0:                   # заморозка (зеркало r15)
                filelen = cursor
            return "dbz", cursor + v, filelen
        # DB
        while True:
            ps.skip_seps()
            if ps.at_eol():
                break
            if ps.peek() == 0x24:
                _err(lineno)                   # ссылка в DB
            v = ps.hexbyte()
            if v is None:
                _err(lineno)
            out[cursor] = v
            cursor += 1
        return "db", cursor, filelen
    if c == 0x5A:                              # 'Z' — DZ
        ps.adv()
        ps.skip_seps()
        v = ps.hexval()
        if v is None:
            _err(lineno)
        _expect_eol(buf, ps.p, lineno)
        if pas == 2:
            for _ in range(v):
                out[cursor] = 0
                cursor += 1
        else:
            cursor += v
        return "dz", cursor, filelen
    if c in (0x44, 0x51):                      # 'D'/'Q' — DD/DQ
        width = 4 if c == 0x44 else 8
        ps.adv()
        # ПРИМЕЧАНИЕ: реализация принимает пустой список DD/DQ (0 байт);
        # SPEC/08 обещает ошибку — отклонение зафиксировано в лаборатории.
        while True:
            ps.skip_seps()
            if ps.at_eol():
                break
            if ps.peek() == 0x24:              # $имя — RVA метки
                ps.adv()
                addr, n = ps.name()
                if addr is None:
                    _err(lineno)
                if pas == 2:
                    name = buf[addr:addr + n].decode()
                    if name not in labels:
                        _err(lineno)
                    val = (labels[name] + 0x1000) & 0xFFFFFFFF
                    out[cursor:cursor + width] = val.to_bytes(width,
                                                              "little")
                cursor += width
            else:
                v = ps.hexval()
                if v is None:
                    _err(lineno)
                if pas == 2:
                    out[cursor:cursor + width] = v.to_bytes(width,
                                                            "little")
                cursor += width
        return "ddq", cursor, filelen
    _err(lineno)


def load(path):
    with open(path, "rb") as f:
        return assemble(f.read())


if __name__ == "__main__":
    import sys
    print("OK %d байт" % len(load(sys.argv[1])))
