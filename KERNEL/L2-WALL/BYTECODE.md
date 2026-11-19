# BYTECODE. Модуль M2-WALL — карта образа

Паспорт файла: KERNEL/L2-WALL/BYTECODE.md | слой: L2 | роль: разбор образа wall.exe.

## 1. Сводка

| Параметр | Значение |
|---|---|
| Файл | KERNEL/L2-WALL/wall.exe, 87040 байт (0x15400) |
| SHA-256 | B2AC45F43CCC6FD66489A0F4327850105CC9B6BDE42FE98495DAFA0A46EE1CF7 |
| Происхождение | ГЕНЕРИРУЕМЫЙ артефакт (E6.4d-5/3-2): сборка из wall.wall — wall.exe(splice(wall.wall)) -> wall.b2 -> enc -> wall.brick -> brick -> pegen + wall.peg. Воспроизводимость закреплена в батарее (T-E6-49a/49b); протокол замены — VERIFY-E6D5.md |
| Исходник | KERNEL/L2-WALL/wall.wall — корень + 18 частей wall_self_*.wall (WALL v2, разрез SPEC/10); склейка 168930 Б (~65% предела входа 256 КиБ), 4588 строк (E7.2-2F: +11 строк фикса №23) |
| Тело секции | 86307 байт (0x15123), RVA 0x1000, SRD 0x15200 |
| VirtualSize | 0x15123 (одна секция) |
| Точка входа | 0x1200 (:_entry — константа SPEC/11 п.6: после фиксированной области импортов 0x200) |
| idata / iat / intt | 0x1000 (0x28) / 0x1028 (0x48) / 0x1070 — фиксированная область импортов SPEC/11 п.6 |
| Импорты | kernel32.dll, 8 функций: GetStdHandle, WriteFile, ExitProcess, GetCommandLineA, CreateFile2, ReadFile, CloseHandle, GlobalAlloc (CreateFile2+widen и GlobalAlloc — сервис каркаса) |
| DOS-заглушка | «Universal L0 wall. No DOS support.» (имя модуля — wall.peg) |
| M-строк в исходнике | 17766 (wall.b2 — 19117 строк; плоский, генерируемый) |
| Меток в исходнике | 968 из 2048 (лимит brick; карта — LAB/ai/label_map.py) |
| Функций | 117 (карта — §2) + данные (§4) |
| Компилятор сборки | сам wall.exe (фикс-пункт самосборки: wall.exe(wall.wall) == wall.b2 байт-в-байт — T-E6-49a) |

## 2. Карта функций (RVA — LAB/ai/label_map.py по wall.brick)

Группировка — по частям каркаса wall.wall (состав и назначение каждой
части — CARD.md; кирпичи K2-* — MAP/M2-WALL.md).

