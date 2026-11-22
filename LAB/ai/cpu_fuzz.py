"""cpu_fuzz.py — диффтест эмулятора: lab_thread против универсального пути.

Вход:  нет (генератор с фиксированным зерном; ~10 с).
Выход: [OK]/[FAIL] строки; код возврата 0/1.
Функция: гарантия, что «threaded code» (lab_thread.build) совпадает с
       универсальным путём (lab_cpu._op_*) на СЛУЧАЙНЫХ программах:
       два CPU с одинаковым начальным состоянием (регистры — включая
       отрицательные значения после cdqe; память — образ и стек, в т.ч.
       доступы ВНЕ регионов) исполняют одну и ту же последовательность
       инструкций — один замыканиями, второй partial(_op_*); сравниваются
       финальные состояния, счётчики шагов, полные трассы rip и
       сообщения об ошибках. call (прямой, до заглушек), push/pop,
       jmp/jcc (в пределах программы), все ALU/сдвиги/mov/movzx/lea/
       neg/inc/dec/imul/cdqe/cqo/cdq. НЕ генерируются: ret/int3 (поле
       батареи на каждом круге), idiv (не специализируется — оба пути
       универсальные). Завершение: ExitProcess заглушки (call EXIT),
       ошибка (MemoryError и пр.) или предел шагов — все три класса
       сравниваются.
Запуск: python3 LAB/ai/cpu_fuzz.py  (из корня репозитория)
"""
import os
import random
import sys
from functools import partial

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_cpu                             # noqa: E402
import lab_thread                          # noqa: E402

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261118
PROGS = 500                # программ (итоговое сравнение)
LOCK = 150                 # из них — с пошаговым сравнением состояния
INSTRS = 60                # инструкций в программе
STEPS = 4000               # предел шагов на программу
IMG_BASE = 0x140001000
IMG_SIZE = 0x2000
STACK_BASE = 0x7FF700000000
STACK_SIZE = 0x10000
CODE0 = 0x100              # смещение первой инструкции в образе
PTR_SLOT = 0x80            # слот образа с адресом EXIT (косвенный call)
PTR2_SLOT = 0x88           # слот с rip финального call EXIT (jmp FF /4)
EXIT_ADDR = 0x7FF900000000

BOUND = [0, 1, 2, 7, 0x7F, 0x80, 0xFF, 0x100, 0x7FFF, 0x8000, 0xFFFF,
         0x10000, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0x100000000,
         0x7FFFFFFFFFFFFFFF, 0x8000000000000000, (1 << 64) - 1]

CC = ["o", "no", "b", "ae", "z", "nz", "be", "a", "s", "ns", "p", "np",
      "l", "ge", "le", "g"]


def rnd_val(r):
    t = r.randrange(6)
    if t == 0:
        return r.choice(BOUND)
    if t == 1:
        return -r.choice(BOUND[:8])       # отрицательные (как после cdqe)
    if t == 2:
        return r.randrange(-64, 64)
    if t == 3:
        return r.randrange(1 << 64)
    if t == 4:
        return IMG_BASE + r.randrange(IMG_SIZE)
    return STACK_BASE + r.randrange(STACK_SIZE)


def rnd_imm(r, size):
    v = rnd_val(r)
    if size == 8:
        return v & 0xFF
    if size == 16:
        return v & 0xFFFF
    if size == 32:
        return v & 0xFFFFFFFF
    return v & ((1 << 64) - 1)


def rnd_mem(r, size):
    """Память: динамическая (base/index/disp) или riprel-константа.
    Большинство адресов — валидные (длинные трассы); каждый шестой —
    сознательно вне регионов (сравнение сообщений об ошибке)."""
    if r.randrange(6) == 0:
        if r.randrange(6):
            addr = r.choice([IMG_BASE + r.randrange(IMG_SIZE),
                             STACK_BASE + r.randrange(STACK_SIZE)])
        else:
            addr = IMG_BASE + IMG_SIZE + 0x1000      # вне регионов
        return ("m", None, None, 1, 0, size, ("abs", addr))
    base = r.choice([None, 4, 10, 5, 2, r.randrange(16)])
    index = r.choice([None, None, r.randrange(16)])
    scale = r.choice([1, 1, 2, 4, 8])
    if r.randrange(8):
        disp = r.choice([0, 8, -8, 16, -16, r.randrange(-128, 128)])
    else:
        disp = r.choice([0x7FFFFFFF, -0x80000000])
    return ("m", base, index, scale, disp, size, None)


def rnd_rm(r, size, allow_imm=True):
    t = r.randrange(10)
    if t < 4:
        return ("r", r.randrange(16), size)
    if t < 6 and allow_imm:
        return ("i", rnd_imm(r, size), size)
    return rnd_mem(r, size)


