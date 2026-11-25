#!/usr/bin/env python3
"""gen_bytecode_e94_4b.py — регенерация KERNEL/L5-BRIDGE/BYTECODE.md
после пересборки bridge.exe срезом E9.4-4b-1 (развилка «семья | чужой»
+ pf.wall/pi.wall). Читает карту меток (bridge_labelmap.py), вход —
старый BYTECODE.md НЕ используется для RVA (только описания — в
таблице PARTS ниже); числа §1 — из фактов самопрогона."""
import io
import subprocess
import sys

ROOT = "/home/z/my-project/repo"

# карта меток -> RVA
out = subprocess.run([sys.executable, "LAB/ai/bridge_labelmap.py"],
                     cwd=ROOT, capture_output=True, text=True).stdout
LAB = {}
for ln in out.splitlines():
    p = ln.split()
    if len(p) == 3:
        LAB[p[0]] = p[2]

# функции: часть -> [(имя, описание)]
PARTS = [
    ("сервис (bridge_self_c.wall — реинкарнации K3-C001..C007 ядра kernel.wall):", [
        ("print_error", "печать сообщения + ExitProcess(код)"),
        ("skip0", "пропуск argv0 + разделителей"),
        ("read_arg", "слово-аргумент (>= 128 -> код 3)"),
        ("check_end", "ровно три аргумента (иначе справка, код 2)"),
        ("widen", "имя -> UTF-16LE для CreateFile2"),
        ("copy_str", "копия n байтов в буфер (факт-строка)"),
        ("out_dec", "десятичная запись числа в буфер"),
        ("out_hex", "8 ЗАГЛАВНЫХ hex-цифр в буфер")]),
    ("общий фронт PE и семейные проверки-предикат (bridge_self_pe.wall — часть 1, E9.2-1 + E9.4-4b-1):", [
        ("rd16", "LE u16 по байтовому смещению"),
        ("rd32", "LE u32 по байтовому смещению"),
        ("fail_family", "ERR=FAMILY + выход 6 (ОБЩИЙ отказ: не семья И не чужой)"),
        ("guard", "границы чтения [off, off+n) из exebuf: 0/1 (предикат)"),
        ("check_head", "ОБЩИЙ фронт: MZ + PE-сигнатура + раскладка полей ОТ e_lfanew (lfanew/coffoff/optoff/sizopt/numsect/tbloff)"),
        ("check_opt", "Machine/NSections/OptHdr/Chars/Magic/Subsys — предикат"),
        ("check_base", "ImageBase (2 dword)/SectAlign/FileAlign — предикат"),
        ("check_sect", "имя .text/vaddr/chars; vsize/raw/rawptr + codevaddr/falign/fend"),
        ("check_size", "SizeOfImage/Headers/Raw/файл; вход в секции — предикат"),
        ("check_body", "тело не пустое и не из одних нулей — предикат"),
        ("stub_name", "имя модуля из DOS-заглушки (префикс/игла) — предикат")]),
    ("импорты семейства, цепочка, факт-строка (bridge_self_pi.wall — часть 2, разрез pe по лимиту 500):", [
        ("rva_off", "RVA тела (0x1000+) -> файловое смещение"),
        ("walk_descs", "дескрипторы IDT по DD[1] @optoff+0x78 (1 шт + терминатор), thunk"),
        ("cstr_len", "длина C-строки (quirk: без NUL -> len-1)"),
        ("check_dll", "имя DLL == kernel32.dll (без регистра)"),
        ("walk_funcs", "счёт записей INT/IAT (терминатор/чётность)"),
        ("fam_chain", "СЕМЕЙНАЯ ЦЕПОЧКА-ПРЕДИКАТ: 0 = семейство, 1 = нет (развилка в main — E9.4-4b-1)"),
        ("print_facts", "факт-строка MODULE/ENTRY/.../BSS в stdout")]),
    ("ЧУЖОЙ ПУТЬ развилки (bridge_self_pf.wall — часть 3, E9.4-4b-1):", [
        ("foreign_front", "порт parse_foreign: Machine/Magic, FileAlignment степень 2, секция кода ПО ВХОДУ, EXECUTE, файл покрывает raw, тело не нулевое, вход в raw-части; глобали спуска"),
        ("print_ffacts", "ЧУЖАЯ факт-строка FOREIGN=1 SECT=… (== parse_foreign; эмиссия — срезы E9.4-4b-2+)")]),
    ("декодер x86-подмножества SPEC/05, часть 1 (bridge_self_d.wall — E9.2-2/3a; границы — fend, E9.4-4b-1):", [
        ("fb", "байт ТЕЛА с границей fend (отказ — данные)"),
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
        ("decmod", "test/mov/lea 84..8D")]),
    ("декодер, часть 2 (bridge_self_d2.wall — E9.2-3a; FF — делегация в decff):", [
        ("decimm", "push/pop/cdqe/cqo/mov r,imm/терминалы C3/CC"),
        ("decshift", "сдвиги C0/C1/D3 (imm8 | cl, маска 63/31)"),
        ("decgrp", "imm-группа 80/81/83 (reg с REX.R)"),
        ("decgrp2", "хвостовые C6/C7/F6/F7 (FF -> decff — E9.4-4a)"),
        ("decbr", "переходы E8/E9/EB/jcc rel8 (классы 2/3/4)"),
        ("decode_ins", "диспетчер: REX, 0F, множества байтов; da*/om*")]),
    ("декодер, часть 3 — группа FF (bridge_self_d3.wall — срез E9.4-4a):", [
        ("decff", "FF: peek ext с REX.R ДО modrm_read; /0 inc /1 dec /2 call /4 jmp r/m64 (КОСВЕННЫЙ — размер /4 ВСЕГДА 64, класс 5 — терминал спуска)")]),
    ("спуск от входа (bridge_self_w.wall — срезы E9.2-2/3a + E9.4-4a + 4-4b-1):", [
        ("push_tgt", "цель в стек — ДЕДУПЛИКАЦИЯ по значению (карта pushmap; вне [0, rawlim) не кладётся; предел pend 1+rawlim)"),
        ("jtab", "таблицы переходов: jmp qword [rip+X] — qword-строки «до первого non-code qword» -> кандидаты (== _jtab; чтение — тело+вирт. нули)"),
        ("walk_code", "стек целей (куча), проход, тени/нули/терминалы (dcls 5 — терминал + jtab; цели — push_tgt); старт — entryrva-codevaddr"),
        ("sweep_ins", "выжившие (младший адрес), inscount/maxend; СДАМП sdump (E9.2-3a) — старты по возрастанию"),
        ("calc_target", "target (вилка falign образа — E9.4-4b-1; семья 0x200) и bss")]),
    ("примитивы эмиссии b2 (bridge_self_e.wall — срез E9.2-3a; драйвер — ветвь L с E9.2-3b; с E9.2-4 — и вызов ptpl_dec ветви G):", [
        ("fill_offs", "смещения NUL-имён блоба -> массив offs"),
        ("init_tables", "таблицы мнемоник/условий/регистров + шапки b2/PEG"),
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
        ("app_tpl", "кусок шаблона шапки из tplb")]),
    ("карты и семантика (bridge_self_l.wall — часть 1, срез E9.2-3b):", [
        ("imp_hints", "записи INT/IAT -> hhrv/hno/hnl (бит 63: v<0 -> +2^63; сравнение с 2^63 НЕВОЗМОЖНО — урок)"),
        ("san_put", "имя функции k -> блоб snam «iat_»+san (ASCII, «_», 59, «f»)"),
        ("imp_offs", "базы импортов: iatoff/intoff/nameoff/idtoff (DD[1] @optoff+0x78 — E9.4-4b-1)"),
        ("imp_labels", "метки iat_/d* (представимость!) + knownoff; impbad"),
        ("build_sstate", "карта выживших: 1 старт / 2 внутри"),
        ("sem_add", "кандидат-тройка (off, kind, h); совпадение off — замена"),
        ("dq_base", "твонки IAT/INT: валидность значений + меток hint"),
        ("dd_idt", "дескриптор IDT — кандидат DD"),
        ("sem_filter", "приёмка: сортировка + конфликты (инструкции/строки/метки внутри) -> semstate"),
        ("ins_labels", "метки l*/d* по операндам (цели/rip; приоритет iat_ > l > d)")]),
    ("рендер и драйвер (bridge_self_l2.wall — часть 2, срез E9.2-3b/c):", [
        ("out_hexl", "СТРОЧНЫЙ hex без нулей (имена l*/d*)"),
        ("emit_labname", "имя метки по labmap (d/l/iat_ из snam)"),
        ("emit_cut", "строка разреза «:имя ; @смещ4»"),
        ("emit_dollar", "dword -> «$имя» (knownoff) | ЗАГЛАВНЫЙ hex"),
        ("emit_sem", "строка DD (5 значений) / DQ ($имя | 0)"),
        ("build_maps", "сборка карт: кучи + sstate + импорты + семантика + метки операндов"),
        ("emit_body", "ДРАЙВЕР (КАНОН): шапка + проход по разрезам [0, target) — выжившая сначала m_line (M), при провале emit_h; счёты mcount/hcount; запись .b2 (коды 8/9)")]),
    ("примитивы ветви M (bridge_self_m.wall — срез E9.2-3c):", [
        ("m_put", "байт в буфер кодировки mbuf"),
        ("m_put4", "dword LittleEndian в mbuf (imm32/disp32)"),
        ("m_rex", "REX-префикс по аргументам-значениям (w==64, r/x/b — коды регистров)"),
        ("m_enc_mem", "modrm+SIB+disp операнда-памяти (rip -> слот 4 Б в конце) — == _enc_mem"),
        ("m_cmp", "СВЕРКА mbuf с телом (слот последним; значение слота == метка - конец слота) — == _template"),
        ("m_kw", "слово размера byte/word/dword/qword + пробел"),
        ("m_dollar", "«$имя» ($base/-4096 | labmap; «:1» при rel8)"),
        ("m_opmem", "рендер памяти [base+idx±disp] | [rip+$имя] (kw; масштаб 1)"),
        ("m_opr", "рендер одного операнда (рег/imm/cnt/cl/mem; 16 бит -> H)")]),
    ("кодировщики простых семейств (bridge_self_m2.wall — E9.2-3c):", [
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
        ("m_bff", "inc/dec (FF /0 /1)")]),
    ("кодировщики ALU и MOV (bridge_self_m3.wall — E9.2-3c):", [
        ("m_alu_base", "базовый опкод ALU по dname (00/08/20/28/30/38)"),
        ("m_alu_ext", "/ext ALU по dname (0/1/4/5/6/7)"),
        ("m_alu_imm", "форма группы imm 80/83/81 по значению/размеру (глобали mopc/mis8)"),
        ("m_balu", "add/or/and/sub/xor/cmp по парам операндов (r,r/r,i/r,m/m,r/m,i)"),
        ("m_bmov", "mov по парам (r,r/r,i8 B0/r,i32 B8/r64 C7/r,m 8A-8B/m,r 88-89/m,i C6-C7; imm64 -> H)")]),
    ("драйвер ветви M (bridge_self_m4.wall — E9.2-3c):", [
        ("m_body", "диспетчер по dname: имя мнемоники (jcc — j+cc) + кодировщик семейства (рендер операндов)"),
        ("m_line", "ДРАЙВЕР M-строки: decode + «M » + m_body + m_cmp + хвост « ; @смещ4»; провал — откат и 1 (H-фолбэк)")]),
    ("PEG-выход (bridge_self_g.wall — срез E9.2-4; idata/iat — вычисляемые смещения E9.4-4b-1):", [
        ("ptpl_dec", "HEX-литерал s_ptpl (72 Б) -> массив ptplb (шапка PEG)"),
        ("emit_peg", "ДРАЙВЕР PEG: шапка + !module/!entry/!idata/!iat/!bss/!stackcom/!heapcom (SPEC/15 п. 8 == _peg_text; DD[1]/DD[12] по optoff); запись .peg (коды 8/9)")]),
]

