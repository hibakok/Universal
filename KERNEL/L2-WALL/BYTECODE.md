# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 28160 байт (0x6E00) |
| SHA-256 | 295730EF1D170D04652E7DD398C0F6A3EB957E4D65F060D66859C3D64774C661 |
| Тело секции | 27338 байт (0x6AAC), RVA 0x1000 (дефект №21,
  E6.4d-4/3c-2/2: +0xC — pc_staged := base / base+cnt в P014;
  до этого E6.4g-4+№20: +0x3F chain_count, +1 калибровка DZ 3) |
| Точка входа | 0x1000 (:entry) |
| idata / iat / intt | 0x79AE / 0x79D6 / 0x7A16; dll 0x7A56; VirtualSize 0x7E8EE2 (№21: адреса данных сдвинуты на +0xC; E6.4g-4: filebuf в хвосте bss — рост vsize на 0x41000; №20: +0x3F; калибровка wall.peg из карты меток brick, wall_build.py) |
| bss (DBZ) | 0x7E2418 — единая область :scalars (E6.4g-4: filebuf
  256 КиБ перенесён в хвост — r13+7A1418 DBZ 41000) |
| М-строк в исходнике | 5220 (21 файл .b2: корень + 20 частей !include;
  №21: +3 — pc_staged := base (mov) и base+cnt (add ×2) в P014;
  E6.4g-4+№20: +28 — флаг «конец операнда» chain_count; +61 — фикс №19) |
| Меток в исходнике | 585 (лимит brick 2048 вкл. base; №20: +1
  cc_setoper; фикс №19: +5 pa_top/pa_base/pa_l1/pa_l2/p1c_md, −1
  pas_st; срез 4b: +41 — pw_*, ppc_*, ppp_*, ac_*, psc_*,
  p1n_astore/p1a_*, p2n_astore/p2a_*) |
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
  arr_size ............. 26B8-2753   P019 (E6.4c-3/4): разбор [n] объявления:
                                        число 1..4096, флаг v2, RAX размер /
                                        RDX признак
  p_expr ............... 1A48        P010: аддитивный уровень
  p_mul ................ 1BF4        P011: конъюнкция (& << >>)
  p_mdm ................ 1E16        P01A (E6.4c-3/1): уровень * / % — тот же
                                        механизм tdepth; флаг v2 [r13+18190]
  p_unary .............. 2005        P012: унарный минус
  p_prim ............... 2D9B        P013 (срез 4b): ОБЁРТКА — pp_prim0 +
                                        постфикс [..] (pp_strchk 34DA ->
                                        pp_pcount 3210 -> pp_pairs 32DE;
                                        откат r12, prim на d+k);
                                        pp_prim0 2E32 (pp_paren 2EE3,
                                        pp_addr 2F11, pp_getb 3098,
                                        pp_len 318B, pp_value 31E2)
                                        (pp_paren 2E0D, pp_addr 2E3B, pp_getb
                                        2ECA, pp_len 30B5, pp_value 310C)
  p_args/pa_stage ...... 2792-29C7   P014/P017 (фикс №19, E6.4d-4/2):
                                        счёт/max need в РАМКЕ, базы C-слотов
                                        (pc_cact/pc_staged/pc_cbase);
                                        стейджинг C(base+i) (5-й ext -> S5)
  p_call_tail .......... 2A06-2CAE   P015 (№19: загрузки из C(pc_cbase+i)):
                                        rcx/rdx/r8/r9, call $f /
                                        call [rip+$_iat_e], want -> mov r10,rax
  call_stats ........... 2CED-2D5C   P016 (№19: maxc = pc_cbase + n), ext5
  astore_chk/pp_strchk . 346D-3649   P01D/P01E (wall_pi.b2): имя-цель
                                        astore (не str/func/ext) и
                                        запрет индексации строки
                                        (psc_open/root/close/chk)
  p_cond ............... 3688-3A67   P018: условия if/while — цепочки && / ||
                                        (E6.4c-3/3): предподсчёт m (pcd_scan
                                        307E), цикл дизъюнктов/конъюнктов
                                        (pcd_cmp 31E4..pcd_after 3450), статы
                                        1+max КАЖДОГО сравнения, флаг v2,
                                        guard: jcc -> lfail/d<i+1> (pcd_jgo
                                        3318), финальная t-метка; m=1 —
                                        выход байт-в-байт как v1

