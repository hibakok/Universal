"""lab_splice.py — оракул SPLICE v1 (SPEC/10): склейка исходников по !include.

Вход:  splice(корень, host) -> плоский текст (bytes); host: {имя: bytes}
       (ключи нормализуются: \\ -> /, нижний регистр).
Выход: bytes — каждая строка + LF; исключение SpliceError(code, msg),
       где code — код возврата splice.exe, msg — хвост строки ERR=...
Функция: независимая реализация SPEC/10 — эталон для KERNEL/L1-SPLICE/
         splice.exe (E6.3) и фиксатор семантики разреза исходников.
         Порядок проверок дословно повторяет контракт инструмента:
         глубина -> имя -> открытие/чтение/размер; FORMAT распознаётся
         раньше спуска.
"""
MAXDEPTH = 8        # уровни 0..7 (корень + 7 вложенных включений)
FILECAP = 0x40000   # 256 КиБ на файл (E6.4e-2; сентинелу нужен запас — как enc)
OUTCAP = 0x40000    # 256 КиБ вывода (E6.4e-2; предел потребителей конвейера)
NAMECAP = 0x7F      # 127 байт на полное имя файла


class SpliceError(Exception):
    """code — код возврата splice.exe; msg — хвост строки ERR=..."""

    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def norm(name):
    """Нормализация имени: \\ -> /, без ведущих /, нижний регистр."""
    if isinstance(name, bytes):
        name = name.decode("latin1")
    return name.replace("\\", "/").strip("/").lower()


def _read(host, name):
    key = norm(name)
    if key not in host:
        raise SpliceError(4, "OPEN SRC")
    data = host[key].split(b"\x00", 1)[0]     # байт 00 — сентинел конца
    if len(data) >= FILECAP:
        raise SpliceError(7, "BIG SRC")
    return data, key


def _lines(data):
    """Терминаторы LF/CRLF/CR (как enc, SPEC/09); пустой файл — строк нет."""
    out, start, i, n = [], 0, 0, len(data)
    while i < n:
        c = data[i]
        if c == 0x0A:
            out.append(data[start:i])
            i += 1
            start = i
        elif c == 0x0D:
            out.append(data[start:i])
            i += 1
            if i < n and data[i] == 0x0A:
                i += 1
            start = i
        else:
            i += 1
    if start < n:
        out.append(data[start:n])
    return out


def splice(root, host):
    """Склеить корень со включениями; вернуть плоский текст (bytes)."""
    if isinstance(root, bytes):
        root = root.decode("latin1")
    host = {norm(k): v for k, v in host.items()}
    if len(root.encode("latin1")) > NAMECAP:
        raise SpliceError(3, "LONG NAME")
    out = bytearray()
    line = [0]                                # сквозной счётчик строк

    def process(name, depth):
        data, key = _read(host, name)
        pref = key.rfind("/") + 1             # каталог включающего файла
        for ln in _lines(data):
            line[0] += 1
            if ln[:1] == b"!":
                if len(ln) < 10 or ln[:9] != b"!include ":
                    raise SpliceError(6, "FORMAT AT=%04X"
                                      % (line[0] & 0xFFFF))
                if depth + 1 >= MAXDEPTH:     # раньше сборки имени (как enc)
                    raise SpliceError(11, "DEPTH")
                full = key[:pref] + ln[9:].decode("latin1")
                if len(full.encode("latin1")) > NAMECAP:
                    raise SpliceError(3, "LONG NAME")
                process(full, depth + 1)
            else:
                if len(out) + len(ln) + 1 > OUTCAP:
                    raise SpliceError(10, "BIG OUT")
                out.extend(ln)
                out.append(0x0A)

    process(root, 0)
    return bytes(out)


def expect(root, host):
    """splice + перевод исключения в (stdout-хвост, код) для батареи."""
    try:
        return splice(root, host), 0, None
    except SpliceError as e:
        return None, e.code, "U-L1-SPLICE ERR=%s" % e
