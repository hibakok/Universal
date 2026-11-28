"""lab_run.py — прогон EXE под эмуляцией с командной строкой.

Вход:  run(exe_path, args=[], host_files={}, cwd='KERNEL')
Выход: Result: stdout (bytes), exit_code (int), files {имя: bytes},
       steps (int), error (str|None).
Функция: одна точка входа для сценариев батареи — как командная
         строка Windows, но без Windows.
"""
import lab_win


def run(exe_path, args=(), host_files=None, max_steps=200_000_000):
    """Прогнать EXE. host_files: {'l0-seed/seed.hex': bytes, ...} —
    файлы, которые программа может открыть (ключи нормализуются).
    max_steps — предел шагов эмуляции (по умолчанию 200 млн; для
    МБ-масштаба — E9.5-1b: фолд PEG v2 на образе 3 МиБ ~250 млн)."""
    m = lab_win.Machine(exe_path, list(args), host_files or {})
    return m.run(max_steps)


def run_kv(exe_path, args=(), host_files=None, max_steps=200_000_000):
    """То же, но имена host-файлов можно передавать в стиле Windows."""
    norm = {k.replace("\\", "/").strip("/").lower(): v
            for k, v in (host_files or {}).items()}
    return run(exe_path, list(args), norm, max_steps)


if __name__ == "__main__":
    import sys
    r = run(sys.argv[1], sys.argv[2:])
    print(r)
    print("steps:", r.steps)