STRINGS = ["s_use", "s_long", "s_oexe", "s_rexe", "s_family", "s_big",
           "s_oout", "s_wout", "s_f1", "s_f2", "s_f3", "s_f4", "s_f5",
           "s_f6", "s_f7", "s_f8", "s_f9", "s_fa", "s_ff1", "s_crlf",
           "s_pref", "s_needle", "s_dll", "s_h", "s_at", "s_ml",
           "s_ripl", "s_base", "s_s1", "s_kw", "s_dz", "s_db", "s_iat",
           "s_dd", "s_dq", "s_mem", "s_rip", "s_cl", "s_j", "s_comma",
           "s_mn", "s_cc", "s_r64", "s_r8", "s_r16", "s_r32", "s_tpl",
           "s_ptpl", "s_dotexe", "s_pm", "s_pe", "s_pi", "s_pa",
           "s_pb", "s_ps", "s_ph"]
GLOBALS = ["hstdout", "cmdline", "written", "wlen", "exebuf", "exelen",
           "entryrva", "vsize", "rawsize", "rawptr", "modlen", "thunk",
           "dllfile", "impn", "insmap", "lenmap", "pend", "pushmap",
           "rawlim", "psp", "inscount", "maxend", "swcur", "target",
           "bss", "dlen", "dcls", "dtgt", "dpos", "mpos", "mreg",
           "dname", "dcc", "dargc", "da1k", "da2k", "da1r", "da2r",
           "da1s", "da2s", "da1v", "da2v", "damem", "ombase", "omidx",
           "omscale", "omdisp", "omsize", "omrip", "mkind", "mrreg",
           "mrdip", "mripon", "sdump", "outmem", "outbuf", "outcur",
           "iatoff", "intoff", "nameoff", "idtoff", "impbad", "kn",
           "snlen", "semcnt", "semacc", "hhrv", "hno", "hnl", "snam",
           "noffs", "knownoff", "semrows", "labmap", "sstate",
           "semstate", "mblen", "mslot", "mslotz", "mslof", "mopc",
           "mis8", "mcount", "hcount", "lfanew", "coffoff", "optoff",
           "sizopt", "numsect", "tbloff", "codevaddr", "falign",
           "fend", "fsect"]
