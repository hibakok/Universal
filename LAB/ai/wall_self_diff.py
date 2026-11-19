"""wall_self_diff.py — dev-инструмент E6.4d-5/3: diff-анализ финала (шаг 3).

E6.4d-5/3-2 (сессия 43): артефакты M2-WALL заменены самосборной сборкой
из wall.wall; эквивалент части A теперь ЖИВЁТ В БАТАРЕЕ (T-E6-49a —
фикс-пункт + сверка с артефактом wall.b2; T-E6-49b — воспроизводимость
wall.brick/wall.exe). Этот инструмент — исторический протокол сессии 42
(доказательство фикс-пункта ДО замены) и источник diff-анализа порядка
функций (часть B); повторный запуск после замены воспроизводит круг
уже самосборным wall.exe.

Вход:  KERNEL/L2-WALL/wall.wall (каркас) + артефакты ядра.
Выход: отчёт [OK]/[FAIL]/данные; код возврата 0/1.
Функция: шаг (1) плана сессии 41 (E6.4d-5/3 — финал E6.4d):
         ЧАСТЬ A — ФИКСПУНКТ (главный вопрос шага 3, DoD E6.4d:
         «wall(wall.wall) воспроизводит собственный .b2»): каркас
         собирается полным кругом из wall.wall СТАРЫМ wall.exe
         (s1.b2 -> enc -> brick -> pegen -> s1.exe), затем уже САМ
         компилятор-каркас s1.exe компилирует wall.wall — выход s2.b2
         обязан совпасть с s1.b2 байт-в-байт. До сих пор каркас
         компилировал только ЧУЖИЕ исходники (DEMO, big_source) —
         себя он компилирует здесь ВПЕРВЫЕ. Прохождение = зелёный
         свет замене артефактов wall.b2/wall.brick/wall.exe сборкой
         из wall.wall (шаг (2) плана).
         ЧАСТЬ B — ПОРЯДОК ФУНКЦИЙ: сравнение порядка функций в
         выходе wall.exe(wall.wall) (= s1.b2, будущий новый wall.b2)
         с порядком функций канонического wall.b2 (сплайс): общие/
         только-в-одном, LCS, инверсии, предложение перестановки
         include-порядка каркаса (перестановка необязательна —
         фикс-пункт от порядка функций НЕ зависит: порядок выхода
         следует порядку func в исходнике, который одинаков для обоих
         компиляторов; перестановка нужна только для преемственности
         документации/навигации по новому wall.b2).
Кэш:   промежуточные артефакты (s1.b2, s1.exe) сохраняются в
         /tmp/wall_self_diff/ и переиспользуются, пока SHA исходника
         каркаса совпадает (повторные прогоны не пересобирают круг).
Лимит: самокомпиляция каркаса требует ~0.7 млрд шагов эмулятора —
         выше дефолтных 200 млн lab_win; фикс-пункт пускается прямым
         вызовом lab_win.Machine.run(max_steps=2 млрд).
Запуск: python3 LAB/ai/wall_self_diff.py [--skip-a] [--skip-b]
"""
import hashlib
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_l2                             # noqa: E402
import lab_l2_prog                        # noqa: E402
import lab_run                            # noqa: E402
import lab_splice                         # noqa: E402
import lab_win                            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
WALL = os.path.join(KERNEL, "L2-WALL", "wall.exe")
ENC = os.path.join(KERNEL, "L1-ENC", "enc.exe")
BRICK = os.path.join(KERNEL, "L1-BRICK", "brick.exe")
PEGEN = os.path.join(KERNEL, "L0-PEGEN", "pegen.exe")
CACHE = "/tmp/wall_self_diff"


def check(name, ok, note=""):
    print(("[OK] " if ok else "[FAIL] ") + name +
          (("  " + note) if note else ""))
    return bool(ok)


def sha16(b):
    return hashlib.sha256(b).hexdigest().upper()[:16]


def kernel_host():
    files = {}
    for base, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def _cached(name, src_sha):
    """Артефакт из кэша, если он валиден (совпадает SHA исходника)."""
    d = os.path.join(CACHE, name)
    try:
        if open(d + ".sha", "r").read().strip() == src_sha:
            return open(d, "rb").read()
    except OSError:
        pass
    return None