def gen_prog(r):
    prog = []
    rips = [IMG_BASE + CODE0 + i for i in range(INSTRS)]
    for _i in range(INSTRS - 2):
        t = r.randrange(100)
        size = r.choice([8, 16, 32, 64])
        if t < 22:                        # mov (mem,mem не бывает — как
            dst = rnd_rm(r, size, False)  # в реальном подмножестве)
            if dst[0] == "m":
                src = ("r", r.randrange(16), size)
            else:
                src = rnd_rm(r, size)
            prog.append(("mov", (dst, src)))
        elif t < 28:                       # movzx: dst 32/64, src 8/16
            prog.append(("movzx", (("r", r.randrange(16),
                                    r.choice([32, 64])),
                                   rnd_rm(r, r.choice([8, 16]), False))))
        elif t < 32:                       # lea
            prog.append(("lea", (("r", r.randrange(16), 64),
                                 rnd_mem(r, 64))))
        elif t < 50:                       # ALU (mem,mem не бывает)
            op = r.choice(["add", "sub", "cmp", "test", "and", "or",
                           "xor"])
            dst = rnd_rm(r, size, False)
            if dst[0] == "m":
                src = rnd_rm(r, size)      # reg или imm
                if src[0] == "m":
                    src = ("r", r.randrange(16), size)
            else:
                src = rnd_rm(r, size)
            prog.append((op, (dst, src)))
        elif t < 56:
            prog.append((r.choice(["neg", "inc", "dec"]),
                         (rnd_rm(r, size, False),)))
        elif t < 62:                       # сдвиги
            cnt = r.choice([r.randrange(64), "cl"])
            prog.append((r.choice(["shl", "shr", "sar", "rol"]),
                         (rnd_rm(r, size, False), cnt)))
        elif t < 66:                       # imul
            prog.append(("imul", (("r", r.randrange(16), size),
                                  rnd_rm(r, size, False))))
        elif t < 72:
            op = r.choice(["cdqe", "cqo", "cdq"])
            if op == "cdqe":              # декодер всегда даёт args
                prog.append((op, (("r", 0, r.choice([32, 64])),)))
            else:
                prog.append((op, ()))
        elif t < 78:                       # push/pop
            prog.append((r.choice(["push", "pop"]),
                         (("r", r.randrange(16), 64),)))
        elif t < 94:                       # jcc/jmp в пределах программы
            tgt = r.choice(rips)
            if r.randrange(2):
                prog.append(("jcc", (r.choice(CC), ("t", tgt))))
            elif r.randrange(3) == 0:    # E9.4-1: косвенный jmp — [rip+PTR2]
                prog.append(("jmp", (("m", None, None, 1, 0, 64,
                                       ("abs", IMG_BASE + PTR2_SLOT)),)))
            elif r.randrange(3) == 1:    # E9.4-1: косвенный jmp — r64
                prog.append(("jmp", (("r", r.randrange(16), 64),)))
            else:
                prog.append(("jmp", (("t", tgt),)))
        else:                              # call: прямой EXIT или
            if r.randrange(2):              # косвенный (через память)
                prog.append(("call", (("t", EXIT_ADDR),)))
            elif r.randrange(2):            # слот с адресом EXIT
                prog.append(("call", (("m", None, None, 1, 0, 32,
                                       ("abs", IMG_BASE + PTR_SLOT)),)))
            else:                           # случайная память
                prog.append(("call", (rnd_mem(r, 32),)))
    prog.append(("call", (("t", EXIT_ADDR),)))
    prog.append(("jmp", (("t", rips[-1]),)))     # замкнуть хвост
    return prog


def _exit_stub(cpu):
    raise lab_cpu.ExitProcess(7)