ARRAYS = [("arg1", "0x80"), ("arg2", "0x80"), ("arg3", "0x80"),
          ("factbuf", "0xC0"), ("o_mn", "0xE8"), ("o_cc", "0x88"),
          ("o_r64", "0x88"), ("o_r8", "0x88"), ("o_r16", "0x88"),
          ("o_r32", "0x88"), ("o_kw", "0x28"), ("tplb", "0xC8"),
          ("mbuf", "0xC0"), ("ptplb", "0x48"), ("w1", "0x200")]


def lines4(items, per=4):
    """строки данных: «имя RVA …» по per штук."""
    out, cur = [], []
    for it in items:
        cur.append(it)
        if len(cur) == per:
            out.append("  " + " ".join(cur))
            cur = []
    if cur:
        out.append("  " + " ".join(cur))
    return out


missing = [n for g in GLOBALS + STRINGS for n in [g] if n not in LAB]
missing += [n for head, fns in PARTS for n, _d in fns if n not in LAB]
if missing:
    sys.exit("нет меток: %r" % missing)

S = []
S.append("# BYTECODE. Модуль M5-BRIDGE — карта образа")
S.append("")
S.append("Паспорт файла: KERNEL/L5-BRIDGE/BYTECODE.md | слой: L5 | "
         "роль: разбор образа bridge.exe.")