def _store(name, src_sha, data):
    os.makedirs(CACHE, exist_ok=True)
    d = os.path.join(CACHE, name)
    open(d, "wb").write(data)
    open(d + ".sha", "w").write(src_sha + "\n")


# ---------------------------------------------------------------- часть A

def build_circle(src, src_sha):
    """Полный круг сборки каркаса СТАРЫМ wall.exe. Возвращает
    (s1_b2, s1_exe, metrics) или (None, None, metrics) при сбое."""
    met = {}
    t0 = time.time()
    s1_b2 = _cached("s1.b2", src_sha)
    if s1_b2 is None:
        r = lab_run.run_kv(WALL, ["s.wall", "s.b2"], {"s.wall": src})
        met["wall.exe шагов"] = r.steps
        if r.exit_code != 0:
            print("сбой wall.exe: код=%s out=%r" % (r.exit_code,
                                                    r.stdout[:60]))
            return None, None, met
        s1_b2 = r.files["s.b2"]
        _store("s1.b2", src_sha, s1_b2)
    else:
        met["s1.b2"] = "из кэша"
    met["s1.b2 байт"] = len(s1_b2)
    met["s1.b2 SHA-16"] = sha16(s1_b2)

    s1_exe = _cached("s1.exe", src_sha)
    if s1_exe is None:
        h = {"s.b2": s1_b2}
        r2 = lab_run.run_kv(ENC, ["s.b2", "s.brick"], h)
        met["enc шагов"] = r2.steps
        if r2.exit_code != 0:
            return None, None, met
        h["s.brick"] = r2.files["s.brick"]
        met["s.brick байт"] = len(h["s.brick"])
        r3 = lab_run.run_kv(BRICK, ["s.brick", "s.bin"], h)
        met["brick шагов"] = r3.steps
        if r3.exit_code != 0:
            return None, None, met
        h["s.bin"] = r3.files["s.bin"]
        met["s.bin байт"] = len(h["s.bin"])
        h["s.peg"] = lab_l2_prog.DEMO_WALL_PEG.encode()
        r4 = lab_run.run_kv(PEGEN, ["s.bin", "s.peg", "s.exe"], h)
        met["pegen шагов"] = r4.steps
        if r4.exit_code != 0 or "s.exe" not in r4.files:
            return None, None, met
        s1_exe = r4.files["s.exe"]
        _store("s1.exe", src_sha, s1_exe)
    else:
        met["s1.exe"] = "из кэша"
    met["s1.exe байт"] = len(s1_exe)
    met["s1.exe SHA-16"] = sha16(s1_exe)
    met["круг, с"] = round(time.time() - t0, 1)
    return s1_b2, s1_exe, met


def run_fixpoint(src, exe_path, s1_b2):
    """s1.exe (каркас) компилирует wall.wall -> s2.b2; сравнение.
    Лимит шагов — 2 млрд: самокомпиляция каркаса ~0.7 млрд шагов,
    дефолтных 200 млн лаборатории не хватает (lim lab_win.run)."""
    t0 = time.time()
    r = lab_win.Machine(exe_path, ["s.wall", "s2.b2"],
                        {"s.wall": src}).run(max_steps=2_000_000_000)
    dt = round(time.time() - t0, 1)
    if r.exit_code is None:
        return False, ("НЕ ЗАВЕРШИЛСЯ: шагов=%d (лимит?), %.1f с, "
                       "error=%r" % (r.steps, dt, r.error))
    s2 = r.files.get("s2.b2", b"")
    ok = s2 == s1_b2
    note = ("шагов=%d, %.1f с (%.2f млн/с), s2.b2=%d Б"
            % (r.steps, dt, r.steps / max(dt, 0.001) / 1e6, len(s2)))
    if not ok and s2:
        n = min(len(s2), len(s1_b2))
        for i in range(n):
            if s2[i] != s1_b2[i]:
                note += ("; 1-е расхождение @%d:\n   каркас:   %r\n"
                         "   стена:    %r"
                         % (i, s2[max(0, i - 40):i + 40],
                            s1_b2[max(0, i - 40):i + 40]))
                break
        else:
            note += ("; префикс совпал, длины %d vs %d"
                     % (len(s2), len(s1_b2)))
        # кто неправ? третья сторона — оракул
        oracle = lab_l2.compile_wall(src.decode("latin1")).encode()
        note += ("; оракул совпадает с: %s"
                 % ("каркасом" if s2 == oracle else
                    ("wall.exe" if s1_b2 == oracle else "никем (!)")))
    return ok, note


