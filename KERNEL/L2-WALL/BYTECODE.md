# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 28160 байт (0x6E00) |
| SHA-256 | E04BA41BBC14680CFEE2D80B7E4951756C00FA3F6A4AFA66BF279F529067BA91 |
| Тело секции | 27262 байта (0x6A5E), RVA 0x1000 |
| Точка входа | 0x1000 (:entry) |
| idata / iat / intt | 0x7963 / 0x798B / 0x79CB; dll 0x7A0B; VirtualSize 0x7A7E76 (E6.4d-4/2: фикс №19 — рост P014/P017/P015/P016/P013a/S00D на 0x10C, адреса данных сдвинуты; калибровка wall.peg из карты меток brick, wall_build.py) |
| bss (DBZ) | 0x7A1418 — единая область :scalars (начало в теле 0x6976) |
| М-строк в исходнике | 5189 (21 файл .b2: корень + 20 частей !include;
  20-я — wall_pi.b2, механика индексации среза 4b; +61 в E6.4d-4/2 —
  фикс №19: рамочные счётчики P014, pa_stage-эмит с базами, загрузки
  P015 с pc_cbase, call_stats с базами, S00D maxd) |
| Меток в исходнике | 584 (лимит brick 2048 вкл. base; фикс №19: +5
  pa_top/pa_base/pa_l1/pa_l2/p1c_md, −1 pas_st; срез 4b: +41 —
  pw_*, ppc_*, ppp_*, ac_*, psc_*, p1n_astore/p1a_*, p2n_astore/p2a_*) |
| Кирпичей | 79 карточек (MAP/M2-WALL.md; +P01B/P01C/P01D/P01E) |

## 2. Карта ветвей (RVA — по трассировке меток LAB/ai/label_map.py)

