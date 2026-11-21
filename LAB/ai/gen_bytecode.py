"""gen_bytecode.py — (частное) регенерация KERNEL/L5-BRIDGE/BYTECODE.md
(срез E9.2-3b): карта меток bridge.brick (labels_of) + таблица
описаний функций/данных -> секции 1-4. Запуск из корня репозитория.
Обновлять таблицу FUNCS при добавлении функций ветвей.
"""
import io
import sys

sys.path.insert(0, "LAB/py")
sys.path.insert(0, "LAB/ai")

from label_map import labels_of          # noqa: E402

FUNCS = {
    "c": ("сервис (bridge_self_c.wall — реинкарнации K3-C001..C007 "
          "ядра kernel.wall)", [
        ("print_error", "печать сообщения + ExitProcess(код)"),
        ("skip0", "пропуск argv0 + разделителей"),
        ("read_arg", "слово-аргумент (>= 128 -> код 3)"),
        ("check_end", "ровно три аргумента (иначе справка, код 2)"),
        ("widen", "имя -> UTF-16LE для CreateFile2"),
        ("copy_str", "копия n байтов в буфер (факт-строка)"),
        ("out_dec", "десятичная запись числа в буфер"),
        ("out_hex", "8 ЗАГЛАВНЫХ hex-цифр в буфер"),
    ]),
    "pe": ("разбор PE и семейство (bridge_self_pe.wall — срез "
           "E9.2-1)", [
        ("rd16", "LE u16 по байтовому смещению"),
        ("rd32", "LE u32 по байтовому смещению"),
        ("fail_family", "ERR=FAMILY + выход 6 (единственный отказ)"),
        ("guard", "границы чтения [off, off+n) из exebuf"),
        ("check_head", "MZ + PE-сигнатура по e_lfanew + длина 0x1B0"),
        ("check_opt", "Machine/NSections/OptHdr/Chars/Magic/Subsys"),
        ("check_base", "ImageBase (2 dword)/SectAlign/FileAlign"),
        ("check_sect", "имя .text/vaddr/chars; vsize/raw/rawptr"),
        ("check_size", "SizeOfImage/Headers/Raw/файл; вход в секции"),
        ("check_body", "тело не пустое и не из одних нулей"),
        ("stub_name", "имя модуля из DOS-заглушки (префикс/игла)"),
        ("rva_off", "RVA тела (0x1000+) -> файловое смещение"),
        ("walk_descs", "дескрипторы IDT (1 шт + терминатор), thunk"),
        ("cstr_len", "длина C-строки (quirk: без NUL -> len-1)"),
        ("check_dll", "имя DLL == kernel32.dll (без регистра)"),
        ("walk_funcs", "счёт записей INT/IAT (терминатор/чётность)"),
        ("print_facts", "факт-строка MODULE/ENTRY/.../BSS в stdout"),
    ]),
    "d": ("декодер x86-подмножества SPEC/05, часть 1 "
          "(bridge_self_d.wall — E9.2-2/3a)", [
        ("fb", "байт файла с границей (отказ — данные)"),
        ("rel8", "знаковый байт"),
        ("rel32", "знаковый dword (2^32 — произведением)"),
        ("u32", "БЕЗзнаковый dword (imm32/disp32 SIB)"),
        ("u64", "БЕЗзнаковый qword (imm64; 2^32 множителем)"),
        ("modrm_read", "полный разбор modrm+SIB+disp -> om*"),
        ("set_reg", "операнд-регистр в слот 1/2"),
        ("set_rm", "операнд из modrm (рег mod=3 | память)"),
        ("set_imm", "непосредственный в слот (знаковая печать)"),
        ("set_immu", "imm64 в слот (БЕЗзнаковая печать, вид 7)"),
        ("set_tgt", "операнд-цель перехода в слот 1"),
        ("set_cl", "операнд «cl» в слот 2"),
        ("set_cnt", "счётчик сдвига (целое) в слот 2"),
        ("alu_id", "id мнемоники ALU по байту (таблица)"),
        ("dec0f", "группа 0F (movzx/test/imul)"),
        ("decalu", "семейство ALU 00..3D"),
        ("decmod", "test/mov/lea 84..8D"),
    ]),
    "d2": ("декодер, часть 2 (bridge_self_d2.wall — E9.2-3a)", [
        ("decimm", "push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC"),
        ("decshift", "сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)"),
        ("decgrp", "imm-группа 80/81/83 (reg с REX.R)"),
        ("decgrp2", "хвостовые C6/C7/F6/F7/FF (call косвенный)"),
        ("decbr", "переходы E8/E9/EB/jcc rel8 (классы 2/3/4)"),
        ("decode_ins", "диспетчер: REX, 0F, множества байтов; da*/om*"),
    ]),
    "w": ("спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a)", [
        ("walk_code", "стек целей (куча), проход, тени/нули/терминалы"),
        ("sweep_ins", "выжившие (младший адрес), inscount/maxend; "
                      "СДАМП sdump (E9.2-3a) — старты по возрастанию"),
        ("calc_target", "target (вилка raw-0x1FF) и bss"),
    ]),
    "e": ("примитивы эмиссии b2 (bridge_self_e.wall — срез "
          "E9.2-3a; драйвер — ветвь L с E9.2-3b)", [
        ("fill_offs", "смещения NUL-имён блоба -> массив offs"),
        ("init_tables", "таблицы мнемоник/условий/регистров + шапка"),
        ("tpl_dec", "HEX-литерал s_tpl (199 Б) -> массив tplb"),
        ("app_ch", "байт в буфер вывода"),
        ("app_name", "имя из блоба по таблице смещений"),
        ("app_reg", "имя регистра (блоб по размеру 8/16/32/64)"),
        ("out_hexv", "ЗАГЛАВНЫЙ hex без ведущих нулей (v >= 0)"),
        ("out_hxs", "знаковый hex (imm/цель/счётчик)"),
        ("out_hxu64", "hex u64 (отрицательное = битовый образ)"),
        ("out_hex2", "ровно 2 hex-цифры (байты H/DB)"),
        ("out_hex4m", "минимум 4 hex-цифры (@смещения)"),
        ("out_sdec", "знаковый dec со знаком +/-"),
        ("note_op", "примечание одного операнда (== _note)"),
        ("emit_note", "примечание H-строки (jcc/имена/[rip±d])"),
        ("emit_h", "H-строка выжившей инструкции"),
        ("emit_data", "данные сегмента DZ/DB (== оракул)"),
        ("app_tpl", "кусок шаблона шапки из tplb"),
    ]),
    "l": ("карты и семантика (bridge_self_l.wall — часть 1, срез "
          "E9.2-3b)", [
        ("imp_hints", "записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> "
                      "+2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)"),
        ("san_put", "имя функции k -> блоб snam «iat_»+san (ASCII, "
                    "«_», 59, «f»)"),
        ("imp_offs", "базы импортов: iatoff/intoff/nameoff/idtoff"),
        ("imp_labels", "метки iat_/d* (представимость!) + knownoff; "
                       "impbad"),
        ("build_sstate", "карта выживших: 1 старт / 2 внутри"),
        ("sem_add", "кандидат-тройка (off, kind, h); совпадение off — "
                    "замена"),
        ("dq_base", "твонки IAT/INT: валидность значений + меток hint"),
        ("dd_idt", "дескриптор IDT — кандидат DD"),
        ("sem_filter", "приёмка: сортировка + конфликты (инструкции/"
                       "строки/метки внутри) -> semstate"),
        ("ins_labels", "метки l*/d* по операндам (цели/rip; приоритет "
                       "iat_ > l > d)"),
        ("out_hexl", "СТРОЧНЫЙ hex без нулей (имена l*/d*)"),
        ("emit_labname", "имя метки по labmap (d/l/iat_ из snam)"),
        ("emit_cut", "строка разреза «:имя ; @смещ4»"),
        ("emit_dollar", "dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex"),
        ("emit_sem", "строка DD (5 значений) / DQ ($имя | 0)"),
        ("build_maps", "сборка карт: кучи + sstate + импорты + "
                       "семантика + метки операндов"),
    ]),
    "l2": ("рендер и драйвер (bridge_self_l2.wall — часть 2, срез "
           "E9.2-3b/c)", [
        ("out_hexl", "СТРОЧНЫЙ hex без нулей (имена l*/d*)"),
        ("emit_labname", "имя метки по labmap (d/l/iat_ из snam)"),
        ("emit_cut", "строка разреза «:имя ; @смещ4»"),
        ("emit_dollar", "dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex"),
        ("emit_sem", "строка DD (5 значений) / DQ ($имя | 0)"),
        ("emit_body", "ДРАЙВЕР (КАНОН): шапка + проход по разрезам "
                      "[0, target) — выжившая сначала m_line (M), при "
                      "провале emit_h; счёты mcount/hcount; запись .b2 "
                      "(коды 8/9)"),
    ]),
    "m": ("примитивы ветви M (bridge_self_m.wall — срез E9.2-3c)", [
        ("m_put", "байт в буфер кодировки mbuf"),
        ("m_put4", "dword LittleEndian в mbuf (imm32/disp32)"),
        ("m_rex", "REX-префикс по аргументам-значениям (w==64, r/x/b "
                  "— коды регистров)"),
        ("m_enc_mem", "modrm+SIB+disp операнда-памяти (rip -> слот 4 Б "
                      "в конце) — == _enc_mem"),
        ("m_cmp", "СВЕРКА mbuf с телом (слот последним; значение слота "
                  "== метка - конец слота) — == _template"),
        ("m_kw", "слово размера byte/word/dword/qword + пробел"),
        ("m_dollar", "«$имя» ($base/-4096 | labmap; «:1» при rel8)"),
        ("m_opmem", "рендер памяти [base+idx±disp] | [rip+$имя] (kw; "
                    "масштаб 1)"),
        ("m_opr", "ренер одного операнда (рег/imm/cnt/cl/mem; 16 бит "
                  "-> H)"),
    ]),
    "m2": ("кодировщики простых семейств (bridge_self_m2.wall — "
           "E9.2-3c)", [
        ("m_bsimple", "cdqe/cqo/ret/int3 (SIMPLE)"),
        ("m_bjmp", "jmp ($base/метка; EB слот 1 / E9 слот 4)"),
        ("m_bjcc", "jcc (70|cc слот 1 / 0F 80|cc слот 4)"),
        ("m_bcall", "call (E8 $метка | FF 15 [rip+$имя])"),
        ("m_bmovzx", "movzx r32/r64 <- r8/mem 8/16 (0F B6/B7, kw)"),
        ("m_bstack", "push/pop r64 (5x + REX.B)"),
        ("m_btest", "test r,r (84/85)"),
        ("m_blea", "lea r32/r64, mem (8D, без kw)"),
        ("m_bimul", "imul r64,r64 (REX.WRB 0F AF /r)"),
        ("m_bshift", "rol/shl/shr/sar (C0/C1 imm8 | D2/D3 cl)"),
        ("m_bf7", "neg/idiv (F7 /3 /7)"),
        ("m_bff", "inc/dec (FF /0 /1)"),
    ]),
    "m3": ("кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c)", [
        ("m_alu_base", "базовый опкод ALU по dname (00/08/20/28/30/38)"),
        ("m_alu_ext", "/ext ALU по dname (0/1/4/5/6/7)"),
        ("m_alu_imm", "форма группы imm 80/83/81 по значению/размеру "
                      "(глобали mopc/mis8)"),
        ("m_balu", "add/or/and/sub/xor/cmp по парам операндов "
                   "(r,r/r,i/r,m/m,r/m,i)"),
        ("m_bmov", "mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/"
                   "r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)"),
    ]),
    "m4": ("драйвер ветви M (bridge_self_m4.wall — E9.2-3c)", [
        ("m_body", "диспетчер по dname: имя мнемоники (jcc — j+cc) + "
                   "кодировщик семейства (рендер операндов)"),
        ("m_line", "ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + "
                   "хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)"),
    ]),
}

