# M2-WALL — карточки кирпичей компилятора WALL v1/v2 (107)

Паспорт файла: MAP/M2-WALL.md | слой: L2 | роль: реестр кирпичей M2-WALL.
Формат карточки — SPEC/01-METHOD-CARD.md; указатель — MAP/METHODS.md.
С E6.4c инструмент поддерживает v2-подмножество (сводка): `* / %`
(уровень p_mdm); `break`/`continue` (kwtab 14; bstk 3072x32 — дефект
№15); цепочки `&&`/`||` (guard-канон SPEC/11 п.8; E036-38; m=1 ==
v1 дословно); массивы `var a[n]` (DZ 8n / n слотов кадра), базы
адресов, `len(массив)`, записи: ntab вид 5, varr ×16 {idx, size},
larr ×32 {ptr, len, size}, ftab ×80 (+0x48 nslots); индексация
`e[i]`/astore — срез 4b (pp_pcount/pp_pairs/astore_chk/pp_strchk).
E6.4d — самохостинг wall.wall (каркас на WALL v2, разрез SPEC/10);
проходы 0/1 полны; проход 2 — срезы A (пролог), B (функции), C-1
(секции данных), C-2/1 (return-выражения; дефект №20 закрыт
синхронно), C-2/2 (вызовы/getb/индексация; дефект №21), C-2/3
(СТАТЫ-ИМЕНА: присваивания/вызовы-утверждения/astore/setb — часть
wall_self_t.wall; дефект №22 astore_chk lay-окно — только каркас);
эпики пределов: enc/brick 2 МиБ, вход 256 КиБ, nlab 2000. Детали —
LAB/ai/JOURNAL.md + VERIFY-E6D*.md.


## Поток исполнения (X)

- **K2-X001 prepare** — вход: командная строка; выход: кадр 0x38, RBX/R13
  (база :scalars), R10/R12 (outbuf), RSI (текст). Функция: подготовка
  регистров и вызов трёх проходов. Состоит из: C001, G004, N002, S001, Y001.
- **K2-X002 exit_ok** — вход: —; выход: ExitProcess(0). Функция: нормальный
  выход после записи. Используется в: X001.

## Командная строка (C) — реинкарнации K1-C011..C016

- **K2-C001 get_cmdline** — GetCommandLineA -> RDI; skip_argv0 с кавычками.
- **K2-C002 next_arg** — слово -> буфер R8; LONG NAME -> G003(1).
- **K2-C003 read_word/copy_word_dst** — границы слова, копирование <= 127.
- **K2-C004 skip_seps** — пробелы/табуляции.

## Ошибки и печать (G/H/U)

- **K2-G002 fail_format** — вход: curline; выход: «U-L2-WALL ERR=FORMAT
  AT=XXXX» + ExitProcess(6). Состоит из: H001, U001.
- **K2-G003 print_error** — errtab[ECX] (смещение блоба) + ExitProcess(код).
- **K2-G004 stream_args** — вход: fname_in/fname_out; выход: хэндлы,
  filebuf+NUL, srclen, textend; коды 2..5. Состоит из: C002, F001, F004.
- **K2-H001 hex16_to_4** — 4 ЗАГЛАВНЫЕ hex-цифры номера строки в [RDI].
- **K2-U001 print_line** — WriteFile(hstdout, RDX, R8D).

## Файлы (F) — реинкарнации K1-F011..F015

- **K2-F001 open_file_read / F002 create_file_write / F003 close_file /
  F004 read_whole_dst / F005 write_all** — CreateFileA/ReadFile/
  CloseHandle/WriteFile; коды 4,5,8,9.

## Разбиение строк и проход 0 (N)

- **K2-N001 line_next** — вход: RSI; выход: R14/R15 (строка без
  терминатора), RSI (за ним), curline++, RAX=1|0. Функция: разбиение
  LF/CRLF/CR как re.split оракула (терминаторов+1 записей).
- **K2-N002 pass0** — вход: filebuf/srclen; выход: sm_arr[строка]={ptr,
  len} для всех строк, lastnonempty, nlentries, nlines_v. Функция: полная
  лексика каждой строки + карта текстов. Состоит из: N001, N003.
- **K2-N003 lex_line** — вход: R14/R15; выход: sm_arr[lineidx], sm_stop.
  Функция: токены до стопа; обрезка пробелов текста строки.
- **K2-N004 set_lastline** — curline := lastnonempty (или nlentries).

## Лексер (L)

- **K2-L001 lex_tok** — вход: RCX в [R14,R15); выход: EAX kind (0 число/
  1 имя/2 символ/3 строка/4 стоп), tok_val/tok_ptr/tok_end. Функция:
  один токен: пробелы/табы сам пропускает; ';' -> стоп; числа 0..
  0x7FFFFFFF (переполнение -> G002); имена [A-Za-z_][A-Za-z0-9_]*;
  строки '...' с экранами n r t 0 \ ' (байты 0x20..0x7E); двухсимвольные
  == != <= >= << >> и && || (E6.4c-3/3: lt_and/lt_or — ветвление по
  2-му байту после односимвольных & |); односимвольные ( ) = , - + < >
  | & ^ ! и * / % (E6.4c-3/1).

## Разбор (P)