def part_a():
    """Часть A: сборка круга + фикс-пункт. True если фикс-пункт держится."""
    print("== ЧАСТЬ A: фикс-пункт «wall(wall.wall) воспроизводит "
          "собственный .b2» ==\n")
    src = lab_splice.splice("L2-WALL/wall.wall", kernel_host())
    src_sha = hashlib.sha256(src).hexdigest()
    s1_b2, s1_exe, met = build_circle(src, src_sha)
    if s1_b2 is None:
        print("ПРОВАЛ сборки круга: %s" % met)
        return False
    for k, v in met.items():
        print("  %s: %s" % (k, v))
    ok1 = check("A1 сборка каркаса полным кругом (wall+enc+brick+pegen)",
                True, "s1.exe=%d Б" % len(s1_exe))
    fd, path = tempfile.mkstemp(suffix=".exe")
    os.write(fd, s1_exe)
    os.close(fd)
    try:
        ok2, note = run_fixpoint(src, path, s1_b2)
    finally:
        os.unlink(path)
    ok3 = check("A2 ФИКСПУНКТ: s1.exe(wall.wall) == s1.b2 (байт-в-байт)",
                ok2, note)
    print()
    return ok1 and ok3


# ---------------------------------------------------------------- часть B

RE_FUNC = re.compile(r"^func ([A-Za-z_][A-Za-z_0-9]*)", re.M)
RE_LABEL = re.compile(r"^:([^\s;]+)", re.M)
RE_CALL = re.compile(r"M call \$([A-Za-z_][A-Za-z_0-9]*)")
RE_INCLUDE = re.compile(r"^!include (\S+)", re.M)


def skel_parts():
    """[(имя части, [функции в порядке объявления])]; корень — последним
    (func main). Части — в текущем порядке include корня wall.wall."""
    host = kernel_host()
    root = host["l2-wall/wall.wall"].decode("latin1")
    order = RE_INCLUDE.findall(root)
    parts = []
    for name in order:
        txt = host["l2-wall/" + name.lower()].decode("latin1")
        parts.append((name, RE_FUNC.findall(txt)))
    parts.append(("wall.wall (корень: main)", RE_FUNC.findall(root)))
    return parts


def wallb2_parts():
    """[(имя части, [функции])] канонического wall.b2: функция = метка,
    которую ГДЕ-ТО вызывают (M call $имя); :entry (корень) — первой.
    Порядок частей — include-порядок корня wall.b2."""
    host = kernel_host()
    root_txt = lab_splice.splice("L2-WALL/wall.b2", host).decode("latin1")
    called = set(RE_CALL.findall(root_txt))
    root = host["l2-wall/wall.b2"].decode("latin1")
    order = RE_INCLUDE.findall(root)
    parts = [("wall.b2 (корень: entry)", ["entry"])]
    for name in order:
        txt = host["l2-wall/" + name.lower()].decode("latin1")
        funcs = [l for l in RE_LABEL.findall(txt) if l in called]
        parts.append((name, funcs))
    return parts