GLOB_ORDER = ["hstdout", "cmdline", "written", "wlen", "exebuf",
              "exelen", "entryrva", "vsize", "rawsize", "rawptr",
              "modlen", "thunk", "dllfile", "impn", "insmap", "lenmap",
              "pend", "rawlim", "psp", "inscount", "maxend", "swcur",
              "target", "bss", "dlen", "dcls", "dtgt", "dpos", "mpos",
              "mreg", "dname", "dcc", "dargc", "da1k", "da2k", "da1r",
              "da2r", "da1s", "da2s", "da1v", "da2v", "damem",
              "ombase", "omidx", "omscale", "omdisp", "omsize", "omrip",
              "mkind", "mrreg", "mrdip", "mripon", "sdump", "outmem",
              "outbuf", "outcur", "iatoff", "intoff", "nameoff",
              "idtoff", "impbad", "kn", "snlen", "semcnt", "semacc",
              "hhrv", "hno", "hnl", "snam", "noffs", "knownoff",
              "semrows", "labmap", "sstate", "semstate",
              "mblen", "mslot", "mslotz", "mslof", "mopc", "mis8",
              "mcount", "hcount"]
ARRS = [("arg1", 0x80), ("arg2", 0x80), ("arg3", 0x80),
        ("factbuf", 0xC0), ("o_mn", 0xE8), ("o_cc", 0x88),
        ("o_r64", 0x88), ("o_r8", 0x88), ("o_r16", 0x88),
        ("o_r32", 0x88), ("o_kw", 0x28), ("tplb", 0xC8),
        ("mbuf", 0xC0), ("w1", 0x200)]
