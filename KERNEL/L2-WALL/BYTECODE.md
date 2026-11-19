# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 87040 байт (0x15400) |
| SHA-256 | FE41C2B77C6759FB9F7D08FDF561D7799F04BDD70387C7307EFFBE1D61482BC3 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E6.4d-5/3-2): сборка из wall.wall — wall.exe(splice(wall.wall)) -> wall.b2 -> enc -> wall.brick -> brick -> pegen + wall.peg. Воспроизводимость закреплена в батарее (T-E6-49a/49b); протокол замены — VERIFY-E6D5.md |
| Исходник | KERNEL/L2-WALL/wall.wall — корень + 18 частей wall_self_*.wall (WALL v2, разрез SPEC/10); склейка 168050 Б (64% предела входа 256 КиБ), 4578 строк |
| Тело секции | 86528 байт (0x151D0), RVA 0x1000, SRD 0x15200 |
| VirtualSize | 0x150A9 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п.6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п.6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc (CreateFile2+widen и GlobalAlloc — сервис каркаса) |
| DOS-заглушка | «Universal L0 wall. No DOS support.» (имя модуля — wall.peg) |
| M-строк в исходнике | 17739 (wall.b2 — 19736 строк; плоский, генерируемый) |
| Меток в исходнике | 966 из 2048 (лимит brick; карта — LAB/ai/label_map.py) |
| Функций | 117 (карта — §2) + данные (§4) |
| Компилятор сборки | сам wall.exe (фикс-пункт самосборки: wall.exe(wall.wall) == wall.b2 байт-в-байт — T-E6-49a) |

## 2. Карта функций (RVA — LAB/ai/label_map.py по wall.brick)

Группировка — по частям каркаса wall.wall (состав и назначение каждой
части — CARD.md; кирпичи K2-* — MAP/M2-WALL.md).

