# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 25088 байт (0x6200) |
| SHA-256 | 78FE21D305FF2EF7476A063CA4D365394A3C5AFF27B132876F41CE92618EF0BF |
| Тело секции | 24272 байта (0x5ED0), RVA 0x1000 |
| Точка входа | 0x1000 (:entry) |
| idata / iat / intt | 0x6DB5 / 0x6DDD / 0x6E1D; dll 0x6E5D; VirtualSize 0x7A72E8 |
| bss (DBZ) | 0x7A1418 — единая область :scalars (RVA 0x6ED0) |
| М-строк в исходнике | 4552 (20 файлов .b2: корень + 19 частей !include) |
| Меток в исходнике | 528 (лимит brick 1024 вкл. base; срез 3: +21 — lt_and/lt_or,
  pcd_*, E036-E038) |
| Кирпичей | 74 карточки (MAP/M2-WALL.md) |

## 2. Карта ветвей (RVA-диапазоны, по убыванию granularity — полный список меток генерируется трассировкой)

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
  lex_tok..lt_idend .... 169C-188E   L001: числа(<=0x7FFFFFFF)/имена/строки
                                        с экранами n r t 0 \ ' /двухсимв.оп.
                                        (E6.4c-3/1: + * / % односимвольные;
                                        E6.4c-3/3: + && / || — lt_and 19D2 /
                                        lt_or 19F1, ветвление по 2-му байту)

парсер (ветви P):
  want_sym1..kw_lookup . 2090-227B   P001-P005: поглощение, at_end, kwtab
                                        (граница kwtab — 14, E)
  names_find/add, local_find 227B-23D0 P006-P008: реестр имён, локали
  chain_count .......... 23D0-2610   P009: число операций уровня (K; ур.0/1/2;
                                        сравнения и && / || — терминаторы,
                                        E6.4c-3/1 и E6.4c-3/3)
  p_expr ............... 1A36        P010: аддитивный уровень
  p_mul ................ 1BE2        P011: конъюнкция (& << >>)
  p_mdm ................ 1E04        P01A (E6.4c-3/1): уровень * / % — тот же
                                        механизм tdepth; флаг v2 [r13+18190]
  p_unary .............. 1FF3        P012: унарный минус
  p_prim ............... 2B22        P013: числа/имена/&/len/getb/скобки/вызовы
  p_args/pa_stage ...... 2610-27A9   P014/P017: стейджинг C-слотов (5-й ext -> S5)
  p_call_tail .......... 27A9-2A82   P015: загрузки rcx/rdx/r8/r9, call $f /
                                        call [rip+$_iat_e], want -> mov r10,rax
  call_stats ........... 2A82-2B22   P016: maxc = max(...), ext5
  p_cond ............... 2EFF-331D   P018: условия if/while — цепочки && / ||
                                        (E6.4c-3/3): предподсчёт m (pcd_scan
                                        2F3B), цикл дизъюнктов/конъюнктов
                                        (pcd_cmp 2FA9..pcd_fin 32E5), статы
                                        1+max КАЖДОГО сравнения, флаг v2,
                                        guard: jcc -> lfail/d<i+1> (pcd_jgo
                                        31D5), финальная t-метка; m=1 —
                                        выход байт-в-байт как v1

проход 1 (статы):
  pass1, p1_line ....... 3706-393C   S001/S002: цикл, диспетчер (+0C/0D —
                                        E6.4c-3/2)
  p1_decl .............. 393C-3C53   S003: var/str/ext (проверки имён)
  p1_funchdr ........... 3C53-3F22   S004: ftab-запись, st_* сброс, push {func}
  fh_param ............. 3F22-400C   S00E: параметры (дубликаты в окне locoff)
  names_find_ci ........ 400C-40CB   S005: без учёта регистра (ext)
  p1s_var..p1s_setb .... 40CB-44E0   S006-S00C: статы утверждений (p1s_else
                                        42C3, p1s_if 4326, p1s_while 4399 —
                                        зовут p_cond в режиме статов)
  p1_namestmt .......... 44E0-45B6   S00D: вызов/присваивание
  p1s_brk .............. 45B6-4608   S00F (E6.4c-3/2): break/continue — скан
                                        bstk до while, флаг v2 (одна точка
                                        входа на оба ключевых слова)
  (локали: larr, дубликаты, maxd/maxc/setb/ext5)

