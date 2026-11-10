# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 24064 байта (0x5E00) |
| SHA-256 | 67EA2C198FCD25523CFB9333ECB8E07DF2C60DF505D5080589A2FFE6740474E9 |
| Тело секции | 23240 байт (0x5AC8), RVA 0x1000 |
| Точка входа | 0x1000 (:entry) |
| idata / iat / intt | 0x69AD / 0x69D5 / 0x6A15; dll 0x6A55; VirtualSize 0x7A6EE0 |
| bss (DBZ) | 0x7A1418 — единая область :scalars (RVA 0x6AC8) |
| М-строк в исходнике | 4343 (19 файлов .b2: корень + 18 частей !include) |
| Меток в исходнике | 499 (лимит brick 512 вкл. base; E6.4c-3/1: -14 bss-меток) |
| Кирпичей | 69 карточек (MAP/M2-WALL.md) |

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
  want_sym1..kw_lookup . 1F00-2058   P001-P004: поглощение, chk_name, kwtab
  names_find/add, local_find 2058-2274 P006-P008: реестр имён, локали
  chain_count .......... 2392-24A0   P009: число операций уровня (K; ур.0/1/2;
                                        сравнения — терминаторы, E6.4c-3/1)
  p_expr ............... 19F8        P010: аддитивный уровень
  p_mul ................ 1BA4        P011: конъюнкция (& << >>)
  p_mdm ................ 1DC6        P01A (E6.4c-3/1): уровень * / % — тот же
                                        механизм tdepth; флаг v2 [r13+18190]
  p_unary .............. 1FB5        P012: унарный минус
  p_prim ............... 2AD2        P013: числа/имена/&/len/getb/скобки/вызовы
  p_args/pa_stage ...... 2AD2-2EAE   P014/P017: стейджинг C-слотов (5-й ext -> S5)
  p_call_tail .......... 2AD2-2EAE   P015: загрузки rcx/rdx/r8/r9, call $f /
                                        call [rip+$_iat_e], want -> mov r10,rax
  call_stats ........... 2EAE-2EAF   P016: maxc = max(...), ext5
  p_cond ............... 2EAF-3364   P018: операнды@2, инверсия -> индекс jcc

проход 1 (статы):
  pass1, p1_line ....... 3364-4234   S001/S002: цикл, диспетчер
  p1_decl .............. 3364-3DA0   S003: var/str/ext (проверки имён)
  fh_param ............. 3DA0-3E80   S00E: параметры (дубликаты в окне locoff)
  names_find_ci ........ 3E80-3F00   S005: без учёта регистра (ext)
  p1_funchdr ........... 3F00-4234   S004: ftab-запись, st_* сброс, push {func}
  p1s_var..p1s_setb .... 4234-4234   S006-S00C: статы утверждений
  (локали: larr, дубликаты, maxd/maxc/setb/ext5)

проход 2 (эмитция):
  pass2, p2_line ....... 4234-52D2   Y001/Y002: цикл, карта текстов строк
  p2_funchdr ........... 4234-5415   Y00A: раскладка из ftab, пролог
  p2s_end/else/if/while 5415-5656   Y004-Y007: bstk {kind,k,seq,lineidx}
  p2s_return/setb/namest 5656-5CA6  Y008/Y009/Y00B: эпилоги, S-слоты, цели
  emit_jcc/jmp/iflab/wlab 5CA6-5E5E E029-E02C: метки _if/_w (сквозной kctr)

эмиттеры:
  out_ch/out_copy/str .. 46E7-52D2   E001-E004: байты вывода, strtab2-адресация
  out_hex/out_hex2 ..... 52D2        E005/E006: ЗАГЛАВНЫЙ hex
  div10 ................ —           E007: деление на 10 бит за битом (маска!)
  out_dec .............. —           E008: десятичные числа
  emit_cmt/kadr/vyhod .. —           E009/E010: " ; текст", "кадр/выход имя"
  emit_lab ............. —           E011: ":имя"
  lower_copy ........... —           E012: scr (нижний регистр для _iat_)
  str_dlen/str_emit .... —           E013/E014: декодирование экранов, DB<=16
  emit_header .......... 52D2        E015: заголовок v1/v2 (флаг [r13+18190])
  emit_entry, calc_framesize, пролог/эпилог 5415-5656  E016-E019
  emit_alu ............. 554F        E020: add/sub/and/or/xor r10, r11
  emit_shift ........... 5656        E021: mov rcx,r11; shl/shr r10, cl
  emit_imul ............ 5656        E034 (E6.4c-3/1): imul r10, r11
  emit_divmod .......... 5666        E035 (E6.4c-3/1): rax/cqo/idiv/rax|rdx
  get_ext/emit_imports . 4EFC-5CA6  E025/E026: импорты (см. данные)
  emit_strdata/globdata  —           E027/E028: секции данных

данные (ветвь D):
  digits ............... 5CA6  K2-D001 (16 Б)
  kwtab ................ 5CB6  K2-D002 (12x20 Б)
  jcctab ............... 5D76  K2-D003 ({смещ,длина})
  alutab ............... 5DA6  K2-D004
  argtab ............... 5DCE  K2-D005
  errtab ............... 5DEE  K2-D006 (7x20 Б)
  strblob .............. 5E5E  K2-D007 (0x7C6 Б, 113 строк канона;
                                E6.4c-3/1: +imul/cqo/idiv/r10-rdx, hdr v2)
  strtab2 .............. 6624  K2-D008 (113x8 Б)
  импорты .............. 69AD  K2-D010: idt 0x28 (idata 69AD, iat 69D5),
                                intt 6A15, dll 6A55 (13+DZ2), hints:
                                gsh 6A64, wf 6A74, ep 6A80, gcl 6A8E,
                                cf 6AA0, rf 6AAE, ch 6ABA (чётные RVA,
                                инвариант 7 SPEC/04; калибровка DZ 2)
  bss .................. 6AC8  K2-D011: :scalars DBZ 7A1418 — ЕДИНАЯ область
                                (bstk 4096x24 + скаляры + буферы, база R13);
                                E6.4c-3/1: метки буферов -> смещения r13+X
                                (fname_in r13+18208 … outbuf r13+5A1418);
                                флаг v2 — скаляр [r13+18190]
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
