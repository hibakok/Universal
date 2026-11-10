# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 24064 байта (0x5E00) |
| SHA-256 | A40A5FF668CE010BF6042D8D59E7F2589AE92F9500302A4D0A4E44D92724181D |
| Тело секции | 23370 байт (0x5B4A), RVA 0x1000 |
| Точка входа | 0x1000 (:entry) |
| idata / iat / intt | 0x6A2F / 0x6A57 / 0x6A97; dll 0x6AD7; VirtualSize 0x7A6F62 |
| bss (DBZ) | 0x7A1418 — единая область :scalars (RVA 0x6B4A) |
| М-строк в исходнике | 4358 (19 файлов .b2: корень + 18 частей !include) |
| Меток в исходнике | 507 (лимит brick 512 вкл. base; срез 2: +8 меток S00F/Y00C) |
| Кирпичей | 71 карточка (MAP/M2-WALL.md) |

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
  lex_tok..lt_idend .... 169C-1880   L001: числа(<=0x7FFFFFFF)/имена/строки
                                        с экранами n r t 0 \ ' /двухсимв.оп.
                                        (E6.4c-3/1: + * / % односимвольные)

парсер (ветви P):
  want_sym1..kw_lookup . 2052-2158   P001-P004: поглощение, chk_name, kwtab
                                        (E6.4c-3/2: граница kwtab — 14, E)
  names_find/add, local_find 2158-2392 P006-P008: реестр имён, локали
  chain_count .......... 2392-25C0   P009: число операций уровня (K; ур.0/1/2;
                                        сравнения — терминаторы, E6.4c-3/1)
  p_expr ............... 19F8        P010: аддитивный уровень
  p_mul ................ 1BA4        P011: конъюнкция (& << >>)
  p_mdm ................ 1DC6        P01A (E6.4c-3/1): уровень * / % — тот же
                                        механизм tdepth; флаг v2 [r13+18190]
  p_unary .............. 1FB5        P012: унарный минус
  p_prim ............... 2AD2        P013: числа/имена/&/len/getb/скобки/вызовы
  p_args/pa_stage ...... 25C0-2759   P014/P017: стейджинг C-слотов (5-й ext -> S5)
  p_call_tail .......... 2759-2A32   P015: загрузки rcx/rdx/r8/r9, call $f /
                                        call [rip+$_iat_e], want -> mov r10,rax
  call_stats ........... 2A32-2AD2   P016: maxc = max(...), ext5
  p_cond ............... 2EAF-3364   P018: операнды@2, инверсия -> индекс jcc

проход 1 (статы):
  pass1, p1_line ....... 3364-4266   S001/S002: цикл, диспетчер (+0C/0D —
                                        E6.4c-3/2)
  p1_decl .............. 359A-38B1   S003: var/str/ext (проверки имён)
  p1_funchdr ........... 38B1-3B80   S004: ftab-запись, st_* сброс, push {func}
  fh_param ............. 3B80-3C6A   S00E: параметры (дубликаты в окне locoff)
  names_find_ci ........ 3C6A-3D29   S005: без учёта регистра (ext)
  p1s_var..p1s_setb .... 3D29-413E   S006-S00C: статы утверждений
  p1_namestmt .......... 413E-4214   S00D: вызов/присваивание
  p1s_brk .............. 4214-4266   S00F (E6.4c-3/2): break/continue — скан
                                        bstk до while, флаг v2 (одна точка
                                        входа на оба ключевых слова)
  (локали: larr, дубликаты, maxd/maxc/setb/ext5)

проход 2 (эмитция):
  pass2, p2_line ....... 4266-4F56   Y001/Y002: цикл, карта текстов строк
                                        (+0C/0D — E6.4c-3/2)
  p2_funchdr ........... 443A-45B4   Y00A: раскладка из ftab, пролог
  emit_jcc/jmp/iflab/wlab 45B4-47B8  E029-E02D: метки _if/_w (сквозной kctr)
  p2s_end/else/if/while  47B8-4B54   Y004-Y007: bstk {kind,k,seq,lineidx}
  p2s_return ........... 4B54-4BBD   Y008: выражение + эпилог
  p2s_break/continue ... 4BBD-4C17   Y00C (E6.4c-3/2): e-флаг EDX->R11, скан
                                        bstk до while, k=+8, E02A: jmp
                                        $_w<k>[e]; недостижимый путь — int3
  p2s_setb/namestmt .... 4C17-4F56   Y009/Y00B: S-слоты, цели