проход 2 (эмитция):
  pass2, p2_line ....... 4608-47DC   Y001/Y002: цикл, карта текстов строк
                                        (+0C/0D — E6.4c-3/2)
  p2_funchdr ........... 47DC-4956   Y00A: раскладка из ftab, пролог
  emit_jcc/jmp/iflab/wlab 4956-4B5A  E029-E02D: метки _if/_w (сквозной kctr);
                                        E029 вызывается теперь из p_cond —
                                        последний дизъюнкт (E6.4c-3/3)
  p2s_end/else/if/while  4B5A-4EDA   Y004-Y007: bstk {kind,k,seq,lineidx};
                                        Y006/Y007 передают p_cond pfx/e/k
                                        (guard внутри; E6.4c-3/3)
  p2s_return ........... 4EDA-4F43   Y008: выражение + эпилог
  p2s_break/continue ... 4F43-4F9D   Y00C (E6.4c-3/2): e-флаг EDX->R11, скан
                                        bstk до while, k=+8, E02A: jmp
                                        $_w<k>[e]; недостижимый путь — int3
  p2s_setb/namestmt .... 4F9D-52DC   Y009/Y00B: S-слоты, цели

guard-эмиттеры (E6.4c-3/3, wall_pg.b2):
  emit_jccd ............ 3594-362D   E036: "M <mnem> $<pfx><k>d<i>" (jcc на
                                        d-метку; jcctab, суффиксы 'd'+dec(i))
  emit_jmpt ............ 362D-367E   E037: "M jmp $<pfx><k>t" (успех дизъюнкта)
  emit_glab ............ 367E-3706   E038: ":<pfx><k>d<i>" / ":<pfx><k>t"
                                        (R8=0 -> t); nlab++ (предел 500)

эмиттеры:
  out_ch/out_copy/str .. 52DC-5337   E001-E005: байты вывода, strtab2-адресация
  out_hex/out_hex2 ..... 5337/538E   E005/E006: ЗАГЛАВНЫЙ hex
  div10 ................ 53BB        E007: деление на 10 бит за битом (маска!)
  out_dec .............. 53FD        E008: десятичные числа
  emit_cmt/kadr ........ 5477/549D   E009/E010: " ; текст", "кадр/выход имя"
  emit_lab ............. 54FD        E011: ":имя"
  lower_copy ........... 5513        E012: scr (нижний регистр для _iat_)
  str_dlen/str_emit .... 554F/5585   E013/E014: декодирование экранов, DB<=16
  emit_header .......... 56BA        E015: заголовок v1/v2 (флаг [r13+18190];
                                        ставится * / % (P01A), break/continue
                                        (S00F) и цепочками && / || (P018) —
                                        E6.4c-3/1..3)
  emit_entry ........... 5750        E016
  calc_framesize ....... 5794        E017
  emit_prologue/эпилог . 57FD/5909   E018/E019
  emit_alu ............. 5937        E020: add/sub/and/or/xor r10, r11
  emit_shift ........... 59DF        E021: mov rcx,r11; shl/shr r10, cl
  emit_imul ............ 5A3E        E034 (E6.4c-3/1): imul r10, r11
  emit_divmod .......... 5A4E        E035 (E6.4c-3/1): rax/cqo/idiv/rax|rdx
  get_ext/emit_imports . 5ABC/5AF8   E025/E026: импорты (см. данные)
  emit_strdata/globdata  5E92/5FC8   E027/E028: секции данных

