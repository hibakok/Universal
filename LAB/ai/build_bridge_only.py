"""build_bridge_only.py — (частное) фаза 1 пересборки M5-BRIDGE:
lab_t_bridge.build (конвейер wall/enc/brick/pegen под эмуляцией,
шаг wall > 200 млн — прямой lab_win 2 млрд) + ЗАПИСЬ артефактов
bridge.b2/brick/exe — БЕЗ прогона секции 18 (фаза 2 — dev_t22.py /
battery_groups.py 4). Хронометраж фаз (лимит песочницы 10 мин на
вызов — прецедент bridge_test.py; срез E9.2-3c).
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "py"))

import lab_t_bridge                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
KERNEL = os.path.join(ROOT, "KERNEL")
L5 = os.path.join(KERNEL, "L5-BRIDGE")


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


def main():
    ok, a, note = lab_t_bridge.build(kpath, kfile, kernel_host)
    print("[OK] сборка" if ok else "[FAIL] сборка", note)
    if not ok:
        return 1
    for name, data in (("bridge.b2", a["b2"]),
                       ("bridge.brick", a["brick"]),
                       ("bridge.exe", a["exe"])):
        with open(os.path.join(L5, name), "wb") as f:
            f.write(data)
        print("записан %s (%d байт, SHA-256 %s)"
              % (name, len(data),
                 hashlib.sha256(data).hexdigest().upper()))
    print("тело: %d байт" % len(a["bin"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