S.append("")
S.append("## 1. Сводка")
S.append("")
S.append("| Параметр | Значение |")
S.append("|---|---|")
S.append("| Файл | KERNEL/L5-BRIDGE/bridge.exe, 98816 байт (0x18200) |")
S.append("| SHA-256 | 4D23B561D68A26D9C8C70ADAF6FDCC541186EDC324356ED36D65F1CE5821C13C |")
S.append("| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E9.2-1/2/3a/3b/3c/4 + E9.4-4a + E9.4-4b-1): сборка из bridge.wall — wall.exe(splice(bridge.wall)) -> bridge.b2 -> enc -> bridge.brick -> brick -> pegen + bridge.peg. Воспроизводимость закреплена в батарее (T-E9-17); bridge.b2 == оракулу LAB/py/lab_l2.py байт-в-байт |")
S.append("| Исходник | KERNEL/L5-BRIDGE/bridge.wall — корень + 16 частей bridge_self_*.wall (WALL v2, разрез SPEC/10; +pi/pf — E9.4-4b-1); склейка 152669 Б (57% предела входа 256 КиБ; 4958 строк — заголовок bridge.b2) |")
S.append("| Тело секции | 97858 байт (0x17E42), RVA 0x1000, SRD 0x18000 |")
S.append("| VirtualSize | 0x17E42 (одна секция); target 0x17E01, bss 0x41 (хвост — виртуальные нули) |")
S.append("| Точка входа | 0x1200 (:_entry — константа SPEC/11 п. 6: после фиксированной области импортов 0x200) |")
S.append("| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п. 6 |")
S.append("| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc |")
S.append("| DOS-заглушка | «Universal L0 bridge. No DOS support.» (имя модуля — bridge.peg) |")
S.append("| M-строк в исходнике | 20894 (bridge.b2; 100% M — H=0, круг T-E9-20: M=20894 H=0) |")
S.append("| Меток в исходнике | 1309 из 2048 (лимит brick; карта — LAB/ai/bridge_labelmap.py) |")
S.append("| Функций | 122 (карта — §2; +fam_chain/foreign_front/print_ffacts — E9.4-4b-1) + данные (§3) |")
S.append("| Компилятор сборки | wall.exe (M2-WALL, самосборный) — конвейер под эмуляцией LAB (T-E9-17: 717365516 + 71093226 + 75589252 + 5046 шагов; шаг wall выше лимита lab_run 200 млн — возобновляемые срезы build_bridge_resume.py, прецедент T-E6-49a) |")
S.append("")
S.append("## 2. Карта функций (RVA — LAB/ai/bridge_labelmap.py по bridge.brick)")
S.append("")
S.append("Группировка — по частям bridge.wall (состав — CARD.md; кирпичи K5-* — MAP/M5-BRIDGE.md, MAP/M5-BRIDGE-D.md, MAP/M5-BRIDGE-E.md, MAP/M5-BRIDGE-L.md, MAP/M5-BRIDGE-M.md и MAP/M5-BRIDGE-G.md).")
S.append("")
S.append("```")
for head, fns in PARTS:
    S.append(head)
    for name, desc in fns:
        rva = LAB[name]
        S.append("  %-18s %s  %s" % (name, rva, desc))
    S.append("")
