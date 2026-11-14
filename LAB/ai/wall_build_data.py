"""wall_build_data.py — генератор KERNEL/L2-WALL/wall_data.b2 (данные M2-WALL).

Вход:  нет (строки канона извлечены из выхода оракула LAB/py/lab_l2*.py —
       байт-точные; запускать из корня репозитория).
Выход: пишет wall_data.b2 (таблицы, блоб строк, импорты, bss) и
       scripts/strtab_map.py (соответствие имя-строки -> индекс).
Функция: генератор данных модуля M2-WALL (прецедент — LAB/ai/enc_build.py).
         Строки упакованы в единый блоб :strblob с таблицей смещений
         :strtab2 — экономия меток brick (лимит 512 на модуль).
"""
import os

OUT = os.path.join("KERNEL", "L2-WALL", "wall_data.b2")

# Полные строки канона (байт-точные из выхода оракула SPEC/11).
FULL = {
    "s_hdr1":  "; UNIVERSAL / WALL v1 / сгенерировано компилятором WALL (SPEC/11)",
    "s_secimp": "; --- импорты: фиксированная область 0x200 байт (SPEC/11) ---",
    "s_idtf":  "DD $_intt 0 0 $_dll $_iat ; описатель импорта kernel32",
    "s_idtn":  "DD 0 0 0 0 0 ; без импортов",
    "s_idtterm": "DZ 14 ; терминатор IDT",
    "s_dll":   'DB 6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00 ; "kernel32.dll\\0"',
    "s_dz1":   "DZ 1 ; выравнивание",
    "s_free":  "DZ 22 ; свободный слот импорта",
    "s_dz2a":  "DZ 2A ; выравнивание области до 0x200",
    "s_dz148": "DZ 148 ; без импортов: выравнивание области до 0x200",
    "s_seccode": "; --- код ---",
    "s_ent1":  "M sub rsp, 8 ; вход: выравнивание стека для вызова main",
    "s_ent2":  "M call $main ; вход: вызов main",
    "s_ent3":  "M int3 ; вход: возврат из main без ExitProcess — ловушка",
    "s_secstr": "; --- данные: строки ---",
    "s_secglob": "; --- данные: глобальные переменные (нулевые ячейки) ---",
}
FRAG = {
    "s_h2a": "; исходник: ",
    "s_h2b": " строк; функций: ",
    "s_h2c": "; ext: ",
    "s_h2d": "; str: ",
    "s_h2e": "; глобальных var: ",
    "s_kadr": "кадр ",
    "s_vyhod": "выход ",
    "s_cmt": " ; ",
    "s_mpush": "M push rbp",
    "s_mrbp": "M mov rbp, rsp",
    "s_mrsp": "M mov rsp, rbp",
    "s_mpop": "M pop rbp",
    "s_mret": "M ret",
    "s_msub": "M sub rsp, ",
    "s_movr10": "M mov r10, ",
    "s_movr10m": "M mov r10, [rbp-",
    "s_movr11m": "M mov r11, [rbp-",
    "s_movr10rip": "M mov r10, [rip+$",
    "s_lear10rip": "M lea r10, [rip+$",
    "s_lear10m": "M lea r10, [rbp-",
    "s_movm": "M mov [rbp-",
    "s_r10": "], r10",
    "s_mr11": "M mov r11, r10",
    "s_mneg": "M neg r10",
    "s_mcmp": "M cmp r10, r11",
    "s_mrcxr11": "M mov rcx, r11",
    "s_mmovzx": "M movzx r10d, byte [r10+r11]",
    "s_mrax": "M mov rax, r10",
    "s_mr10rax": "M mov r10, rax",
    "s_movrip": "M mov [rip+$",
    "s_ripr10": "], r10",
    "s_msp20": "M mov [rsp+20], r10",
    "s_mal": "M mov al, [rbp-",
    "s_mr10r11al": "M mov [r10+r11], al",
    "s_mcall": "M call $",
    "s_mcalliat": "M call [rip+$_iat_",
    "s_mmov": "M mov ",
    "s_argpost": ", [rbp-",
    "s_brack": "], ",
    "s_endbr": "]",
    "s_mjmpif": "M jmp $_if",
    "s_mjmpw": "M jmp $_w",
    "s_iflbl": ":_if",
    "s_wlbl": ":_w",
    "s_m": "M ",
    "s_ifref": " $_if",
    "s_wref": " $_w",
    "s_e": "e",
    "s_db": "DB ",
    "s_dz8": "DZ 8",
    "s_dz0": "DZ 0",
    "s_q1": ' ; "',
    "s_q2": '"',
    "s_dq": "DQ ",
    "s_zero": "0",
    "s_iatlbl": ":_iat_",
    "s_dqhint": "DQ $_hint_",
    "s_hintlbl": ":_hint_",
    "s_hintref": "$_hint_",
    "s_colon": ":",
    "s_lidt": ":_idt",
    "s_liat": ":_iat",
    "s_lintt": ":_intt",
    "s_ldll": ":_dll",
    "s_lentry": ":_entry",
    "s_jne": "jne", "s_je": "je", "s_jge": "jge",
    "s_jg": "jg", "s_jle": "jle", "s_jl": "jl",
    "s_alutail": " r10, r11", "s_shcl": " r10, cl",
    "s_add": "add", "s_sub": "sub", "s_and": "and",
    "s_or": "or", "s_xor": "xor", "s_shl": "shl", "s_shr": "shr",
    "s_rcx": "rcx", "s_rdx": "rdx", "s_r8": "r8", "s_r9": "r9",
}
# E6.4c-3/1 (срез 1: * / %) — эмиттеры imul/divmod и заголовок v2.
# ВНИМАНИЕ: строки добавляются ТОЛЬКО В КОНЕЦ блоба (правило журнала
# E6.4c-3/1: индексы strtab2 укоренились в коде — 108..112 = 0x6C..0x70).
APPEND = {
    "s_mimul": "M imul r10, r11",
    "s_mcqo": "M cqo",
    "s_midiv": "M idiv r11",
    "s_mr10rdx": "M mov r10, rdx",
    "s_hdr1v2": "; UNIVERSAL / WALL v2 / сгенерировано компилятором "
                "WALL (SPEC/11)",
}
# E6.4c-3/4 (срез 4b: индексация e[i] и astore) — хвосты канона SPEC/11
# (загрузка элемента: shl r10,3 / mov r11,r10 / mov r10,[T] / add /
# mov r10,[r10]; запись: shl r11,3 / add / mov [r10],r11).
# ВНИМАНИЕ: только В КОНЕЦ блоба (индексы 113..116 = 0x71..0x74;
# правило журнала E6.4c-3/1: индексы strtab2 укоренились в коде).
APPEND2 = {
    "s_shl3": "M shl r10, 3",
    "s_mmr10r10": "M mov r10, [r10]",
    "s_shl11_3": "M shl r11, 3",
    "s_mmr10r11": "M mov [r10], r11",
}
UTIL = {
    "s_usage": "U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>\r\n",
    "s_errlong": "U-L2-WALL ERR=LONG NAME\r\n",
    "s_erropensrc": "U-L2-WALL ERR=OPEN SRC\r\n",
    "s_errreadsrc": "U-L2-WALL ERR=READ SRC\r\n",
    "s_errbigsrc": "U-L2-WALL ERR=BIG SRC\r\n",
    "s_erropenout": "U-L2-WALL ERR=OPEN OUT\r\n",
    "s_errwriteout": "U-L2-WALL ERR=WRITE OUT\r\n",
    "s_fmtpfx": "U-L2-WALL ERR=FORMAT AT=",
}
# E6.4c-3/2: +break (индекс 0C), +continue (индекс 0D) — только В КОНЕЦ
# таблицы: индексы укоренились в диспетчерах (cmp eax, 0C/0D)
KWS = ["var", "str", "ext", "func", "end", "else",
       "if", "while", "return", "setb", "getb", "len",
       "break", "continue"]