```
код потока и сервисов:
  entry ................ 1000-10B0   X001/X002: кадр, регистры, три прохода,
                                        запись выхода, ExitProcess(0)
  get_cmdline..noargs .. 1026-10B0   C001: GetCommandLineA, разбор argv0
  word1..ok7 ........... 10B0-11C9   G004: аргументы, чтение файла, сентинел
  hex16_to_4 ........... 11CA-11F0   H001: 4 hex-цифры номера строки
  fail_format .......... 11F0-1271   G002: ERR=FORMAT AT=XXXX + выход 6
  print_error .......... 1271-12B3   G003: errtab[ECX] + выход
  print_line ........... 12B3-12D9   U001: WriteFile(hstdout)
  next_arg..skip_seps .. 12D9-1394   C002-C004: слова командной строки
  open_file_read..wa_err 1394-1487   F001-F005: CreateFileA/ReadFile/CloseHandle

проход 0 (строки и лексика):
  line_next..ln_cnt .... 1487-150E   N001: LF/CRLF/CR, нумерация
  pass0..p0_set ........ 150E-159D   N002: nlentries/nlines/lastnonempty
  lex_line..ll_ret ..... 159D-167C   N003: полная лексика + карта текстов
  set_lastline ......... 167D-169C   N004: curline := lastnonempty|nlentries
  lex_tok..lt_idend .... 169C-18A0   L001: числа(<=0x7FFFFFFF)/имена/строки
                                        с экранами n r t 0 \ ' /двухсимв.оп.
                                        (E6.4c-3/1: + * / % односимвольные;
                                        E6.4c-3/3: + && (19E4) / || (1A03);
                                        E6.4c-3/4: + [ 5B / ] 5D — lt_cls)

парсер (ветви P):
  want_sym1..kw_lookup . 20A2-21A2   P001-P004: поглощение, at_end, kwtab
                                        (граница kwtab — 14, E)
  chk_name ............. 21A8-228D   P005: имена (строчные, <= 63)
  names_find/add ....... 228D-2369   P006/P007: реестр имён ntab
  local_find ........... 2369-2427   P008: окно larr -> базовый слот + размер
                                        (E6.4c-3/4: префиксная сумма размеров,
                                        RDX = размер; кадр [rbp-8])
  chain_count .......... 2427-2679   P009: число операций уровня (K; ур.0/1/2;
                                        сравнения и && / || — терминаторы
                                        (E6.4c-3/1 и /3); [ ] — глубина
                                        (E6.4c-3/4, подготовка среза 4b))
  arr_size ............. 2679-2753   P019 (E6.4c-3/4): разбор [n] объявления:
                                        число 1..4096, флаг v2, RAX размер /
                                        RDX признак
  p_expr ............... 1A48        P010: аддитивный уровень
  p_mul ................ 1BF4        P011: конъюнкция (& << >>)
  p_mdm ................ 1E16        P01A (E6.4c-3/1): уровень * / % — тот же
                                        механизм tdepth; флаг v2 [r13+18190]
  p_unary .............. 2005        P012: унарный минус
  p_prim ............... 2D50        P013 (срез 4b): ОБЁРТКА — pp_prim0 +
                                        постфикс [..] (pp_strchk 34CE ->
                                        pp_pcount 3204 -> pp_pairs 32D2;
                                        откат r12, prim на d+k);
                                        pp_prim0 2E26 (pp_paren 2ED7,
                                        pp_addr 2F05, pp_getb 308C,
                                        pp_len 317F, pp_value 31D6)
                                        (pp_paren 2E01, pp_addr 2E2F, pp_getb
                                        2ECA, pp_len 30A9, pp_value 3100)
  p_args/pa_stage ...... 2753-29BB   P014/P017 (фикс №19, E6.4d-4/2):
                                        счёт/max need в РАМКЕ, базы C-слотов
                                        (pc_cact/pc_staged/pc_cbase);
                                        стейджинг C(base+i) (5-й ext -> S5)
  p_call_tail .......... 29BB-2CA2   P015 (№19: загрузки из C(pc_cbase+i)):
                                        rcx/rdx/r8/r9, call $f /
                                        call [rip+$_iat_e], want -> mov r10,rax
  call_stats ........... 2CA2-2D50   P016 (№19: maxc = pc_cbase + n), ext5
  astore_chk/pp_strchk . 3422-363D   P01D/P01E (wall_pi.b2): имя-цель
                                        astore (не str/func/ext) и
                                        запрет индексации строки
                                        (psc_open/root/close/chk)
  p_cond ............... 363D-3A5B   P018: условия if/while — цепочки && / ||
                                        (E6.4c-3/3): предподсчёт m (pcd_scan
                                        307E), цикл дизъюнктов/конъюнктов
                                        (pcd_cmp 31D8..pcd_after 3444), статы
                                        1+max КАЖДОГО сравнения, флаг v2,
                                        guard: jcc -> lfail/d<i+1> (pcd_jgo
                                        3318), финальная t-метка; m=1 —
                                        выход байт-в-байт как v1

эмиттеры адресов/длин/загрузок (E6.4c-3/4 — ветви массивов):
  emit_addr ............ 3A5B-3B3A   E022: &имя — локаль/массив: lea r10,
                                        [rbp-8*(база+размер)] (ea_local 35F0);
                                        var/str/массив (вид 5): lea rip (ea_rip
                                        34DB)
  emit_len ............ 3B3A-3C37   E023: len — сначала локальный массив
                                        (eln_glob 365D), затем str (eln_str
                                        35E5) / глобальный массив из varr
                                        (eln_arr 36AF); печать eln_print 3701
  emit_load ............ 3C37-3D92   E024: имя — локаль (el_local 3C15):
                                        скаляр mov / массив (el_lscal 382D
                                        — lea arrbase); var mov rip (el_var
                                        36B4); str/массив lea rip (el_str
                                        36DD)
guard-эмиттеры (E6.4c-3/3, wall_pg.b2):
  emit_jccd ............ 3D7C-3E15   E036: "M <mnem> $<pfx><k>d<i>" (jcc на
                                        d-метку; jcctab, суффиксы 'd'+dec(i))
  emit_jmpt ............ 3E15-3E66   E037: "M jmp $<pfx><k>t" (успех дизъюнкта)
  emit_glab ............ 3E66-3EEE   E038: ":<pfx><k>d<i>" / ":<pfx><k>t"
                                        (R8=0 -> t); nlab++ (предел 2000,
                                        E6.4d-3/3-1: было 500)

проход 1 (статы):
  pass1, p1_line ....... 3EEE-4124   S001/S002: цикл, диспетчер (+0C/0D —
                                        E6.4c-3/2; ftab-скан ×80 — срез 4a)
  p1_decl .............. 4124-4470   S003: var/str/ext (проверки имён);
                                        var a[n] (E6.4c-3/4): P019 -> вид 5,
                                        varr ×16 {idx, size} (d1_vscal 3CB6)
  p1_funchdr ........... 4470-4753   S004: ftab-запись ×80 (+0x48 nslots),
                                        st_nslots := nparams, push {func}
  fh_param ............. 4753-4848   S00E: параметры (larr ×32 {ptr,len,1})
  names_find_ci ........ 4848-4907   S005: без учёта регистра (ext)
  p1s_var .............. 4907-4A61   S006: локаль (+ [n] -> размер larr,
                                        st_nslots += size; p1v_glob 44C2)
  p1s_end .............. 4A61-4B30   S007: финализация ftab (+ nslots +0x48)
  p1s_else/if/while .... 4B30-4C53   S008/S009/S00A: статы условий (зовут
                                        p_cond в режиме статов)
  p1s_return ........... 4C53-4CA2   S00B: [выражение] -> maxd
  p1s_setb ............. 4CA2-4D4D   S00C: три выражения, st_setb=1
  p1_namestmt .......... 4D4D-4E3E   S00D (срез 4b): вызов/присваивание/
                                        astore (p1n_astore 4E18: pre-count,
                                        astore_chk, база-цепочка, S-статы)
  p1s_brk .............. 4F3E-4F90   S00F (E6.4c-3/2): break/continue — скан
                                        bstk до while, флаг v2 (одна точка
                                        входа на оба ключевых слова)

проход 2 (эмитция):
  pass2, p2_line ....... 4F90-5164   Y001/Y002: цикл, карта текстов строк
                                        (+0C/0D — E6.4c-3/2); в конце Y001 —
                                        предел меток выхода nlab ≤ 2000
                                        (cmp rax,7D0; E6.4d-3/3-1: было 1F4)
  p2_funchdr ........... 5164-52B3   Y00A: раскладка из ftab ×80 (nbase :=
                                        nslots +0x48 — срез 4a), пролог
  p2s_var .............. 52B3-52E2   Y003: last_ret=0
  emit_jcc/jmp/iflab/wlab 52E2-5495  E029-E02C: метки _if/_w (сквозной kctr);
                                        E029 вызывается из p_cond — последний
                                        дизъюнкт (E6.4c-3/3)
  emit_sstore .......... 5495-54E6   E02D: стейджинг S-слотов
  p2s_end/else/if/while  54E6-5866   Y004-Y007: bstk {kind,k,seq,lineidx};
                                        Y006/Y007 передают p_cond pfx/e/k
                                        (guard внутри; E6.4c-3/3)
  p2s_return ........... 5866-58CF   Y008: выражение + эпилог
  p2s_break/continue ... 58CF-5929   Y00C (E6.4c-3/2): e-флаг EDX->R11, скан
                                        bstk до while, k=+8, E02A: jmp
                                        $_w<k>[e]; недостижимый путь — int3
  p2s_setb ............. 5929-5A79   Y009: S-слоты S0/S1/S2, mov [r10+r11], al
  p2_namestmt .......... 5A79-5E09   Y00B: вызов / присваивание: локаль mov
                                        [rbp-8*(база+1)] (p2n_local 5D94);
                                        срез 4a: массив (размер > 1) — G002
                                        (p2n_arrw 5DD1); var -> mov rip

эмиттеры:
  out_ch/out_copy/str .. 5E09-5EBB   E001-E004: байты вывода, strtab2-адресация
  out_hex/out_hex2 ..... 5E64/5EBB   E005/E006: ЗАГЛАВНЫЙ hex
  div10 ................ 5EE8        E007: деление на 10 бит за битом (маска!)
  out_dec .............. 5F2A        E008: десятичные числа
  emit_cmt/kadr ........ 5FA4/5FCA   E009/E010: " ; текст", "кадр/выход имя"
  emit_lab ............. 602A        E011: ":имя"
  lower_copy ........... 6040        E012: scr (нижний регистр для _iat_)
  str_dlen/str_emit .... 607C/60B2   E013/E014: декодирование экранов, DB<=16
  emit_header .......... 61ED        E015: заголовок v1/v2 (флаг [r13+18190];
                                        ставится * / % (P01A), break/continue
                                        (S00F), цепочками && / || (P018) и
                                        объявлениями массивов (P019) —
                                        E6.4c-3/1..4)
  emit_entry ........... 6283        E016
  calc_framesize ....... 62C7        E017: слоты из ftab+0x48 (срез 4a)
  emit_prologue/эпилог . 6330/643C   E018/E019
  emit_alu ............. 646A        E020: add/sub/and/or/xor r10, r11
  emit_shift ........... 6512        E021: mov rcx,r11; shl/shr r10, cl
  emit_imul ............ 6571        E034 (E6.4c-3/1): imul r10, r11
  emit_divmod .......... 6581        E035 (E6.4c-3/1): rax/cqo/idiv/rax|rdx
  get_ext/emit_imports . 65EF/662B   E025/E026: импорты (см. данные)
  emit_strdata/globdata 69C5/6AFB   E027/E028: секции данных; E028 — DZ 8n
                                        (срез 4a: 'D','Z',' ' прямым байтом
                                        + out_hex(8*size) из varr)

данные (ветвь D):
  digits ............... 6BE4  K2-D001 (16 Б)
  kwtab ................ 6BF4  K2-D002 (14x16 Б; E6.4c-3/2: +break/+continue)
  jcctab ............... 6CD4  K2-D003 ({смещ,длина}; jne je jge jg jle jl)
  alutab ............... 6D04  K2-D004
  argtab ............... 6D2C  K2-D005
  errtab ............... 6D4C  K2-D006 (7x20 Б)
  strblob .............. 6DBC  K2-D007 (0x832 Б, 117 строк канона;
                                E6.4c-3/1: +imul/cqo/idiv/r10-rdx, hdr v2;
                                срез 4b: +shl r10,3 / mov r10,[r10] /
                                shl r11,3 / mov [r10],r11 — хвосты
                                индексации (индексы 113..116 = 0x71..0x74);
                                'd'/'t'/'DZ ' прямым байтом)
  strtab2 .............. 75BA  K2-D008 (117x8 Б)
  импорты .............. 7963  K2-D010: idt 0x28 (idata 7963, iat 798B),
                                intt 79C5, dll 7A0B (13+DZ2), hints:
                                gsh 7A1A, wf 7A2A, ep 7A36, gcl 7A44,
                                cf 7A56, rf 7A64, ch 7A70 (чётные RVA,
                                инвариант 7 SPEC/04; калибровка DZ 2)
  bss .................. 7A7E  K2-D011: :scalars DBZ 7A1418 — ЕДИНАЯ область
                                (bstk 3072x32 + скаляры + буферы, база R13;
                                E6.4c-3/2: записи 24 -> 32 Б — дефект №15;
                                E6.4c-3/1: метки буферов -> смещения r13+X
                                (fname_in r13+18208 … outbuf r13+5A1418);
                                флаг v2 — [r13+18190]; st_nslots —
                                [r13+180D8] (E6.4c-3/4, бывший lay_setb))
```

