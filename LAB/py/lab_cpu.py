"""lab_cpu.py — эмулятор x86-64 (исполнитель инструкций).

Вход:  память-регионы (объект с read/write), начальный rip.
Выход: состояние CPU: регистры, флаги, rip; пошаговое исполнение.
Функция: исполнять декодированные lab_x86 инструкции подмножества
         SPEC/05 с Win64-семантикой; состав файла (E6.4d-5/0):
         CPU (кэш/цикл/память/флаги) + «threaded code» lab_thread
         (замыкания под конкретную форму операндов — «зашитые»
         константы; построители тел — lab_thread_ops) + универсальный
         путь _op_<имя> (референс — примесь lab_cpu_ops.OpsMixin;
         диффтест путей — LAB/ai/cpu_fuzz.py).

Память: регион = (base, bytearray). Доступ — read/write с выбором
        региона по адресу. Уровни скорости: кэш инструкций по rip (код
        самомодифицируемым не бывает) + замыкания lab_thread +
        одноэлементная подсказка региона memo (только при
        непересекающихся регионах). Инварианты для замыканий:
        r/fl/rscan/stubs НЕ перевязываются (только мутируются);
        fl = [zf, cf, sf, of] — всегда 0/1.
"""
import lab_x86
import lab_thread
from functools import partial
from lab_cpu_ops import (OpsMixin, M64, M32, BYTE, WORD, DWORD,
                         QWORD, NBYTES, _CC)  # noqa: F401 — реэкспорт


class ExitProcess(Exception):
    """ExitProcess(код) от заглушки Win32."""

    def __init__(self, code):
        self.code = code


class CPU(OpsMixin):
    def __init__(self, image, image_base, regions=None):
        self.img = image              # bytearray образа (заголовки+секции)
        self.img_base = image_base    # виртуальный адрес image[0]
        self.regions = [(image_base, image)] if regions is None else \
            regions
        self.r = [0] * 16             # rax..r15 (беззнаковые 64-бит)
        self.fl = [0, 0, 0, 0]        # [zf, cf, sf, of] — всегда 0/1;
                                      # захватывается lab_thread
        self.rip = 0
        self.stubs = {}               # адрес заглушки -> callable(cpu)
        self.retguard = None          # адрес-ловушка возврата из entry
        self.cache = {}               # rip -> (имя, длина, fn)
        self.trace = None             # опционально: collect list
        self.steps = 0
        self.rscan = [(b, b + len(m), m) for b, m in self.regions]
        # подсказка региона для lab_thread (одноэлементный кэш): только
        # при НЕпересекающихся регионах — иначе совпадение с подсказкой
        # могло бы отличаться от первого совпадения _region
        ovl = any(self.rscan[i][0] < self.rscan[j][1] and
                  self.rscan[j][0] < self.rscan[i][1]
                  for i in range(len(self.rscan))
                  for j in range(i + 1, len(self.rscan)))
        self.memo = None if ovl else [0, 0, None]

    # --- флаги: совместимый доступ zf/cf/sf/of поверх списка fl ---
    def _get_zf(self):
        return self.fl[0]

    def _set_zf(self, v):
        self.fl[0] = v

    zf = property(_get_zf, _set_zf)

    def _get_cf(self):
        return self.fl[1]

    def _set_cf(self, v):
        self.fl[1] = v

    cf = property(_get_cf, _set_cf)

    def _get_sf(self):
        return self.fl[2]

    def _set_sf(self, v):
        self.fl[2] = v

    sf = property(_get_sf, _set_sf)

    def _get_of(self):
        return self.fl[3]

    def _set_of(self, v):
        self.fl[3] = v

    of = property(_get_of, _set_of)

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

    # --- исполнение ---
    def _fb(self, name, args, nrip):
        # универсальный путь (fallback): та же семантика, что у
        # замыканий lab_thread — rip ПО достоинству инструкции,
        # возврат — следующий rip (переходы оставляют свой в self.rip)
        self.rip = nrip
        getattr(self, "_op_" + name)(*args)
        return self.rip

    def _decode(self, rip):
        # декодировать rip ОДИН раз и построить замыкание под конкретную
        # форму операндов (lab_thread; None — универсальный _fb/_op_*;
        # прежде на каждом шаге был getattr + fn(*args) с разбором
        # операндов внутри — ускорение E6.4d-5/0)
        name, length, args = lab_x86.decode(self.fetch, rip)
        fn = lab_thread.build(self, name, args)
        if fn is None:
            fn = partial(self._fb, name, args)
        full = (name, length, fn)
        self.cache[rip] = full
        return full

    def step(self):
        # пошаговое исполнение (трассировщики LAB/ai); порядок тот же,
        # что в run(): замыканию передаётся продвижение rip, следующий
        # rip — возврат замыкания
        rip = self.rip
        ins = self.cache.get(rip)
        if ins is None:
            ins = self._decode(rip)
        name, length, fn = ins
        if self.trace is not None:
            self.trace.append(rip)
        self.steps += 1
        self.rip = fn(rip + length)
        return name

    def run(self, max_steps=100_000_000):
        # Горячий цикл, развёрнутый из step() (ускорения E6.4d-3/3-1 и
        # E6.4d-5/0): замыкание ВОЗВРАЩАЕТ следующий rip — присвоение
        # атрибута self.rip на каждом шаге не нужно (синхронизация — в
        # finally); без трассы — отдельная ветка цикла (без проверки).
        # Счётчики шагов и сообщения об ошибках идентичны прежним.
        cache_get = self.cache.get
        steps = self.steps
        rip = self.rip
        try:
            if self.trace is None:
                while True:
                    ins = cache_get(rip)
                    if ins is None:
                        ins = self._decode(rip)
                    steps += 1
                    rip = ins[2](rip + ins[1])
                    if steps > max_steps:
                        raise RuntimeError("предел шагов (зависание?)"
                                           " @ rip=%X" % rip)
            else:
                trace = self.trace
                while True:
                    ins = cache_get(rip)
                    if ins is None:
                        ins = self._decode(rip)
                    trace.append(rip)
                    steps += 1
                    rip = ins[2](rip + ins[1])
                    if steps > max_steps:
                        raise RuntimeError("предел шагов (зависание?)"
                                           " @ rip=%X" % rip)
        finally:
            self.steps = steps
            self.rip = rip