- **K2-P001 want_sym1** — следующий токен = символ RCX, поглотить.
- **K2-P002 at_end_chk** — токенов больше нет (иначе G002).
- **K2-P003 want_id** — следующий токен = имя, поглотить.
- **K2-P004 kw_lookup** — RCX/RDX (имя) -> EAX индекс kwtab | -1.
- **K2-P005 chk_name** — проверка имени (длина <= 63, [A-Za-z][A-Za-z0-9_]*,
  строчные если не ext, без ведущего '_').
- **K2-P006 names_find** — индекс ntab | -1 (побайтовое сравнение).
- **K2-P007 names_add** — запись ntab {ptr, len, вид, мета, curline}.
- **K2-P008 local_find** — вход RCX/RDX (имя); выход: RAX = базовый
  слот в окне larr[locoff..locoff+loccnt), RDX = размер записи
  (срез 4: префиксная сумма размеров — скаляры после массива
  сдвигаются), RAX = -1 — не найдено; кадр [rbp-8] — аккумулятор.
  Запись larr: {ptr, len, size} ×32 Б.
- **K2-P009 chain_count** — RCX уровень (0 адд/1 конъюнкция/2 v2:
  * / %); выход: RAX = K операций уровня до ')' на глубине 0 / ',' /
  конца строки. Функция: предварительный подсчёт для tdepth = d+K-1
  (левоассоциативность без AST). Скобки считаются глубиной (скан без
  потребления). E6.4c-3/1: сравнения (== != <= >= < >) — конец ЛЮБОЙ
  цепочки: правый операнд сравнения не считается в цепочку левого
  (дефект E6.4b, пойман экспериментом E6.4c-3/1). E6.4c-3/3: цепочки
  && / || — тоже конец ЛЮБОЙ цепочки (cc_sym2: al==26/7C -> cc_done).
  E6.4c-3/4: `[` -> cc_open, `]` -> cc_close — скобки глубины
  (индексация — постфикс первичного: содержимое прозрачно для внешней
  цепочки, `]` на глубине 0 — конец скана; подготовка среза 4b).
- **K2-P01A p_mdm (E6.4c-3/1)** — вход: RCX = d; выход: RAX = need;
  эмит: как p_expr/p_mul (chain_count ур.2; первый операнд на d+K,
  правые на tdepth+1, T-склад на tdepth, tdepth убывает; декремент
  inline в каждом хвосте операции). Операция * -> E034, / и % ->
  E035 (EAX 0/1); ставит флаг v2 [r13+18190] (заголовок «WALL v2»).
  Состоит из: P012, P009, E034, E035. Реинкарнация на WALL
  (E6.4d-4/3c-2/1): p_mdm(d) части wall_self_ph.wall (оба плеча).
- **K2-P010 p_expr** — аддитивное выражение; RCX=d; статы: RAX=need;
  эмит: код. Первый операнд на d+K, правые на tdepth+1, T-склад на
  tdepth (nbase+tdepth), tdepth убывает. Состоит из: P01A, P009, E009,
  E020. Реинкарнация на WALL (E6.4d-4/3c-2/1): p_expr(d) части
  wall_self_ph.wall — оба плеча (pc_mode 0/1; emit_tstore/emit_tload
  части wall_self_g.wall).
- **K2-P011 p_mul** — конъюнкция (& << >>); операнды через P01A
  (v2: уровень * / % ниже конъюнкции — SPEC/11 п.2). '&' -> E020,
  '<<'/'>>' -> E021 (через cl). Состоит из: P01A, P009. Реинкарнация
  на WALL (E6.4d-4/3c-2/1): p_mul(d) части wall_self_ph.wall +
  НОВЫЙ хелпер mul_peek (0 '&' / 1 '<<' / 2 '>>' / -1; оба плеча).
- **K2-P012 p_unary** — унарный '-' (глубина та же) / P013.
  Реинкарнация на WALL (E6.4d-4/3c-2/1): p_unary(d) части
  wall_self_ph.wall — эмит-плечо «M neg r10» (s_mneg 1258/9).
- **K2-P013 p_prim (срез 4b)** — обёртка: pp_prim0 (P013a) — первичное,
  затем peek `[`: pp_strchk (P01E) -> pp_pcount (P01B). k=0 — v1-выход;
  k>0 — эмит: откат r12, prim на d+k, pp_pairs (P01C); статы:
  pp_pairs(d, k, need_prim).
- **K2-P013a pp_prim0** — тело прежнего P013 (первичное без постфикса);
  фикс №19: после p_args need вызова читается из рамки [rbp-20] (RAX
  p_args), не из глобали tmp6 (затиралась вложенными).
- **K2-P01B pp_pcount (wall_pi.b2, срез 4b)** — число пар [..] в
  остатке строки; скан от pc_cur БЕЗ потребления (паттерн P009):
  '[' на глубине 0 = пара, вложенные скобки — глубина; курсор
  восстанавливается; RAX = k; k>0 ставит флаг v2 [r13+18190].
