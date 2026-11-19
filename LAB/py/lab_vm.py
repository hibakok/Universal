"""lab_vm.py — оракул UNIVM (SPEC/12 ISA v0 + SPEC/13 .UP v1).

Вход:  текст ассемблера (str) или байты контейнера .UP.
Выход: результат исполнения — RunResult (консоль, код, шаги, ловушка,
       регистры, память) либо байты .UP (у assemble).
Функция: эталонная семантика виртуального процессора UNIVM v0
         для будущего ядра kernel.exe (E7.2, правило R8: ядро ==
         оракулу по наблюдаемому поведению); мини-ассемблер для
         авторинга тестовых программ (синтаксис — ниже).

Мини-ассемблер (LAB-инструмент; мнемоники — контракт SPEC/12 п. 8):
  - строка := [метка ':'] [инструкция | директива] [';' комментарий]
    (строка из одних разделителей/запятых — пуста, пропускается; E7.3-1)
  - директива: .mem <число>          — memsize (обязательна, одна,
    до первой инструкции; отсутствие — ошибка строки 1)
  - инструкции (SPEC/12 п. 8):
      const rD, число        mov rD, rA
      add/sub/and/or/xor/shl/shr/lt/eq rD, rA, rB
      ldb/ldq rD, rA[+смещ]          (смещ — знаковое; +0 можно опустить)
      stb/stq rA[+смещ], rB
      jmp метка|число       jnz rD, метка|число     halt число
  - регистры r0..r15 (строчные); метки [a-z_][a-z0-9_]* (строчные);
  - числа: десятичные со знаком или 0x-hex; диапазон imm32:
    -2^31 .. 2^32-1 (F2 знаковые поля хранят дополнение до двух);
  - метка перехода = смещение в коде (разрешается на пассе 2).

Семантика ISA — ТОЛЬКО по SPEC/12 (оракул — независимый свидетель;
всякое расхождение с ядром E7.2 — находка, не повод подгонки).
"""
import re

M64 = (1 << 64) - 1
MEM_MAX = 67108864            # 64 МиБ — предел memsize (SPEC/13 п. 3)
CODE_MAX = 67108864           # 64 МиБ — предел codesize
DEVWIN = 4096                 # окно устройств (SPEC/12 п. 6)
DEFAULT_MAX_STEPS = 200000000

# --- реестр опкодов (SPEC/12 п. 5) -----------------------------------
# имя -> (опкод, формат); формат: 1 = F1(3Б), 2 = F2(6Б), 3 = F3(6Б)
OPS = {
    "const": (0x01, 2), "mov": (0x02, 1),
    "add": (0x03, 1), "sub": (0x04, 1),
    "and": (0x05, 1), "or": (0x06, 1), "xor": (0x07, 1),
    "shl": (0x08, 1), "shr": (0x09, 1),
    "lt": (0x0A, 1), "eq": (0x0B, 1),
    "ldb": (0x0C, 2), "stb": (0x0D, 2),
    "ldq": (0x0E, 2), "stq": (0x0F, 2),
    "jmp": (0x10, 3), "jnz": (0x11, 3), "halt": (0x12, 3),
}
OPNAME = {op: name for name, (op, _f) in OPS.items()}
FMT_LEN = {1: 3, 2: 6, 3: 6}

# --- ошибки -----------------------------------------------------------
TRAP_BAD = 1                  # недопустимая инструкция (SPEC/12 п. 7)
TRAP_FETCH = 2                # выборка вне кода
TRAP_LOAD = 3                 # чтение вне памяти
TRAP_STORE = 4                # запись вне памяти
TRAP_STEPS = 6                # предел шагов (диагностический, не ISA)


class AsmError(Exception):
    """Ошибка ассемблирования; line — номер строки с 1."""

    def __init__(self, line, msg):
        super().__init__("строка %d: %s" % (line, msg))
        self.line = line
        self.msg = msg


class UpError(Exception):
    """Отказ разбора контейнера .UP (причина — SPEC/13 п. 4)."""

    def __init__(self, reason):
        super().__init__("ERR=%s" % reason)
        self.reason = reason


# --- разбор чисел и операндов -----------------------------------------
_RE_REG = re.compile(r"^r([0-9]|1[0-5])$")
_RE_MEMOP = re.compile(r"^(r(?:[0-9]|1[0-5]))(?:([+-])(\d+|0x[0-9A-Fa-f]+))?$")
_RE_LABEL = re.compile(r"^[a-z_][a-z0-9_]*$")


def _toks(line):
    """'ldb r1, r2+16' -> ['ldb', 'r1', 'r2+16'] (пробелы/запятые)."""
    return [t for t in re.split(r"[,\s]+", line.strip()) if t]