## 3. Соглашения ветвей кода (в развитие «ветвей» SPEC/06)

Каждая ветвь — файл(ы) разреза; кирпичи ветви нумеруются своим префиксом:
X (поток), C (командная строка), G (ошибки), H (hex), U (печать),
F (файлы), N (строки/проход 0), L (лексер), P (парсер), S (проход 1),
Y (проход 2), E (эмиттеры), D (данные). Реинкарнации из M1-ENC:
C/F/H/G/U — перенос алгоритма, не байтов.

## 4. Таблицы форматов

- ntab (имя): {ptr, len, вид(1 var/2 str/3 ext/4 func/5 массив), мета,
  строка} 40 Б; мета: var/массив -> индекс varr, str -> sarr, ext ->
  earr, func -> ftab (вид 5 — E6.4c-3/4).
- ftab (функция): {nameptr, namelen, nparams, maxd, maxc, flags(1 setb,
  2 ext5), locoff, loccnt, hdrline, nslots} 80 Б (E6.4c-3/4: +nslots —
  сумма слотов окна с массивами; loccnt — длина окна larr).
- larr (локаль): {ptr, len, size} 32 Б (E6.4c-3/4: size — слотов; у
  параметров 1); окно функции [locoff, locoff+loccnt).
- varr (глобальная var): {ntab_idx, size} 16 Б (E6.4c-3/4: size — для
  DZ 8n; у скаляров 1).