```
сервис (wall_self_c.wall — реинкарнации K1-C011..C016):
  print_error .......... 120A  G003: errtab-строка + ExitProcess(код)
  skip0 ................ 1285  пропуск ведущих пробелов/табов
  read_arg ............. 1658  слово аргумента (имена >= 127 -> код 3)
  widen ................ 198F  имя -> UTF-16 для CreateFile2

проход 0 (wall_self_n.wall):
  stq .................. 1B41  запись QWORD в smem-карту
  fail_format .......... 1C08  G002: ERR=FORMAT AT=XXXX + выход 6
  lex_line ............. 1EA8  N003: полная лексика строки + обрезка текста
  pass0 ................ 2C47  N002: разбиение LF/CRLF/CR + карта текстов

хелперы прохода 1 (wall_self_pe.wall):
  max2/tok_is1 ......... 2F97/2FDB  max(a,b); сравнение токена с символом
  getq/tok_next ........ 30D1/3184  чтение QWORD из smem; L001: след. токен
  kw_lookup ............ 3A77  P004: индекс kwtab | -1
  chk_name ............. 3CBF  P005: [A-Za-z][A-Za-z0-9_]*, <= 63
  names_find/find_ci ... 3FDA/41E6  P006: поиск в ntab (точный/без регистра)
  local_find ........... 44B8  P008: окно larr -> базовый слот + размер
  names_add ............ 4805  P007+S005: запись в ntab
  arr_size ............. 49C4  P019: разбор [n], 1..4096, флаг v2
  at_end/want_id/sym1 .. 4BEE/4C5C/4CCA  P002/P003/P001

выражения (wall_self_ph.wall + wall_self_pp.wall + wall_self_pa.wall):
  chain_count .......... 4DD9  P009: K операций уровня (без AST)
  mul_peek ............. 566A  peek '&'/'<<'/'>>'
  p_expr ............... 588A  P010: аддитивный уровень
  p_mul ................ 5C46  P011: конъюнкция & << >>
  p_mdm ................ 5F13  P01A (v2): уровень * / %; флаг v2
  p_unary .............. 62E1  P012: унарный '-'
  p_prim ............... 63B7  P013: обёртка индексации (откат outcur)
  pp_prim0 ............. 658A  P013a: число/скобки/&имя/getb/len/вызов/имя
  pp_pcount ............ 6E7B  P01B: число пар [..] вперёд
  pp_pairs ............. 70B7  P01C: цикл пар индексации (T-склад, хвост)
  pp_strchk ............ 7398  P01E: база-имя вида str запрещена
  p_args ............... 7829  P014: аргументы до ')' (фикс №19+№21)
  pa_stage ............. 7BA2  P017: стейджинг C(base+cnt+1)/S5
  emit_argload ......... 7D4C  загрузки ARGREG из C-слотов
  p_call_tail .......... 7F39  P015: вызов func/ext + хвост «M mov r10, rax»
  call_stats ........... 84F4  P016: статистика вызова (стат-плечо)
  astore_chk ........... 86D1  P01D: цель присваивания (фикс №22)

условия (wall_self_pc.wall):
  p_cond ............... 8896  P018: if/while — стат- и эмит-плечо
                              (m-скан дизъюнктов, T1, cmp, jcc-инверсии,
                              d/t-метки; m=1 — как v1)

проход 1 (wall_self_pd.wall + wall_self_p1.wall + wall_self_p1s.wall):
  p1_decl .............. 937B  S003: var/str/ext (+ var a[n])
  p1_funchdr ........... 9C3D  S004: заголовок func (+окно дублей)
  fh_param ............. A785  S00E: параметры (<= 4; larr/bstk/ftab)
  set_lastline ......... AA4F  N004: curline := lastnonempty
  p1_line .............. AAA9  S002: диспетчер kw (14 слов)
  pass1 ................ AF1B  S001: цикл строк + пост-проверка main
  p1s_var .............. B542  S006: локальные var (скаляры/массивы)
  p1s_if/p1s_while ..... B87B/BAFE  S009/S00A: bstk + p_cond(0,0,0)
  p1s_else ............. BCFB  S008: kind 2->3, ifarr
  p1s_brk .............. BF70  S00F: break/continue (скан bstk до while)
  p1s_end .............. C0B0  S007: закрытие func, запись ftab
  p1s_return ........... C49C  S00B
  p1s_setb ............. C577  S00C
  p1_namestmt .......... C799  S00D: вызов/astore/присваивание

примитивы вывода (wall_self_e.wall — реинкарнации E001..E008/E012/E025):
  blob_dec/init_blob ... CCE5/CEFD  декодер блоба канона -> sblob (outmem)
  out_ch/copy/str/line . D0A4/D10F/D1EA/D23B  E001..E004
  out_hex/out_hex2 ..... D2A0/D4A3  E005/E006: ЗАГЛАВНЫЙ hex
  out_dec .............. D550  E008
  lower_copy ........... D75E  E012: scr (нижний регистр для _iat_)
  get_ext .............. D868  E025: смещение ext в области импортов
  emit_cmt ............. D9C3  E009: « ; текст строки» из карты smem
  str_dlen ............. DA49  E013: декодированная длина с экранами
  esc_code ............. DB2B  экраны n r t 0 \ ' (ранние возвраты)
  str_emit/se_doline ... DC2C/DEC2  E014: DB-строки <= 16 + комментарий
  set_cmt .............. DFC1  строка №ln -> cmt_ptr/cmt_len (smem)

секции данных (wall_self_d.wall):
  emit_strdata ......... E07D  E027: «:имя» + DZ 0 / DB-строки
  emit_globdata ........ E41D  E028: «:имя» + DZ 8n + комментарий

кадры (wall_self_f.wall):
  emit_kadr/emit_vyhod . E701/E7AA  E010: «кадр/выход имя»
  emit_lab ............. E853  E011: «:имя»
  calc_framesize ....... E8B7  E017: align16(8*nslots)+0x30 (ftab+0x48)
  emit_prologue ........ EBDC  E018: push rbp/mov rbp,rsp/sub rsp/ARGREG
  emit_epilogue ........ EF13  E019

эмиттеры выражений (wall_self_g.wall):
  emit_tstore/tload .... EFA2/F044  T-склад уровней (nbase+tdepth)
  alu_tail/emit_alu .... F0FF/F19B  E020: + - | ^ & (if-цепочка 43/45/...)
  emit_shift ........... F34B  E021 (через cl)
  emit_imul ............ F443  E034 (v2)
  emit_divmod .......... F482  E035 (v2): rax/cqo/idiv/rax|rdx
  emit_addr ............ F584  E022: «M mov r10, rip+имя»/lea [rbp-X]
  emit_len ............. F81D  E023
  emit_load ............ FBDA  E024

статы-имена (wall_self_t.wall):
  emit_sstore .......... FF12  E02D: S-слот s(i)=nbase+maxd+maxc+i+1
  p2s_setb ............. FFF3  Y009: S0/S1/S2 + байтовая запись [r10+r11]
  p2_namestmt .......... 103B3  Y00B: вызов/astore/присваивание (эмит)

guard-эмиттеры (wall_self_pg.wall):
  jcc_name ............. 10DCD  инверсии jne je jge jg jle jl (индекс 0..5)
  emit_jcc_line ........ 10F88  E029: «M j<инв> $<pfx><k>[e]»
  emit_jmp_line ........ 110A5  E02A
  emit_iflab/emit_wlab . 1118A/11256  E02B/E02C: «:_if/_w<k>[e]», nlab++
  emit_jccd ............ 11322  E036: «M j<инв> $<pfx><k>d<i>»
  emit_jmpt ............ 11422  E037: «M jmp $<pfx><k>t»
  emit_glab ............ 114D5  E038: «:<pfx><k>d<i>»/«t»
  p2s_brk .............. 11607  Y00C: общий хвост break/continue
  p2s_break/continue ... 117B2/117E1  «M jmp $_w<k>[e]»

проход 2 (wall_self_y.wall):
  pass2 ................ 11810  Y001: пролог, pc_mode=1, цикл строк,
                               секции данных, предел nlab 2000
  p2_line .............. 11ABB  Y002: диспетчер kw + плечи
  p2_funchdr ........... 11EF7  Y00A: окно lay из ftab, st_p2nbase/maxd/maxc
  p2s_var .............. 123E9  Y003
  p2s_end .............. 1244D  Y004: while — обратный jmp; if/else — метка
  p2s_if/p2s_while ..... 126E4/12A6C  Y006/Y007: guard p_cond(0,e,k)/(1,1,k)
  p2s_else ............. 12D6C  Y005: jmp $_if<ke> + :_if<k> (ifarr)
  p2s_return ........... 13138  Y008: p_expr(1) + «M mov rax, r10» + эпилог
  emit_header .......... 13234  E015: заголовок v1/v2 (флаг v2)
  emit_imports ......... 133DF  E026
  emit_entry ........... 13D39  E016

корень (wall.wall):
  main ................. 13E22  CLI, чтение входа, GlobalAlloc-буферы,
                               pass0/pass1/pass2, запись выхода
```