- **K2-P01C pp_pairs (wall_pi.b2, срез 4b)** — цикл пар индексации:
  RCX = d (глубина верхнего индекса), RDX = k, R8 = need базы. Пара j:
  T-склад t(cur-1) ПОСЛЕ базы (cur от d+k до d+1), индекс на cur,
  хвост канона SPEC/11 (shl r10,3 / mov r11,r10 / mov r10,[T] /
  add r10,r11 / mov r10,[r10]); статы: c = 1 + max(c, need индекса).
- **K2-P01D astore_chk (wall_pi.b2, срез 4b)** — RCX/RDX = имя: локаль
  или параметр (local_find; копия окна st_locoff/loccnt в lay — ТОЛЬКО
  в стате pc_mode == 0, в проходе 2 окно уже выставлено p2_funchdr)
  либо вид ntab 1 (var) / 5 (массив); str/func/ext/неизвестное ->
  G002. Реинкарнация (E6.4d-3/2, wall_self_pa.wall); фикс №22
  (E6.4d-4/3c-2/3): каркас копировал окно БЕЗУСЛОВНО — в проходе 2
  затирал lay прошлогонними значениями (guard вернул, как P01D).
- **K2-P01E pp_strchk (wall_pi.b2, срез 4b)** — RCX = курсор до prim:
  корень = k '(' + id (не getb/len) + k ')'; вид str -> G002; прочее
  разрешено. Счётчик k — В КАДРЕ (kw_lookup/lex_tok затирают r8/r9/rdi).
- **K2-P014 p_args (фикс №19 + №21)** — аргументы до ')' включительно.
  Рамка: d/base/cnt/mx/eflg/need — ЛОКАЛЬНЫ (вложенные вызовы не
  затирают объемлющий). Глобальные: pc_cact (вход: base :=
  pc_staged при pc_cact>0, иначе 0), pc_staged — **base+staged**
  самого внутреннего АКТИВНОГО вызова (ДЕФЕКТ №21: до фикса —
  только счёт без базы; теперь вход := base, на аргумент :=
  base+cnt), pc_argcnt/pc_cbase — интерфейс для P015/P016. Выход:
  RAX = max need аргументов (потребляется P013a/S00D). Каждый
  аргумент -> P017 (base, cnt, eflg) — и в стате, и в эмите.
- **K2-P015 p_call_tail (№19)** — RCX want; имя (RDX,R8): func (арность
  из ftab, загрузки ARGREG[i] из C-слотов **C(pc_cbase+i)**, call $имя) /
  ext (<= 5, 5-й из S5 -> [rsp+20], call [rip+$_iat_имя]); want ->
  mov r10, rax.
- **K2-P016 call_stats (№19)** — maxc = max(maxc, **pc_cbase +**
  n | pc_cbase + min(n,4)) — одновременное использование C-слотов
  объемлющего и вложенного вызовов; ext5.
- **K2-P017 pa_stage (№19)** — эмит стейджинга одного аргумента: вход
  RCX = base, RDX = cnt (до инкремента), R8 = extflg; слот =
  C(base+cnt+1) — SPEC/11 п.5/8; 5-й аргумент ext -> S5 (фиксированный);
  стат-режим не эмитит (счёт — в рамке P014; было: tmp5++/tmp6 в
  глобали — вложенные вызовы затирали их).
- **K2-P018 p_cond** — условие if/while — цепочки `&&` / `||` (v2,
  срез 3). Вход (проход 2): RCX = pfx (0=if, 1=while), RDX = e
  (суффикс lfalse), R8 = k (сквозной счётчик if/while); в проходе 1
  параметры не задаются. Разбор: дизъюнкты по `||`, внутри — сравнения
  по `&&`; операнды на глубине 2, T1-склад, cmp r10, r11. Предподсчёт
  m — числа `||` в строке (pcd_scan, скан без потребления, только в
  режиме эмитции). Статы (проход 1): maxd = max(maxd, 1+max(need_l,
  need_r)) КАЖДОГО сравнения; флаг v2 [r13+18190] при первом && / ||.
  Эмит (проход 2, guard SPEC/11 п.8): каждое сравнение — j<инв> на
  lfail (последний дизъюнкт — E029; иначе d<i+1> — E036); после
  дизъюнкта i<m — «M jmp $<pfx><k>t» (E037) + метка d<i+1> (E038);
  при m>1 — финальная метка t (E038, nlab++); m=1 — без d/t-меток и
  jmp: выход байт-в-байт как v1. Состоит из: P010, E003, E005, E009,
  E029, E036, E037, E038. Используется в: S009, S00A, Y006, Y007.
  Реинкарнация на WALL (E6.4d-3/3): p_cond части
  KERNEL/L2-WALL/wall_self_pc.wall — ТОЛЬКО стат-плечо (проход 1):
  цикл сравнений (левый p_expr(2), оператор, правый p_expr(2), maxd =
  max+1 на каждое), '&&' / '||' — потребление + v2flag + следующее
  сравнение; m-скан, инверсия jcc и guard-эмиттеры — проход 2
  (E6.4d-4+); курсор pcur/ple; maxd — max2 порознь (вложенные вызовы
  в аргументах wall.exe не разбирает — дефект №19).
