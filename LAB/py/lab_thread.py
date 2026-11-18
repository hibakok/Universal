"""lab_thread.py — «threaded code»: генератор специализированных инструкций.

Вход:  CPU (lab_cpu.CPU), имя инструкции, args — семантический кортеж
       lab_x86.decode (дескрипторы 'r'/'i'/'m'/'t' — см. lab_x86).
Выход: build(cpu, name, args) -> fn — замыкание fn(nrip) ПОД
       КОНКРЕТНУЮ инструкцию (номера регистров, маски, смещения и цели
       переходов — константы исходника; ВОЗВРАЩАЕТ следующий rip),
       либо None — форма не специализируется (lab_cpu исполняет
       универсальный _op_<имя> из lab_cpu_ops).
Функция: убрать из горячего цикла универсальный разбор операндов
       (get/put/_opaddr): каждому rip соответствует функция с уже
       «зашитыми» константами. Ускорение lab_cpu ~2x (план — журнал,
       сессия 40, шаг (0) перед E6.4d-5/3: после замены wall.exe
       самосборкой секции 9-11 батареи подорожают ~10x).

Состав (лимит 500 строк): ЭТОТ файл — хелперы операндов (чтение/
       запись/адресация/скан регионов), компиляция _gen и вход build;
       построители тел инструкций — lab_thread_ops (ленивый импорт
       разрывает цикл зависимости).

Метод: исходник функции генерируется текстом и компилируется ОДИН раз
       на уникальную форму (кэш _FACTORY; другой imm/disp/цель — другой
       исходник; суммарная компиляция по батарее ~1 с против минут
       прогона). Оракул неизменности: тела ПОБАЙТОВО повторяют
       lab_cpu._op_* (те же выражения над теми же сырыми значениями;
       regs может содержать отрицательные Python-int после cdqe —
       маски стоят ровно там же, где в эталоне). Проверки: батарея
       (выходы байт-в-байт), счётчики шагов wall_self_canary.py,
       диффтест LAB/ai/cpu_fuzz.py (случайные программы: замыкания
       против универсального пути, вкл. сообщения об ошибках).

Захват замыканиями (инварианты lab_cpu; НЕ перевязывать после
       __init__ — только мутировать): regs = cpu.r, fl = cpu.fl
       ([zf, cf, sf, of], всегда 0/1), regions = cpu.rscan
       ([(lo, hi, buf)] по self.regions), stubs = cpu.stubs; cpu —
       только rip/retguard (переходы и диагностика). Абсолютные
       (riprel/безбазовые) адреса разрешаются в регион ещё при
       декодировании (buf/offset — константы); динамические —
       сканирование регионов на каждом доступе с одноэлементной
       подсказкой memo (cpu.memo; только при непересекающихся
       регионах — разрешение то же, что у _region: первое совпадение).
       Память читается/пишется через struct.unpack_from/pack_into
       (_S) — без срезов-копий; формат %X в сообщениях сохранён.
"""
import struct

M64 = (1 << 64) - 1

# размер операнда -> (маска, сдвиг знакового бита, байтов, 1 << размер)
_SZ = {
    8: ("0xFF", 7, 1, "0x100"),
    16: ("0xFFFF", 15, 2, "0x10000"),
    32: ("0xFFFFFFFF", 31, 4, "0x100000000"),
    64: ("0xFFFFFFFFFFFFFFFF", 63, 8, "0x10000000000000000"),
}

# Форматы struct для чтения/записи памяти (в 2 раза быстрее
# int.from_bytes(bb[o:o+n]) — без среза-копии; границы гарантирует
# проверка региона — как и прежде)
_S = {1: struct.Struct("<B"), 2: struct.Struct("<H"),
      4: struct.Struct("<I"), 8: struct.Struct("<Q")}

# условия jcc как тест истинности на fl = [zf, cf, sf, of] (значения
# флагов всегда 0/1, поэтому not/| эквивалентны арифметике таблицы
# _CC из lab_cpu: «a» = (1-cf)&(1-zf) <-> not (cf|zf) и т.д.)
_CCE = {
    "o": "fl[3]", "no": "not fl[3]",
    "b": "fl[1]", "ae": "not fl[1]",
    "z": "fl[0]", "nz": "not fl[0]",
    "be": "fl[1] | fl[0]", "a": "not (fl[1] | fl[0])",
    "s": "fl[2]", "ns": "not fl[2]",
    "p": "False", "np": "True",
    "l": "fl[2] ^ fl[3]", "ge": "not (fl[2] ^ fl[3])",
    "le": "fl[0] | (fl[2] ^ fl[3])",
    "g": "not (fl[0] | (fl[2] ^ fl[3]))",
}