данные (ветвь D):
  digits ............... 608E  K2-D001 (16 Б)
  kwtab ................ 609E  K2-D002 (14x16 Б; E6.4c-3/2: +break/+continue)
  jcctab ............... 617E  K2-D003 ({смещ,длина}; jne je jge jg jle jl)
  alutab ............... 61AE  K2-D004
  argtab ............... 61D6  K2-D005
  errtab ............... 61F6  K2-D006 (7x20 Б)
  strblob .............. 6266  K2-D007 (0x7C6 Б, 113 строк канона;
                                E6.4c-3/1: +imul/cqo/idiv/r10-rdx, hdr v2;
                                срез 3 — без изменений: 'd'/'t' прямым байтом)
  strtab2 .............. 6A2C  K2-D008 (113x8 Б)
  импорты .............. 6DB5  K2-D010: idt 0x28 (idata 6DB5, iat 6DDD),
                                intt 6E1D, dll 6E5D (13+DZ2), hints:
                                gsh 6E6C, wf/ep/gcl/cf/rf/ch далее (чётные
                                RVA, инвариант 7 SPEC/04; калибровка DZ 2)
  bss .................. 6ED0  K2-D011: :scalars DBZ 7A1418 — ЕДИНАЯ область
                                (bstk 3072x32 + скаляры + буферы, база R13;
                                E6.4c-3/2: записи 24 -> 32 Б — дефект №15;
                                E6.4c-3/1: метки буферов -> смещения r13+X
                                (fname_in r13+18208 … outbuf r13+5A1418);
                                флаг v2 — скаляр [r13+18190])
```

## 3. Соглашения ветвей кода (в развитие «ветвей» SPEC/06)

Каждая ветвь — файл(ы) разреза; кирпичи ветви нумеруются своим префиксом:
X (поток), C (командная строка), G (ошибки), H (hex), U (печать),
F (файлы), N (строки/проход 0), L (лексер), P (парсер), S (проход 1),
Y (проход 2), E (эмиттеры), D (данные). Реинкарнации из M1-ENC:
C/F/H/G/U — перенос алгоритма, не байтов.

## 4. Таблицы форматов

- ntab (имя): {ptr, len, вид(1 var/2 str/3 ext/4 func), мета, строка} 40 Б;
  мета: var -> индекс varr, str -> sarr, ext -> earr, func -> ftab.
- ftab (функция): {nameptr, namelen, nparams, maxd, maxc, flags(1 setb,
  2 ext5), locoff, loccnt, hdrline} 72 Б.
- larr (локаль): {ptr, len} 16 Б; окно функции [locoff, locoff+loccnt).
- sarr (строка): {индекс ntab, литерал ptr, длина} 24 Б.
- bstk (блок): {kind(1 func/2 if/3 else/4 while), k, seq, lineidx} 32 Б
  (E6.4c-3/2, дефект №15: было 24 Б).
- sm_arr (строка исходника): {ptr текста, len} 16 Б.

## 5. Контроль воспроизведения

```
splice.exe wall.b2 t_flat.b2      (склейка 20 файлов)
enc.exe    t_flat.b2 wall.brick   (нормализация v2 -> v1)
brick.exe  wall.brick t_body.bin  (тело 24272 байта)
pegen.exe  t_body.bin wall.peg t.exe
fc /b t.exe wall.exe              -> различий нет (DoD сборки)
```

Батарея: python3 LAB/py/lab_verify.py -> 114/114 (T-E6-25..30 — инструмент,
секция 10; секция 9 — оракул v2). Dev-тест среза 1 (E6.4c-3/1):
python3 LAB/ai/wall_test_v2.py -> 27/27 (якоря * / %, заголовки v1/v2,
круг «U-MDM-OK 52»). Dev-тест среза 2 (E6.4c-3/2): python3
LAB/ai/wall_test_bc.py -> 17/17 (break/continue, дефект №15, круг
«U-BC-OK 25»; с среза 3 полный якорь B2 == оракулу). Dev-тест среза 3
(E6.4c-3/3): python3 LAB/ai/wall_test_cc.py -> 20/20 (цепочки && / ||,
якоря B2/F14/F16, big-255, 10 ошибок, круг «U-CC-OK 31»).