def _num(tok, line):
    """Число: десятичное со знаком или 0x-hex; диапазон imm32."""
    v = None
    try:
        if tok.startswith(("0x", "-0x", "+0x")):
            v = int(tok, 16)
        elif tok.lstrip("+-").isdigit():
            v = int(tok, 10)
    except ValueError:
        v = None
    if v is None or not (-(1 << 31) <= v <= (1 << 32) - 1):
        raise AsmError(line, "плохое число %r" % tok)
    return v


def _reg(tok, line):
    m = _RE_REG.match(tok)
    if not m:
        raise AsmError(line, "плохой регистр %r" % tok)
    return int(m.group(1))


def _memop(tok, line):
    """'r2+16'/'r2-8'/'r2' -> (рег, смещение)."""
    m = _RE_MEMOP.match(tok)
    if not m:
        raise AsmError(line, "плохой операнд памяти %r" % tok)
    off = 0
    if m.group(2):
        off = int(m.group(3), 16 if m.group(3).startswith("0x") else 10)
        if m.group(2) == "-":
            off = -off
    return int(m.group(1)[1:]), off


def _pack2(rd, ra):
    """Байт rd:ra (SPEC/12 п. 4)."""
    return (rd << 4) | ra


def _i32(v):
    return v & 0xFFFFFFFF


def _sext64(v):
    """Знаковое значение 64-битного слова (для lt)."""
    return v - (1 << 64) if v >= (1 << 63) else v


# --- ассемблер ---------------------------------------------------------
def assemble(text):
    """Текст -> байты .UP (SPEC/13). Ошибки — AsmError с номером строки."""
    lines = text.split("\n")
    items = []                 # (строка, имя, операнды-токены)
    labels = {}                # метка -> смещение в коде
    memsize = None
    pc = 0
    pending_labels = []
    for ln, raw in enumerate(lines, 1):
        cut = raw.find(";")
        s = (raw if cut < 0 else raw[:cut]).strip()
        if not s:
            continue
        while True:
            m = re.match(r"^([a-z_][a-z0-9_]*):(?:\s+(.*))?$", s)
            if not m:
                break
            if m.group(1) in labels:
                raise AsmError(ln, "дубликат метки %s" % m.group(1))
            labels[m.group(1)] = None            # смещение — ниже
            pending_labels.append((m.group(1), pc))
            s = m.group(2) or ""
            if not s:
                break
        if not s:
            continue
        toks = _toks(s)
        if not toks:
            continue        # строка из одних разделителей — пуста (E7.3-1)
        if toks[0] == ".mem":
            if memsize is not None:
                raise AsmError(ln, "повторная .mem")
            if len(toks) != 2:
                raise AsmError(ln, ".mem принимает одно число")
            v = _num(toks[1], ln)
            if v < 0 or v > MEM_MAX:
                raise AsmError(ln, "memsize вне 0..%d" % MEM_MAX)
            memsize = v
            continue
        if toks[0].startswith("."):
            raise AsmError(ln, "неизвестная директива %r" % toks[0])
        name = toks[0]
        if name not in OPS:
            raise AsmError(ln, "неизвестная мнемоника %r" % name)
        if memsize is None:
            raise AsmError(1, "нет директивы .mem")
        items.append((ln, pc, name, toks[1:]))
        pc += FMT_LEN[OPS[name][1]]
    if memsize is None:
        raise AsmError(1, "нет директивы .mem")
    for name, at in pending_labels:
        labels[name] = at

    code = bytearray()
    for ln, at, name, args in items:
        op, fmt = OPS[name]
        if fmt == 1:
            code += _enc_f1(ln, op, name, args)
        elif fmt == 2:
            code += _enc_f2(ln, op, name, args)
        else:
            code += _enc_f3(ln, op, name, args, labels)
    return make_up(memsize, bytes(code))


def _want(ln, args, n, name):
    if len(args) != n:
        raise AsmError(ln, "%s принимает %d операнд(ов)" % (name, n))


def _enc_f1(ln, op, name, args):
    """F1: op, rd:ra, rb — mov (rb=0) и ALU."""
    if name == "mov":
        _want(ln, args, 2, name)
        rd, ra = _reg(args[0], ln), _reg(args[1], ln)
        return bytes([op, _pack2(rd, ra), 0])
    _want(ln, args, 3, name)
    rd, ra, rb = (_reg(a, ln) for a in args)
    return bytes([op, _pack2(rd, ra), rb])


