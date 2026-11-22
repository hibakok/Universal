"""lab_t_bridge_corpus.py — корпус ДАННЫХ секции 18 батареи (мост BRIDGE v1).

Паспорт файла: LAB/py/lab_t_bridge_corpus.py | слой: внешний инструмент |
роль: данные тестов моста — вынесены из lab_t_bridge.py по лимиту 500
строк (решение №4 сессии 74, прецедент lab_t_*_corpus.py; срез E9.4-1;
расширен E9.4-2 — таблицы переходов; E9.4-3a — чужой образ foreign_image
+ якоря FOREIGN_*; E9.4-3b — чужой образ foreign2_image со СПУСКОМ +
якоря FOREIGN2_* + мутанты-отказы).

Вход:  байты seed.exe / префикс тела bridge (передаются тестом).
Выход:  CLI-кейсы T-E9-19 (мутанты инвариантов SPEC/04 + легальные
       отклонения), мутанты меток T-E9-22 (hint-ins / imp0 — E9.2-3b),
       синтетика спуска T-E9-21 (synthm — E9.2-2) и синтетика FF /4
       E9.4-1 (synth4/synth5 + якоря — lab_t_bridge_ff.py), синтетика
       таблиц переходов E9.4-2 (synth6/synth7 + якоря —
       lab_t_bridge_jt.py), чужой образ E9.4-3a (foreign_image + якоря
       FOREIGN_* — lab_t_bridge_pe.py) и чужой образ E9.4-3b
       (foreign2_image + якоря FOREIGN2_* + мутанты —
       lab_t_bridge_foreign.py).
Функция: держать данные секции 18 отдельно от логики прогона
       (lab_t_bridge.py), чтобы каждый файл был <= 500 строк.
"""
import lab_bridge
import lab_pe
import lab_pegen

# stdout каркаса bridge.exe (T-E9-19)
S_USE = b"U-L5-BRIDGE CMDS: BRIDGE <IN.EXE> <OUT.B2> <OUT.PEG>\r\n"
S_LONG = b"U-L5-BRIDGE ERR=LONG NAME\r\n"
S_OEXE = b"U-L5-BRIDGE ERR=OPEN EXE\r\n"
S_FAMILY = b"U-L5-BRIDGE ERR=FAMILY\r\n"
S_BIG = b"U-L5-BRIDGE ERR=BIG EXE\r\n"


