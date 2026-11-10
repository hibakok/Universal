# M2-WALL — карточки кирпичей компилятора WALL v1/v2 (71)

Паспорт файла: MAP/M2-WALL.md | слой: L2 | роль: реестр кирпичей M2-WALL.
Формат карточки — SPEC/01-METHOD-CARD.md; указатель — MAP/METHODS.md.
С E6.4c-3/1 инструмент поддерживает v2-подмножество: операторы `* / %`
(уровень p_mdm между конъюнкцией и унарным) + заголовок «WALL v1/v2»;
с E6.4c-3/2 — `break`/`continue` (только в while; kwtab 14; bstk 3072x32
— дефект №15).

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
  == != <= >= << >>; односимвольные ( ) = , - + < > | & ^ !
  и * / % (E6.4c-3/1).

## Разбор (P)

- **K2-P001 want_sym1** — следующий токен = символ RCX, поглотить.
- **K2-P002 at_end_chk** — токенов больше нет (иначе G002).
- **K2-P003 want_id** — следующий токен = имя, поглотить.
- **K2-P004 kw_lookup** — RCX/RDX (имя) -> EAX индекс kwtab | -1.
- **K2-P005 chk_name** — проверка имени (длина <= 63, [A-Za-z][A-Za-z0-9_]*,
  строчные если не ext, без ведущего '_').
- **K2-P006 names_find** — индекс ntab | -1 (побайтовое сравнение).
- **K2-P007 names_add** — запись ntab {ptr, len, вид, мета, curline}.
- **K2-P008 local_find** — индекс в окне larr[locoff..locoff+loccnt).
- **K2-P009 chain_count** — RCX уровень (0 адд/1 конъюнкция/2 v2:
  * / %); выход: RAX = K операций уровня до ')' на глубине 0 / ',' /
  конца строки. Функция: предварительный подсчёт для tdepth = d+K-1
  (левоассоциативность без AST). Скобки считаются глубиной (скан без
  потребления). E6.4c-3/1: сравнения (== != <= >= < >) — конец ЛЮБОЙ
  цепочки: правый операнд сравнения не считается в цепочку левого
  (дефект E6.4b, пойман экспериментом E6.4c-3/1).
- **K2-P01A p_mdm (E6.4c-3/1)** — вход: RCX = d; выход: RAX = need;
  эмит: как p_expr/p_mul (chain_count ур.2; первый операнд на d+K,
  правые на tdepth+1, T-склад на tdepth, tdepth убывает; декремент
  inline в каждом хвосте операции). Операция * -> E034, / и % ->
  E035 (EAX 0/1); ставит флаг v2 [r13+18190] (заголовок «WALL v2»).
  Состоит из: P012, P009, E034, E035.
- **K2-P010 p_expr** — аддитивное выражение; RCX=d; статы: RAX=need;
  эмит: код. Первый операнд на d+K, правые на tdepth+1, T-склад на
  tdepth (nbase+tdepth), tdepth убывает. Состоит из: P01A, P009, E009,
  E020.
- **K2-P011 p_mul** — конъюнкция (& << >>); операнды через P01A
  (v2: уровень * / % ниже конъюнкции — SPEC/11 п.2). '&' -> E020,
  '<<'/'>>' -> E021 (через cl). Состоит из: P01A, P009.
