"""lab_t_bridge_pe.py — секция 18e батареи: произвольный PE32+ в оракуле
(E9.4-3a; SPEC/15 п. 10 — фундамент чужих EXE для PEG v2).

Вход:  колбэк check из lab_verify + kfile (артефакты семейства —
       нейтральность); чистый Python, без эмуляции инструментов.
Выход:  проверка T-E9-28: разбор PE в оракуле (lab_pe.parse) обобщён
         с образов семейства на ПРОИЗВОЛЬНЫЕ PE32+:
         (1) чужой образ (e_lfanew 0x100, ДВЕ секции, ДВЕ DLL — крафт
         lab_t_bridge_corpus.foreign_image) — поля заголовков читаются
         ПО e_lfanew (fixed-смещения 0x84/0x98 читали бы DOS-заглушку),
         pe["sections"] == ВСЕ слоты таблицы, импорты ОБЕИХ DLL: имена
         функций и hint-RVA через RVA-отображение по секциям (имена в
         .rdata), легаси-поля sec_*/body_rva == слот 0, body — сырые
         байты первой секции (вход @0x1020 = 48 31 C0 C3);
         (2) НЕЙТРАЛЬНОСТЬ семейства: у всех 12 артефактов секция
         ОДНА, sections[0] == sec_* (легаси-поля из того же слота),
         импорт один — kernel32.dll: значения как до обобщения
         (выходы моста не менялись — снимок до/после сессии 78;
         якоря T-E9-25 в той же батарее).
Функция: «сначала истина семантики» (прецедент E9.1): фундамент
         чужих EXE закладывается в оракуле ДО инструмента —
         parse_family и bridge.exe НЕ менялись (порт — E9.4-4+,
         при первом чужом круге). Число проверок: 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lab_pe                              # noqa: E402
import lab_t_bridge_corpus as K            # noqa: E402 — данные E9.4-3a

# все артефакты семейства (как ARTIFACTS lab_t_bridge.py, вкл. bridge)
ARTIFACTS = ["L0-SEED/seed", "L0-SEED2/seed2", "L0-HXDUMP/hxdump",
             "L0-HEXGEN/hexgen", "L0-PEGEN/pegen", "L1-BRICK/brick",
             "L1-ENC/enc", "L1-SPLICE/splice", "L2-WALL/wall",
             "L3-UNIVM/kernel", "L3-UVA/uva", "L5-BRIDGE/bridge"]


def run(check, kfile):
    """Секция 18e: T-E9-28 — произвольный PE32+ в оракуле (E9.4-3a)."""
    bad = []
    # (1) чужой образ: поля по e_lfanew + ВСЕ секции + импорты многих DLL
    pe = lab_pe.parse(K.foreign_image())
    for k, v in K.FOREIGN_FIELDS.items():
        if pe[k] != v:
            bad.append("поле %s: %r != %X" % (k, pe[k], v))
    if pe["sections"] != K.FOREIGN_SECTIONS:
        bad.append("секции %r" % (pe["sections"],))
    if pe["imports"] != K.FOREIGN_IMPORTS:
        bad.append("импорты %r" % (pe["imports"],))
    for k, v in K.FOREIGN_LEGACY.items():
        if pe[k] != v:
            bad.append("легаси %s: %r != %X" % (k, pe[k], v))
    if not (pe["mz"] and pe["pe_sig_ok"] and pe["size"] == 0xA00
            and len(pe["body"]) == 0x400
            and pe["body"][0x20:0x24] == b"\x48\x31\xC0\xC3"):
        bad.append("тело/сигнатуры/размер")
    # (2) нейтральность семейства: 12 артефактов — одна секция == sec_*
    for m in ARTIFACTS:
        fp = lab_pe.parse(kfile("%s.exe" % m))
        if len(fp["sections"]) != 1:
            bad.append("%s: секций %d" % (m, len(fp["sections"])))
            continue
        s0 = fp["sections"][0]
        if (s0["vsize"] != fp["sec_vsize"] or s0["vaddr"] != fp["sec_vaddr"]
                or s0["raw_size"] != fp["sec_raw_size"]
                or s0["raw_ptr"] != fp["sec_raw_ptr"]
                or s0["chars"] != fp["sec_chars"]
                or s0["name"] != fp["sec_name"]):
            bad.append("%s: sec_* != sections[0]" % m)
        if len(fp["imports"]) != 1 \
                or fp["imports"][0]["dll"].lower() != "kernel32.dll":
            bad.append("%s: импорты" % m)
    check("T-E9-28 произвольный PE32+ в оракуле: e_lfanew 0x100 +"
          " 2 секции + 2 DLL (поля/sections/импорты/легаси) +"
          " нейтральность 12 артефактов", not bad,
          "; ".join(bad[:3]) if bad else
          "чужой: секции .text+.rdata, импорты kernel32+user32;"
          " семья: 12x1 секция == sec_*")