Служебные метки (RVA): `_idt` 1000, `_iat` 1028, `_intt` 1070,
`_hint_<имя>` — 8 записей (инвариант 7 SPEC/04), `_dll`, `_entry` 1200;
guard-метки `_if<k>[e]`, `_w<k>[e]`, `_if<k>d<i>/t` — порядок встречаемости
(966 меток всего; полный список — LAB/ai/label_map.py).

## 3. Соглашения ветвей кода

Ветви = части каркаса wall.wall (WALL v2); префиксы кирпичей K2-*
сохранены (см. MAP/M2-WALL.md): C (командная строка), G/H (ошибки),
N (проход 0), L (лексер — внутри tok_next), P (парсер/выражения),
S (проход 1), Y (проход 2), E (эмиттеры), D (данные). Регистровые
соглашения — канон WALL (SPEC/11 п.5-8): rbp-кадры, T/C/S-склады,
ARGREG rcx/rdx/r8/r9, рабочие r10/r11; подпрограммы сохраняют
rbx/rbp/rsi/rdi/r12-r15 (стандарт пролога канона).

## 4. Данные образа

| Диапазон RVA | Содержимое |
|---|---|
| 120A-13E21 | код 117 функций (§2) |
| 144FF-14648 | строки ошибок/справки s_use, s_long, s_osrc, s_rsrc, s_big, s_oout, s_wout, s_fmt, s_hexd, s_sym2, s_sym1, s_kws (errtab каркаса) |
| 14649-15648 | sd0..sd7 — блоб канона: 8 x 512 симв. hex-литералов (4096 ASCII-байт -> 2048 Б строк канона; генератор LAB/ai/wall_self_data.py; декодер blob_dec) |
| 15649-160A9 | глобали каркаса (DZ 8): hstdout, cmdline, written, wlen; буферы имён arg1/arg2, w1/w2 (UTF-16 для CreateFile2); скаляры srcbuf, smem, srclen, lineidx, curline, nlentries, nlines, lastnonempty, fmtbuf, tabmem; лексер tokptr/tokend/tokval; aspos/asflag, v2flag; счётчики ncount/fcount/scount/vcount/ecount; fdepth/ifseq/seenfunc/fcur/lcount/curf; окно lay: st_locoff/loccnt/nslots/maxd/maxc/setb/ext5; выражения pcur/ple, pc_mode, pc_argcnt/argmax/extflg/cact/cbase/staged, lay_lo/lay_hi, lf_size; вывод outmem/outbuf/outcur/scrbuf, nlab; ext_nptr/nlen; проход 2: st_infunc/lret/bcnt/fbase/ifcnt/fptr/flen, cmt_ptr/cmt_len, st_p2nbase/maxd/maxc |