эмиттеры адресов/длин/загрузок (E6.4c-3/4 — ветви массивов):
  emit_addr ............ 3AA6-3B46   E022: &имя — локаль/массив: lea r10,
                                        [rbp-8*(база+размер)] (ea_local 35FC);
                                        var/str/массив (вид 5): lea rip (ea_rip
                                        34DB)
  emit_len ............ 3B85-3C43   E023: len — сначала локальный массив
                                        (eln_glob 3669), затем str (eln_str
                                        35E5) / глобальный массив из varr
                                        (eln_arr 36BB); печать eln_print 370D
  emit_load ............ 3C82-3D9E   E024: имя — локаль (el_local 3C15):
                                        скаляр mov / массив (el_lscal 3839
                                        — lea arrbase); var mov rip (el_var
                                        36B4); str/массив lea rip (el_str
                                        36DD)
guard-эмиттеры (E6.4c-3/3, wall_pg.b2):
  emit_jccd ............ 3DC7-3E21   E036: "M <mnem> $<pfx><k>d<i>" (jcc на
                                        d-метку; jcctab, суффиксы 'd'+dec(i))
  emit_jmpt ............ 3E60-3E72   E037: "M jmp $<pfx><k>t" (успех дизъюнкта)
  emit_glab ............ 3EB1-3EFA   E038: ":<pfx><k>d<i>" / ":<pfx><k>t"
                                        (R8=0 -> t); nlab++ (предел 2000,
                                        E6.4d-3/3-1: было 500)

проход 1 (статы):
  pass1, p1_line ....... 3EEE-4124   S001/S002: цикл, диспетчер (+0C/0D —
                                        E6.4c-3/2; ftab-скан ×80 — срез 4a)
  p1_decl .............. 416F-447C   S003: var/str/ext (проверки имён);
                                        var a[n] (E6.4c-3/4): P019 -> вид 5,
                                        varr ×16 {idx, size} (d1_vscal 3CC2)
  p1_funchdr ........... 44BB-475F   S004: ftab-запись ×80 (+0x48 nslots),
                                        st_nslots := nparams, push {func}
  fh_param ............. 479E-4854   S00E: параметры (larr ×32 {ptr,len,1})
  names_find_ci ........ 4893-4913   S005: без учёта регистра (ext)
  p1s_var .............. 4952-4A6D   S006: локаль (+ [n] -> размер larr,
                                        st_nslots += size; p1v_glob 44CE)
  p1s_end .............. 4AAC-4B3C   S007: финализация ftab (+ nslots +0x48)
  p1s_else/if/while .... 4B7B-4C5F   S008/S009/S00A: статы условий (зовут
                                        p_cond в режиме статов)
  p1s_return ........... 4C9E-4CAE   S00B: [выражение] -> maxd
  p1s_setb ............. 4CED-4D59   S00C: три выражения, st_setb=1
  p1_namestmt .......... 4D98-4E4A   S00D (срез 4b): вызов/присваивание/
                                        astore (p1n_astore 4E24: pre-count,
                                        astore_chk, база-цепочка, S-статы)
  p1s_brk .............. 4F89-4F9C   S00F (E6.4c-3/2): break/continue — скан
                                        bstk до while, флаг v2 (одна точка
                                        входа на оба ключевых слова)

проход 2 (эмитция):
  pass2, p2_line ....... 4F90-5164   Y001/Y002: цикл, карта текстов строк
                                        (+0C/0D — E6.4c-3/2); в конце Y001 —
                                        предел меток выхода nlab ≤ 2000
                                        (cmp rax,7D0; E6.4d-3/3-1: было 1F4)
  p2_funchdr ........... 51AF-52BF   Y00A: раскладка из ftab ×80 (nbase :=
                                        nslots +0x48 — срез 4a), пролог
  p2s_var .............. 52FE-52EE   Y003: last_ret=0
  emit_jcc/jmp/iflab/wlab 52E2-5495  E029-E02C: метки _if/_w (сквозной kctr);
                                        E029 вызывается из p_cond — последний
                                        дизъюнкт (E6.4c-3/3)
  emit_sstore .......... 54E0-54F2   E02D: стейджинг S-слотов
  p2s_end/else/if/while  5531-5872   Y004-Y007: bstk {kind,k,seq,lineidx};
                                        Y006/Y007 передают p_cond pfx/e/k
                                        (guard внутри; E6.4c-3/3)
  p2s_return ........... 58B1-58DB   Y008: выражение + эпилог
  p2s_break/continue ... 591A-5935   Y00C (E6.4c-3/2): e-флаг EDX->R11, скан
                                        bstk до while, k=+8, E02A: jmp
                                        $_w<k>[e]; недостижимый путь — int3
  p2s_setb ............. 5974-5A85   Y009: S-слоты S0/S1/S2, mov [r10+r11], al
  p2_namestmt .......... 5AC4-5E15   Y00B: вызов / присваивание: локаль mov
                                        [rbp-8*(база+1)] (p2n_local 5DA0);
                                        срез 4a: массив (размер > 1) — G002
                                        (p2n_arrw 5DDD); var -> mov rip

