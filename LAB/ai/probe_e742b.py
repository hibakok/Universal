"""probe_e742b.py — прототип алгоритмов среза E7.4-2b (LAB/ai; внешний
инструмент диагностики, НЕ часть системы UNIVERSAL).

Проверяет ДО интеграции в ядро два кирпича ветви V (новая часть
kernel_self_alu.wall):
  1) udivmod(a, b) — беззнаковое деление 64-битных слов на языке WALL,
     собранное из простых операций (в WALL только ЗНАКОВЫЕ * / % и
     ЛОГИЧЕСКИЙ >> — SPEC/11 п. 1/2): беззнаковое сравнение — трюк XOR
     знакового бита (a ^ (1<<63) >= b ^ (1<<63) знаково == a >= b
     беззнаково); случай b > 2^63 — частное {0,1} без цикла (иначе
     2r+бит переполнил бы 64 бита); иначе — восстанавливающее деление
     бит за битом (64 итерации; инвариант r < b <= 2^63 — переполнения
     сдвига r << 1 нет). Результат: глобали uq (частное), ur (остаток).
  2) sra64(v, n) — арифметический сдвиг вправо из логического:
     v >= 0 (знаково) — просто v >> n; v < 0 — (v >> n) | маска
     верхних n битов (маска = -(1 << (64-n)); n = 0 — без сдвига).

Метод: генерируется WALL-программа с фиксированными краевыми случаями
+ фаззи (детерминированные псевдослучайные 64-битные операнды),
компилируется ОРАКУЛОМ WALL (lab_l2.compile_wall -> lab_enc.normalize
-> lab_brick.assemble -> lab_pegen.wrap) и исполняется эмулятором LAB;
stdout (байты результатов LE) сверяется с эталоном Python (divmod /
арифметический сдвиг дополнения до двух). Плюс проверка mul: WALL
`*` = imul — младшие 64 бита совпадают с беззнаковым произведением.

Запуск: python3 LAB/ai/probe_e742b.py  (из корня репозитория)
"""
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_brick        # noqa: E402
import lab_enc          # noqa: E402
import lab_l2           # noqa: E402
import lab_pegen        # noqa: E402
import lab_run          # noqa: E402

M64 = (1 << 64) - 1
SIGN = 1 << 63

# --- эталонная семантика (Python) ---------------------------------------

def sext64(v):
    """Знаковое значение 64-битного слова (как _sext64 оракула)."""
    return v - (1 << 64) if v >= SIGN else v


def ref_udivmod(a, b):
    return a // b, a % b                    # беззнаковые (0 <= a,b < 2^64)


def ref_sra(v, n):
    return (sext64(v) >> (n & 63)) & M64    # арифметический сдвиг


def ref_mul(a, b):
    return (a * b) & M64                    # младшие 64 бита


# --- WALL-исходник прототипа --------------------------------------------

FUNCS = """\
; беззнаковое деление a на b (b != 0): uq = a div b, ur = a mod b.
; Беззнаковое сравнение — XOR знакового бита + знаковое сравнение WALL;
; b > 2^63 — частное 0/1 (a < 2^64 <= 2b); иначе восстанавливающее
; деление бит за битом: инвариант r < b <= 2^63 — сдвиг r << 1 не
; переполняет 64 бита (2r+1 <= 2^64-1).
func udivmod(a, b)
  var i
  var r
  var s
  s = 1 << 63
  if (b ^ s) > 0
    uq = 0
    ur = a
    if (a ^ s) >= (b ^ s)
      uq = 1
      ur = a - b
    end
    return 0
  end
  uq = 0
  r = 0
  i = 63
  while i >= 0
    r = (r << 1) | ((a >> i) & 1)
    if (r ^ s) >= (b ^ s)
      r = r - b
      uq = uq | (1 << i)
    end
    i = i - 1
  end
  ur = r
  return 0
end

; арифметический сдвиг вправо v >> n (n — счётчик сырой, маска 63):
; v >= 0 (знаково) — логический сдвиг совпадает; v < 0 — логический
; сдвиг + маска верхних n битов (n > 0; маска = -(1 << (64-n)))
func sra64(v, n)
  n = n & 63
  if v < 0
    if n > 0
      v = (v >> n) | (-(1 << (64 - n)))
    end
  else
    v = v >> n
  end
  return v
end

; младшие 64 бита произведения (WALL * = imul — тот же битовый образ)
func mul64(a, b)
  return a * b
end

; сборка 64-битной константы из четырёх 16-битных слов (литерали WALL
; ограничены 0..2^31-1 — SPEC/11 п. 9)
func big4(w3, w2, w1, w0)
  return (w3 << 48) | (w2 << 32) | (w1 << 16) | w0
end

; 8 байт значения v (LE, битовый образ) в buf с позиции k; возврат k+8
func emit64(k, v)
  var j
  j = 0
  while j < 8
    setb(buf, k + j, (v >> (j * 8)) & 255)
    j = j + 1
  end
  return k + 8
end
"""

HEAD = """\
; probe_e742b.wall — прототип E7.4-2b (udivmod/sra/mul на WALL)
ext GetStdHandle
ext WriteFile
ext ExitProcess

var hstdout
var written
var buf[256]
var uq
var ur

"""

PEG = """\
; UNIVERSAL / PEG v1 / обёртка WALL v2 (SPEC/11)
!module probe742b
!entry 1200
!idata 1000 28
!iat 1028 48
!stackcom 4000
!heapcom 4000
"""