Буферы времени выполнения — GlobalAlloc (куча, не образ):
srcbuf 262145 (вход, E6.4g-4), smem 1048592 (карта текстов),
tabmem 4948032 (ntab/varr/sarr/earr/larr/ftab/bstk 3072x32/ifarr
32768x8 — единая область, смещения в коде), outmem 2103264 (sblob
2048 + scr 64 + outbuf 2 МиБ). Форматы записей таблиц — §5.

## 5. Таблицы форматов

- ntab (имя): {ptr, len, вид(1 var/2 str/3 ext/4 func/5 массив), мета,
  строка} 40 Б; мета: var/массив -> индекс varr, str -> sarr, ext ->
  earr, func -> ftab (вид 5 — E6.4c-3/4).
- ftab (функция): {nameptr, namelen, nparams, maxd, maxc, flags(1 setb,
  2 ext5), locoff, loccnt, hdrline, nslots} 80 Б (nslots — сумма слотов
  окна с массивами; loccnt — длина окна larr).
- larr (локаль): {ptr, len, size} 32 Б (size — слотов; у параметров 1);
  окно функции [locoff, locoff+loccnt).
- varr (глобальная var): {ntab_idx, size} 16 Б (size — для DZ 8n; у
  скаляров 1).
- sarr (строка): {индекс ntab, литерал ptr, длина} 24 Б.
- bstk (блок): {kind(1 func/2 if/3 else/4 while), k, seq, lineidx} 32 Б
  (дефект №15: было 24 Б).
- sm_arr (строка исходника): {ptr текста, len} 16 Б.

## 6. Контроль воспроизведения (E6.4d-5/3-2)

```
wall.exe  wall.wall  wall.b2      (фикс-пункт: выход == артефакту wall.b2;
                                    ~548 млн шагов эмулятора, T-E6-49a)
enc.exe   wall.b2    wall.brick   (== артефакту, T-E6-49b)
brick.exe wall.brick t_body.bin   (тело 86528 байт)
pegen.exe t_body.bin wall.peg wall.exe  (== артефакту, T-E6-49b;
                                    wall.peg — константа SPEC/11 п.6)
```

Батарея: python3 LAB/py/lab_verify.py -> 140/140 (T-E6-49a — фикс-пункт
+ равенство артефакту wall.b2; T-E6-49b — воспроизводимость wall.brick/
wall.exe; T-E6-30 — SHA/PE/импорты-восьмёрка). Приёмочные: LAB/ai/
wall_self_canary.py -> 9/9 (6 DEMO-кругов + big_source/big_source2
каркасом); протокол фикс-пункта и замены — VERIFY-E6D5.md.

## 7. История

До E6.4d-5/3-2 образ собирался из wall.b2 (корень + 20 частей
wall_*.b2, BRICK v2; вход 1000, импорты-семёрка на CreateFileA, 28160
Б, SHA-256 295730EF…). Карты того образа и его реестры — в истории
этого файла (коммит, предшествующий E6.4d-5/3-2) и в VERIFY-E6D*.md.
Части wall_*.b2 удалены: источник истины — wall.wall (WALL v2);
прообразом reincarnations послужили алгоритмы, не байты.
