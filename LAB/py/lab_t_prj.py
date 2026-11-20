"""lab_t_prj.py — секция 17 батареи: проекты PROJECTS/ (E8.3, DoD этапа 8).

Вход:  колбэк check из lab_verify (kpath/kfile — единая сигнатура
         секций); исходники проектов читаются ИЗ РЕПОЗИТОРИЯ напрямую
         (PROJECTS/<имя>/<имя>.uva — реальные байты, как kfile для
         KERNEL: правка программы без обновления якоря = красный тест).
Выход:  проверки T-P-01..02 — полный круг ИНСТРУМЕНТАМИ для каждого
         проекта: splice.exe (склейка !include, SPEC/10/14) ->
         uva.exe (байты .UP == ассемблеру оракула lab_vm.assemble) ->
         kernel.exe (stdout == якорю И оракулу lab_l4; код 0).
Функция: DoD этапа 8 — библиотека L4 используется минимум ДВУМЯ
         разными программами (DOCS/03-ROADMAP, E8.3):
         (1) T-P-01 banner — ВСЕ ЧЕТЫРЕ ветви C+N+S+M: строки .data,
             разделитель mem_fill+buf_out, print_u64/print_i64 (край
             -2^63 из .data через ldq), str_len; контейнер .UP v2;
         (2) T-P-02 fib — ветви C+N (зависимость N->C: обе части),
             собственное вычисление ряда на ALU, состояние цикла
             в сохраняемых r5..r10 (ABI), стек ветви N; контейнер v1.
         Свидетели: инструменты (круг) == оракул lab_l4 (композиция
         по контракту программы) == якорь (ручной литерал вывода,
         TESTS/T-PROJECTS.md). Число проверок: 2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_l4 as L                      # noqa: E402
import lab_run                          # noqa: E402
import lab_vm                           # noqa: E402

_PROJECTS = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "PROJECTS")
_ROOT_BANNER = "projects/banner/banner.uva"   # виртуальный путь (эмуляция)
_ROOT_FIB = "projects/fib/fib.uva"


def _pfile(root):
    """Реальные байты исходника проекта из PROJECTS/ (свидетель №0:
    тест держит файл, а не копию текста)."""
    return open(os.path.join(_PROJECTS, root.split("/", 1)[1]),
                "rb").read()


def _host(kfile, root):
    """Виртуальная ФС круга: исходник проекта + все части L4 по путям
    !include (от каталога включающего — SPEC/10; ключи — как в
    лаб_t_l4: полный путь без лексической нормализации ../, нижний
    регистр делает run_kv). Лишние части в хосте безвредны — splice
    читает только то, что включено программой."""
    files = {root: _pfile(root)}
    for b in "cnsm":
        files["%s/../../KERNEL/L4-LIB/lib_%s.uva"
              % (root.rsplit("/", 1)[0], b)] = kfile("L4-LIB/lib_%s.uva" % b)
    return files


def _circle(check, kpath, kfile, root, name, want, anchor, tid, title):
    """Полный круг инструментами (прецедент T-E8-11/16/21/26):
    splice.exe -> uva.exe -> kernel.exe (эмуляция LAB); тройной
    свидетель: консоль kernel == want (оракул) == anchor (литерал),
    байты .UP == ассемблеру оракула, коды возврата всех шагов 0."""
    try:
        rs = lab_run.run_kv(kpath("L1-SPLICE/splice.exe"),
                            [root, name + ".flat.uva"], _host(kfile, root))
        flat = rs.files.get(name + ".flat.uva", b"")
        ru = lab_run.run_kv(kpath("L3-UVA/uva.exe"),
                            [name + ".flat.uva", name + ".up"],
                            {name + ".flat.uva": flat})
        up = ru.files.get(name + ".up", b"")
        rk = lab_run.run_kv(kpath("L3-UNIVM/kernel.exe"), [name + ".up"],
                            {name + ".up": up})
        ok = (rs.exit_code == 0 and ru.exit_code == 0
              and rk.exit_code == 0 and rk.stdout == want
              and rk.stdout == anchor
              and up == lab_vm.assemble(flat.decode("utf-8")))
        detail = ("splice=%d uva=%d kernel=%d up=%dБ out=%r"
                  % (rs.exit_code, ru.exit_code, rk.exit_code, len(up),
                     rk.stdout[:24]))
    except Exception as e:                     # noqa: BLE001 — любая = провал
        ok, detail = False, "EXC:" + repr(e)
    check("%s %s: круг инструментами == оракулу == якорю" % (tid, title),
          ok, detail)


def _want_banner():
    """Оракул вывода banner: композиция lab_l4 по контракту программы
    (как модель T-E8-24, но из .data banner.uva: строки/2^63/буферы)."""
    m = bytearray(4096)
    m[0:10] = b"UNIVERSAL\x00"
    m[10:15] = b"OPS \x00"
    m[15:21] = b" RAM \x00"
    m[21:26] = b"I64 \x00"
    m[26:31] = b"LEN \x00"
    m[31:39] = (1 << 63).to_bytes(8, "little")
    L.mem_fill(m, 100, 61, 24)
    return (L.str_out(bytes(m[0:10])) + L.crlf_out()
            + L.buf_out(bytes(m[100:124])) + L.crlf_out()
            + L.str_out(bytes(m[10:15])) + L.print_u64(24)
            + L.str_out(bytes(m[15:21])) + L.print_u64(4096) + L.crlf_out()
            + L.str_out(bytes(m[21:26])) + L.print_i64(1 << 63) + L.crlf_out()
            + L.str_out(bytes(m[26:31])) + L.print_u64(9) + L.crlf_out())


def _want_fib():
    """Оракул вывода fib: ряд Фибоначчи на Python (независимый счёт)."""
    a, b, out = 1, 1, b""
    for i in range(1, 14):
        out += (L.print_u64(i) + L.chr_out(58) + L.chr_out(32)
                + L.print_u64(a) + L.crlf_out())
        a, b = b, a + b
    return out


# Якоря (свидетель №3): полные литералы вывода — TESTS/T-PROJECTS.md
_ANCHOR_BANNER = (b"UNIVERSAL\r\n"
                  b"========================\r\n"
                  b"OPS 24 RAM 4096\r\n"
                  b"I64 -9223372036854775808\r\n"
                  b"LEN 9\r\n")
_ANCHOR_FIB = (b"1: 1\r\n2: 1\r\n3: 2\r\n4: 3\r\n5: 5\r\n6: 8\r\n7: 13\r\n"
               b"8: 21\r\n9: 34\r\n10: 55\r\n11: 89\r\n12: 144\r\n"
               b"13: 233\r\n")


def run(check, kpath, kfile, kernel_host):
    """Секция 17: T-P-01..02 — проекты PROJECTS (DoD этапа 8, E8.3)."""

    # T-P-01: banner — все 4 ветви C+N+S+M; .UP v2 (.data 39 Б)
    _circle(check, kpath, kfile, _ROOT_BANNER, "banner", _want_banner(),
            _ANCHOR_BANNER, "T-P-01", "banner (C+N+S+M)")

    # T-P-02: fib — C+N (зависимость N->C), вычисление ряда, .UP v1
    _circle(check, kpath, kfile, _ROOT_FIB, "fib", _want_fib(),
            _ANCHOR_FIB, "T-P-02", "fib (C+N, вычисление)")