- **K2-P012 p_unary** — унарный '-' (глубина та же) / P013.
- **K2-P013 p_prim** — первичное: число (E024: mov r10,hex); имя ->
  E024 (локаль/[rip+$var]/lea str); &имя -> E022; len(имя) -> E023
  (str_dlen); getb(a,i) (T-склад, movzx r10d, byte [r10+r11]);
  (выражение) — прозрачные скобки; имя( — вызов (P014+P015).
- **K2-P014 p_args** — аргументы до ')' включительно; tmp5 = число,
  tmp6 = max need; каждый аргумент -> P017.
- **K2-P015 p_call_tail** — RCX want; имя (RDX,R8): func (арность из
  ftab, загрузки ARGREG[i] из C-слотов, call $имя) / ext (<= 5, 5-й из
  S5 -> [rsp+20], call [rip+$_iat_имя]); want -> mov r10, rax.
- **K2-P016 call_stats** — maxc = max(maxc, n|min(n,4)), ext5.
- **K2-P017 pa_stage** — стейджинг аргумента в C-слот c(i) / S5 (ext,
  5-й); tmp5++; tmp6 = max(tmp6, need).
- **K2-P018 p_cond** — условие: операнды на глубине 2, T1-склад,
  cmp r10, r11; выход: EAX индекс инверсии jcc (0..5: jne je jge jg jle
  jl); статы: maxd = max(maxd, 1+max(need)).

## Проход 1 — статы (S)

- **K2-S001 pass1** — сброс таблиц; цикл строк; пост-проверки:
  незакрытый блок (set_lastline), ровно одна main без параметров.
- **K2-S002 p1_line** — диспетчер: kw -> объявления (до func) или
  утверждения (в теле); func -> S004; имя -> S00D; break/continue
  (kw 0C/0D) -> S00F (E6.4c-3/2); иначе G002.
- **K2-S003 p1_decl** — var/str/ext: chk_name, дубликаты (ext —
  регистронезависимо, S005), литерал <= 512 (str_dlen), ext <= 8;
  заполнение ntab/varr/sarr/earr.
- **K2-S004 p1_funchdr** — имя, параметры <= 4 (S00E, окно дублей —
  от locoff ЗАХВАЧЕННОГО ДО параметров), ftab-запись, сброс st_*,
  push {func}; seen_func1/infunc1.
- **K2-S005 names_find_ci** — поиск без учёта регистра (для ext).
- **K2-S006 p1s_var** — локаль: дубликаты в окне/глобальных; larr+,
  st_loccnt++.
- **K2-S007 p1s_end** — pop bstk; func -> финализация ftab (maxd/maxc/
  flags/loccnt), infunc1=0; лишний end -> G002.
- **K2-S008 p1s_else** — верхний блок if? -> kind=else, ifarr[seq]=1
  (флаг непустого else).
- **K2-S009 p1s_if** — p_cond (статы), ifseq1++, ifarr[seq]=0,
  push {if, 0, seq}.
- **K2-S00A p1s_while** — p_cond (статы), push {while, 0, 0}.
- **K2-S00B p1s_return** — [выражение] -> статы maxd.
- **K2-S00C p1s_setb** — три выражения (статы), st_setb=1.
- **K2-S00D p1_namestmt** — вызов-утверждение (P014+P016) или
  присваивание (статы maxd).
- **K2-S00E fh_param** — параметр: chk_name, дубликат в окне/глобальных,
  larr+.
- **K2-S00F p1s_brk (E6.4c-3/2)** — вход: ключевое слово break/continue
  (kw-индекс 0C/0D из S002; одна точка входа — поведение прохода 1
  идентично); выход: OK или G002. Функция: поглотить слово, at_end_chk
  (хвост «break 1» — ошибка строки), скан bstk сверху вниз до ближайшей
  записи kind=4 (while) — иначе fail_format «вне while» (ERRORS2:
  строки 2/2/3); ставит флаг v2 [r13+18190] (заголовок «WALL v2»);
  статистика кадров не меняется. Состоит из: P002, G002.

## Проход 2 — эмитция (Y)

- **K2-Y001 pass2** — сброс; emit_header/imports/entry; цикл строк;
  секции данных (E027/E028); предел меток 500 (строка 0).
- **K2-Y002 p2_line** — карта текстов -> srctxt; диспетчер как S002
  (break/continue -> Y00C, E6.4c-3/2).
- **K2-Y003 p2s_var** — верхний уровень: last_ret=0 (строка не эмитится).
- **K2-Y004 p2s_end** — pop: func -> эпилог (если !last_ret); while ->
  jmp $_w<k> (E02A, srctxt из строки while) + :_w<ke> (E02C); if/else ->
  :_if<ke> (E02B).
- **K2-Y005 p2s_else** — pop {if}: ifarr[seq]? -> jmp $_if<ke> (E02A,
  srctxt из строки if) + :_if<k>; push {else, k, seq}.
- **K2-Y006 p2s_if** — kctr++; p_cond (эмит); ifarr[seq]? jcc $_if<k> :
  jcc $_if<ke> (E029, r9=0); push {if, k, seq, lineidx}; last_ret=0.
- **K2-Y007 p2s_while** — kctr++; :_w<k> (E02C); p_cond (эмит); jcc
  $_w<ke> (E029, r9=1); push {while, k, 0, lineidx}; last_ret=0.
- **K2-Y008 p2s_return** — [выражение] -> mov rax, r10; эпилог (E019);
  верхний уровень: last_ret=1.
- **K2-Y009 p2s_setb** — три выражения -> S0/S1/S2 (E02D); mov r10/r11/
  al из S-слотов; mov [r10+r11], al; last_ret=0.
- **K2-Y00A p2_funchdr** — ftab -> lay_*; пролог E018; push {func};
  last_ret=0.
- **K2-Y00B p2_namestmt** — вызов (P014+P015, want=0) или
  присваивание: локаль -> mov [rbp-X], r10; var -> mov [rip+$имя], r10.
- **K2-Y00C p2s_break/p2s_continue (E6.4c-3/2)** — вход: ключевое слово
  (kw 0C — точка входа p2s_break, 0D — p2s_continue; e-флаг: 1/0 в EDX
  -> R11 — скретч, переживает скан); выход: «M jmp $_w<ke>» (break) /
  «M jmp $_w<k>» (continue) + комментарий emit_cmt (текст строки).
  Функция: скан bstk до ближайшей записи kind=4, k = поле +8,
  emit_jmp_line (E02A, форма while); путь «вне while» — int3
  (недостижимо: pass 1 уже отверг). Состоит из: E02A. Используется в:
  Y002. Канон — SPEC/11 п.8 (формы v2).

## Эмиттеры (E)

- **K2-E001 out_ch / E002 out_copy / E003 out_str / E004 out_line** —
  байт; (RDX,R8); запись strtab2[RCX] (смещение+байты из strblob); +LF.
- **K2-E005 out_hex / E006 out_hex2** — ЗАГЛАВНЫЙ hex без ведущих нулей
  / ровно 2 цифры.
- **K2-E007 div10** — RAX/10 -> RAX, RDX (бит за битом, маска `and r9,1`).
- **K2-E008 out_dec** — десятичное (кадр; цифры с конца).
- **K2-E009 emit_cmt** — « ; » + srctxt + LF (трассируемость R10).
- **K2-E010 emit_kadr/emit_vyhod** — « ; кадр/выход имя-функции».
- **K2-E011 emit_lab** — «:имя» + LF; nlab++.
- **K2-E012 lower_copy** — имя -> scr (нижний регистр); RAX = длина.
- **K2-E013 str_dlen** — длина литерала с учётом экранов.
- **K2-E014 str_emit** — литерал -> строки «DB xx .. xx» <= 16 байт
  (экраны -> байты; кадр-буфер 16Б).
- **K2-E015 emit_header** — 2 строки заголовка; строка 1 выбирается
  по флагу v2 [r13+18190]: «; UNIVERSAL / WALL v1/v2 / …» (E6.4c-3/1;
  счётчики — как прежде, десятичные).
- **K2-E016 emit_entry** — «; --- код ---» + :_entry + 3 M-строки входа.
- **K2-E017 calc_framesize** — ftab -> RAX = align16(8*nslots)+0x30.
- **K2-E018 emit_prologue** — :имя, push rbp/mov rbp,rsp/sub rsp,hex;
  параметры mov [rbp-8*(i+1)], ARGREG[i] (argtab).
- **K2-E019 emit_epilogue** — mov rsp,rbp / pop rbp / ret (+vyhod).
- **K2-E020 emit_alu** — байт операции -> «M add/sub/and/or/xor r10, r11»
  (alutab, смещения блоба).
- **K2-E021 emit_shift** — «M mov rcx, r11» + «M shl/shr r10, cl».
- **K2-E034 emit_imul (E6.4c-3/1)** — «M imul r10, r11» + комментарий
  (v2: хвост операции `*`).
- **K2-E035 emit_divmod (E6.4c-3/1)** — EAX = 0 '/' / 1 '%':
  «M mov rax, r10 / M cqo / M idiv r11 / M mov r10, rax|rdx» +
  комментарии (канон SPEC/11 п.8 форм v2).
- **K2-E022 emit_addr** — &имя: локаль -> lea r10,[rbp-X]; var/str ->
  lea r10,[rip+$имя]; иначе G002.
- **K2-E023 emit_len** — len(имя): str_dlen -> «M mov r10, hex».
- **K2-E024 emit_load** — имя: локаль -> mov r10,[rbp-X]; var ->
  mov r10,[rip+$имя]; str -> lea r10,[rip+$имя]; func/ext -> G002.
- **K2-E025 get_ext** — earr[i] -> (RDX,R8) имя + scr + RAX длина.
- **K2-E026 emit_imports** — фиксированная область 0x200 (SPEC/11 п.6):
  idt/iat/intt/dll/hints (счётчик байта в кадре — r9/rax затираются
  вызовами!), DZ 148/2A.
- **K2-E027 emit_strdata** — секция строк: :имя, DZ 0 / DB-строки.
- **K2-E028 emit_globdata** — секция глобальных var: :имя, DZ 8.
- **K2-E029 emit_jcc_line** — RCX jcc, RDX e, R8 k, R9 while ->
  «M <jcc> $_if|_w<k>[e] ; текст» (jcctab — смещения блоба).
- **K2-E02A emit_jmp_line** — «M jmp $_if|_w<k>[e]».
- **K2-E02B emit_iflab / E02C emit_wlab** — «:_if<k>[e]»/«:_w<k>[e]».
- **K2-E02D emit_sstore** — стейджинг S-слота i: «M mov [rbp-X], r10».

## Данные (D)

- **K2-D001 digits** — 16 hex-цифр. **K2-D002 kwtab** — 12 ключевых слов.
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