def cli_cases(seed):
    """Мутанты seed.exe для T-E9-19: (имя, аргументы, хост, ожидание,
    код возврата). CLI-контракт каркаса + семейные отказы (инварианты
    SPEC/04, кроме двух легальных отклонений семейства). Возврат:
    (cases, legal) — legal: (имя, байты мутанта)."""
    seed = bytearray(seed)
    pe = lab_pe.parse(bytes(seed))
    imp = pe["imports"][0]
    dll_off = imp["name_rva"] - pe["sec_vaddr"] + pe["sec_raw_ptr"]
    thunk = imp["oft_rva"] or imp["iat_rva"]
    thunk_off = thunk - pe["sec_vaddr"] + pe["sec_raw_ptr"]

    def mut(off, val):
        b = bytearray(seed)
        b[off] = val
        return bytes(b)

    def vsz(val):
        # vsize (dword @ 0x190): мутанты спуска E9.2-2 — инструкция
        # за VirtualSize (0x3D) / длина тела больше VirtualSize (0x40)
        b = bytearray(seed)
        b[400:404] = val.to_bytes(4, "little")
        return bytes(b)

    zero_body = bytes(seed[:pe["sec_raw_ptr"]]) + \
        bytes(pe["sec_raw_size"])
    idt2_off = pe["dd1_import_rva"] - pe["sec_vaddr"] \
        + pe["sec_raw_ptr"] + 20
    cases = [
        # CLI-контракт (каркас, E9.2-1)
        ("справка", [], {}, S_USE, 2),
        ("два аргумента", ["in.exe", "t.b2"],
         {"in.exe": bytes(seed)}, S_USE, 2),
        ("четвёртый аргумент", ["in.exe", "t.b2", "t.peg", "x"],
         {"in.exe": bytes(seed)}, S_USE, 2),
        ("длинное имя", ["a" * 128, "t.b2", "t.peg"], {}, S_LONG, 3),
        ("нет входа", ["x.exe", "t.b2", "t.peg"], {}, S_OEXE, 4),
        ("большой вход", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": b"\x00" * 262145}, S_BIG, 7),
        ("мусор 64 Б", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": b"MZ\x00" * 21 + b"MZ"}, S_FAMILY, 6),
        ("пустой файл", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": b""}, S_FAMILY, 6),
        # семейные отказы: инварианты SPEC/04 (мутанты seed.exe)
        ("MZ", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(0, 78)}, S_FAMILY, 6),
        ("сигнатура PE", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(128, 81)}, S_FAMILY, 6),
        ("Machine", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(132, 101)}, S_FAMILY, 6),
        ("NumberOfSections", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(134, 2)}, S_FAMILY, 6),
        ("Magic", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(153, 12)}, S_FAMILY, 6),
        ("ImageBase", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(176, 1)}, S_FAMILY, 6),
        ("Subsystem", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(221, 4)}, S_FAMILY, 6),
        ("имя секции", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(392, 120)}, S_FAMILY, 6),
        ("SizeOfImage", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(208, 1)}, S_FAMILY, 6),
        ("SizeOfHeaders", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(213, 3)}, S_FAMILY, 6),
        ("вход вне секции", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(169, 80)}, S_FAMILY, 6),
        ("файл короче raw", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": bytes(seed[:-1])}, S_FAMILY, 6),
        ("нулевой код", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": zero_body}, S_FAMILY, 6),
        ("заглушка", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(64, 117)}, S_FAMILY, 6),
        ("игла", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(81, 120)}, S_FAMILY, 6),
        ("пробел в имени", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(77, 32)}, S_FAMILY, 6),
        ("DLL-имя", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(dll_off, 120)}, S_FAMILY, 6),
        ("hint нечётный", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(thunk_off, seed[thunk_off] | 1)}, S_FAMILY, 6),
        ("терминатор IDT", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": mut(idt2_off, 1)}, S_FAMILY, 6),
        ("инструкция за vsize", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": vsz(61)}, S_FAMILY, 6),
        ("длина тела > vsize", ["in.exe", "t.b2", "t.peg"],
         {"in.exe": vsz(64)}, S_FAMILY, 6),
    ]
    legal = [("вход 0x1100 (внутри секции)", mut(169, 17)),
             ("регистр DLL-имени", mut(dll_off, 75))]
    return cases, legal


def seed_hints(seed_exe):
    """Мутанты seed.exe для T-E9-22 (синтетика меток E9.2-3b):
    hint-ins — INT[0] указывает СТРОГО ВНУТРЬ выжившей инструкции 0x2B+1
    (метка d102c не создаётся, обе таблицы DQ — сырыми байтами, b2
    валиден — правило представимости SPEC/15 п. 6); imp0 — таблица INT
    пуста (impn=0: без отказа, DD + DQ «0» терминатора). Возврат:
    (hint_ins, imp0)."""
    fam = lab_bridge.parse_family(seed_exe)
    imp = fam["pe"]["imports"][0]
    intf = imp["oft_rva"] - 0x1000 + fam["pe"]["sec_raw_ptr"]
    hint = bytearray(seed_exe)
    hint[intf:intf + 8] = (0x102C).to_bytes(8, "little")
    imp0 = bytearray(seed_exe)
    imp0[intf:intf + 8] = (0).to_bytes(8, "little")
    return bytes(hint), bytes(imp0)


# T-E9-21: синтетика спуска (тень/нули/ret — E9.2-2): 0x200 jz +2,
# 0x202 mov eax,imm32, 0x204 (цель jz) — add eax,imm32 — ТЕНЬ,
# 0x207 ret, 0x208 нули — данные
SYNTH_CRAFT = bytes([0x74, 0x02, 0xB8, 0x05, 0x05, 0x05, 0x05,
                     0xC3, 0x00, 0x00])
SYNTH_PEG = "; synth\n!module synthm\n!entry 1200\n" \
            "!idata 1000 28\n!iat 1028 48\n"


def synth_image(body200):
    """synthm из T-E9-21: образ = (тело bridge)[:0x200] + крафт."""
    return lab_pegen.wrap(body200 + SYNTH_CRAFT, SYNTH_PEG)


# --- E9.4-1: синтетика FF /4 — косвенный jmp (T-E9-26, секция 18c) ---
# synth4 (память): 0x200 mov eax,5050505; 0x205 jmp [rip+0] — слот
# qword-«таблица» @0x20B (терминал спуска; слот — данные, d-метка от
# rip-операнда; хвостовые нули слота — виртуальные нули !bss)
FF4_CRAFT4 = bytes([0xB8, 0x05, 0x05, 0x05, 0x05,
                    0xFF, 0x25, 0x00, 0x00, 0x00, 0x00,
                    0x09, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
# synth5 (регистр): 0x200 mov eax,1209; 0x205 jmp rax; 0x207.. — ДАННЫЕ:
# 41 FF E4 (jmp r12 — НЕ код: путь закончен на терминале), C3 (ret)
FF4_CRAFT5 = bytes([0xB8, 0x09, 0x12, 0x00, 0x00,
                    0xFF, 0xE0,
                    0x41, 0xFF, 0xE4, 0xC3])
FF4_PEG = "; synth\n!module %s\n!entry 1200\n" \
          "!idata 1000 28\n!iat 1028 48\n"

# якоря декодера (fetch по bs, rip 0): r64 mod11; REX.B r64; [rip+disp32]
FF4_DECODE = [
    (b"\xFF\xE0", ("jmp", 2, (("r", 0, 64),))),
    (b"\x41\xFF\xE4", ("jmp", 3, (("r", 12, 64),))),
    (b"\xFF\x25\x00\x00\x00\x00",
     ("jmp", 6, (("m", None, None, 1, 0, 64, ("abs", 6)),))),
]

# якорные факты/строки/PEG (выведены вручную из SPEC/05 «E9.4» +
# SPEC/15 п. 3-8; совпадение с оракулом — проверяет сам T-E9-26)
FF4_FACTS4 = {"module": "synth4", "target": 0x20D, "bss": 6,
              "vsize": 0x213, "raw": 0x400,
              "ins": [(0x200, "mov", 5), (0x205, "jmp", 6)],
              "arg": (("m", None, None, 1, 0, 64, ("abs", 0x20B)),)}
FF4_FACTS5 = {"module": "synth5", "target": 0x20B, "bss": 0,
              "vsize": 0x20B, "raw": 0x400,
              "ins": [(0x200, "mov", 5), (0x205, "jmp", 2)],
              "arg": (("r", 0, 64),)}
FF4_LINES4 = [
    "M mov eax, 5050505 ; @0200",
    "H FF 25 00 00 00 00 ; @0205 jmp [rip+4619]",
    ":d120b ; @020B",
    "DB 09 12 ; @020B",
]
FF4_LINES5 = [
    "M mov eax, 1209 ; @0200",
    "H FF E0 ; @0205 jmp rax",
    "DB 41 FF E4 C3 ; @0207",
]
FF4_PEG4 = "; UNIVERSAL / PEG v1 / мост BRIDGE v1 (SPEC/15) / исходник:" \
           " synth4.exe\n!module synth4\n!entry 1200\n!idata 1000 28\n" \
           "!iat 1028 48\n!bss 6\n"
FF4_PEG5 = "; UNIVERSAL / PEG v1 / мост BRIDGE v1 (SPEC/15) / исходник:" \
           " synth5.exe\n!module synth5\n!entry 1200\n!idata 1000 28\n" \
           "!iat 1028 48\n"

# --- E9.4-2: синтетика таблиц переходов (T-E9-27, секция 18d) ---
# PEG-шаблон синтетики (как FF4_PEG)
JT_PEG = "; synth\n!module %s\n!entry 1200\n" \
         "!idata 1000 28\n!iat 1028 48\n"

# synth6 (switch-таблица): 0x200 mov eax,6060606; 0x205 jmp qword
# [rip+5] -> таблица @0x210: qword 0x20B (ret) + qword 0x20C (ret);
# терминатор — qword 0 (нуль @0x220). Спуск: 4 инструкции (2 цели
# из данных — ДО первого non-code qword)
JT_CRAFT6 = bytes([0xB8, 0x06, 0x06, 0x06, 0x06,
                    0xFF, 0x25, 0x05, 0x00, 0x00, 0x00,
                    0xC3, 0xC3,
                    0x11, 0x22, 0x33,
                    0x0B, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x0C, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
# synth7 (терминатор — qword ВНЕ тела): таблица @0x218: qword 0x20B
# (валид) + qword 0x9000 (вне VirtualSize — терминатор); qword 0x20C
# ПОСЛЕ терминатора — НЕ кандидат (спуск ровно 3 инструкции; 0x20C —
# данные 44…)
JT_CRAFT7 = bytes([0xB8, 0x07, 0x07, 0x07, 0x07,
                    0xFF, 0x25, 0x0D, 0x00, 0x00, 0x00,
                    0xC3] + [0x44] * 12 +
                   [0x0B, 0x02] + [0x00] * 6 +
                   [0x00, 0x90] + [0x00] * 6 +
                   [0x0C, 0x02] + [0x00] * 6)

# якорные факты/строки/PEG (выведены вручную из SPEC/15 п. 3-8 +
# «Расширение E9.4» SPEC/05; совпадение с оракулом — проверяет сам
# T-E9-27)
JT_FACTS6 = {"module": "synth6", "target": 0x21A, "bss": 0xE,
              "vsize": 0x228, "raw": 0x400,
              "ins": [(0x200, "mov", 5), (0x205, "jmp", 6),
                      (0x20B, "ret", 1), (0x20C, "ret", 1)],
              "arg": (("m", None, None, 1, 5, 64, ("abs", 0x210)),)}
JT_FACTS7 = {"module": "synth7", "target": 0x22A, "bss": 6,
              "vsize": 0x230, "raw": 0x400,
              "ins": [(0x200, "mov", 5), (0x205, "jmp", 6),
                      (0x20B, "ret", 1)],
              "arg": (("m", None, None, 1, 13, 64, ("abs", 0x218)),)}
JT_LINES6 = [
    "M mov eax, 6060606 ; @0200",
    "H FF 25 05 00 00 00 ; @0205 jmp [rip+4624]",
    "M ret ; @020B",
    "M ret ; @020C",
    "DB 11 22 33 ; @020D",
    ":d1210 ; @0210",
    "DB 0B 02 ; @0210",
    "DZ 6 ; @0212",
    "DB 0C 02 ; @0218",
]
JT_LINES7 = [
    "M mov eax, 7070707 ; @0200",
    "H FF 25 0D 00 00 00 ; @0205 jmp [rip+4632]",
    "M ret ; @020B",
    "DB 44 44 44 44 44 44 44 44 44 44 44 44 ; @020C",
    ":d1218 ; @0218",
    "DB 0B 02 ; @0218",
    "DZ 7 ; @021A",
    "DB 90 ; @0221",
    "DZ 6 ; @0222",
    "DB 0C 02 ; @0228",
]
JT_PEG6 = "; UNIVERSAL / PEG v1 / мост BRIDGE v1 (SPEC/15) / исходник:" \
          " synth6.exe\n!module synth6\n!entry 1200\n!idata 1000 28\n" \
          "!iat 1028 48\n!bss E\n"
JT_PEG7 = "; UNIVERSAL / PEG v1 / мост BRIDGE v1 (SPEC/15) / исходник:" \
          " synth7.exe\n!module synth7\n!entry 1200\n!idata 1000 28\n" \
          "!iat 1028 48\n!bss 6\n"

# --- E9.4-3a: произвольный PE32+ в оракуле (T-E9-28, секция 18e) ---
# Чужой образ (НЕ семейство): e_lfanew = 0x100 (длинная DOS-заглушка),
# ДВЕ секции (.text @0x1000 + .rdata @0x2000), ДВЕ DLL импорта
# (kernel32.dll: ExitProcess/GetStdHandle; user32.dll: MessageBoxA).
# Макет (RVA -> файл = rva - vaddr + raw_ptr):
#   заголовки 0x000..0x400 (таблица секций @0x208, 2 слота);
#   .text 0x400..0x800 (вход @RVA 0x1020 = файл 0x420);
#   .rdata 0x800..0xA00: IDT @0x2000 (2 дескриптора + терминатор),
#   INT1 @0x2040 / INT2 @0x2058, IAT1 @0x2068 / IAT2 @0x2080,
#   имена DLL @0x2090/@0x20A0, hint-записи @0x20B0/@0x20C0/@0x20D0
#   (чётные RVA, как у семейства). Файл = 0xA00.
import struct as _st


def foreign_image():
    """Собрать чужой образ PE32+ (2 секции, 2 DLL; e_lfanew 0x100).
    Якоря полей — FOREIGN_* ниже; совпадение проверяет T-E9-28
    (lab_t_bridge_pe.py)."""
    b = bytearray(0xA00)
    b[0:2] = b"MZ"
    _st.pack_into("<I", b, 0x3C, 0x100)             # e_lfanew
    b[0x40:0x62] = b"Foreign PE32+ image (E9.4-3a).\r\r\n$"
    b[0x100:0x104] = b"PE\x00\x00"
    _st.pack_into("<HHIIIHH", b, 0x104, 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    _st.pack_into("<H", b, 0x118, 0x020B)            # Magic PE32+
    _st.pack_into("<I", b, 0x128, 0x1020)           # вход (в .text)
    _st.pack_into("<Q", b, 0x130, 0x180000000)      # ImageBase (чужой)
    _st.pack_into("<I", b, 0x138, 0x1000)            # SectionAlignment
    _st.pack_into("<I", b, 0x13C, 0x200)            # FileAlignment
    _st.pack_into("<I", b, 0x150, 0x3000)           # SizeOfImage
    _st.pack_into("<I", b, 0x154, 0x400)            # SizeOfHeaders
    _st.pack_into("<H", b, 0x15C, 3)                # Subsystem console
    _st.pack_into("<II", b, 0x190, 0x2000, 60)      # DD[1] Import
    _st.pack_into("<II", b, 0x1E8, 0x2068, 40)      # DD[12] IAT
    b[0x208:0x210] = b".text\x00\x00\x00"           # слот 0 (имя 8 Б)
    _st.pack_into("<IIII", b, 0x210, 0x400, 0x1000, 0x400, 0x400)
    _st.pack_into("<I", b, 0x22C, 0x60000020)      # слот 0: CODE+EXEC+READ
    b[0x230:0x238] = b".rdata\x00\x00"               # слот 1 (имя 8 Б)
    _st.pack_into("<IIII", b, 0x238, 0x200, 0x2000, 0x200, 0x800)
    _st.pack_into("<I", b, 0x254, 0x40000040)      # слот 1: DATA+READ
    b[0x420:0x424] = b"\x48\x31\xC0\xC3"           # код @входе (xor rax,rax; ret)
    _st.pack_into("<IIIII", b, 0x800, 0x2040, 0, 0, 0x2090, 0x2068)
    _st.pack_into("<IIIII", b, 0x814, 0x2058, 0, 0, 0x20A0, 0x2080)
    _st.pack_into("<QQQ", b, 0x840, 0x20B0, 0x20C0, 0)      # INT1
    _st.pack_into("<QQ", b, 0x858, 0x20D0, 0)               # INT2
    _st.pack_into("<QQQ", b, 0x868, 0x20B0, 0x20C0, 0)      # IAT1
    _st.pack_into("<QQ", b, 0x880, 0x20D0, 0)               # IAT2
    b[0x890:0x89D] = b"kernel32.dll\x00"
    b[0x8A0:0x8AB] = b"user32.dll\x00"
    _st.pack_into("<H", b, 0x8B0, 0x023A)
    b[0x8B2:0x8BE] = b"ExitProcess\x00"
    _st.pack_into("<H", b, 0x8C0, 0x0266)
    b[0x8C2:0x8CF] = b"GetStdHandle\x00"
    _st.pack_into("<H", b, 0x8D0, 0x019A)
    b[0x8D2:0x8DE] = b"MessageBoxA\x00"
    return bytes(b)


# якоря полей заголовков (выведены из макета foreign_image вручную;
# совпадение с оракулом проверяет сам T-E9-28)
FOREIGN_FIELDS = {"e_lfanew": 0x100, "machine": 0x8664, "num_sections": 2,
                  "size_opt_header": 0xF0, "characteristics": 0x22,
                  "magic": 0x20B, "addr_entry_point": 0x1020,
                  "image_base": 0x180000000, "sect_align": 0x1000,
                  "file_align": 0x200, "size_of_image": 0x3000,
                  "size_of_headers": 0x400, "subsystem": 3,
                  "dd1_import_rva": 0x2000, "dd1_import_size": 60,
                  "dd12_iat_rva": 0x2068, "dd12_iat_size": 40}
FOREIGN_SECTIONS = [
    {"name": ".text", "vsize": 0x400, "vaddr": 0x1000, "raw_size": 0x400,
     "raw_ptr": 0x400, "chars": 0x60000020},
    {"name": ".rdata", "vsize": 0x200, "vaddr": 0x2000, "raw_size": 0x200,
     "raw_ptr": 0x800, "chars": 0x40000040}]
FOREIGN_IMPORTS = [
    {"dll": "kernel32.dll",
     "funcs": [("ExitProcess", 0x20B0), ("GetStdHandle", 0x20C0)],
     "iat_rva": 0x2068, "oft_rva": 0x2040, "name_rva": 0x2090},
    {"dll": "user32.dll", "funcs": [("MessageBoxA", 0x20D0)],
     "iat_rva": 0x2080, "oft_rva": 0x2058, "name_rva": 0x20A0}]
FOREIGN_LEGACY = {"sec_name": ".text", "sec_vsize": 0x400, "sec_vaddr": 0x1000,
                  "sec_raw_size": 0x400, "sec_raw_ptr": 0x400,
                  "sec_chars": 0x60000020, "body_rva": 0x1000}


# --- E9.4-3b: спуск в чужом теле (T-E9-29, секция 18f) ---
# Чужой образ с ЖИВЫМ кодом (вход 0x1020 -> спуск): .text vsize 0x400
# при raw 0x200 (НАСТОЯЩАЯ bss-вилка чужого образа), .rdata — импорты
# двух DLL (RVA-раскладка как у foreign_image). Макет .text (смещения
# секции): 0x20 mov eax,11; 0x25 call 0x40; 0x2A jz 0x68 (rel32);
# 0x30 jmp qword [rip+0x12] — терминал + ТАБЛИЦА @0x48 (3 цели + 0);
# 0x36..0x48 данные; 0x40 add eax,7; 0x43 ret; 0x68 xor eax,eax;
# 0x6A ret; 0x70..0x73 три ret (цели таблицы); хвост — нули.
def foreign2_image():
    """Собрать чужой образ PE32+ для E9.4-3b (спуск в чужом теле).
    Якоря — FOREIGN2_* ниже; совпадение проверяет T-E9-29
    (lab_t_bridge_foreign.py)."""
    b = bytearray(0x800)
    b[0:2] = b"MZ"
    _st.pack_into("<I", b, 0x3C, 0x100)             # e_lfanew
    b[0x40:0x62] = b"Foreign PE32+ image (E9.4-3b).\r\r\n$"
    b[0x100:0x104] = b"PE\x00\x00"
    _st.pack_into("<HHIIIHH", b, 0x104, 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    _st.pack_into("<H", b, 0x118, 0x020B)            # Magic PE32+
    _st.pack_into("<I", b, 0x128, 0x1020)           # вход (в .text)
    _st.pack_into("<Q", b, 0x130, 0x180000000)      # ImageBase (чужой)
    _st.pack_into("<I", b, 0x138, 0x1000)            # SectionAlignment
    _st.pack_into("<I", b, 0x13C, 0x200)            # FileAlignment
    _st.pack_into("<I", b, 0x150, 0x3000)           # SizeOfImage
    _st.pack_into("<I", b, 0x154, 0x400)            # SizeOfHeaders
    _st.pack_into("<H", b, 0x15C, 3)                # Subsystem console
    _st.pack_into("<II", b, 0x190, 0x2000, 60)      # DD[1] Import
    _st.pack_into("<II", b, 0x1E8, 0x2068, 40)      # DD[12] IAT
    b[0x208:0x210] = b".text\x00\x00\x00"           # слот 0 (имя 8 Б)
    _st.pack_into("<IIII", b, 0x210, 0x400, 0x1000, 0x200, 0x400)
    _st.pack_into("<I", b, 0x22C, 0x60000020)      # слот 0: CODE+EXEC+READ
    b[0x230:0x238] = b".rdata\x00\x00"               # слот 1 (имя 8 Б)
    _st.pack_into("<IIII", b, 0x238, 0x200, 0x2000, 0x200, 0x600)
    _st.pack_into("<I", b, 0x254, 0x40000040)      # слот 1: DATA+READ
    t = 0x400                                        # .text: файл 0x400
    b[t + 0x20:t + 0x25] = bytes([0xB8, 0x11, 0x00, 0x00, 0x00])
    b[t + 0x25:t + 0x2A] = bytes([0xE8, 0x16, 0x00, 0x00, 0x00])
    b[t + 0x2A:t + 0x30] = bytes([0x0F, 0x84, 0x38, 0x00, 0x00, 0x00])
    b[t + 0x30:t + 0x36] = bytes([0xFF, 0x25, 0x12, 0x00, 0x00, 0x00])
    b[t + 0x36:t + 0x40] = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE,
                                  0x11, 0x22, 0x33, 0x44, 0x55])
    b[t + 0x40:t + 0x43] = bytes([0x83, 0xC0, 0x07])
    b[t + 0x43:t + 0x44] = bytes([0xC3])
    b[t + 0x44:t + 0x48] = bytes([0x66, 0x77, 0x88, 0x99])
    for k, v in enumerate((0x70, 0x71, 0x72, 0)):
        _st.pack_into("<Q", b, t + 0x48 + 8 * k, v)  # таблица @0x48
    b[t + 0x68:t + 0x6A] = bytes([0x31, 0xC0])
    b[t + 0x6A:t + 0x6B] = bytes([0xC3])
    b[t + 0x6B:t + 0x70] = bytes([0x90] * 5)
    for a in (0x70, 0x71, 0x72):                     # цели таблицы
        b[t + a:t + a + 1] = bytes([0xC3])
    r = 0x600                                        # .rdata: файл 0x600
    _st.pack_into("<IIIII", b, r, 0x2040, 0, 0, 0x2090, 0x2068)
    _st.pack_into("<IIIII", b, r + 0x14, 0x2058, 0, 0, 0x20A0, 0x2080)
    _st.pack_into("<QQQ", b, r + 0x40, 0x20B0, 0x20C0, 0)      # INT1
    _st.pack_into("<QQ", b, r + 0x58, 0x20D0, 0)               # INT2
    _st.pack_into("<QQQ", b, r + 0x68, 0x20B0, 0x20C0, 0)      # IAT1
    _st.pack_into("<QQ", b, r + 0x80, 0x20D0, 0)               # IAT2
    b[r + 0x90:r + 0x9D] = b"kernel32.dll\x00"
    b[r + 0xA0:r + 0xAB] = b"user32.dll\x00"
    _st.pack_into("<H", b, r + 0xB0, 0x023A)
    b[r + 0xB2:r + 0xBE] = b"ExitProcess\x00"
    _st.pack_into("<H", b, r + 0xC0, 0x0266)
    b[r + 0xC2:r + 0xCF] = b"GetStdHandle\x00"
    _st.pack_into("<H", b, r + 0xD0, 0x019A)
    b[r + 0xD2:r + 0xDE] = b"MessageBoxA\x00"
    return bytes(b)


# якоря (выведены из макета вручную; совпадение с оракулом проверяет
# сам T-E9-29): секция кода по входу, факты, спуск (11 инструкций),
# операнды переходов (цели call/jz, rip-таблица)
FOREIGN2_SECTIONS = [
    {"name": ".text", "vsize": 0x400, "vaddr": 0x1000, "raw_size": 0x200,
     "raw_ptr": 0x400, "chars": 0x60000020},
    {"name": ".rdata", "vsize": 0x200, "vaddr": 0x2000, "raw_size": 0x200,
     "raw_ptr": 0x600, "chars": 0x40000040}]
FOREIGN2_CODE = FOREIGN2_SECTIONS[0]
FOREIGN2_FACTS = {"entry_off": 0x20, "vsize": 0x400, "raw": 0x200,
                  "target": 0x73, "bss": 0x38D}
FOREIGN2_INS = [(0x20, "mov", 5), (0x25, "call", 5), (0x2A, "jcc", 6),
                (0x30, "jmp", 6), (0x40, "add", 3), (0x43, "ret", 1),
                (0x68, "xor", 2), (0x6A, "ret", 1), (0x70, "ret", 1),
                (0x71, "ret", 1), (0x72, "ret", 1)]
FOREIGN2_ARGS = {
    0x25: (("t", 0x40),),                      # call rel32 — кандидат
    0x2A: ("z", ("t", 0x68)),                  # jz rel32 — кандидат
    0x30: (("m", None, None, 1, 0x12, 64, ("abs", 0x48)),),  # таблица
}


def foreign2_rejects():
    """Мутанты foreign2 для T-E9-29: (имя, байты) — все обязаны дать
    BridgeError в parse_foreign: вход вне секций, нет EXECUTE у секции
    входа, вход в bss (вне raw-части), файл короче raw, Machine не
    x86-64, FileAlignment не степень 2, num_sections 0 (секции
    пусты — вход вне секций)."""
    base = bytearray(foreign2_image())

    def mut(off, val):
        b = bytearray(base)
        b[off:off + len(val)] = val if isinstance(val, bytes) \
            else bytes([val])
        return bytes(b)

    def entry(v):
        return mut(0x128, v.to_bytes(4, "little"))

    return [
        ("вход вне секций (0x5000)", entry(0x5000)),
        ("в секции входа нет EXECUTE", mut(0x22C, b"\x40\x00\x00\x00")),
        ("вход в bss (0x1300)", entry(0x1300)),
        ("файл короче raw", bytes(base[:0x5FF])),
        ("Machine 0x014C", mut(0x104, b"\x4C\x01")),
        ("FileAlignment 0x201", mut(0x13C, b"\x01\x02")),
        ("num_sections 0", mut(0x106, b"\x00")),
    ]