- **K2-P019 arr_size (E6.4c-3/4)** — вход: pc_cur после имени
  объявления; выход: RAX = размер (1..1000hex = 4096; 1 = скобок
  нет), RDX = 1 если `[n]` присутствовал, иначе 0; потребляет
  `[` число `]`; диапазон 1..4096; ставит флаг v2 [r13+18190].
  Ошибки (не число / вне диапазона / нет `]`) -> G002 (строка
  объявления — как у оракула _array_size). Используется в: S003,
  S006. Состоит из: L001, P001, G002.

## Проход 1 — статы (S)

- **K2-S001 pass1** — сброс таблиц; цикл строк; пост-проверки:
  незакрытый блок (set_lastline), ровно одна main без параметров.
- **K2-S002 p1_line** — диспетчер: kw -> объявления (до func) или
  утверждения (в теле); func -> S004; имя -> S00D; break/continue
  (kw 0C/0D) -> S00F (E6.4c-3/2); иначе G002.
- **K2-S003 p1_decl** — var/str/ext: chk_name, дубликаты (ext —
  регистронезависимо, S005), литерал <= 512 (str_dlen), ext <= 8;
  заполнение ntab/varr/sarr/earr. Срез 4 (E6.4c-3/4): var — разбор
  опционального [n] (P019) до at_end_chk (порядок проверок — как
  оракула); при [n] вид ntab = 5 (массив), varr-запись ×16 Б
  {ntab_idx, size} (скаляр — size 1; глобальный [1] — массив:
  lea rip, присваивание запрещено — квирк оракула).
- **K2-S004 p1_funchdr** — имя, параметры <= 4 (S00E, окно дублей —
  от locoff ЗАХВАЧЕННОГО ДО параметров), ftab-запись (×80 Б — срез 4:
  +0x48 nslots = 0, заполняет S007), сброс st_* (срез 4:
  st_nslots := nparams), push {func}; seen_func1/infunc1.
- **K2-S005 names_find_ci** — поиск без учёта регистра (для ext).
- **K2-S006 p1s_var** — локаль: разбор опционального [n] (P019,
  срез 4) до at_end_chk; дубликаты в окне/глобальных; larr+
  (×32 Б: {ptr, len, size}), st_loccnt++, st_nslots += size
  (локальный [1] — скаляр для присваивания/len: квирк оракула).
  Реинкарнация на WALL (E6.4d-3/1): p1s_var части
  KERNEL/L2-WALL/wall_self_p1s.wall — окно дублей
  [st_locoff, st_locoff+st_loccnt) побайтовым сравнением larr
  (как fh_param), larr/bstk/ftab — в куче tabmem со смещениями;
  диспетчер p1_line части wall_self_p1.wall — плечо var
  (kw==0, раньше end — порядок wall.exe).
- **K2-S007 p1s_end** — pop bstk; func -> финализация ftab (maxd/maxc/
  flags/loccnt; срез 4: + nslots в +0x48), infunc1=0; лишний end ->
  G002.
- **K2-S008 p1s_else** — верхний блок if? -> kind=else, ifarr[seq]=1
  (флаг непустого else). Реинкарнация на WALL (E6.4d-3/3): p1s_else
  части wall_self_p1s.wall — at_end; fdepth==0 или верхняя запись
  bstk не kind 2 — ERR=FORMAT; запись мутируется на месте (kind 3),
  ifarr — окно tabmem+4685888.
- **K2-S009 p1s_if** — p_cond (статы), ifseq1++, ifarr[seq]=0,
  push {if, 0, seq}. Реинкарнация на WALL (E6.4d-3/3): p1s_if части
  wall_self_p1s.wall — p_cond (wall_self_pc) + at_end + ifseq++ +
  ifarr[ifseq]=0 + push bstk {2, 0, ifseq} + fdepth++ (lineidx не
  пишется — как wall.exe); сброс ifseq — pass1 (wall_self_p1).
- **K2-S00A p1s_while** — p_cond (статы), push {while, 0, 0}.
  Реинкарнация на WALL (E6.4d-3/3): p1s_while части
  wall_self_p1s.wall — p_cond + at_end + push bstk {4, 0, 0} +
  fdepth++.
- **K2-S00B p1s_return** — [выражение] -> статы maxd. Реинкарнация
  на WALL (E6.4d-3/2): p1s_return части wall_self_p1s.wall —
  выражение есть -> p_expr(1) (уровни — wall_self_ph) + maxd,
  иначе сразу at_end (плечо p1r_noexpr wall.exe).
- **K2-S00C p1s_setb** — три выражения (статы), st_setb=1.
  Реинкарнация на WALL (E6.4d-3/2): p1s_setb части
  wall_self_p1s.wall — '(' выр ',' выр ',' выр ')' + at_end +
  st_setb=1; maxd — max2 после каждого p_expr(1).