# скаляры: одна область :scalars (bstk в начале — база R13), смещения
# в LAB/ai/scalars_map.py; доступ [r13+X]
SCALARS = [
    ("hstdout", 8), ("written", 8), ("srclen", 8), ("wa_len", 8),
    ("curline", 8), ("lineidx", 8), ("nlentries", 8), ("nlines_v", 8),
    ("lastnonempty", 8), ("textend", 8),
    ("tok_kind", 8), ("tok_val", 8), ("tok_ptr", 8), ("tok_end", 8),
    ("pc_cur", 8), ("pc_d", 8), ("pc_mode", 8), ("pc_extflg", 8),
    ("st_maxd", 8), ("st_maxc", 8), ("st_setb", 8), ("st_ext5", 8),
    ("st_locoff", 8), ("st_loccnt", 8),
    ("lay_nbase", 8), ("lay_maxd", 8), ("lay_maxc", 8),
    # lay_setb (180D8) свободен с E6.4b — срез 4 занят под st_nslots
    ("st_nslots", 8),
    ("lay_ext5", 8), ("lay_fidx", 8),
    ("lay_locoff", 8), ("lay_loccnt", 8),
    ("kctr", 8), ("nlab", 8), ("last_ret", 8),
    ("ifseq1", 8), ("ifseq2", 8),
    ("ntab_cnt", 8), ("ftab_cnt", 8), ("larr_cnt", 8), ("sarr_cnt", 8),
    ("varr_cnt", 8), ("earr_cnt", 8), ("bstk_sp", 8),
    ("seen_func1", 8), ("seen_func2", 8), ("infunc1", 8), ("infunc2", 8),
    ("cur_fsp", 8), ("sm_stop", 8), ("sd_len", 8), ("tmp1", 8),
    ("srctxt_ptr", 8), ("srctxt_len", 8),
    ("cur_nameptr", 8), ("cur_namelen", 8), ("cur_fidx", 8),
    ("strbase", 8),
    ("tmp2", 8), ("tmp3", 8), ("tmp4", 8), ("tmp5", 8), ("tmp6", 8),
    ("tmp7", 8), ("tmp8", 8),
]
BSTK_SIZE = 3072 * 32  # дефект №15: 4 поля × 8 Б = 32 Б/запись (было 24 —
                    # push if затирал lineidx объемлющего while); площадь
                    # области не изменилась (0x18000), ёмкость 4096 -> 3072