_FACTORY = {}          # исходник -> фабрика _mk (компиляция один раз)


def _gen(pre, body, memo):
    """Собрать фабрику замыканий по строкам исходника (с кэшем).
    pre — строки тела _mk (привязка buf/uN/pN/m); body — строки
    fn(nrip): замыкание ВОЗВРАЩАЕТ следующий rip (nrip — продвижение
    по длине инструкции; переходы возвращают цель; call заглушке —
    nrip). memo — активна ли подсказка региона (cpu.memo не None)."""
    lines = ["def _mk(regs, fl, cpu, regions, stubs, memo):"]
    lines.extend("    " + l for l in pre)
    lines.append("    def fn(nrip):")
    lines.extend("        " + l for l in (body if body else ["pass"]))
    lines.append("    return fn")
    text = "\n".join(lines)
    f = _FACTORY.get(text)
    if f is None:
        ns = {"_S1": _S[1], "_S2": _S[2], "_S4": _S[4], "_S8": _S[8]}
        exec(compile(text, "<lab_thread>", "exec"), ns)
        f = ns["_mk"]
        _FACTORY[text] = f
    return f


# --- разбор дескрипторов операндов ---

def _bits(op):
    """Размер операнда в битах ('r'/'i'/'m')."""
    if op[0] == "m":
        return op[5]
    return op[2]


def _rreg(op):
    """Выражение чтения регистра (маска по размеру; 64 — сырое)."""
    _, i, size = op
    if size == 64:
        return "regs[%d]" % i
    return "regs[%d] & %s" % (i, _SZ[size][0])


def _wreg(op, val):
    """Строка записи регистра (правила put: 32 бита обнуляют старшие,
    8/16 — слияние со старшими битами)."""
    _, i, size = op
    if size == 64:
        return "regs[%d] = %s & 0xFFFFFFFFFFFFFFFF" % (i, val)
    if size == 32:
        return "regs[%d] = %s & 0xFFFFFFFF" % (i, val)
    keep = "~0xFF" if size == 8 else "~0xFFFF"
    m = "0xFF" if size == 8 else "0xFFFF"
    return "regs[%d] = (regs[%d] & %s) | (%s & %s)" % (i, i, keep, val, m)


def _addrp(op):
    """Адресация памяти -> ('const', адрес) | ('dyn', выражение).
    Выражение повторяет _opaddr: disp + r[base] + r[index]*scale,
    итог & M64; riprel — абсолютный адрес БЕЗ маски (как в эталоне)."""
    _, b, i, s, d, _sz, rr = op
    if rr is not None:
        return "const", rr[1]
    if b is None and i is None:
        return "const", d & M64
    parts = []
    if b is not None:
        parts.append("regs[%d]" % b)
    if i is not None:
        parts.append("regs[%d]" % i if s == 1 else
                     "regs[%d] * %d" % (i, s))
    if d:
        parts.append(repr(d))           # отрицательное — со знаком
    return "dyn", "(%s) & 0xFFFFFFFFFFFFFFFF" % " + ".join(parts)


def _resolve(cpu, const, n):
    """Константный адрес -> (индекс региона, смещение) или None
    (вне регионов: сканирование на исполнении — как в _region)."""
    for k, (lo, hi, _b) in enumerate(cpu.rscan):
        if lo <= const and const + n <= hi:
            return k, const - lo
    return None


def _scan_read(var, addr, n, memo):
    """Строки чтения n байт по динамическому адресу (скан регионов;
    memo — список-подсказка [lo, hi, buf] при непересекающихся
    регионах: попадание — 2 сравнения вместо прохода списка)."""
    L = ["%s_a = %s" % (var, addr)]
    rd = '%s = u%d(bb, %s_a - lo)[0]' % (var, n, var)
    err = (f'        raise MemoryError("доступ вне регионов: %X (+%d)"'
           f' % ({var}_a, {n}))')
    if memo:
        L += ["if m[0] <= %s_a and %s_a + %d <= m[1]:" % (var, var, n),
              "    %s = u%d(m[2], %s_a - m[0])[0]" % (var, n, var),
              "else:",
              "    for lo, hi, bb in regions:",
              "        if lo <= %s_a and %s_a + %d <= hi:" % (var, var, n),
              "            m[0] = lo",
              "            m[1] = hi",
              "            m[2] = bb",
              "            " + rd,
              "            break",
              "    else:",
              "        " + err.strip()]
    else:
        L += ["for lo, hi, bb in regions:",
              "    if lo <= %s_a and %s_a + %d <= hi:" % (var, var, n),
              "        " + rd,
              "        break",
              "else:",
              "    " + err.strip()]
    return L