def make_cpu(seed, prog, spec, overlap=False):
    r = random.Random(seed)
    image = bytearray(IMG_SIZE)
    stack = bytearray(STACK_SIZE)
    for i in range(0, IMG_SIZE, 7):
        image[i] = r.randrange(256)
    for i in range(0, STACK_SIZE, 11):
        stack[i] = r.randrange(256)
    image[PTR_SLOT:PTR_SLOT + 8] = EXIT_ADDR.to_bytes(8, "little")
    # E9.4-1: слот косвенного jmp — rip финального call EXIT (чистый выход)
    image[PTR2_SLOT:PTR2_SLOT + 8] = \
        (IMG_BASE + CODE0 + len(prog) - 2).to_bytes(8, "little")
    if overlap:
        # ПЕРЕКРЫВАЮЩИЕСЯ регионы: memo запрещена (cpu.memo None) —
        # разрешение всегда первым совпавшим (как _region)
        shadow = bytearray(IMG_SIZE)
        regions = [(IMG_BASE, image),
                   (IMG_BASE + IMG_SIZE // 2, shadow),
                   (STACK_BASE, stack)]
    else:
        regions = [(IMG_BASE, image), (STACK_BASE, stack)]
    cpu = lab_cpu.CPU(image, IMG_BASE, regions)
    cpu.r[4] = STACK_BASE + STACK_SIZE // 2
    for i in range(16):
        if i != 4:
            cpu.r[i] = rnd_val(r)
    cpu.stubs[EXIT_ADDR] = _exit_stub
    cpu.trace = []
    for i, (name, args) in enumerate(prog):
        if spec:
            fn = lab_thread.build(cpu, name, args)   # как в _decode:
            if fn is None:                            # отказ -> fallback
                fn = partial(cpu._fb, name, args)
        else:
            fn = partial(cpu._fb, name, args)
        cpu.cache[IMG_BASE + CODE0 + i] = (name, 1, fn)
    cpu.rip = IMG_BASE + CODE0
    return cpu


def run_cpu(cpu):
    try:
        cpu.run(STEPS)
        return ("end", None)
    except lab_cpu.ExitProcess as e:
        return ("exit", e.code)
    except Exception as e:                 # noqa: BLE001
        return ("err", "%s: %s" % (type(e).__name__, e))


def exc_key(e):
    return (type(e).__name__, str(e), getattr(e, "code", None))


def lockstep(c1, c2, cap):
    """Пошаговое сравнение ПОСЛЕ КАЖДОГО шага (rip/regs/флаги и
    исключения). None — идентичны; иначе описание расхождения."""
    while True:
        if c1.rip != c2.rip or c1.r != c2.r or c1.fl != c2.fl:
            return "состояние после шага %d: rip %X/%X fl %r/%r" % (
                c1.steps, c1.rip, c2.rip, c1.fl, c2.fl)
        try:
            c1.step()
        except Exception as e1:            # noqa: BLE001
            try:
                c2.step()
            except Exception as e2:        # noqa: BLE001
                return None if exc_key(e1) == exc_key(e2) else \
                    "исключение: %r vs %r" % (exc_key(e1), exc_key(e2))
            return "исключение только в замыкании: %r" % (exc_key(e1),)
        try:
            c2.step()
        except Exception as e2:            # noqa: BLE001
            return "исключение только в универсальном: %r" % (exc_key(e2),)
        if c1.steps >= cap:
            return None


def main():
    r = random.Random(SEED)
    n_spec = 0
    n_fb = 0
    total = 0
    for p in range(PROGS):
        prog = gen_prog(r)
        seed = r.randrange(1 << 30)
        ovl = (seed % 3 == 0)         # каждый третий — перекрытие
        c1 = make_cpu(seed, prog, True, ovl)
        c2 = make_cpu(seed, prog, False, ovl)
        for i, (name, args) in enumerate(prog):
            if isinstance(c1.cache[IMG_BASE + CODE0 + i][2], partial):
                n_fb += 1                # форма без специализации
            else:
                n_spec += 1
        e1, e2 = run_cpu(c1), run_cpu(c2)
        ok = (e1 == e2 and c1.steps == c2.steps and c1.r == c2.r and
              c1.fl == c2.fl and
              all(bytes(x[1]) == bytes(y[1]) for x, y in
                  zip(c1.regions, c2.regions)) and
              c1.trace == c2.trace)
        note = ""
        if ok and p < LOCK:               # глубокое сравнение: каждый шаг
            c3 = make_cpu(seed, prog, True, ovl)
            c4 = make_cpu(seed, prog, False, ovl)
            d = lockstep(c3, c4, STEPS)
            if d is not None:
                ok = False
                note = "lockstep: " + d
                c1, c2 = c3, c4          # для отчёта — пошаговые копии
        if not ok:
            print("[FAIL] программа %d: расхождение" % p)
            if note:
                print("  " + note)
            for k, name in enumerate(["итог", "шаги", "regs", "fl",
                                      "image", "stack", "trace"]):
                v1 = (e1, c1.steps, c1.r, c1.fl,
                      bytes(c1.regions[0][1]), bytes(c1.regions[1][1]),
                      c1.trace)[k]
                v2 = (e2, c2.steps, c2.r, c2.fl,
                      bytes(c2.regions[0][1]), bytes(c2.regions[1][1]),
                      c2.trace)[k]
                if v1 != v2:
                    if name in ("image", "stack"):
                        i0 = next((j for j in
                                   range(min(len(v1), len(v2)))
                                   if v1[j] != v2[j]), -1)
                        v1 = "первый отличающийся байт @%d" % i0
                        v2 = ""
                    if name == "trace" and isinstance(v1, list):
                        v1 = "%d записей, до %r" % (len(v1), v1[-8:])
                        v2 = "%d записей, до %r" % (len(v2), v2[-8:])
                    print("  %s: замыкание=%r универсальный=%r"
                          % (name, v1, v2))
            print("  программа (первые 25):")
            for name, args in prog[:25]:
                print("   ", name, args)
            return 1
        if p % 100 == 0:
            print("[OK] %d/%d программ (итог %r, шагов %d%s)"
                  % (p, PROGS, e1[0], c1.steps,
                     "; lockstep" if p < LOCK else ""))
        total += c1.steps
    print("\nИТОГ: %d/%d программ идентичны (%d пошагово); замыканий %d,"
          " fallback %d; всего шагов %d"
          % (PROGS, PROGS, LOCK, n_spec, n_fb, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
