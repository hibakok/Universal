# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 23040 байт (0x5A00) |
| SHA-256 | 0129BED660F49323E3E8EB7A03E8FF80929F3052FA8D046FBB2224F6E65307C6 |
| Тело секции | 22216 байт (0x56C8), RVA 0x1000 |
| Точка входа | 0x1000 (:entry) |
| idata / iat | 0x65AE / 0x65D6 |
| bss (DBZ) | 0x7A1418; VirtualSize 0x7A6AE0 |
| М-строк в исходнике | ~5040 (19 файлов, разрез !include) |
| Меток в исходнике | 496 (лимит brick 512) |
| Кирпичей | 66 карточек (MAP/M2-WALL.md) |

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

парсер (ветви P):
  want_sym1..kw_lookup . 1F00-2058   P001-P004: поглощение, chk_name, kwtab
  names_find/add, local_find 2058-2274 P006-P008: реестр имён, локали
  chain_count .......... 2549-2660   P009: число операций уровня (K)
  p_expr/p_mul/p_unary . 2F72-3185   P010-P012: цепочки, tdepth = d+K-1
  p_prim ............... 3185-3560   P013: числа/имена/&/len/getb/скобки/вызовы
  p_args/pa_stage ...... 3560-37A0   P014/P017: стейджинг C-слотов (5-й ext -> S5)
  p_call_tail .......... 37A0-3D00   P015: загрузки rcx/rdx/r8/r9, call $f /
                                        call [rip+$_iat_e], want -> mov r10,rax
  call_stats ........... 3D00-3DA0   P016: maxc = max(...), ext5
  p_cond ............... 3DA0-4100   P018: операнды@2, инверсия -> индекс jcc

проход 1 (статы):
  pass1, p1_line ....... 4100-4400   S001/S002: цикл, диспетчер
  p1_decl .............. 4400-4C00   S003: var/str/ext (проверки имён)
  fh_param ............. 4C00-4D00   S00E: параметры (дубликаты в окне locoff)
  names_find_ci ........ 4D00-4E00   S005: без учёта регистра (ext)
  p1_funchdr ........... 4E00-5100   S004: ftab-запись, st_* сброс, push {func}
  p1s_var..p1s_setb .... 5100-5700   S006-S00C: статы утверждений
  (локали: larr, дубликаты, maxd/maxc/setb/ext5)

проход 2 (эмитция):
  pass2, p2_line ....... 5700-5A00   Y001/Y002: цикл, карта текстов строк
  p2_funchdr ........... 5A00-5C00   Y00A: раскладка из ftab, пролог
  p2s_end/else/if/while 5C00-6100    Y004-Y007: bstk {kind,k,seq,lineidx}
  p2s_return/setb/namest 6100-6600   Y008/Y009/Y00B: эпилоги, S-слоты, цели
  emit_jcc/jmp/iflab/wlab 6600-6A00  E029-E02C: метки _if/_w (сквозной kctr)

эмиттеры:
  out_ch/out_copy/str .. 4B00-4D00   E001-E004: байты вывода, strtab2-адресация
  out_hex/out_hex2 ..... 4D00-4E80   E005/E006: ЗАГЛАВНЫЙ hex
  div10 ................ 4E80-4F00   E007: деление на 10 бит за битом (маска!)
  out_dec .............. 4F00-5080   E008: десятичные числа
  emit_cmt/kadr/vyhod .. 5080-5200   E009/E010: " ; текст", "кадр/выход имя"
  emit_lab ............. 5200-5280   E011: ":имя"
  lower_copy ........... 5280-5330   E012: scr (нижний регистр для _iat_)
  str_dlen/str_emit .... 5330-5400   E013/E014: декодирование экранов, DB<=16
  emit_header/entry .... 5400-5460   E015/E016: 2 строки заголовка, вход
  calc_framesize ....... 5460-54E0   E017: align16(8*nslots)+0x30
  emit_prologue/epilogue 54E0-5600   E018/E019: кадр, mov [rbp-8], ARGREG[i]
  emit_alu/shift ....... 5600-5720   E020/E021: r10,r11 / cl
  get_ext/emit_imports . 5383-5759   E025/E026: область 0x200 (SPEC/11 п.6)
  emit_strdata/globdata  5759-5955   E027/E028: секции данных

данные (ветвь D):
  digits ............... 5955  K2-D001 (16 Б)
  kwtab ................ 5965  K2-D002 (12x16 Б)
  jcctab/alutab/argtab . 5A25..     K2-D003..D005 ({смещ,длина})
  errtab ............... 5A9D  K2-D006 (7x16 Б)
  strblob .............. 5B0D  K2-D007 (0x740 Б, 108 строк канона)
  strtab2 .............. 624D  K2-D008 (108x8 Б)
  импорты .............. 65AE  K2-D010: idt 0x28, iat 0x48 (7+term),
                                intt 0x40, dll 13+DZ1, hints по 0xC-0x12
                                (чётные RVA, инвариант 7 SPEC/04)
  bss .................. 66C8  K2-D011: scalars 0x18208 (bstk+66 скаляров),
                                fname 2x0x80, linebuf 0x40, scr 0x80,
                                sm_arr 0x100010, ntab 0x140000, ftab 0x120000,
                                larr 0x100000, sarr 0xC0000, varr 0x40000,
                                earr 0x40, ifarr 0x8000, filebuf 0x21000,
                                outbuf 0x200000
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
splice.exe wall.b2 t_flat.b2      (склейка 19 частей)
enc.exe    t_flat.b2 wall.brick   (нормализация v2 -> v1)
brick.exe  wall.brick t_body.bin  (тело 22216 байт)
pegen.exe  t_body.bin wall.peg t.exe
fc /b t.exe wall.exe              -> различий нет (DoD сборки)
```

Батарея: python3 LAB/py/lab_verify.py -> 111/111 (T-E6-25..30 — инструмент, секция 10; секция 9 с E6.4c включает и оракул v2).