эмиттеры:
  out_ch/out_copy/str .. 5E54-5EC7   E001-E004: байты вывода, strtab2-адресация
  out_hex/out_hex2 ..... 5EAF/5EBB   E005/E006: ЗАГЛАВНЫЙ hex
  div10 ................ 5F33        E007: деление на 10 бит за битом (маска!)
  out_dec .............. 5F75        E008: десятичные числа
  emit_cmt/kadr ........ 5FEF/5FCA   E009/E010: " ; текст", "кадр/выход имя"
  emit_lab ............. 6075        E011: ":имя"
  lower_copy ........... 608B        E012: scr (нижний регистр для _iat_)
  str_dlen/str_emit .... 60C7/60B2   E013/E014: декодирование экранов, DB<=16
  emit_header .......... 6238        E015: заголовок v1/v2 (флаг [r13+18190];
                                        ставится * / % (P01A), break/continue
                                        (S00F), цепочками && / || (P018) и
                                        объявлениями массивов (P019) —
                                        E6.4c-3/1..4)
  emit_entry ........... 62CE        E016
  calc_framesize ....... 6312        E017: слоты из ftab+0x48 (срез 4a)
  emit_prologue/эпилог . 637B/643C   E018/E019
  emit_alu ............. 64B5        E020: add/sub/and/or/xor r10, r11
  emit_shift ........... 655D        E021: mov rcx,r11; shl/shr r10, cl
  emit_imul ............ 65BC        E034 (E6.4c-3/1): imul r10, r11
  emit_divmod .......... 65CC        E035 (E6.4c-3/1): rax/cqo/idiv/rax|rdx
  get_ext/emit_imports . 663A/662B   E025/E026: импорты (см. данные)
  emit_strdata/globdata 69C5/6AFB   E027/E028: секции данных; E028 — DZ 8n
                                        (срез 4a: 'D','Z',' ' прямым байтом
                                        + out_hex(8*size) из varr)

данные (ветвь D):
  digits ............... 6C2F  K2-D001 (16 Б)
  kwtab ................ 6C3F  K2-D002 (14x16 Б; E6.4c-3/2: +break/+continue)
  jcctab ............... 6D1F  K2-D003 ({смещ,длина}; jne je jge jg jle jl)
  alutab ............... 6D4F  K2-D004
  argtab ............... 6D77  K2-D005
  errtab ............... 6D97  K2-D006 (7x20 Б)
  strblob .............. 6E07  K2-D007 (0x832 Б, 117 строк канона;
                                E6.4c-3/1: +imul/cqo/idiv/r10-rdx, hdr v2;
                                срез 4b: +shl r10,3 / mov r10,[r10] /
                                shl r11,3 / mov [r10],r11 — хвосты
                                индексации (индексы 113..116 = 0x71..0x74);
                                'd'/'t'/'DZ ' прямым байтом)
  strtab2 .............. 7605  K2-D008 (117x8 Б)
  импорты .............. 79AE  K2-D010: idt 0x28 (idata 79AE, iat 79D6),
                                intt 7A16, dll 7A56 (13+DZ3 — №20), hints:
                                gsh 7A66, wf 7A76, ep 7A82, gcl 7A90,
                                cf 7AA2, rf 7AB0, ch 7ABC (чётные RVA,
                                инвариант 7 SPEC/04; калибровка DZ 2)
  bss .................. 7ACA  K2-D011: :scalars DBZ 7A1418 — ЕДИНАЯ область
                                (bstk 3072x32 + скаляры + буферы, база R13;
                                E6.4c-3/2: записи 24 -> 32 Б — дефект №15;
                                E6.4c-3/1: метки буферов -> смещения r13+X
                                (fname_in r13+18208 … outbuf r13+5A1418;
                                E6.4g-4: filebuf r13+7A1418 DBZ 41000 —
                                256 КиБ, перенесён из r13+580418 в хвост);
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