BSS = [
    ("fname_in", 0x80), ("fname_out", 0x80),
    ("linebuf", 0x40), ("scr", 0x80),
    ("sm_arr", 65537 * 16),
    ("ntab", 32768 * 40),
    # срез 4: записи выросли (ftab 72→80, larr 16→32, varr 8→16),
    # площадь областей НЕ изменилась (смещения буферов в коде живы):
    # ftab 0x120000/80 = 15564 функции, larr 0x100000/32 = 32768 записей,
    # varr 0x40000/16 = 16384 глобальных — с запасом на 256 КиБ исходника
    ("ftab", 0x120000),
    ("larr", 0x100000),
    ("sarr", 32768 * 24),
    ("varr", 0x40000),
    ("earr", 8 * 8),
    ("ifarr", 32768),
    ("filebuf", 0x21000),
    ("outbuf", 0x200000),
]


def db_rows(data):
    out = []
    for i in range(0, len(data), 16):
        out.append("DB " + " ".join("%02X" % b for b in data[i:i + 16]))
    return out


def pack8(name):
    b = name.encode("ascii")
    return int.from_bytes(b + b"\x00" * (8 - len(b)), "little")


def main():
    # единый блоб строк: базовый порядок — сортировка имён (детерминизм),
    # добавления поздних срезов — СТРОГО в конец (индексы в коде)
    strings = dict(UTIL)
    strings.update(FULL)
    strings.update(FRAG)
    order = sorted(strings)
    strings.update(APPEND)
    order += [n for n in APPEND]
    strings.update(APPEND2)
    order += [n for n in APPEND2]
    blob = bytearray()
    for name in order:
        data = strings[name].encode("utf-8")
        strings[name] = (len(blob), len(data))
        blob += data

    L = []
    A = L.append
    A("; ===== K2-D001 таблица цифр hex =====")
    A(":digits")
    A("DB 30 31 32 33 34 35 36 37 38 39 41 42 43 44 45 46")
    A("")
    A("; ===== K2-D002 kwtab: 14 ключевых слов {имя(8Б), длина, код, 0} =====")
    A(":kwtab")
    for i, kw in enumerate(KWS):
        A("DD %X %X %X %X ; %s" % (pack8(kw) & 0xFFFFFFFF,
                                    (pack8(kw) >> 32) & 0xFFFFFFFF,
                                    len(kw), i, kw))
    A("")
    A("; ===== K2-D003 jcctab: инверсии сравнений {смещ, длина} =====")
    A(":jcctab")
    for s in ("s_jne", "s_je", "s_jge", "s_jg", "s_jle", "s_jl"):
        A("DD %X %X ; %s" % (strings[s][0], strings[s][1], s))
    A("")
    A("; ===== K2-D004 alutab: АЛУ-операторы {смещ, длина} =====")
    A(":alutab")
    for s in ("s_add", "s_sub", "s_and", "s_or", "s_xor"):
        A("DD %X %X ; %s" % (strings[s][0], strings[s][1], s))
    A("")
    A("; ===== K2-D005 argtab: регистры аргументов {смещ, длина} =====")
    A(":argtab")
    for s in ("s_rcx", "s_rdx", "s_r8", "s_r9"):
        A("DD %X %X ; %s" % (strings[s][0], strings[s][1], s))
    A("")
    A("; ===== K2-D006 errtab: 7 записей {смещ, длина, код, 0} =====")
    A(":errtab")
    for s, code in (("s_usage", 2), ("s_errlong", 3), ("s_erropensrc", 4),
                    ("s_errreadsrc", 5), ("s_errbigsrc", 7),
                    ("s_erropenout", 8), ("s_errwriteout", 9)):
        A("DD %X %X %X 0 ; код %d" % (strings[s][0], strings[s][1],
                                       code, code))
    A("")
    A("; ===== K2-D007 strblob: единый блоб строк =====")
    A(":strblob")
    L.extend(db_rows(bytes(blob)))
    A("")
    A("; ===== K2-D008 strtab2: смещения/длины (индекс = номер) =====")
    A(":strtab2")
    for name in order:
        A("DD %X %X ; %s" % (strings[name][0], strings[name][1], name))
    A("")
    A("; ===== K2-D010 таблица импортов kernel32.dll =====")
    A("DZ 1 ; выравнивание чётности RVA hint-записей (инвариант 7 SPEC/04)")
    # калибровка чётности (механизм E4a): рост тела/данных до dll_name
    # сдвигает hint-записи; DZ после dll_name подбирается чётным
    DZ_DLL = 2  # E6.4c-3/4b: фактические idata 0x76DD (нечётное) —
                # hints = idata+0xB0+13+DZ_DLL = 0x779C (чётное, инвариант 7)
    A(":idt")
    A("DD $intt 0 0 $dll_name $iat ; описатель импорта")
    A("DZ 14 ; терминатор IDT")
    A(":iat")
    A(":iat_gsh")
    A("DQ $hint_gsh ; GetStdHandle")
    A(":iat_wf")
    A("DQ $hint_wf ; WriteFile")
    A(":iat_ep")
    A("DQ $hint_ep ; ExitProcess")
    A(":iat_gcl")
    A("DQ $hint_gcl ; GetCommandLineA")
    A(":iat_cf")
    A("DQ $hint_cf ; CreateFileA")
    A(":iat_rf")
    A("DQ $hint_rf ; ReadFile")
    A(":iat_ch")
    A("DQ $hint_ch ; CloseHandle")
    A("DQ 0 ; терминатор")
    A(":intt")
    A("DQ $hint_gsh $hint_wf $hint_ep $hint_gcl $hint_cf $hint_rf $hint_ch 0")
    A(":dll_name")
    A("DB 6B 65 72 6E 65 6C 33 32 2E 64 6C 6C 00 ; kernel32.dll")
    A("DZ %d ; чётность RVA hint-записей" % DZ_DLL)
    A(":hint_gsh")
    A("DB 00 00 47 65 74 53 74 64 48 61 6E 64 6C 65 00 ; GetStdHandle")
    A("DZ 1")
    A(":hint_wf")
    A("DB 00 00 57 72 69 74 65 46 69 6C 65 00 ; WriteFile")
    A(":hint_ep")
    A("DB 00 00 45 78 69 74 50 72 6F 63 65 73 73 00 ; ExitProcess")
    A(":hint_gcl")
    A("DB 00 00 47 65 74 43 6F 6D 6D 61 6E 64 4C 69 6E 65 ; GetCommandLineA")
    A("DB 41 00")
    A(":hint_cf")
    A("DB 00 00 43 72 65 61 74 65 46 69 6C 65 41 00 ; CreateFileA")
    A(":hint_rf")
    A("DB 00 00 52 65 61 64 46 69 6C 65 00 ; ReadFile")
    A("DZ 1")
    A(":hint_ch")
    A("DB 00 00 43 6C 6F 73 65 48 61 6E 64 6C 65 00 ; CloseHandle")
    A("")
    A("; ===== K2-D011 виртуальные нули (bss) =====")
    # E6.4c-3/1: единая область :scalars — буферы адресуются смещениями
    # r13+X (не метками): освобождено 14 записей labtab (предел brick 512).
    total = BSTK_SIZE + 8 * len(SCALARS)
    offs = {}
    off = BSTK_SIZE
    for name, _sz in SCALARS:
        offs[name] = off
        off += 8
    bufs = []
    for name, size in BSS:
        bufs.append(";   %-10s %s DBZ %X"
                    % (name, ("r13+%X" % off).ljust(11), size))
        off += size
        total += size
    A(":scalars")
    A("DBZ %X ; bstk[3072x32] + скаляры + ВСЕ буферы (база R13)." % total)
    A("; E6.4c-3/1: буферы адресуются смещениями от R13, а не метками")
    A("; (освобождено 14 записей labtab — предел меток brick 512).")
    A("; Сумма прежних DBZ не изменилась (0x7A1418). Карта:")
    L.extend(bufs)

    with open(os.path.join("LAB", "ai", "scalars_map.py"), "w") as f:
        f.write("# смещения скаляров в :scalars (база R13)\n")
        f.write("SCALOFF = %r\n" % (offs,))
    text = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(text.encode("utf-8"))
    with open(os.path.join("LAB", "ai", "strtab_map.py"), "w") as f:
        f.write("# соответствие имя-строки -> индекс strtab2 (генерация)\n")
        f.write("STRMAP = %r\n" % ({n: i for i, n in enumerate(order)},))
    print("written %s: %d строк, блоб %d байт, bss=0x%X, строк=%d"
          % (OUT, len(L), len(blob), total, len(order)))


if __name__ == "__main__":
    main()
