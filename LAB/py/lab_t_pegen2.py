"""lab_t_pegen2.py — секция 8d батареи: ПОРТ wrap2 (PEG v2) в pegen.exe
(E9.4-4b-4; SPEC/07 «Рост v2», оракул lab_pegen.wrap2 — E9.4-3c-1).

Вход:  колбэк check из lab_verify; артефакт pegen.exe + корпуса крафтов
       lab_t_bridge_peg2 (якорные тексты PEG v2 + мутанты + синтетика).
Выход: проверка T-M5-18: (1) ПОРТ: два чужих крафта (тела target-байтов +
       якорные тексты) — pegen.exe под ЭМУЛЯЦИЕЙ == lab_pegen.wrap2
       байт-в-байт (== исходным чужим образам); (2) ОТКАЗЫ: 19 мутантов
       якоря + 5 структурных синтетик + v1-текст с !pev2 внутри — код 9
       ERR=FORMAT, оракул ValueError. Число проверок: 2.
Функция: «оракул впереди» (прецедент E9.1): сборщик был закреплён оракулом
         ДО порта; инструмент повторяет его на телах крафтов. Нейтральность
         v1 (9 кругов модулей) — секция 7-8c (lab_t_exe, T-M5-02..06).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_pegen                            # noqa: E402
import lab_run                              # noqa: E402
import lab_t_bridge_corpus as K             # noqa: E402
from lab_t_bridge_peg2 import (             # noqa: E402
    FOREIGN_PEG2, FOREIGN2_PEG2, _mutants, _synth, _target_body)

ERRFMT = b"U-L0-PEGEN ERR=FORMAT\r\n"


def _oracle_rejects(body, text):
    try:
        lab_pegen.wrap2(body, text)
        return False
    except ValueError:
        return True


def run(check, kpath):
    """Секция 8d: T-M5-18 — порт PEG v2 (wrap2) в pegen.exe (E9.4-4b-4)."""
    pegen_exe = kpath("L0-PEGEN/pegen.exe")
    # (1) ПОРТ: чужие крафты -> pegen.exe == wrap2 байт-в-байт
    bad = []
    img1, img2 = K.foreign_image(), K.foreign2_image()
    b1, b2 = _target_body(img1), _target_body(img2)
    for name, img, body, text in [
            ("foreign", img1, b1, FOREIGN_PEG2),
            ("foreign2", img2, b2, FOREIGN2_PEG2)]:
        want = lab_pegen.wrap2(body, text)
        if want != img:
            bad.append("%s: оракул != образу (якорь T-E9-30)" % name)
        r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": body,
                            "t.peg": text.encode("utf-8")})
        if not (r.exit_code == 0 and r.files.get("t.exe") == want):
            bad.append("%s: pegen != wrap2 (код=%s)" % (name, r.exit_code))
    check("T-M5-18 ПОРТ wrap2: 2 чужих крафта — pegen.exe =="
          " оракулу байт-в-байт (эмуляция)", not bad,
          "; ".join(bad) if bad else "тела foreign/foreign2 как T-E9-30")

    # (2) ОТКАЗЫ: мутанты + синтетика + граница версий
    cases = [(nm, txt, body) for nm, txt, body in _mutants()]
    for nm, txt in [
            ("нет MZ (_synth)", _synth(mz=False)),
            ("нет PE (_synth)", _synth(sig=b"XX\x00\x00")),
            ("таблица вне H", _synth(nsec_field=1, nsec_slots=1)),
            ("raw в заголовках", _synth(raw0=(0x40, 0x10))),
            ("наложение raw", _synth(raw0=(0x100, 0x10),
                                    raw1=(0x108, 0x10), nsec_slots=2)),
            ("!sec на пустой raw", _synth(sec1=True)),
            ("v1-текст с !pev2 внутри", "; v\n!module seed\n!entry 1000\n"
             "!pev2 40\n!idata 1100 28\n!iat 1130 20\n")]:
        cases.append((nm, txt, None))
    bad = []
    for nm, txt, body in cases:
        body = body if body is not None else b"\x90" * 0x40
        r = lab_run.run_kv(pegen_exe, ["t.bin", "t.peg", "t.exe"],
                           {"t.bin": body,
                            "t.peg": txt.encode("utf-8")})
        if not (r.exit_code == 9 and r.stdout == ERRFMT
                and _oracle_rejects(body, txt)):
            bad.append("%s (код=%s, оракул %s)" % (
                nm, r.exit_code, "принял" if not _oracle_rejects(
                    body, txt) else "отказ"))
    check("T-M5-18 ОТКАЗЫ: %d мутантов/синтетик v2 — ERR=FORMAT, оракул"
          " ValueError" % len(cases), not bad,
          "; ".join(bad[:3]) if bad else "все отказы совпали")