- **K2-S00D p1_namestmt** — вызов-утверждение (P014+P016; фикс №19,
  E6.4d-4/2: need вызова (RAX p_args) -> st_maxd, как у присваивания —
  зеркалит _scan оракула; до фикса maxd call-утверждений не считался ни
  у кого — T-слот налезал на C-слот: f(y, 1+2) отправлял в f «1» вместо
  y), присваивание (статы maxd) или astore (срез 4b: после имени '[' ->
  pp_pcount -> astore_chk -> база (k=1: need 0; k>1: pp_prim0(k) +
  pp_pairs(1, k-1)) -> пара/значение через p_expr(1) -> maxd = max
  трёх need -> st_setb=1 (S-слоты)). Реинкарнация на WALL
  (E6.4d-3/2): p1_namestmt части wall_self_p1s.wall — имя в
  tokptr/tokend ДО потребления; peek '(' -> p_args(1)+call_stats
  (wall_self_pa) + at_end; фикс №19 (E6.4d-4/2): mx = p_args(1) ->
  st_maxd = max2(st_maxd, mx) (локаль рамки); peek '[' -> astore (pp_pcount/
  astore_chk/база-цепочка — wall_self_pp/pa; maxd — max2 порознь);
  иначе '=' p_expr(1) + at_end; в стат-режиме st_maxd — max2
  (порядок обновлений не наблюдаем).
- **K2-S00E fh_param** — параметр: chk_name, дубликат в окне/глобальных,
  larr+ (×32 Б: {ptr, len, size=1} — срез 4).
- **K2-S00F p1s_brk (E6.4c-3/2)** — вход: kw break/continue (0C/0D;
  одна точка входа — поведение прохода 1 идентично); выход: OK/G002.
  Функция: поглотить слово, at_end_chk, скан bstk до ближайшей
  записи kind=4 (while) — иначе fail_format «вне while»; ставит флаг
  v2 (заголовок «WALL v2»); статистика кадров не меняется.
  Состоит из: P002, G002.

## Проход 2 — эмитция (Y)

- **K2-Y001 pass2** — сброс; emit_header/imports/entry; цикл строк;
  секции данных (E027/E028); предел меток выхода nlab ≤ 2000
  (строка 0; E6.4d-3/3-1: 500 -> 2000, cmp rax,7D0; ёмкость brick
  2048 вкл. base -> запас 48; граница 2000/2001 — T-E6-50).
  СРЕЗЫ A+B+C-1 НА WALL ВЫПОЛНЕНЫ (E6.4d-4/3a..3c-1): pass2 части
  wall_self_y.wall — сброс + пролог + ЦИКЛ СТРОК по smem + СЕКЦИИ
  ДАННЫХ (заголовки при непустой секции + emit_strdata/emit_globdata
  части wall_self_d.wall; после цикла, до предела nlab) + предел nlab. НОВЫЕ кирпичи
  каркаса: blob_dec/init_blob (часть wall_self_e.wall; кириллица
  канона невыразима в str-литерале SPEC/11 п.2), глобали состояния
  st_bcnt/st_fbase/st_infunc/st_lret/st_ifcnt/st_fptr/st_flen и
  cmt_ptr/cmt_len (аналоги 18158/18180/18178/18110/18100/181B0/
  181B8/181A0/181A8; сброс/установка — как wall.exe).
- **K2-Y002 p2_line** — карта текстов -> srctxt; диспетчер как S002
  (break/continue -> Y00C). Реинкарнация (E6.4d-4/3b..3c-2/3):
  p2_line(pos, le) части wall_self_y.wall — цикл строк по smem;
  kw-плечи — форма wall.exe (func раньше «в функции»; вне функции —
  пропуск; не-имя — fail_format); cmt_ptr/cmt_len = pos/le-pos на
  входе — читают emit_cmt и секции данных; C-2/3: kwi == 9 ->
  p2s_setb, цепочка имён -> p2_namestmt (как p2l_name Y002), 12/13
  (break/continue) — пропуск до C-3.
- **K2-Y003 p2s_var** — верхний уровень: last_ret=0 (строка не эмитится).
  СРЕЗ B НА WALL ВЫПОЛНЕН (E6.4d-4/3b): p2s_var части
  wall_self_y.wall — if st_bcnt == st_fbase+1: st_lret = 0.
- **K2-Y004 p2s_end** — pop: func -> эпилог (если !last_ret); while ->
  jmp $_w<k> (E02A, srctxt из строки while) + :_w<ke> (E02C); if/else ->
  :_if<ke> (E02B). СРЕЗ B НА WALL ВЫПОЛНЕН ЧАСТИЧНО (E6.4d-4/3b):
  p2s_end части wall_self_y.wall — pop bstk (st_bcnt), kind 1:
  emit_epilogue (если не st_lret) + сброс st_infunc/st_lret;
  while/if/else-метки — срез C.
- **K2-Y005 p2s_else** — pop {if}: ifarr[seq]? -> jmp $_if<ke> (E02A,
  srctxt из строки if) + :_if<k>; push {else, k, seq}.
  МЕХАНИКА НА WALL ВЫПОЛНЕНА (E6.4d-4/3b): p2s_else части
  wall_self_y.wall — мутация kind 2 -> 3 на месте (k/seq
  сохраняются); эмитция jmp/iflab — срез C.
- **K2-Y006 p2s_if** — kctr++, ifseq2++ -> seq; e = ifarr[seq]
  (чтение ДО p_cond — ifarr стабилен после pass 1); p_cond(0, e, k)
  — guard внутри (E6.4c-3/3); at_end_chk; push {if, k, seq, lineidx};
  last_ret=0. МЕХАНИКА НА WALL ВЫПОЛНЕНА (E6.4d-4/3b): p2s_if
  части wall_self_y.wall — ifseq/st_ifcnt++, push bstk {2, k,
  ifseq, curline} (ifarr читает срез C); last_ret-правило.