def _scan_write(addr, val, n, vm, memo):
    """Строки записи val (маска vm) по динамическому адресу."""
    L = ["_a = %s" % addr]
    wr = 'p%d(bb, _a - lo, %s & %s)' % (n, val, vm)
    err = (f'    raise MemoryError("доступ вне регионов: %X (+%d)"'
           f' % (_a, {n}))')
    if memo:
        L += ["if m[0] <= _a and _a + %d <= m[1]:" % n,
              "    p%d(m[2], _a - m[0], %s & %s)" % (n, val, vm),
              "else:",
              "    for lo, hi, bb in regions:",
              "        if lo <= _a and _a + %d <= hi:" % n,
              "            m[0] = lo",
              "            m[1] = hi",
              "            m[2] = bb",
              "            " + wr,
              "            break",
              "    else:",
              "        " + err.strip()]
    else:
        L += ["for lo, hi, bb in regions:",
              "    if lo <= _a and _a + %d <= hi:" % n,
              "        " + wr,
              "        break",
              "else:",
              "    " + err.strip()]
    return L


def _read(cpu, op, var, force8=False):
    """Чтение операнда -> (pre, строки, выражение-значение).
    force8: читать память 8 байт независимо от размера операнда
    (косвенный call — IAT PE32+, как self.read(..., 8) в _op_call)."""
    k = op[0]
    if k == "r":
        return [], [], _rreg(op)
    if k == "i":
        return [], [], repr(op[1])
    n = 8 if force8 else _SZ[_bits(op)][2]
    memo = cpu.memo is not None
    kind, v = _addrp(op)
    if kind == "const":
        r = _resolve(cpu, v, n)
        if r is not None:
            k2, off = r
            return (["buf = regions[%d][2]" % k2,
                     "u%d = _S%d.unpack_from" % (n, n)], [],
                    "u%d(buf, %d)[0]" % (n, off))
        addr = repr(v)
    else:
        addr = v
    pre = ["u%d = _S%d.unpack_from" % (n, n)]
    if memo:
        pre.append("m = memo")
    return pre, _scan_read(var, addr, n, memo), var


def _write(cpu, op, val):
    """Запись значения в операнд -> (pre, строки)."""
    if op[0] == "r":
        return [], [_wreg(op, val)]
    n = _SZ[_bits(op)][2]
    vm = {1: "0xFF", 2: "0xFFFF", 4: "0xFFFFFFFF",
          8: "0xFFFFFFFFFFFFFFFF"}[n]
    memo = cpu.memo is not None
    kind, v = _addrp(op)
    if kind == "const":
        r = _resolve(cpu, v, n)
        if r is not None:
            k2, off = r
            return (["buf = regions[%d][2]" % k2,
                     "p%d = _S%d.pack_into" % (n, n)],
                    ["p%d(buf, %d, %s & %s)" % (n, off, val, vm)])
        addr = repr(v)
    else:
        addr = v
    pre = ["p%d = _S%d.pack_into" % (n, n)]
    if memo:
        pre.append("m = memo")
    return pre, _scan_write(addr, val, n, vm, memo)

def build(cpu, name, args):
    """Собрать замыкание инструкции; None — универсальный путь."""
    import lab_thread_ops             # отложенно: разрывает цикл
    b = lab_thread_ops._BUILDERS.get(name)
    if b is None:
        return None
    try:
        r = b(cpu, args)
    except Exception:    # неожиданная форма — не рискуем
        return None
    if not r:
        return None
    pre, body = r
    pre = list(dict.fromkeys(pre))   # чтение+запись одного abs-операнда
                                     # дают одинаковые строки buf — дубль
    if len([l for l in pre if l.startswith("buf =")]) > 1:
        return None       # разные abs-операнды: не бывает; отказ
    return _gen(pre, body, cpu.memo is not None)(
        cpu.r, cpu.fl, cpu, cpu.rscan, cpu.stubs, cpu.memo)