- sarr (строка): {индекс ntab, литерал ptr, длина} 24 Б.
- bstk (блок): {kind(1 func/2 if/3 else/4 while), k, seq, lineidx} 32 Б
  (E6.4c-3/2, дефект №15: было 24 Б).
- sm_arr (строка исходника): {ptr текста, len} 16 Б.

## 5. Контроль воспроизведения

```
splice.exe wall.b2 t_flat.b2      (склейка 20 файлов)
enc.exe    t_flat.b2 wall.brick   (нормализация v2 -> v1)
brick.exe  wall.brick t_body.bin  (тело 24952 байта)
pegen.exe  t_body.bin wall.peg t.exe
fc /b t.exe wall.exe              -> различий нет (DoD сборки)
```

Батарея: python3 LAB/py/lab_verify.py -> 124/124 (T-E6-25..30 — инструмент,
секция 10; секция 9 — оракул v2; секция 11 — v2-срезы 1-3 + 4a). Dev-тест
среза 1 (E6.4c-3/1): python3 LAB/ai/wall_test_v2.py -> 27/27 (якоря * / %,
заголовки v1/v2, круг «U-MDM-OK 52»). Dev-тест среза 2 (E6.4c-3/2):
python3 LAB/ai/wall_test_bc.py -> 17/17 (break/continue, дефект №15, круг
«U-BC-OK 25»; с среза 3 полный якорь B2 == оракулу). Dev-тест среза 3
(E6.4c-3/3): python3 LAB/ai/wall_test_cc.py -> 20/20 (цепочки && / ||,
якоря B2/F14/F16, big-255, 10 ошибок, круг «U-CC-OK 31»). Dev-тест среза
4a (E6.4c-3/4): python3 LAB/ai/wall_test_arr.py -> 28/28 (объявления
массивов, базы, len, big_arr, 14 ошибок, круг «U-ARR-OK 45»).