- **K2-Y007 p2s_while** — kctr++; :_w<k> (E02C); p_cond(1, 1, k) —
  guard внутри (E6.4c-3/3; lfalse = _w<ke>); at_end_chk; push {while,
  k, 0, lineidx}; last_ret=0. МЕХАНИКА НА WALL ВЫПОЛНЕНА
  (E6.4d-4/3b): p2s_while части wall_self_y.wall — st_ifcnt++,
  push {4, k, 0, curline}; :_w<k> + guard — срез C.
- **K2-Y008 p2s_return** — [выражение] -> mov rax, r10; эпилог (E019);
  верхний уровень: last_ret=1. СРЕЗ B НА WALL ВЫПОЛНЕН ЧАСТИЧНО
  (E6.4d-4/3b): p2s_return части wall_self_y.wall — emit_epilogue
  сразу (и для голого, и после выражения); эмитция «M mov r10 /
  M mov rax, r10» — срез C; верхний уровень — st_lret = 1.
- **K2-Y009 p2s_setb** — три выражения -> S0/S1/S2 (E02D); mov r10/r11/
  al из S-слотов; mov [r10+r11], al; last_ret=0. Реинкарнация (C-2/3,
  wall_self_t.wall): p2s_setb(pos, le) — pcur/ple, три p_expr(1) +
  emit_sstore(0..2) + хвост 4 строки блоба; верхний уровень —
  st_lret = 0.
- **K2-Y00A p2_funchdr** — ftab (×80 Б) -> lay_*; nbase [180C0] :=
  ftab+0x48 nslots, loccnt [180F8] — окно local_find; пролог E018;
  push {func}; last_ret=0. Реинкарнация (E6.4d-4/3b..3c-2/1):
  p2_funchdr части wall_self_y.wall — имя -> ntab мета = fidx; curf;
  st_fptr/st_flen; st_p2maxd/maxc/nbase + lay-окна из ftab;
  emit_prologue; push bstk {1, 0, 0}.
- **K2-Y00B p2_namestmt** — вызов (P014+P015, want=0), присваивание
  (локаль -> mov [rbp-X], r10; var -> mov [rip+$имя], r10; массив —
  G002) или astore (срез 4b: '[' -> pp_pcount -> astore_chk; база —
  emit_load / цепочка pp_prim0(k)+pp_pairs(1,k-1); затем emit_sstore
  S0/S1/S2 вокруг пары/значения и хвост mov r10,[S0] / mov r11,[S1] /
  shl r11,3 / add r10,r11 / mov r11,[S2] / mov [r10],r11).
  Реинкарнация (C-2/3, wall_self_t.wall): p2_namestmt(pos, le) — имя
  в tokptr/tokend; peek '(' — pc_extflg по виду ntab + p_args(1) +
  p_call_tail(0, iptr, ilen); '[' — astore (выше); иначе '=' p_expr(1)
  + local_find (lf_size > 1 — G002) / names_find вид 1 (var); цель
  валидируется ЗДЕСЬ (проход 1 цель не проверяет — как wall.exe);
  верхний уровень — st_lret = 0.
- **K2-Y00C p2s_break/p2s_continue (E6.4c-3/2)** — вход: ключевое слово
  (kw 0C — точка входа p2s_break, 0D — p2s_continue; e-флаг: 1/0 в EDX
  -> R11 — скретч, переживает скан); выход: «M jmp $_w<ke>» (break) /
  «M jmp $_w<k>» (continue) + комментарий emit_cmt (текст строки).
  Функция: скан bstk до ближайшей записи kind=4, k = поле +8,
  emit_jmp_line (E02A, форма while); путь «вне while» — int3
  (недостижимо: pass 1 уже отверг). Состоит из: E02A. Используется в:
  Y002. Канон — SPEC/11 п.8 (формы v2).

## Эмиттеры (E)

- **K2-E001..E004 out_ch/out_copy/out_str/out_line** — байт; (RDX,R8);
  запись strtab2[RCX]; +LF. Реинкарнация (E6.4d-4/3a, wall_self_e.wall):
  курсор — глобаль outcur (setb в outbuf); out_str(off,n) — смещение
  в блобе sblob (outmem+0), не индекс strtab2 (таблица индексов
  каркасу не нужна; смещения — в wall_self_blob.wall).
- **K2-E005/E006 out_hex/out_hex2** — ЗАГЛАВНЫЙ hex без ведущих нулей /
  2 цифры. Реинкарнация (E6.4d-4/3a): out_hex — ЛОКАЛЬНЫЙ buf[16];
  hex2 — вложенный getb в аргументе out_ch (корректен с №19).
- **K2-E007 div10** — RAX/10 -> RAX, RDX (бит за битом, маска `and r9,1`).
  НЕ реинкарнирован: E6.4d-4/3a out_dec каркаса использует операторы
  / и % (idiv в ISA с E6.4c) — цифры те же, код проще.
- **K2-E008 out_dec** — десятичное. Реинкарнация (E6.4d-4/3a):
  wall_self_e.wall — buf[20] + v%10/v/10 (idiv с E6.4c).