S.append("вход (bridge.wall):")
S.append("  main ................. %s  CLI -> чтение EXE -> общий фронт -> РАЗВИЛКА" % LAB["main"])
S.append("                               «семья | чужой» (E9.4-4b-1): семья -> спуск ->")
S.append("                               таблицы -> карты (L) -> эмиссия .b2 (КАНОН M/H)")
S.append("                               -> PEG-выход (E9.2-4) -> факты M=/H=; чужой ->")
S.append("                               фронт P2 -> спуск -> чужие факты FOREIGN")
S.append("```")
S.append("")
S.append("## 3. Данные образа (RVA)")
S.append("")
S.append("```")
S.append("строки (%d):" % len(STRINGS))
S.extend(lines4(["%s %s" % (n, LAB[n]) for n in STRINGS]))
S.append("глобали (%d):" % len(GLOBALS))
S.extend(lines4(["%s %s" % (n, LAB[n]) for n in GLOBALS]))
S.extend(lines4(["%s %s (%s)" % (n, LAB[n], sz) for n, sz in ARRAYS],
                per=3))
S.append("конец тела: 17E42 (vsize 0x17E42)")
S.append("```")
S.append("")
S.append("Массивы объявлены ПОСЛЕ скаляров, ПОСЛЕДНИЙ — w1[64] (0x200 Б; урок E9.2-2, ОБЩЁН срезом E9.2-3b): выравнивающий хвост (0x17E01..0x17E42, 0x41 Б) всегда < 0x200 Б и падает внутрь w1 при ЛЮБОМ vsize (w1base = vsize-0x200 <= raw-0x1FF — БЕЗУСЛОВНЫЙ инвариант, пересчёт при росте больше не нужен); rip-ссылок внутрь хвоста нет (lea — только базы массивов, они ниже target), разбор моста над bridge.exe даёт 0 H-строк (M=20894; как kernel/uva — T-E9-20). E9.2-4: массив ptplb[9] (0x48 Б) добавлен ПЕРЕД w1 — инвариант сохранён (проверен кругом T-E9-20). E9.4-4b-1: скаляры развилки lfanew/coffoff/optoff/sizopt/numsect/tbloff/codevaddr/falign/fend/fsect (+80 Б, кластер ветвей P/P2 после mcount/hcount) — инвариант хвоста внутри w1 не задет (хвост 0x41 Б; круг T-E9-20 зелёный, M=20894 H=0).")
S.append("")
S.append("## 4. Контроль воспроизведения")
S.append("")
S.append("Сборка из исходника (под эмуляцией LAB; то же делает батарея T-E9-17):")
S.append("")
S.append("```")
S.append("splice.exe bridge.wall bridge_s.flat")
S.append("wall.exe   bridge_s.flat bridge_s.b2      (== оракулу WALL байт-в-байт)")
S.append("enc.exe    bridge_s.b2  bridge_s.brick")
S.append("brick.exe  bridge_s.brick bridge_s.bin")
S.append("pegen.exe  bridge_s.bin bridge.peg bridge.exe   (== артефакт)")
S.append("```")
S.append("")
S.append("SHA-256 артефактов: bridge.b2 — A86F5669…D1387D9, bridge.brick — 9D2E51BD…36486398, bridge.exe — 4D23B561…82113C (полные — VERIFY.md).")

io.open(ROOT + "/KERNEL/L5-BRIDGE/BYTECODE.md", "w",
        encoding="utf-8").write("\n".join(S) + "\n")
print("BYTECODE.md: %d строк" % (len(S) + 1))