def _enc_f2(ln, op, name, args):
    """F2: op, rd:ra, imm32 — const и память."""
    if name == "const":
        _want(ln, args, 2, name)
        rd, v = _reg(args[0], ln), _num(args[1], ln)
        return bytes([op, _pack2(rd, 0)]) + _i32(v).to_bytes(4, "little")
    if name in ("ldb", "ldq"):
        _want(ln, args, 2, name)
        rd, (ra, off) = _reg(args[0], ln), _memop(args[1], ln)
        return bytes([op, _pack2(rd, ra)]) + _i32(off).to_bytes(4, "little")
    _want(ln, args, 2, name)                     # stb/stq: адрес первым
    (rd, off), ra = _memop(args[0], ln), _reg(args[1], ln)
    return bytes([op, _pack2(rd, ra)]) + _i32(off).to_bytes(4, "little")


def _enc_f3(ln, op, name, args, labels):
    """F3: op, rd, imm32 — jmp/jnz/halt; цель — метка или число."""
    if name == "jmp":
        _want(ln, args, 1, name)
        v = _target(args[0], ln, labels)
        return bytes([op, 0]) + _i32(v).to_bytes(4, "little")
    if name == "jnz":
        _want(ln, args, 2, name)
        rd, v = _reg(args[0], ln), _target(args[1], ln, labels)
        return bytes([op, rd]) + _i32(v).to_bytes(4, "little")
    _want(ln, args, 1, name)                     # halt
    return bytes([op, 0]) + _i32(_num(args[0], ln)).to_bytes(4, "little")


def _target(tok, ln, labels):
    if _RE_LABEL.match(tok):
        if tok not in labels:
            raise AsmError(ln, "неизвестная метка %r" % tok)
        return labels[tok]
    return _num(tok, ln)


# --- контейнер .UP (SPEC/13) -------------------------------------------
def make_up(memsize, code):
    """(memsize, код) -> байты .UP v1."""
    if not (0 <= memsize <= MEM_MAX):
        raise UpError("MEM")
    if not (1 <= len(code) <= CODE_MAX):
        raise UpError("CODE0" if not code else "LEN")
    head = (b"UP01" + (1).to_bytes(4, "little")
            + memsize.to_bytes(8, "little")
            + len(code).to_bytes(4, "little")
            + (0).to_bytes(4, "little"))
    return head + code


def parse_up(data):
    """Байты .UP -> (memsize, код); отказы — UpError (SPEC/13 п. 4)."""
    if len(data) < 24 or data[:4] != b"UP01":
        raise UpError("SIG")
    ver = int.from_bytes(data[4:8], "little")
    if ver != 1:
        raise UpError("VER")
    memsize = int.from_bytes(data[8:16], "little")
    if memsize > MEM_MAX:
        raise UpError("MEM")
    codesize = int.from_bytes(data[16:20], "little")
    if codesize == 0:
        raise UpError("CODE0")
    if len(data) != 24 + codesize:
        raise UpError("LEN")
    if int.from_bytes(data[20:24], "little") != 0:
        raise UpError("RES")
    return memsize, data[24:]


# --- исполнитель (SPEC/12 п. 3, 5, 6, 7) --------------------------------
class RunResult:
    """Наблюдаемое поведение прогона (контракт совпадения с ядром E7.2)."""

    def __init__(self, m):
        self.exit_code = m.exit_code
        self.console = bytes(m.console)
        self.steps = m.steps
        self.trap = m.trap
        self.regs = list(m.regs)
        self.mem = bytes(m.mem)