- **K2-E009 emit_cmt** — « ; » + srctxt + LF. Реинкарнация (3c-1):
  wall_self_e.wall — out_str(25,3) + out_copy(srcbuf+cmt_ptr,
  cmt_len); srctxt — глобали cmt_ptr/cmt_len (181A0/A8).
- **K2-E010 emit_kadr/emit_vyhod** — « ; кадр/выход имя». Реинкарнация
  (3b, wall_self_f.wall): out_str блоба + out_copy(srcbuf+st_fptr,
  st_flen) (аналог 181B0/B8).
- **K2-E011 emit_lab** — «:имя» + LF; nlab++. Реинкарнация (3b):
  wall_self_f.wall — out_ch(58) + out_copy + LF (nlab++ —
  в emit_prologue).
- **K2-E012 lower_copy** — имя -> scr (нижний регистр); RAX = длина.
  Реинкарнация (3a): lower_copy(dst,a,n) — dst параметр (scr =
  outmem+2048).
- **K2-E013 str_dlen** — длина литерала с учётом экранов.
  Реинкарнация (3c-1): проверка <= 512 не дублируется (проход 0).
- **K2-E014 str_emit** — литерал -> «DB xx .. xx» <= 16 байт (экраны ->
  байты; фикс №16: буфер НЕ пересекается с локальными). Реинкарнация
  (3c-1, wall_self_e.wall): str_emit + se_doline(buf,k) + esc_code —
  буфер ЛОКАЛЬНЫЙ buf[16] (дефект №16 невозможен конструктивно).
- **K2-E015 emit_header** — 2 строки заголовка; v1/v2 по флагу
  [r13+18190] (E6.4c-3/1). Реинкарнация (3a, wall_self_y.wall):
  v2flag глобаль, счётчики nlines/fcount/ecount/scount/vcount.
- **K2-E016 emit_entry** — «; --- код ---» + :_entry + 3 M-строки входа.
  Реинкарнация на WALL (E6.4d-4/3a): части wall_self_y.wall.
- **K2-E017 calc_framesize** — ftab -> align16(8*nslots)+0x30; nslots
  = nbase+maxd+maxc+S (setb/astore ×3, ext5). Реинкарнация (3b,
  wall_self_f.wall): ftab[curf] напрямую (maxd +24 / maxc +32 /
  nslots +72 / флаги +40); align16 — (v+15)/16*16.
- **K2-E018 emit_prologue** — :имя, push/mov/sub rsp; параметры mov
  [rbp-8*(i+1)], ARGREG[i]. Реинкарнация (3b, wall_self_f.wall):
  ARGREG — if-цепочка по блобу (s_rcx/s_rdx/s_r8/s_r9), argtab не
  нужен; nlab++ за :имя.
- **K2-E019 emit_epilogue** — mov rsp,rbp / pop rbp / ret (+vyhod).
  Реинкарнация (3b): s_mrsp/s_mpop/s_mret + emit_vyhod.
- **K2-E020 emit_alu** — байт операции -> «M add/sub/and/or/xor r10,
  r11» (alutab). Реинкарнация (C-2/1, wall_self_g.wall): if-цепочка
  по байту (43/45/38/124/94), alutab не нужна.
- **K2-E021 emit_shift** — «M mov rcx, r11» + «M shl/shr r10, cl».
  Реинкарнация (C-2/1): emit_shift(dir), s_mrcxr11/s_shl/s_shr/s_shcl.
- **K2-E034 emit_imul (E6.4c-3/1)** — «M imul r10, r11» (v2 '*').
  Реинкарнация (C-2/1): s_mimul 1856/15.
- **K2-E035 emit_divmod (E6.4c-3/1)** — EAX = 0 '/' / 1 '%': mov
  rax,r10 / cqo / idiv r11 / mov r10,rax|rdx. Реинкарнация (C-2/1):
  emit_divmod(m), wall_self_g.wall.
- **K2-E022 emit_addr** — &имя: локаль -> lea r10,[rbp-8*(база+
  размер)]; var/str/массив -> lea r10,[rip+$имя]; иначе G002.
  Реинкарнация (C-2/1): emit_addr(iptr, ilen) (размер — lf_size
  от local_find).
- **K2-E023 emit_len** — len(имя): срез 4 — сначала local_find
  (локальный массив -> константа размера; локальный скаляр -> G002,
  как оракул); затем str_dlen -> «M mov r10, hex»; глобальный
  массив (вид 5) -> размер из varr. Реинкарнация на WALL
  (E6.4d-4/3c-2/1): emit_len(iptr, ilen) части wall_self_g.wall
  (sarr +1835008 x24 / varr +1310720 x16 — конвенция каркаса).
- **K2-E024 emit_load** — имя: локаль -> mov r10,[rbp-X]; var ->
  mov r10,[rip+$имя]; str -> lea r10,[rip+$имя]; func/ext -> G002.
  Срез 4: локальный массив (размер > 1) -> lea r10,[rbp-arrbase]
  (адрес a[0]); глобальный вид 5 -> lea r10,[rip+$имя] (как str).
  Реинкарнация на WALL (E6.4d-4/3c-2/1): emit_load(iptr, ilen)
  части wall_self_g.wall.
