"""lab_t_l4.py — секция 16 батареи: оракул библиотеки L4 (SPEC/14, LIB-1).

Вход:  колбэк check из lab_verify (kpath/kfile/kernel_host — единая
         сигнатура секций; здесь не используются: у оракула нет
         артефактов KERNEL — реализация .uva появится на E8.2).
Выход: проверки T-E8-01..07 (E8.1, «сначала истина семантики» —
         прецедент E7.1: спецификация + оракул + якоря ДО реализации).
Функция: сверка оракула lab_l4.py с якорями lab_l4_cases.py
         (третий свидетель — ручные литералы):
         (1) T-E8-01 print_u64: 13 значений — края разрядов,
             степени двойки, максимум u64;
         (2) T-E8-02 print_i64: 6 значений — край -2^63, -1, -10;
         (3) T-E8-03 u64_to_dec_rev: реверс-порядок цифр + длина
             (0; 10; максимум — 20 цифр);
         (4) T-E8-04 str_len/str_out: до ПЕРВОГО NUL (хвост невидим);
         (5) T-E8-05 mem_copy: перекрытия обоих направлений по формуле
             SPEC/14 п. 4, n=0, копия сам на себя;
         (6) T-E8-06 mem_fill: r2 AND 255, n=0;
         (7) T-E8-07 консоль-кирпичи chr/crlf/buf/buf_rev + композиция
             печати числа с CRLF.
"""
import lab_l4 as L
from lab_l4_cases import (DEC, I64, REV, STR, BUF, CPY, FILL,
                          CMP_U64, CMP_I64)


def run(check, kpath, kfile, kernel_host):
    """Секция 16: T-E8-01..07 (оракул библиотеки L4, SPEC/14)."""

    # T-E8-01: print_u64 == якорям DEC (десятичная запись u64)
    bad = []
    for v, want in DEC:
        got = L.print_u64(v)
        if got != want.encode("ascii"):
            bad.append("%d: %r != %r" % (v, got, want))
    check("T-E8-01 print_u64 == якорям (%d)" % len(DEC), not bad,
          "; ".join(bad[:2]))

    # T-E8-02: print_i64 == якорям I64 (знаковая запись)
    bad = []
    for v, want in I64:
        got = L.print_i64(v)
        if got != want.encode("ascii"):
            bad.append("%d: %r != %r" % (v, got, want))
    check("T-E8-02 print_i64 == якорям (%d)" % len(I64), not bad,
          "; ".join(bad[:2]))

    # T-E8-03: u64_to_dec_rev == якорям REV (реверс цифр + длина)
    bad = []
    for v, rev, ln in REV:
        got, gotln = L.u64_to_dec_rev(v)
        if got != rev.encode("ascii") or gotln != ln:
            bad.append("%d: %r/%d != %r/%d" % (v, got, gotln, rev, ln))
    check("T-E8-03 u64_to_dec_rev == якорям (%d)" % len(REV), not bad,
          "; ".join(bad[:2]))

    # T-E8-04: str_len/str_out == якорям STR (до первого NUL)
    bad = []
    for full, want, ln in STR:
        got_out, got_len = L.str_out(full), L.str_len(full)
        if got_out != want.encode("ascii") or got_len != ln:
            bad.append("%r: out=%r/%d != %r/%d"
                       % (full, got_out, got_len, want, ln))
    check("T-E8-04 str_len/str_out == якорям (%d)" % len(STR), not bad,
          "; ".join(bad[:2]))

    # T-E8-05: mem_copy == якорям CPY (формула по возрастанию)
    bad = []
    for init, dst, src, n, want in CPY:
        got = L.mem_copy(bytearray(init), dst, src, n)
        if bytes(got) != want:
            bad.append("dst=%d src=%d n=%d: %r != %r"
                       % (dst, src, n, bytes(got), want))
    check("T-E8-05 mem_copy == якорям (%d, вкл. перекрытия)" % len(CPY),
          not bad, "; ".join(bad[:2]))

    # T-E8-06: mem_fill == якорям FILL (r2 AND 255)
    bad = []
    for init, dst, b, n, want in FILL:
        got = L.mem_fill(bytearray(init), dst, b, n)
        if bytes(got) != want:
            bad.append("dst=%d b=%X n=%d: %r != %r"
                       % (dst, b, n, bytes(got), want))
    check("T-E8-06 mem_fill == якорям (%d)" % len(FILL), not bad,
          "; ".join(bad[:2]))

    # T-E8-07: консоль-кирпичи + композиция печати числа с CRLF
    bad = []
    if L.chr_out(0x141) != b"A" or L.chr_out(0) != b"\x00":
        bad.append("chr_out: AND 255")
    if L.crlf_out() != b"\r\n":
        bad.append("crlf_out")
    for buf, direct, rev in BUF:
        if L.buf_out(buf) != direct.encode("ascii") \
                or L.buf_out_rev(buf) != rev.encode("ascii"):
            bad.append("buf %r" % buf)
    for v, want in CMP_U64:
        got = L.print_u64(v) + L.crlf_out()
        if got != want.encode("ascii"):
            bad.append("cmp %d: %r != %r" % (v, got, want))
    for v, want in CMP_I64:
        got = L.print_i64(v) + L.crlf_out()
        if got != want.encode("ascii"):
            bad.append("cmp %d: %r != %r" % (v, got, want))
    check("T-E8-07 консоль-кирпичи + композиция (%d+%d+%d)"
          % (len(BUF), len(CMP_U64), len(CMP_I64)), not bad,
          "; ".join(bad[:2]))