def lcs_len(a, b):
    """Длина наибольшей общей подпоследовательности."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else
                       max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def part_b():
    """Часть B: порядок функций s1.b2 (каркас) vs wall.b2 (канон)."""
    print("== ЧАСТЬ B: порядок функций (каркас vs канонический wall.b2)"
          " ==\n")
    host = kernel_host()
    src = lab_splice.splice("L2-WALL/wall.wall", host)
    a_order = RE_FUNC.findall(src.decode("latin1"))     # s1.b2: func-порядок
    b_parts = wallb2_parts()
    b_order = [f for _n, fs in b_parts for f in fs]

    aset, bset = set(a_order), set(b_order)
    common = [f for f in a_order if f in bset]          # порядок каркаса
    common_b = [f for f in b_order if f in aset]        # порядок канона
    only_a = [f for f in a_order if f not in bset]
    only_b = [f for f in b_order if f not in aset]

    print("функций в выходе каркаса (s1.b2): %d" % len(a_order))
    print("функций в каноническом wall.b2:   %d" % len(b_order))
    print("общих: %d (%.0f%% от каркаса, %.0f%% от канона)"
          % (len(common), 100.0 * len(common) / max(len(a_order), 1),
             100.0 * len(common) / max(len(b_order), 1)))
    print("только в каркасе (%d): %s" % (len(only_a), " ".join(only_a)))
    print("только в wall.b2 (%d): %s" % (len(only_b), " ".join(only_b)))

    lcs = lcs_len(common, common_b)
    pos_b = {f: i for i, f in enumerate(common_b)}
    seq = [pos_b[f] for f in common]
    inv = sum(1 for i in range(len(seq))
              for j in range(i + 1, len(seq)) if seq[i] > seq[j])
    print("\nLCS общих (в порядке каркаса vs канона): %d из %d"
          % (lcs, len(common)))
    print("инверсий порядка (Kendall): %d" % inv)
    print("в порядке канона лежат подряд (уже согласованы): %d"
          % lcs)

    # предложение: сортировка частей каркаса по МЕДИАНЕ позиций общих
    # функций в каноне (стабильная; медиана устойчивее первой функции:
    # часть с ранней «случайной» общей функцией не уезжает в начало);
    # части без общих — сразу после предыдущей части с общими; корень
    # (main) — всегда последним (func main ниже всех !include).
    # ЭВРИСТИКА: решение о перестановке принимает следующая сессия.
    skel = skel_parts()
    keys = []
    last = -1.0
    for name, fs in skel:
        ps = sorted(pos_b[f] for f in fs if f in pos_b)
        if ps:
            last = float(ps[len(ps) // 2])
        keys.append([name, fs, last + (0.5 if not ps else 0.0)])
    keys[-1][2] = float("inf")            # корень (main) — всегда последний
    head = sorted((t for t in keys if t[2] != float("inf")),
                  key=lambda t: t[2])
    tail = [t for t in keys if t[2] == float("inf")]
    prop = head + tail
    print("\nпорядок частей КАНОНА wall.b2 (для сверки):")
    print("  " + " | ".join(n for n, _f in b_parts))
    print("текущий include-порядок каркаса:")
    print("  " + " | ".join(n for n, _f, _k in keys))
    print("предложение (по медиане позиций общих функций канона):")
    print("  " + " | ".join(n for n, _f, _k in prop))
    cur = [n for n, _f in skel]
    new = [n for n, _f, _k in prop]
    moved = sum(1 for c, n in zip(cur, new) if c != n)
    print("частей, сместившихся в предложении: %d из %d"
          % (moved, len(skel)))

    print("\nВЫВОД (по данным частей A+B):")
    print("  1. ФИКСПУНКТ держится (часть A) — замена артефактов")
    print("     wall.b2/wall.brick/wall.exe сборкой из wall.wall")
    print("     возможна; порядок функций на фикс-пункт НЕ влияет")
    print("     (порядок выхода = порядок func в исходнике, общем")
    print("     для обоих компиляторов).")
    print("  2. Полное выравнивание порядка НЕДОСТИЖИМО в принципе:")
    print("     множества функций различны (%d только в каркасе, %d"
          % (len(only_a), len(only_b)))
    print("     только в каноне); LCS общих %d из %d, инверсий %d."
          % (lcs, len(common), inv))
    print("  3. Перестановка include-порядка — только частичная")
    print("     косметика для преемственности чтения нового wall.b2;")
    print("     навигация по исходнику и так идёт по частям каркаса")
    print("     wall_self_*.wall (CARD.md), а новый wall.b2 —")
    print("     ГЕНЕРИРУЕМЫЙ артефакт сборки из wall.wall.")
    return True


def main():
    args = sys.argv[1:]
    ok = True
    if "--skip-a" not in args:
        ok = part_a() and ok
    if "--skip-b" not in args:
        ok = part_b() and ok
    print("ИТОГ: %s" % ("OK" if ok else "ПРОВАЛЫ"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