```
сервис (wall_self_c.wall — реинкарнации K1-C08B..C090):
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
  pp_pcount ............ 6E7B  P01B: число пар [..] вперёд (№23: стоп и на двухсимвольных операторах глубины 0)
  pp_pairs ............. 7131  P01C: цикл пар индексации (T-склад, хвост)
  pp_strchk ............ 7412  P01E: база-имя вида str запрещена
  p_args ............... 78A3  P014: аргументы до ')' (фикс №19+№21)
  pa_stage ............. 7C1C  P017: стейджинг C(base+cnt+1)/S5
  emit_argload ......... 7DC6  загрузки ARGREG из C-слотов
  p_call_tail .......... 7FB3  P015: вызов func/ext + хвост «M mov r10, rax»
  call_stats ........... 856E  P016: статистика вызова (стат-плечо)
  astore_chk ........... 874B  P01D: цель присваивания (фикс №22)

условия (wall_self_pc.wall):
  p_cond ............... 8910  P018: if/while — стат- и эмит-плечо
                              (m-скан дизъюнктов, T1, cmp, jcc-инверсии,
                              d/t-метки; m=1 — как v1)

проход 1 (wall_self_pd.wall + wall_self_p1.wall + wall_self_p1s.wall):
  p1_decl .............. 93F5  S003: var/str/ext (+ var a[n])
  p1_funchdr ........... 9CB7  S004: заголовок func (+окно дублей)
  fh_param ............. A7FF  S00E: параметры (<= 4; larr/bstk/ftab)
  set_lastline ......... AAC9  N004: curline := lastnonempty
  p1_line .............. AB23  S002: диспетчер kw (14 слов)
  pass1 ................ AF95  S001: цикл строк + пост-проверка main
  p1s_var .............. B5BC  S006: локальные var (скаляры/массивы)
  p1s_if/p1s_while ..... B8F5/BB78  S009/S00A: bstk + p_cond(0,0,0)
  p1s_else ............. BD75  S008: kind 2->3, ifarr
  p1s_brk .............. BFEA  S00F: break/continue (скан bstk до while)
  p1s_end .............. C12A  S007: закрытие func, запись ftab
  p1s_return ........... C516  S00B
  p1s_setb ............. C5F1  S00C
  p1_namestmt .......... C813  S00D: вызов/astore/присваивание

примитивы вывода (wall_self_e.wall — реинкарнации E07B..E082/E08C/E09F):
  blob_dec/init_blob ... CD5F/CF77  декодер блоба канона -> sblob (outmem)
  out_ch/copy/str/line . D11E/D189/D264/D2B5  E07B..E07E
  out_hex/out_hex2 ..... D31A/D51D  E07F/E080: ЗАГЛАВНЫЙ hex
  out_dec .............. D5CA  E082
  lower_copy ........... D7D8  E08C: scr (нижний регистр для _iat_)
  get_ext .............. D8E2  E09F: смещение ext в области импортов
  emit_cmt ............. DA3D  E083: « ; текст строки» из карты smem
  str_dlen ............. DAC3  E08D: декодированная длина с экранами
  esc_code ............. DBA5  экраны n r t 0 \ ' (ранние возвраты)
  str_emit/se_doline ... DCA6/DF3C  E08E: DB-строки <= 16 + комментарий
  set_cmt .............. E03B  строка №ln -> cmt_ptr/cmt_len (smem)

секции данных (wall_self_d.wall):
  emit_strdata ......... E0F7  E0A1: «:имя» + DZ 0 / DB-строки
  emit_globdata ........ E497  E0A2: «:имя» + DZ 8n + комментарий

кадры (wall_self_f.wall):
  emit_kadr/emit_vyhod . E77B/E824  E08A: «кадр/выход имя»
  emit_lab ............. E8CD  E08B: «:имя»
  calc_framesize ....... E931  E091: align16(8*nslots)+0x30 (ftab+0x48)
  emit_prologue ........ EC56  E092: push rbp/mov rbp,rsp/sub rsp/ARGREG
  emit_epilogue ........ EF8D  E093

эмиттеры выражений (wall_self_g.wall):
  emit_tstore/tload .... F01C/F0BE  T-склад уровней (nbase+tdepth)
  alu_tail/emit_alu .... F179/F215  E09A: + - | ^ & (if-цепочка 43/45/...)
  emit_shift ........... F3C5  E09B (через cl)
  emit_imul ............ F4BD  E0AE (v2)
  emit_divmod .......... F4FC  E0AF (v2): rax/cqo/idiv/rax|rdx
  emit_addr ............ F5FE  E09C: «M mov r10, rip+имя»/lea [rbp-X]
  emit_len ............. F897  E09D
  emit_load ............ FC54  E09E

статы-имена (wall_self_t.wall):
  emit_sstore .......... FF8C  E0A7: S-слот s(i)=nbase+maxd+maxc+i+1
  p2s_setb ............. 1006D  Y009: S0/S1/S2 + байтовая запись [r10+r11]
  p2_namestmt .......... 1042D  Y00B: вызов/astore/присваивание (эмит)

guard-эмиттеры (wall_self_pg.wall):
  jcc_name ............. 10E47  инверсии jne je jge jg jle jl (индекс 0..5)
  emit_jcc_line ........ 11002  E0A3: «M j<инв> $<pfx><k>[e]»
  emit_jmp_line ........ 1111F  E0A4
  emit_iflab/emit_wlab . 11204/112D0  E0A5/E0A6: «:_if/_w<k>[e]», nlab++
  emit_jccd ............ 1139C  E0B0: «M j<инв> $<pfx><k>d<i>»
  emit_jmpt ............ 1149C  E0B1: «M jmp $<pfx><k>t»
  emit_glab ............ 1154F  E0B2: «:<pfx><k>d<i>»/«t»
  p2s_brk .............. 11681  Y00C: общий хвост break/continue
  p2s_break/continue ... 1182C/1185B  «M jmp $_w<k>[e]»

проход 2 (wall_self_y.wall):
  pass2 ................ 1188A  Y001: пролог, pc_mode=1, цикл строк,
                               секции данных, предел nlab 2000
  p2_line .............. 11B35  Y002: диспетчер kw + плечи
  p2_funchdr ........... 11F71  Y00A: окно lay из ftab, st_p2nbase/maxd/maxc
  p2s_var .............. 12463  Y003
  p2s_end .............. 124C7  Y004: while — обратный jmp; if/else — метка
  p2s_if/p2s_while ..... 1275E/12AE6  Y006/Y007: guard p_cond(0,e,k)/(1,1,k)
  p2s_else ............. 12DE6  Y005: jmp $_if<ke> + :_if<k> (ifarr)
  p2s_return ........... 131B2  Y008: p_expr(1) + «M mov rax, r10» + эпилог
  emit_header .......... 132AE  E08F: заголовок v1/v2 (флаг v2)
  emit_imports ......... 13459  E0A0
  emit_entry ........... 13DB3  E090

корень (wall.wall):
  main ................. 13E9C  CLI, чтение входа, GlobalAlloc-буферы,
                               pass0/pass1/pass2, запись выхода
```