эмиттеры:
  out_ch/out_copy/str .. 4F56-4FB1   E001-E004: байты вывода, strtab2-адресация
  out_hex/out_hex2 ..... 4FB1        E005/E006: ЗАГЛАВНЫЙ hex
  div10 ................ —           E007: деление на 10 бит за битом (маска!)
  out_dec .............. —           E008: десятичные числа
  emit_cmt/kadr/vyhod .. —           E009/E010: " ; текст", "кадр/выход имя"
  emit_lab ............. —           E011: ":имя"
  lower_copy ........... —           E012: scr (нижний регистр для _iat_)
  str_dlen/str_emit .... —           E013/E014: декодирование экранов, DB<=16
  emit_header .......... 5334        E015: заголовок v1/v2 (флаг [r13+18190];
                                        ставится * / % (P01A) и break/continue
                                        (S00F) — E6.4c-3/1 и E6.4c-3/2)
  emit_entry, calc_framesize, пролог/эпилог 53CA-55B1  E016-E019
  emit_alu ............. 55B1        E020: add/sub/and/or/xor r10, r11
  emit_shift ........... 5659        E021: mov rcx,r11; shl/shr r10, cl
  emit_imul ............ 56B8        E034 (E6.4c-3/1): imul r10, r11
  emit_divmod .......... 56C8        E035 (E6.4c-3/1): rax/cqo/idiv/rax|rdx
  get_ext/emit_imports . 5736-5B0C   E025/E026: импорты (см. данные)
  emit_strdata/globdata  5B0C-5D08   E027/E028: секции данных

данные (ветвь D):
  digits ............... 5D08  K2-D001 (16 Б)
  kwtab ................ 5D18  K2-D002 (14x16 Б; E6.4c-3/2: +break/+continue)
  jcctab ............... 5DF8  K2-D003 ({смещ,длина})
  alutab ............... 5E28  K2-D004
  argtab ............... 5E50  K2-D005
  errtab ............... 5E70  K2-D006 (7x20 Б)
  strblob .............. 5EE0  K2-D007 (0x7C6 Б, 113 строк канона;
                                E6.4c-3/1: +imul/cqo/idiv/r10-rdx, hdr v2)
  strtab2 .............. 66A6  K2-D008 (113x8 Б)
  импорты .............. 6A2F  K2-D010: idt 0x28 (idata 6A2F, iat 6A57),
                                intt 6A97, dll 6AD7 (13+DZ2), hints:
                                gsh 6AE6, wf 6AF6, ep 6B02, gcl 6B10,
                                cf 6B22, rf 6B30, ch 6B3C (чётные RVA,
                                инвариант 7 SPEC/04; калибровка DZ 2)
  bss .................. 6B4A  K2-D011: :scalars DBZ 7A1418 — ЕДИНАЯ область
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
- bstk (блок): {kind(1 func/2 if/3 else/4 while), k, seq, lineidx} 24 Б.
- sm_arr (строка исходника): {ptr текста, len} 16 Б.

## 5. Контроль воспроизведения

```
splice.exe wall.b2 t_flat.b2      (склейка 19 файлов)
enc.exe    t_flat.b2 wall.brick   (нормализация v2 -> v1)
brick.exe  wall.brick t_body.bin  (тело 23240 байт)
pegen.exe  t_body.bin wall.peg t.exe
fc /b t.exe wall.exe              -> различий нет (DoD сборки)
```

Батарея: python3 LAB/py/lab_verify.py -> 111/111 (T-E6-25..30 — инструмент,
секция 10; секция 9 — оракул v2). Dev-тест среза 1 (E6.4c-3/1):
python3 LAB/ai/wall_test_v2.py -> 27/27 (якоря * / %, заголовки v1/v2,
круг «U-MDM-OK 52»).
