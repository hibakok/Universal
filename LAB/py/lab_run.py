"""lab_run.py — прогон EXE под эмуляцией с командной строкой.

Вход:  run(exe_path, args=[], host_files={}, cwd='KERNEL')
Выход: Result: stdout (bytes), exit_code (int), files {имя: bytes},
       steps (int), error (str|None).
Функция: одна точка входа для сценариев батареи — как командная
         строка Windows, но без Windows.
"""
import lab_win


def run(exe_path, args=(), host_files=None):
    """Прогнать EXE. host_files: {'l0-seed/seed.hex': bytes, ...} —
    файлы, которые программа может открыть (ключи нормализуются)."""
    m = lab_win.Machine(exe_path, list(args), host_files or {})
    return m.run()


def run_kv(exe_path, args=(), host_files=None):
    """То же, но имена host-файлов можно передавать в стиле Windows."""
    norm = {k.replace("\\", "/").strip("/").lower(): v
            for k, v in (host_files or {}).items()}
    return run(exe_path, list(args), norm)


if __name__ == "__main__":
    import sys
    r = run(sys.argv[1], sys.argv[2:])
    print(r)
    print("steps:", r.steps)
