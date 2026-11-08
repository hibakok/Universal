"""lab_cpu.py — эмулятор x86-64 (исполнитель инструкций).

Вход:  память-регионы (объект с read/write), начальный rip.
Выход: состояние CPU: регистры, флаги, rip; пошаговое исполнение.
Функция: исполнять декодированные lab_x86 инструкции подмножества
         SPEC/05 с Win64-семантикой (32-битные записи обнуляют
         старшие биты; imm8/imm32 знакорасширяются; rol не трогает ZF).

Память: регион = (base, bytearray). Доступ — read/write с выбором
        региона по адресу. Три уровня скорости: кэш декодированных
        инструкций по rip (код самомодифицируемым не бывает).
"""
import lab_x86

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
BYTE, WORD, DWORD, QWORD = 8, 16, 32, 64
NBYTES = {BYTE: 1, WORD: 2, DWORD: 4, QWORD: 8}


class ExitProcess(Exception):
    """ExitProcess(код) от заглушки Win32."""

    def __init__(self, code):
        self.code = code


class CPU:
    def __init__(self, image, image_base, regions=None):
        self.img = image              # bytearray образа (заголовки+секции)
        self.img_base = image_base    # виртуальный адрес image[0]
        self.regions = [(image_base, image)] if regions is None else \
            regions
        self.r = [0] * 16             # rax..r15 (беззнаковые 64-бит)
        self.zf = self.cf = self.sf = self.of = 0
        self.rip = 0
        self.stubs = {}               # адрес заглушки -> callable(cpu)
        self.retguard = None          # адрес-ловушка возврата из entry
        self.cache = {}               # rip -> (имя, длина, args)
        self.trace = None             # опционально: collect list
        self.steps = 0

    # --- память образа (код и данные секции; маленькие куски) ---
    def fetch(self, addr, n):
        off = addr - self.img_base
        v = int.from_bytes(self.img[off:off + n], "little")
        return v

    def _region(self, addr, n):
        # расширяемая память: образ + внешние регионы (стек и пр.)
        for base, buf in self.regions:
            if base <= addr and addr + n <= base + len(buf):
                return buf, addr - base
        raise MemoryError("доступ вне регионов: %X (+%d)" % (addr, n))

    def read(self, addr, n):
        buf, off = self._region(addr, n)
        return int.from_bytes(buf[off:off + n], "little")

    def write(self, addr, n, val):
        buf, off = self._region(addr, n)
        buf[off:off + n] = (val & ((1 << (n * 8)) - 1)).to_bytes(n,
                                                                "little")

    # --- операнды ---
    def _opaddr(self, op):
        _, base, index, scale, disp, _sz, ripinfo = op
        if ripinfo is not None:      # ('abs', адрес)
            return ripinfo[1]
        addr = disp
        if base is not None:
            addr += self.r[base]
        if index is not None:
            addr += self.r[index] * scale
        return addr & M64

    def get(self, op):
        kind = op[0]
        if kind == "r":
            _, idx, size = op
            if size == BYTE:
                return self.r[idx] & 0xFF
            if size == WORD:
                return self.r[idx] & 0xFFFF
            if size == DWORD:
                return self.r[idx] & M32
            return self.r[idx]
        if kind == "i":
            return op[1]
        if kind == "m":
            n = NBYTES[op[5]]
            return self.read(self._opaddr(op), n)
        raise ValueError(op)

    def put(self, op, val):
        kind = op[0]
        if kind == "r":
            _, idx, size = op
            if size == BYTE:
                self.r[idx] = (self.r[idx] & ~0xFF) | (val & 0xFF)
            elif size == WORD:
                self.r[idx] = (self.r[idx] & ~0xFFFF) | (val & 0xFFFF)
            elif size == DWORD:
                self.r[idx] = val & M32        # 32-бит запись обнуляет
            else:
                self.r[idx] = val & M64
            return
        if kind == "m":
            n = NBYTES[op[5]]
            self.write(self._opaddr(op), n, val)
            return
        raise ValueError(op)

    # --- флаги ---
    def _flags_logic(self, res, size):
        mask = (1 << size) - 1
        res &= mask
        self.zf = 1 if res == 0 else 0
        self.sf = 1 if (res >> (size - 1)) & 1 else 0
        self.cf = 0
        self.of = 0
        return res

    def _flags_add(self, a, b, size):
        mask = (1 << size) - 1
        res = (a + b) & mask
        self.zf = 1 if res == 0 else 0
        self.sf = (res >> (size - 1)) & 1
        self.cf = 1 if (a + b) > mask else 0
        sa = (a >> (size - 1)) & 1
        sb = (b >> (size - 1)) & 1
        sr = self.sf
        self.of = 1 if (sa == sb and sr != sa) else 0
        return res

    def _flags_sub(self, a, b, size):
        mask = (1 << size) - 1
        res = (a - b) & mask
        self.zf = 1 if res == 0 else 0
        self.sf = (res >> (size - 1)) & 1
        self.cf = 1 if a < b else 0
        sa = (a >> (size - 1)) & 1
        sb = (b >> (size - 1)) & 1
        self.of = 1 if (sa != sb and self.sf != sa) else 0
        return res

    # --- исполнение ---
    def step(self):
        rip = self.rip
        ins = self.cache.get(rip)
        if ins is None:
            ins = lab_x86.decode(self.fetch, rip)
            self.cache[rip] = ins
        name, length, args = ins
        if self.trace is not None:
            self.trace.append(rip)
        self.steps += 1
        self.rip = rip + length
        getattr(self, "_op_" + name)(*args)
        return name

    def run(self, max_steps=100_000_000):
        while True:
            self.step()
            if self.steps > max_steps:
                raise RuntimeError("предел шагов (зависание?) @ rip=%X"
                                   % self.rip)

    # --- инструкции ---
    def _op_mov(self, dst, src):
        self.put(dst, self.get(src))

    def _op_movzx(self, dst, src):
        self.put(dst, self.get(src))

    def _op_lea(self, dst, mem):
        self.put(dst, self._opaddr(mem))

    def _op_cdqe(self, reg):
        eax = self.r[0] & M32
        self.r[0] = eax - (1 << 32) if eax & 0x80000000 else eax

    def _op_add(self, dst, src):
        size = dst[2] if dst[0] == "r" else dst[5]
        a, b = self.get(dst), self.get(src)
        self.put(dst, self._flags_add(a, b, size))

    def _op_sub(self, dst, src):
        size = dst[2] if dst[0] == "r" else dst[5]
        a, b = self.get(dst), self.get(src)
        self.put(dst, self._flags_sub(a, b, size))

    def _op_cmp(self, a_op, b_op):
        size = a_op[2] if a_op[0] == "r" else a_op[5]
        self._flags_sub(self.get(a_op), self.get(b_op), size)

    def _op_test(self, a_op, b_op):
        size = a_op[2] if a_op[0] == "r" else a_op[5]
        self._flags_logic(self.get(a_op) & self.get(b_op), size)

    def _op_and(self, dst, src):
        size = dst[2] if dst[0] == "r" else dst[5]
        res = self._flags_logic(self.get(dst) & self.get(src), size)
        self.put(dst, res)

    def _op_or(self, dst, src):
        size = dst[2] if dst[0] == "r" else dst[5]
        res = self._flags_logic(self.get(dst) | self.get(src), size)
        self.put(dst, res)

    def _op_xor(self, dst, src):
        size = dst[2] if dst[0] == "r" else dst[5]
        res = self._flags_logic(self.get(dst) ^ self.get(src), size)
        self.put(dst, res)

    def _op_neg(self, op):
        size = op[2] if op[0] == "r" else op[5]
        a = self.get(op)
        mask = (1 << size) - 1
        self.cf = 1 if a != 0 else 0
        res = (-a) & mask
        self.zf = 1 if res == 0 else 0
        self.sf = (res >> (size - 1)) & 1
        # OF: только для минимального значения (INT_MIN)
        self.of = 1 if a == (1 << (size - 1)) else 0
        self.put(op, res)

    def _op_inc(self, op):
        size = op[2] if op[0] == "r" else op[5]
        cf = self.cf
        self.put(op, self._flags_add(self.get(op), 1, size))
        self.cf = cf                    # inc не трогает CF

    def _op_dec(self, op):
        size = op[2] if op[0] == "r" else op[5]
        cf = self.cf
        self.put(op, self._flags_sub(self.get(op), 1, size))
        self.cf = cf                    # dec не трогает CF

    def _cl(self, count, size=64):
        """Счётчик сдвига: imm или CL. 64-бит — маска 6 бит (REX.W),
        прочие — 5 (правило Intel; найдено E6.2: shr rax,32)."""
        if count != "cl":
            return count
        return self.r[1] & (0x3F if size == QWORD else 0x1F)

    def _op_shl(self, op, count):
        size = op[2] if op[0] == "r" else op[5]
        count = self._cl(count, size)
        if count == 0:
            return
        mask = (1 << size) - 1
        a = self.get(op)
        full = a << count
        res = full & mask
        self.cf = (full >> size) & 1
        self.zf = 1 if res == 0 else 0
        self.sf = (res >> (size - 1)) & 1
        self.put(op, res)

    def _op_shr(self, op, count):
        size = op[2] if op[0] == "r" else op[5]
        count = self._cl(count, size)
        if count == 0:
            return
        a = self.get(op)
        self.cf = (a >> (count - 1)) & 1
        res = a >> count
        self.zf = 1 if res == 0 else 0
        self.sf = (res >> (size - 1)) & 1
        self.put(op, res)

    def _op_rol(self, op, count):
        size = op[2] if op[0] == "r" else op[5]
        cnt = self._cl(count, size)
        if cnt == 0:
            return
        bits = size
        a = self.get(op)
        c = cnt % bits
        res = ((a << c) | (a >> (bits - c))) & ((1 << bits) - 1) if c \
            else a
        self.cf = res & 1               # rol НЕ трогает ZF/SF
        self.put(op, res)

    def _op_sar(self, op, count):
        size = op[2] if op[0] == "r" else op[5]
        count = self._cl(count, size)
        if count == 0:
            return
        a = self.get(op)
        bits = size
        sa = a >> (bits - 1)
        val = a
        for _ in range(count):
            val = (val >> 1) | (sa << (bits - 1))
        self.cf = (a >> 0) & 1
        self.zf = 1 if val == 0 else 0
        self.sf = (val >> (bits - 1)) & 1
        self.put(op, val)

    # --- переходы ---
    def _cond(self, cc):
        zf, cf, sf, of = self.zf, self.cf, self.sf, self.of
        return {"o": of, "no": 1 - of, "b": cf, "ae": 1 - cf,
                "z": zf, "nz": 1 - zf, "be": cf | zf,
                "a": (1 - cf) & (1 - zf), "s": sf, "ns": 1 - sf,
                "p": 0, "np": 1, "l": sf ^ of, "ge": 1 - (sf ^ of),
                "le": zf | (sf ^ of),
                "g": (1 - zf) & (1 - (sf ^ of))}[cc]

    def _op_jmp(self, target):
        self.rip = target[1]

    def _op_jcc(self, cc, target):
        if self._cond(cc):
            self.rip = target[1]

    def _op_call(self, target):
        if target[0] == "t":
            dest = target[1]
        else:                            # косвенный: FF /2 по памяти
            dest = self.read(self._opaddr(target), 8)
        stub = self.stubs.get(dest)
        if stub is not None:
            stub(self)                   # вызов Win32; rip уже за call
            return
        if dest == self.retguard:
            raise RuntimeError("call на ловушку возврата @ %X" % self.rip)
        self.push64(self.rip)
        self.rip = dest

    def _op_ret(self):
        dest = self.pop64()
        if dest == self.retguard:
            raise RuntimeError("возврат из точки входа (нет ExitProcess)")
        self.rip = dest

    def _op_int3(self):
        raise RuntimeError("int3 (страховка) @ rip=%X — поток дошёл до "
                           "ловушки" % (self.rip - 1))

    def _op_push(self, reg):
        self.push64(self.get(reg))

    def _op_pop(self, reg):
        self.put(reg, self.pop64())

    # --- стек ---
    def push64(self, val):
        self.r[4] = (self.r[4] - 8) & M64
        self.write(self.r[4], 8, val)

    def pop64(self):
        val = self.read(self.r[4], 8)
        self.r[4] = (self.r[4] + 8) & M64
        return val