- **K2-E025 get_ext** — earr[i] -> (RDX,R8) имя + scr + RAX длина.
  Реинкарнация на WALL (E6.4d-4/3a): get_ext(i) части
  wall_self_e.wall — оригинал в глобалях ext_nptr/ext_nlen
  (ntab.ptr — СМЕЩЕНИЕ в srcbuf, конвенция таблиц каркаса),
  lowercase-копия — в scrbuf; вернуть длину.
- **K2-E026 emit_imports** — фиксированная область 0x200 (SPEC/11 п.6):
  idt/iat/intt/dll/hints (счётчик байта в кадре — r9/rax затираются
  вызовами!), DZ 148/2A. Реинкарнация на WALL (E6.4d-4/3a): части
  wall_self_y.wall — циклы по ecount/8/9/34 с локальными i/j/n.
- **K2-E027 emit_strdata** — секция строк: :имя, DZ 0 / DB-строки.
  Реинкарнация на WALL (E6.4d-4/3c-1): часть wall_self_d.wall —
  sarr[i] -> ntab (имя, строка объявления) -> set_cmt + emit_lab +
  nlab++ -> пустая ? «DZ 0» + emit_cmt : str_emit; заголовок — pass2
  (s_secstr, при scount > 0).
- **K2-E028 emit_globdata** — секция глобальных var: :имя, DZ 8n
  (срез 4: префикс «DZ » прямым байтом + out_hex(8*size) из varr;
  скаляр — «DZ 8» байт-в-байт).
  Реинкарнация на WALL (E6.4d-4/3c-1): часть wall_self_d.wall —
  varr[i] (ntab, размер n) -> set_cmt + emit_lab + nlab++ + «DZ » +
  out_hex(8*n) + emit_cmt; заголовок — pass2 (s_secglob, при
  vcount > 0).
- **K2-E029 emit_jcc_line** — RCX jcc, RDX e, R8 k, R9 while ->
  «M <jcc> $_if|_w<k>[e] ; текст» (jcctab — смещения блоба).
  Используется в: P018 (последний дизъюнкт guard — E6.4c-3/3).
- **K2-E02A emit_jmp_line** — «M jmp $_if|_w<k>[e]».
- **K2-E02B emit_iflab / E02C emit_wlab** — «:_if<k>[e]»/«:_w<k>[e]».
- **K2-E02D emit_sstore** — стейджинг S-слота i: «M mov [rbp-X], r10»,
  X = 8*(nbase+maxd+maxc+i+1) — s(i) SPEC/11 п.5. Реинкарнация
  (C-2/3, wall_self_t.wall): emit_sstore(i) — строки блоба
  s_movm/s_r10 + X из st_p2nbase/maxd/maxc.
- **K2-E036 emit_jccd (E6.4c-3/3)** — вход: RCX = индекс jcc (0..5,
  jcctab), RDX = pfx (0=if/1=while), R8 = k, R9 = i (>= 2); выход:
  «M <mnem> $<pfx><k>d<i> ; текст» — jcc на d-метку guard-цепочки
  (сравнение не последнего дизъюнкта). Часть wall_pg.b2. Используется
  в: P018.
- **K2-E037 emit_jmpt (E6.4c-3/3)** — вход: RCX = pfx, RDX = k; выход:
  «M jmp $<pfx><k>t ; текст» — успех дизъюнкта -> тело (short-circuit).
  Используется в: P018.
- **K2-E038 emit_glab (E6.4c-3/3)** — вход: RCX = pfx, RDX = k,
  R8 = i (0 -> t-метка, >= 2 -> d-метка); выход: «:<pfx><k>d<i>» /
  «:<pfx><k>t» + nlab++ (предел меток выхода 2000 — E6.4d-3/3-1:
  было 500). Используется в: P018.

## Данные (D)

- **K2-D001 digits** — 16 hex-цифр. **K2-D002 kwtab** — 14 ключевых
  слов (E6.4c-3/2: +break/+continue в конец, индексы 0C/0D).
- **K2-D003 jcctab / D004 alutab / D005 argtab** — {смещ, длина} (блоб).
- **K2-D006 errtab** — 7 записей ошибок. **K2-D007 strblob** — 113 строк
  канона (байт-точные из оракула; E6.4c-3/1: +imul/cqo/idiv,
  mov r10,rdx, заголовок v2). **K2-D008 strtab2** — индексная
  таблица (экономия меток: 499 вместо 660+).
- **K2-D010 импорты** — kernel32 (7), hint-записи на чётных RVA (калибровка DZ 2 после
  dll_name — прецедент E4a/E6.4c-1).
- **K2-D011 bss** — единая область :scalars DBZ 7A1418 (bstk +
  скаляры + ВСЕ буферы, база R13). E6.4c-3/1: 14 меток буферов
  (fname_in..outbuf) заменены смещениями r13+X — предел меток
  brick 512 (освобождено 14 записей labtab). Флаг v2 — [r13+18190].
  Срез 4 (E6.4c-3/4): st_nslots — [r13+180D8] (бывший lay_setb,
  свободен с E6.4b); записи таблиц выросли, ПЛОЩАДИ областей
  прежние (смещения буферов живы): ftab ×80 Б (0x120000 = 15564
  функций), larr ×32 Б (0x100000 = 32768 записей), varr ×16 Б
  (0x40000 = 16384 глобальных).
