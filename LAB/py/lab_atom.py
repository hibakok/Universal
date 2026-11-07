"""lab_atom.py — оракул формата ATOM v1 (SPEC/03-ATOM-FORMAT).

Вход:  текст ATOM (str) — телесная форма (смещение 0 = RVA 0x1000).
Выход: bytes — тело секции; ValueError при нарушении покрытия/грамматики.
Функция: независимая от hexgen.exe материализация листинга байт-в-байт.
"""
HEX = "0123456789ABCDEF"


def assemble(text):
    """Листинг ATOM v1 -> тело секции (bytes). Строгая проверка."""
    out = bytearray()
    covered = 0  # сколько байт покрыто к текущей строке
    lines = text.split("\n")
    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip("\r")  # CR перед LF допускается
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        if s.startswith("Z"):
            parts = s[1:].split()
            if len(parts) != 2:
                raise ValueError("строка %d: Z требует 2 значения" % lineno)
            lo, hi = _hex4(parts[0], lineno), _hex4(parts[1], lineno)
            if lo != covered or hi < lo:
                raise ValueError("строка %d: Z %X..%X разрывает покрытие "
                                 "(ждём %X)" % (lineno, lo, hi, covered))
            out += b"\x00" * (hi - lo)
            covered = hi
        elif s.startswith("@"):
            parts = s[1:].split(";")[0].split()
            if not parts:
                raise ValueError("строка %d: пустая запись @" % lineno)
            off = _hex4(parts[0], lineno)
            if off != covered:
                raise ValueError("строка %d: @%X разрывает покрытие "
                                 "(ждём %X)" % (lineno, off, covered))
            for tok in parts[1:]:
                out.append(_byte(tok, lineno))
            covered = off + len(parts) - 1
        else:
            raise ValueError("строка %d: неизвестная строка %r" %
                             (lineno, s[:20]))
    return bytes(out)


def _hex4(tok, lineno):
    if len(tok) != 4 or any(c not in HEX for c in tok):
        raise ValueError("строка %d:bad смещение %r (4 ЗАГЛАВНЫЕ цифры)" %
                         (lineno, tok))
    return int(tok, 16)


def _byte(tok, lineno):
    if len(tok) != 2 or any(c not in HEX for c in tok):
        raise ValueError("строка %d: плохой байт %r" % (lineno, tok))
    return int(tok, 16)


def load(path):
    with open(path, "rb") as f:
        return assemble(f.read().decode("latin1"))


if __name__ == "__main__":
    import sys
    body = load(sys.argv[1])
    print("OK %d байт" % len(body))