Служебные метки (RVA): `_idt` 1000, `_iat` 1028, `_intt` 1070,
`_hint_<имя>` — 8 записей (инвариант 7 SPEC/04), `_dll`, `_entry` 1200;
guard-метки `_if<k>[e]`, `_w<k>[e]`, `_if<k>d<i>/t` — порядок встречаемости
(968 меток всего; полный список — LAB/ai/label_map.py).

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
| 120A-14578 | код 117 функций (§2; main 13E9C и его guard-метки) |
| 14579-146C2 | строки ошибок/справки s_use, s_long, s_osrc, s_rsrc, s_big, s_oout, s_wout, s_fmt, s_hexd, s_sym2, s_sym1, s_kws (errtab каркаса) |
| 146C3-156C2 | sd0..sd7 — блоб канона: 8 x 512 симв. hex-литералов (4096 ASCII-байт -> 2048 Б строк канона; генератор LAB/ai/wall_self_data.py; декодер blob_dec) |
| 156C3-16122 | глобали каркаса (DZ 8): hstdout, cmdline, written, wlen; буферы имён arg1/arg2, w1/w2 (UTF-16 для CreateFile2); скаляры srcbuf, smem, srclen, lineidx, curline, nlentries, nlines, lastnonempty, fmtbuf, tabmem; лексер tokptr/tokend/tokval; aspos/asflag, v2flag; счётчики ncount/fcount/scount/vcount/ecount; fdepth/ifseq/seenfunc/fcur/lcount/curf; окно lay: st_locoff/loccnt/nslots/maxd/maxc/setb/ext5; выражения pcur/ple, pc_mode, pc_argcnt/argmax/extflg/cact/cbase/staged, lay_lo/lay_hi, lf_size; вывод outmem/outbuf/outcur/scrbuf, nlab; ext_nptr/nlen; проход 2: st_infunc/lret/bcnt/fbase/ifcnt/fptr/flen, cmt_ptr/cmt_len, st_p2nbase/maxd/maxc |

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
brick.exe wall.brick t_body.bin   (тело 86307 байт)
pegen.exe t_body.bin wall.peg wall.exe  (== артефакту, T-E6-49b;
                                    wall.peg — константа SPEC/11 п.6)
```

Батарея: python3 LAB/py/lab_verify.py -> 158/158 (с E7.2-2F — якоря фикса №23 T-E6-61; T-E6-49a — фикс-пункт
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

## 8. Пересборка E7.2-2F (сессия 47 — фикс дефекта №23)

pp_pcount: двухсимвольный оператор (== != <= >= << >> && ||) на глубине
0 — завершитель скана пар [..] (раньше просматривался насквозь — пары
правого операнда засчитывались в цепочку левого, k завышался ->
ложный ERR=FORMAT на «индекс == индекс»). Артефакты пересобраны
конвейером фикс-пункта (wall_fix23_build.py: сборка 548 707 240 шагов,
s2.b2 == wall.b2 байт-в-байт доказан); тело 86185 -> 86307 (+122 Б —
код фикса), функции от pp_pairs (старт не сместился) сдвинулись на
+0x7A; метки 966 -> 968 (guard-метки нового if в pp_pcount); ядро
kernel.exe пересобрано без скобок-обхода в op_eq — байт-в-байт тот же
(скобки прозрачны; .b2/.brick изменили только текст комментариев,
-44 Б). Приёмка: зонд wall_ppc_probe.py — 0 расхождений из 17;
якорь-случаи T-E6-61 в батарее.