class Machine:
    """UNIVM v0: пошаговое исполнение кода SPEC/12."""

    def __init__(self, memsize, code):
        self.memsize = memsize
        self.code = code
        self.mem = bytearray(memsize)
        self.regs = [0] * 16
        self.pc = 0
        self.console = bytearray()
        self.steps = 0
        self.trap = 0
        self.exit_code = 0
        self.halted = False

    # -- ловушка: незавершённая инструкция шагом не считается (SPEC/12 п.7)
    def _trap(self, n):
        self.trap = n
        self.halted = True

    def _byte_read(self, addr):
        """ldb: RAM -> sext8; окно -> 0; вне — ловушка 3."""
        if addr < self.memsize:
            v = self.mem[addr]
            return v - 256 if v >= 128 else v
        if addr < self.memsize + DEVWIN:
            return 0
        self._trap(TRAP_LOAD)
        return 0

    def _byte_write(self, addr, val):
        """stb: RAM -> байт; окно+0 -> консоль; окно+1.. — игнор; вне — 4."""
        if addr < self.memsize:
            self.mem[addr] = val
        elif addr < self.memsize + DEVWIN:
            if addr == self.memsize:
                self.console.append(val)
        else:
            self._trap(TRAP_STORE)

    def step(self):
        """Исполнить одну инструкцию; False — останов (halt/ловушка)."""
        if self.halted:
            return False
        pc = self.pc
        code = self.code
        if pc >= len(code):
            return self._trap(TRAP_FETCH) or False
        op = code[pc]
        if op == 0 or op not in OPNAME:
            return self._trap(TRAP_BAD) or False
        fmt = 1 if 0x02 <= op <= 0x0B else (2 if op in
                                            (0x01, 0x0C, 0x0D, 0x0E, 0x0F)
                                            else 3)
        ln = FMT_LEN[fmt]
        if pc + ln > len(code):
            return self._trap(TRAP_FETCH) or False
        r = self.regs
        if fmt == 1:
            b1, b2 = code[pc + 1], code[pc + 2]
            rd, ra = b1 >> 4, b1 & 15
            if op == 0x02:                       # mov: rb — заполнитель 0
                if b2 != 0:
                    return self._trap(TRAP_BAD) or False
                r[rd] = r[ra]
            else:
                if b2 > 15:
                    return self._trap(TRAP_BAD) or False
                a, b = r[ra], r[b2]
                if op == 0x03:
                    r[rd] = (a + b) & M64
                elif op == 0x04:
                    r[rd] = (a - b) & M64
                elif op == 0x05:
                    r[rd] = a & b
                elif op == 0x06:
                    r[rd] = a | b
                elif op == 0x07:
                    r[rd] = a ^ b
                elif op == 0x08:
                    r[rd] = (a << (b & 63)) & M64
                elif op == 0x09:
                    r[rd] = a >> (b & 63)
                elif op == 0x0A:
                    r[rd] = 1 if _sext64(a) < _sext64(b) else 0
                else:                            # 0x0B eq
                    r[rd] = 1 if a == b else 0
            self.pc = pc + 3
        elif fmt == 2:
            b1 = code[pc + 1]
            rd, ra = b1 >> 4, b1 & 15
            imm = int.from_bytes(code[pc + 2:pc + 6], "little",
                                 signed=True)
            if op == 0x01:                       # const: ra — заполнитель 0
                if ra != 0:
                    return self._trap(TRAP_BAD) or False
                r[rd] = imm & M64
            elif op == 0x0C:                     # ldb
                v = self._byte_read((r[ra] + imm) & M64)
                if self.halted:
                    return False
                r[rd] = v & M64
            elif op == 0x0D:                     # stb: база rd, источник ra
                self._byte_write((r[rd] + imm) & M64, r[ra] & 0xFF)
                if self.halted:
                    return False
            elif op == 0x0E:                     # ldq: только RAM, целиком
                addr = (r[ra] + imm) & M64
                if addr + 8 > self.memsize:
                    return self._trap(TRAP_LOAD) or False
                r[rd] = int.from_bytes(self.mem[addr:addr + 8], "little")
            else:                                # 0x0F stq
                addr = (r[rd] + imm) & M64
                if addr + 8 > self.memsize:
                    return self._trap(TRAP_STORE) or False
                self.mem[addr:addr + 8] = r[ra].to_bytes(8, "little")
            self.pc = pc + 6
        else:                                    # F3
            rd = code[pc + 1]
            imm = int.from_bytes(code[pc + 2:pc + 6], "little")
            if op == 0x10:                       # jmp: rd — заполнитель 0
                if rd != 0:
                    return self._trap(TRAP_BAD) or False
                self.pc = imm
            elif op == 0x11:                     # jnz
                if rd > 15:
                    return self._trap(TRAP_BAD) or False
                self.pc = imm if r[rd] != 0 else pc + 6
            else:                                # halt: rd — заполнитель 0
                if rd != 0:
                    return self._trap(TRAP_BAD) or False
                self.exit_code = imm
                self.halted = True
        self.steps += 1
        return True

    def run(self, max_steps=DEFAULT_MAX_STEPS):
        """Исполнение до останова; предел шагов — trap 6 (диагностика)."""
        while not self.halted:
            if self.steps >= max_steps:
                self.trap = TRAP_STEPS
                break
            self.step()
        return RunResult(self)


def run_up(data, max_steps=DEFAULT_MAX_STEPS):
    """Байты .UP -> RunResult (разбор + исполнение)."""
    memsize, code = parse_up(data)
    return Machine(memsize, code).run(max_steps)


def run_asm(text, max_steps=DEFAULT_MAX_STEPS):
    """Текст ассемблера -> RunResult (сборка + исполнение)."""
    return run_up(assemble(text), max_steps)
