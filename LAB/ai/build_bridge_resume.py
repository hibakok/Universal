"""build_bridge_resume.py — (частное) пересборка M5-BRIDGE ВОЗОБНОВЛЯЕМЫМИ
срезами (лимит песочницы ~10 мин на вызов bash; фоновые процессы между
вызовами не живут — проверено сессией 83). Отличие от
build_bridge_only.py ТОЛЬКО механическое: фаза wall (эмуляция wall.exe,
~650 млн шагов) исполняется срезами по ~280 млн шагов с сохранением
СОСТОЯНИЯ эмулятора (pickle; кэш декодера CPU очищается — он
пересобираётся лениво, на результат не влияет) в
scripts/wall_state.pkl (папка переживает перезапуск песочницы).
Инструкции те же, инструменты те же (wall/enc/brick/pegen + bridge.peg)
— результат БАЙТ-в-БАЙТ как у build_bridge_only.py (срезы лимита
времени не меняют семантику эмуляции: cpu.run — абсолютный счёт шагов).

Запуски (каждый — отдельный вызов, до завершения):
  python3 LAB/ai/build_bridge_resume.py wall    # срез фазы wall
  python3 LAB/ai/build_bridge_resume.py finish  # enc/brick/pegen + запись артефактов
Выход: код 3 — «продолжить следующим вызовом» (фаза wall не окончена);
0 — фаза завершена; 1 — провал.
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_run                              # noqa: E402
import lab_splice                           # noqa: E402
import lab_win                              # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
L5 = os.path.join(KERNEL, "L5-BRIDGE")
WORK = os.path.join(ROOT, "..", "my-project", "scripts")

STATE = os.path.join(WORK, "wall_state.pkl")
B2TMP = os.path.join(WORK, "wall_s.b2")
SLICE = 280_000_000                    # шагов на вызов (~6 мин @ 0.8M/с)


def kpath(rel):
    return os.path.join(KERNEL, rel)


def kfile(rel):
    return open(os.path.join(KERNEL, rel), "rb").read()


def kernel_host():
    files = {}
    for root, _dirs, fs in os.walk(KERNEL):
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, KERNEL).replace(os.sep, "/").lower()
            files[rel] = open(p, "rb").read()
    return files


def phase_wall():
    """Срез фазы wall: продолжение с состояния или новый запуск."""
    import pickle
    if os.path.exists(B2TMP):
        print("фаза wall уже завершена (%s)" % B2TMP)
        return True
    if os.path.exists(STATE):
        with open(STATE, "rb") as f:
            m = pickle.load(f)
        print("возобновление: %d шагов" % m.cpu.steps)
    else:
        src = lab_splice.splice("L5-BRIDGE/bridge.wall", kernel_host())
        m = lab_win.Machine(kpath("L2-WALL/wall.exe"),
                            ["s.wall", "s.b2"], {"s.wall": src})
        print("новый запуск компиляции bridge.wall (склейка %d Б)"
              % len(src))
    m.run(m.cpu.steps + SLICE)
    if m.result.exit_code is not None and "s.b2" in m.files:
        with open(B2TMP, "wb") as f:
            f.write(bytes(m.files["s.b2"].data))
        if os.path.exists(STATE):
            os.unlink(STATE)
        print("фаза wall ЗАВЕРШЕНА: код %s, %d шагов, s.b2 %d Б"
              % (m.result.exit_code, m.cpu.steps,
                 len(m.files["s.b2"].data)))
        return True
    err = m.result.error or ""
    if err and "предел шагов" not in err:
        print("[FAIL] wall: %s" % err)
        return False
    m.cpu.cache = {}
    with open(STATE, "wb") as f:
        pickle.dump(m, f, protocol=4)
    print("срез: %d шагов, состояние сохранено — продолжить вызовом"
          " «wall»" % m.cpu.steps)
    return None


def phase_finish():
    """enc -> brick -> pegen + запись артефактов (как build_bridge_only)."""
    if not os.path.exists(B2TMP):
        print("[FAIL] нет %s — сначала фазы «wall»" % B2TMP)
        return False
    h = {"s.b2": open(B2TMP, "rb").read()}
    r2 = lab_run.run_kv(kpath("L1-ENC/enc.exe"),
                         ["s.b2", "s.brick"], h)
    if r2.exit_code != 0:
        print("[FAIL] enc: код %s" % r2.exit_code)
        return False
    h["s.brick"] = r2.files.get("s.brick", b"")
    r3 = lab_run.run_kv(kpath("L1-BRICK/brick.exe"),
                         ["s.brick", "s.bin"], h)
    if r3.exit_code != 0:
        print("[FAIL] brick: код %s" % r3.exit_code)
        return False
    h["s.bin"] = r3.files.get("s.bin", b"")
    h["s.peg"] = kfile("L5-BRIDGE/bridge.peg")
    r4 = lab_run.run_kv(kpath("L0-PEGEN/pegen.exe"),
                         ["s.bin", "s.peg", "s.exe"], h)
    if r4.exit_code != 0 or "s.exe" not in r4.files:
        print("[FAIL] pegen: код %s" % r4.exit_code)
        return False
    for name, data in (("bridge.b2", h["s.b2"]),
                       ("bridge.brick", h["s.brick"]),
                       ("bridge.exe", r4.files["s.exe"])):
        with open(os.path.join(L5, name), "wb") as f:
            f.write(data)
        print("записан %s (%d байт, SHA-256 %s)"
              % (name, len(data),
                 hashlib.sha256(data).hexdigest().upper()))
    print("тело: %d байт; шаги enc=%d brick=%d pegen=%d"
          % (len(h["s.bin"]), r2.steps, r3.steps, r4.steps))
    os.unlink(B2TMP)
    return True


def main():
    os.makedirs(WORK, exist_ok=True)
    phase = sys.argv[1] if len(sys.argv) > 1 else "wall"
    if phase == "wall":
        r = phase_wall()
        if r is None:
            return 3                # продолжить следующим вызовом
        return 0 if r else 1
    if phase == "finish":
        return 0 if phase_finish() else 1
    print("фаза? wall|finish")
    return 2


if __name__ == "__main__":
    sys.exit(main())