def wall_big(v):
    """64-битная константа как big4(...) из четырёх литералей <= 65535."""
    return "big4(%d, %d, %d, %d)" % (v >> 48, (v >> 32) & 0xFFFF,
                                      (v >> 16) & 0xFFFF, v & 0xFFFF)


def build_src(divs, sras, muls):
    """WALL-исходник: main печатает байты результатов всех случаев."""
    lines = [HEAD, FUNCS, "func main", "  var k", "  var t",
             "  hstdout = GetStdHandle(-11)", "  k = 0"]
    for a, b in divs:
        lines.append("  udivmod(%s, %s)" % (wall_big(a), wall_big(b)))
        lines.append("  k = emit64(k, uq)")
        lines.append("  k = emit64(k, ur)")
    for v, n in sras:
        lines.append("  t = sra64(%s, %d)" % (wall_big(v), n))
        lines.append("  k = emit64(k, t)")
    for a, b in muls:
        lines.append("  t = mul64(%s, %s)" % (wall_big(a), wall_big(b)))
        lines.append("  k = emit64(k, t)")
    lines += ["  WriteFile(hstdout, buf, k, &written, 0)",
              "  ExitProcess(0)", "end", ""]
    return "\n".join(lines)


def expected(divs, sras, muls):
    out = b""
    for a, b in divs:
        q, r = ref_udivmod(a, b)
        out += q.to_bytes(8, "little") + r.to_bytes(8, "little")
    for v, n in sras:
        out += ref_sra(v, n).to_bytes(8, "little")
    for a, b in muls:
        out += ref_mul(a, b).to_bytes(8, "little")
    return out


def run_probe():
    # краевые случаи деления: границы путей b > 2^63 / b == 2^63 /
    # b < 2^63; a = 0/максимум; b = 1/максимум; оба старших бита
    divs = [
        (100, 7), (7, 100), (0, 5), (5, 1),
        (M64, 1), (M64, M64), (M64, 3),
        (M64, SIGN), (SIGN, 3), (SIGN + 7, SIGN),
        (M64, SIGN + 5), (5, SIGN + 5),            # путь b > 2^63
        (SIGN, SIGN), (123456789, 10000),
        (SIGN + 1, 7), (SIGN - 1, 2), (1 << 62, 3),
        ((1 << 62) * 3 + 1, 3), (M64 - 1, SIGN - 1),
        (0xF0F0F0F0F0F0F0F0, 0x0F0F0F0F0F0F0F0F),
        (0xDEADBEEFCAFEBABE, 0x1234567890ABCDEF),
    ]
    sras = [
        (M64, 0), (M64, 1), (M64, 63), (M64, 2),
        (SIGN, 63), (SIGN, 1), (SIGN, 0), (SIGN, 62),
        (-5 & M64, 1), (-5 & M64, 2), (-3 & M64, 70),   # 70 & 63 = 6
        (5, 1), (5, 2), (0, 37), (1 << 62, 2),
        (SIGN + 5, 3), (M64 - 2, 63), (123456789, 7),
        (SIGN, 64), (7, 63),                            # 64 & 63 = 0
    ]
    muls = [
        (M64, M64), (M64, 3), (3, M64), (0, M64), (1, M64),
        (SIGN, 2), (SIGN, SIGN), (0x123456789, 0x987654321),
        (M64 - 1, M64 - 1), (SIGN + 7, 3),
    ]
    # фаззи: детерминированные псевдослучайные операнды
    rng = random.Random(74274)
    for _ in range(48):
        divs.append((rng.getrandbits(64), rng.getrandbits(64) or 1))
    for _ in range(24):
        sras.append((rng.getrandbits(64), rng.randrange(0, 130)))
    for _ in range(16):
        muls.append((rng.getrandbits(64), rng.getrandbits(64)))

    src = build_src(divs, sras, muls)
    b2 = lab_l2.compile_wall(src)
    body = lab_brick.assemble(lab_enc.normalize(b2).encode())
    exe = lab_pegen.wrap(body, PEG)

    fd, path = tempfile.mkstemp(suffix=".exe")
    try:
        os.write(fd, exe)
        os.close(fd)
        r = lab_run.run_kv(path, [], {})
    finally:
        os.unlink(path)

    want = expected(divs, sras, muls)
    n = len(divs) + len(sras) + len(muls)
    print("случаев: %d (div %d, sra %d, mul %d); байт: %d"
          % (n, len(divs), len(sras), len(muls), len(want)))
    print("эмуляция: код=%s шагов=%d stdout=%d байт"
          % (r.exit_code, r.steps, len(r.stdout)))
    if r.exit_code != 0:
        print("[FAIL] код возврата %s" % r.exit_code)
        return 1
    if r.stdout == want:
        print("[OK] все случаи совпали с эталоном Python")
        return 0
    # локализация первого расхождения
    for i in range(min(len(want), len(r.stdout))):
        if r.stdout[i] != want[i]:
            case = i // 8
            print("[FAIL] первый расхождение: байт %d (случай %d)"
                  % (i, case))
            print("  got  %s" % r.stdout[i:i + 8].hex())
            print("  want %s" % want[i:i + 8].hex())
            break
    else:
        print("[FAIL] длина: got %d, want %d"
              % (len(r.stdout), len(want)))
    return 1


if __name__ == "__main__":
    sys.exit(run_probe())