STR_ORDER = ["s_use", "s_long", "s_oexe", "s_rexe", "s_family",
             "s_big", "s_oout", "s_wout", "s_f1", "s_f2", "s_f3",
             "s_f4", "s_f5", "s_f6", "s_f7", "s_f8", "s_f9", "s_fa",
             "s_crlf", "s_pref", "s_needle", "s_dll", "s_h", "s_at",
             "s_ml", "s_ripl", "s_base", "s_s1", "s_kw", "s_dz",
             "s_db", "s_iat", "s_dd", "s_dq", "s_mem", "s_rip",
             "s_cl", "s_j", "s_comma", "s_mn", "s_cc", "s_r64",
             "s_r8", "s_r16", "s_r32", "s_tpl"]

B2_SHA = "E945ED20E63EF1008DCA4D3F920C3EA6D88F141AB27589DE273AFB0D0DF8619F"
BRICK_SHA = "A9EFC7357E1E1D34EF65BC7499054D339E755992BEDEEC4CB0747FEA30C0CD23"
EXE_SHA = "B3598A111827D646BB5D597489BE38F18D68FA38AB90274684AE25BA529BC167"


def main():
    lbl = labels_of(open("KERNEL/L5-BRIDGE/bridge.brick", "rb").read())
    out = []
    w = out.append
    w("# BYTECODE. Модуль M5-BRIDGE — карта образа")
    w("")
    w("Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | роль: "
      "разбор образа bridge.exe.")
    w("")
    w("## 1. Сводка")
    w("")
    w("| Параметр | Значение |")
    w("|---|---|")
    w("| Файл | KERNEL/L5-BRIDGE/bridge.exe, 88576 байтов (0x15A00) |")
    w("| SHA-256 | %s |" % EXE_SHA)
    w("| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c): "
      "сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> "
      "bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. "
      "Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == "
      "оракулу LAB/py/lab_l2.py байт-в-байт |")
    w("| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 12 частей "
      "bridge_self_*.wall (WALL v2, разрез SPEC/10); склейка 123983 Б "
      "(47% предела входа 256 КиБ; 4362 строки — заголовок bridge.b2) |")
    w("| Тело секции | 87943 байта (0x15787), RVA 0x1000, SRD 0x15800 |")
    w("| VirtualSize | 0x15787 (одна секция); target 0x15601, bss 0x186 "
      "(хвост — виртуальные нули) |")
    w("| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после "
      "фиксированной области импортов 0x200) |")
    w("| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — "
      "фиксированная область импортов SPEC/11 п. 6 |")
    w("| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, "
      "ExitProcess, GetCommandLineA, CreateFile2, ReadFile, "
      "CloseHandle, GlobalAlloc |")
    w("| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя "
      "модуля — bridge.peg) |")
    w("| M-строк в исходнике | 18701 (bridge.b2; 100% M — H=0, круг "
      "T-E9-20: M=18701 H=0) |")
    w("| Меток в исходнике | 1203 из 2048 (лимит brick; карта — "
      "LAB/ai/bridge_labelmap.py) |")
    w("| Функций | 114 (карта — §2) + данные (§3) |")
    w("| Компилятор сборки | wall.exe (M2-WALL, самосборный) — "
      "конвейер под эмуляцией LAB (T-E9-17: 594593328 + 63479986 + "
      "63726951 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — "
      "прямой lab_win с лимитом 2 млрд, прецедент T-E6-49a) |")
    w("")
    w("## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по "
      "bridge.brick)")
    w("")
    w("Группировка — по частям bridge.wall (состав — CARD.md; кирпичи "
      "K5-* — MAP/M5-BRIDGE.md, MAP/M5-BRIDGE-D.md, "
      "MAP/M5-BRIDGE-E.md, MAP/M5-BRIDGE-L.md и MAP/M5-BRIDGE-M.md).")
    w("")
    w("```")
    for key in ("c", "pe", "d", "d2", "w", "e", "l", "l2",
                "m", "m2", "m3", "m4"):
        title, funcs = FUNCS[key]
        w("%s:" % title)
        for name, desc in funcs:
            rva = lbl[name]
            if len(desc) > 66:
                w("  %-18s %04X  %s" % (name, rva, desc))
            else:
                w("  %-18s %04X  %s" % (name, rva, desc))
        w("")
    w("вход (bridge.wall):")
    w("  main ................. %04X  CLI -> чтение EXE -> проверки -> "
      "спуск ->" % lbl["main"])
    w("                               таблицы -> карты (L) -> эмиссия .b2 "
      "(КАНОН M/H) -> факты M=/H=")
    w("```")
    w("")
    w("## 3. Данные образа (RVA)")
    w("")
    w("```")
    w("строки (46): " + " ".join(
        "%s %04X" % (n, lbl[n]) for n in STR_ORDER[:4]))
    for i in range(4, len(STR_ORDER), 5):
        w("  " + " ".join("%s %04X" % (n, lbl[n])
                          for n in STR_ORDER[i:i + 5]))
    w("глобали (86): " + " ".join(
        "%s %04X" % (n, lbl[n]) for n in GLOB_ORDER[:4]))
    for i in range(4, len(GLOB_ORDER), 6):
        w("  " + " ".join("%s %04X" % (n, lbl[n])
                          for n in GLOB_ORDER[i:i + 6]))
    arrline = "  " + " ".join("%s %04X (0x%X)" % (n, lbl[n], sz)
                              for n, sz in ARRS[:3])
    w(arrline)
    w("  " + " ".join("%s %04X (0x%X)" % (n, lbl[n], sz)
                      for n, sz in ARRS[3:6]))
    w("  " + " ".join("%s %04X (0x%X)" % (n, lbl[n], sz)
                      for n, sz in ARRS[6:9]))
    w("  " + " ".join("%s %04X (0x%X)" % (n, lbl[n], sz)
                      for n, sz in ARRS[9:12]))
    w("  " + " ".join("%s %04X (0x%X)" % (n, lbl[n], sz)
                      for n, sz in ARRS[12:14]))
    w("конец тела: %04X (vsize 0x15787)" % (lbl["w1"] + 0x200))
    w("```")
    w("")
    w("Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; "
      "урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост "
      "(0x15601..0x15787, 0x186 Б) всегда < 0x200 Б и падает внутрь w1 "
      "при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — "
      "БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); "
      "rip-ссылок внутрь хвоста нет (lea — только базы массивов, они "
      "ниже target), разбор моста над bridge.exe даёт 0 H-строк "
      "(M=18701; как kernel/uva — T-E9-20).")
    w("")
    w("## 4. Контроль воспроизведения")
    w("")
    w("Сборка из исходника (под эмуляцией LAB; то же делает батарея "
      "T-E9-17):")
    w("")
    w("```")
    w("splice.exe bridge.wall bridge_s.flat")
    w("wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL "
      "байт-в-байт)")
    w("enc.exe    bridge_s.b2  bridge_s.brick")
    w("brick.exe  bridge_s.brick bridge_s.bin")
    w("pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)")
    w("```")
    w("")
    w("SHA-256 артефактов: bridge.b2 — E945ED20…F8619F, bridge.brick — "
      "A9EFC735…C0CD23, bridge.exe — B3598A11…29BC167 (полные — "
      "VERIFY.md).")
    w("")
    io.open("KERNEL/L5-BRIDGE/BYTECODE.md", "w",
            encoding="utf-8", newline="\n").write("\n".join(out))
    print("BYTECODE.md записан: %d строк" % len(out))


if __name__ == "__main__":
    main()
