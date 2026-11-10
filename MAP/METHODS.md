# Реестр кирпичей — указатель

Паспорт файла: MAP/METHODS.md | слой: все | роль: указатель реестра кирпичей.

Формат карточки: `SPEC/01-METHOD-CARD.md`. Идентификаторы вечны и не
переиспользуются (правило R5). Поиск: по ID в таблице ниже, затем —
карточка в файле модуля.

## Указатель

| ID | Имя | Ветвь | Статус | Карточка |
|---|---|---|---|---|
| K0-X001 | prepare_stack | X | готов | `MAP/M0-SEED.md` |
| K0-S001 | get_image_base | S | готов | `MAP/M0-SEED.md` |
| K0-S002 | read_sizeofimage | S | готов | `MAP/M0-SEED.md` |
| K0-H001 | hex32_to_ascii8 | H | готов | `MAP/M0-SEED.md` |
| K0-P001 | write_stdout | P | готов | `MAP/M0-SEED.md` |
| K0-X002 | exit_ok | X | готов | `MAP/M0-SEED.md` |
| K0-D001 | данные семени | D | готов | `MAP/M0-SEED.md` |
| K0-D002 | таблица импортов | D | готов | `MAP/M0-SEED.md` |
| K0-X011 | prepare_stack | X | готов | `MAP/M0-SEED2.md` |
| K0-S011 | get_image_base | S | готов | `MAP/M0-SEED2.md` |
| K0-S012 | get_pe_base | S | готов | `MAP/M0-SEED2.md` |
| K0-C001 | get_cmdline | C | готов | `MAP/M0-SEED2.md` |
| K0-C002 | skip_argv0 | C | готов | `MAP/M0-SEED2.md` |
| K0-C003 | read_word | C | готов | `MAP/M0-SEED2.md` |
| K0-C004 | find_command | C | готов | `MAP/M0-SEED2.md` |
| K0-C005 | count_tail | C | готов | `MAP/M0-SEED2.md` |
| K0-H011 | hex32_to_ascii8 | H | готов | `MAP/M0-SEED2.md` |
| K0-P011 | print_line | P | готов | `MAP/M0-SEED2.md` |
| K0-P012 | print_field_line | P | готов | `MAP/M0-SEED2.md` |
| K0-A001 | echo_args | A | готов | `MAP/M0-SEED2.md` |
| K0-U001 | print_usage | U | готов | `MAP/M0-SEED2.md` |
| K0-G001 | dispatch | G | готов | `MAP/M0-SEED2.md` |
| K0-X012 | exit_code | X | готов | `MAP/M0-SEED2.md` |
| K0-D011 | строки вывода | D | готов | `MAP/M0-SEED2.md` |
| K0-D012 | таблица команд | D | готов | `MAP/M0-SEED2.md` |
| K0-D013 | служебные данные | D | готов | `MAP/M0-SEED2.md` |
| K0-D014 | таблица импортов | D | готов | `MAP/M0-SEED2.md` |
| K0-X021 | prepare_stack | X | готов | `MAP/M0-HXDUMP.md` |
| K0-S021 | get_image_base | S | готов | `MAP/M0-HXDUMP.md` |
| K0-C011 | get_cmdline | C | готов | `MAP/M0-HXDUMP.md` |
| K0-C012 | skip_argv0 | C | готов | `MAP/M0-HXDUMP.md` |
| K0-C013 | read_word | C | готов | `MAP/M0-HXDUMP.md` |
| K0-C014 | copy_word | C | готов | `MAP/M0-HXDUMP.md` |
| K0-G021 | dispatch | G | готов | `MAP/M0-HXDUMP.md` |
| K0-F001 | open_file_read | F | готов | `MAP/M0-HXDUMP.md` |
| K0-F002 | read_chunk | F | готов | `MAP/M0-HXDUMP.md` |
| K0-F003 | close_file | F | готов | `MAP/M0-HXDUMP.md` |
| K0-B001 | dump_loop | B | готов | `MAP/M0-HXDUMP.md` |
| K0-B002 | build_line | B | готов | `MAP/M0-HXDUMP.md` |
| K0-H021 | hex32_to_ascii8 | H | готов | `MAP/M0-HXDUMP.md` |
| K0-H022 | hex8_to_ascii2 | H | готов | `MAP/M0-HXDUMP.md` |
| K0-P021 | print_line | P | готов | `MAP/M0-HXDUMP.md` |
| K0-U021 | print_usage | U | готов | `MAP/M0-HXDUMP.md` |
| K0-X022 | exit_code | X | готов | `MAP/M0-HXDUMP.md` |
| K0-D021 | linebuf | D | готов | `MAP/M0-HXDUMP.md` |
| K0-D022 | fname | D | готов | `MAP/M0-HXDUMP.md` |
| K0-D023 | filebuf | D | готов | `MAP/M0-HXDUMP.md` |
| K0-D024 | служебные данные | D | готов | `MAP/M0-HXDUMP.md` |
| K0-D025 | строки вывода | D | готов | `MAP/M0-HXDUMP.md` |
| K0-D026 | таблица импортов | D | готов | `MAP/M0-HXDUMP.md` |
| K0-X031 | prepare_stack | X | готов | `MAP/M0-HEXGEN.md` |
| K0-S031 | get_image_base | S | готов | `MAP/M0-HEXGEN.md` |
| K0-C021 | get_cmdline | C | готов | `MAP/M0-HEXGEN.md` |
| K0-C022 | skip_argv0 | C | готов | `MAP/M0-HEXGEN.md` |
| K0-C023 | read_word | C | готов | `MAP/M0-HEXGEN.md` |
| K0-C024 | copy_word_dst | C | готов | `MAP/M0-HEXGEN.md` |
| K0-C025 | skip_seps | C | готов | `MAP/M0-HEXGEN.md` |
| K0-G031 | dispatch | G | готов | `MAP/M0-HEXGEN.md` |
| K0-F004 | read_whole | F | готов | `MAP/M0-HEXGEN.md` |
| K0-F011 | open_file_read | F | готов | `MAP/M0-HEXGEN.md` |
| K0-F005 | create_file_write | F | готов | `MAP/M0-HEXGEN.md` |
| K0-F006 | write_image | F | готов | `MAP/M0-HEXGEN.md` |
| K0-F013 | close_file | F | готов | `MAP/M0-HEXGEN.md` |
| K0-R001 | parse_atom | R | готов | `MAP/M0-HEXGEN.md` |
| K0-R002 | hex_digit | R | готов | `MAP/M0-HEXGEN.md` |
| K0-R003 | read_hex4 | R | готов | `MAP/M0-HEXGEN.md` |
| K0-R004 | parse_data_line | R | готов | `MAP/M0-HEXGEN.md` |
| K0-R005 | parse_zero_line | R | готов | `MAP/M0-HEXGEN.md` |
| K0-R006 | skip_spaces | R | готов | `MAP/M0-HEXGEN.md` |
| K0-P031 | print_line | P | готов | `MAP/M0-HEXGEN.md` |
| K0-U031 | print_usage | U | готов | `MAP/M0-HEXGEN.md` |
| K0-X032 | exit_code | X | готов | `MAP/M0-HEXGEN.md` |
| K0-D031 | служебные данные | D | готов | `MAP/M0-HEXGEN.md` |
| K0-D032 | строки вывода | D | готов | `MAP/M0-HEXGEN.md` |
| K0-D033 | fname_in | D | готов | `MAP/M0-HEXGEN.md` |
| K0-D034 | fname_out | D | готов | `MAP/M0-HEXGEN.md` |
| K0-D035 | filebuf | D | готов | `MAP/M0-HEXGEN.md` |
| K0-D036 | imagebuf | D | готов | `MAP/M0-HEXGEN.md` |
| K0-D037 | таблица импортов | D | готов | `MAP/M0-HEXGEN.md` |
| K0-X041 | prepare_stack | X | готов | `MAP/M0-PEGEN.md` |
| K0-S041 | get_image_base | S | готов | `MAP/M0-PEGEN.md` |
| K0-C031 | get_cmdline | C | готов | `MAP/M0-PEGEN.md` |
| K0-C032 | skip_argv0 | C | готов | `MAP/M0-PEGEN.md` |
| K0-C033 | read_word | C | готов | `MAP/M0-PEGEN.md` |
| K0-C034 | copy_word_dst | C | готов | `MAP/M0-PEGEN.md` |
| K0-C035 | skip_seps | C | готов | `MAP/M0-PEGEN.md` |
| K0-C036 | next_arg | C | готов | `MAP/M0-PEGEN.md` |
| K0-G041 | dispatch | G | готов | `MAP/M0-PEGEN.md` |
| K0-G042 | print_error | G | готов | `MAP/M0-PEGEN.md` |
| K0-F021 | open_file_read | F | готов | `MAP/M0-PEGEN.md` |
| K0-F022 | create_file_write | F | готов | `MAP/M0-PEGEN.md` |
| K0-F023 | close_file | F | готов | `MAP/M0-PEGEN.md` |
| K0-F024 | read_whole_dst | F | готов | `MAP/M0-PEGEN.md` |
| K0-F025 | write_all | F | готов | `MAP/M0-PEGEN.md` |
| K0-P041 | print_line | P | готов | `MAP/M0-PEGEN.md` |
| K0-Q001 | parse_peg | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q002 | match_keyword | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q003 | read_hexv | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q004 | expect_eol | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q005 | scan_token | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q006 | skip_spaces | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q007 | hex_digit | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q010 | do_module | Q | готов | `MAP/M0-PEGEN.md` |
| K0-Q011 | do_value | Q | готов | `MAP/M0-PEGEN.md` |
| K0-M001 | align_up | M | готов | `MAP/M0-PEGEN.md` |
| K0-E001 | build_header | E | готов | `MAP/M0-PEGEN.md` |
| K0-E002 | patch_dirs | E | готов | `MAP/M0-PEGEN.md` |
| K0-E003 | build_stub | E | готов | `MAP/M0-PEGEN.md` |
| K0-E004 | copy_str | E | готов | `MAP/M0-PEGEN.md` |
| K0-X042 | exit_code | X | готов | `MAP/M0-PEGEN.md` |
| K0-D041 | служебные ячейки | D | готов | `MAP/M0-PEGEN.md` |
| K0-D042 | таблицы | D | готов | `MAP/M0-PEGEN.md` |
| K0-D043 | строки вывода | D | готов | `MAP/M0-PEGEN.md` |
| K0-D044 | шаблон PE-заголовка | D | готов | `MAP/M0-PEGEN.md` |
| K0-D045 | таблица импортов | D | готов | `MAP/M0-PEGEN.md` |
| K0-D046 | буферы | D | готов | `MAP/M0-PEGEN.md` |
| K1-X001 | prepare_stack | X | готов | `MAP/M1-BRICK.md` |
| K1-S001 | get_image_base | S | готов | `MAP/M1-BRICK.md` |
| K1-C001 | get_cmdline | C | готов | `MAP/M1-BRICK.md` |
| K1-C002 | skip_argv0 | C | готов | `MAP/M1-BRICK.md` |
| K1-C003 | next_arg | C | готов | `MAP/M1-BRICK.md` |
| K1-C004 | read_word | C | готов | `MAP/M1-BRICK.md` |
| K1-C005 | copy_word_dst | C | готов | `MAP/M1-BRICK.md` |
| K1-C006 | skip_seps | C | готов | `MAP/M1-BRICK.md` |
| K1-G001 | dispatch | G | готов | `MAP/M1-BRICK.md` |
| K1-G002 | print_error | G | готов | `MAP/M1-BRICK.md` |
| K1-G003 | fail_format | G | готов | `MAP/M1-BRICK.md` |
| K1-A001 | assemble_pass | A | готов | `MAP/M1-BRICK.md` |
| K1-A002 | parse_h | A | готов | `MAP/M1-BRICK.md` |
| K1-A003 | parse_db | A | готов | `MAP/M1-BRICK.md` |
| K1-A004 | parse_dz | A | готов | `MAP/M1-BRICK.md` |
| K1-A005 | parse_ddq | A | готов | `MAP/M1-BRICK.md` |
| K1-A006 | emit_le | A | готов | `MAP/M1-BRICK.md` |
| K1-A007 | read_hex_byte | A | готов | `MAP/M1-BRICK.md` |
| K1-A008 | parse_data | A | готов | `MAP/M1-BRICK.md` |
| K1-A009 | expect_eol | A | готов | `MAP/M1-BRICK.md` |
| K1-A010 | parse_dbz | A | готов | `MAP/M1-BRICK.md` |
| K1-T001 | skip_seps_rsi | T | готов | `MAP/M1-BRICK.md` |
| K1-T002 | hex_digit | T | готов | `MAP/M1-BRICK.md` |
| K1-T003 | read_hexval | T | готов | `MAP/M1-BRICK.md` |
| K1-T004 | read_name | T | готов | `MAP/M1-BRICK.md` |
| K1-N001 | define_label | N | готов | `MAP/M1-BRICK.md` |
| K1-N002 | find_label | N | готов | `MAP/M1-BRICK.md` |
| K1-H001 | hex16_to_4 | H | готов | `MAP/M1-BRICK.md` |
| K1-P001 | print_line | P | готов | `MAP/M1-BRICK.md` |
| K1-F001 | open_file_read | F | готов | `MAP/M1-BRICK.md` |
| K1-F002 | create_file_write | F | готов | `MAP/M1-BRICK.md` |
| K1-F003 | close_file | F | готов | `MAP/M1-BRICK.md` |
| K1-F004 | read_whole_dst | F | готов | `MAP/M1-BRICK.md` |
| K1-F005 | write_all | F | готов | `MAP/M1-BRICK.md` |
| K1-X002 | exit_code | X | готов | `MAP/M1-BRICK.md` |
| K1-D001 | таблица цифр | D | готов | `MAP/M1-BRICK.md` |
| K1-D002 | errtab | D | готов | `MAP/M1-BRICK.md` |
| K1-D003 | строки вывода | D | готов | `MAP/M1-BRICK.md` |
| K1-D004 | таблица импортов | D | готов | `MAP/M1-BRICK.md` |
| K1-D005 | hint-записи | D | готов | `MAP/M1-BRICK.md` |
| K1-D006 | виртуальные нули | D | готов | `MAP/M1-BRICK.md` |
| K1-X011 | prepare_stack | X | готов | `MAP/M1-ENC.md` |
| K1-X012 | exit_code | X | готов | `MAP/M1-ENC.md` |
| K1-C011 | get_cmdline | C | готов | `MAP/M1-ENC.md` |
| K1-C012 | skip_argv0 | C | готов | `MAP/M1-ENC.md` |
| K1-C013 | next_arg | C | готов | `MAP/M1-ENC.md` |
| K1-C014 | read_word | C | готов | `MAP/M1-ENC.md` |
| K1-C015 | copy_word_dst | C | готов | `MAP/M1-ENC.md` |
| K1-C016 | skip_seps | C | готов | `MAP/M1-ENC.md` |
| K1-G011 | dispatch | G | готов | `MAP/M1-ENC.md` |
| K1-G012 | print_error | G | готов | `MAP/M1-ENC.md` |
| K1-G013 | fail_format | G | готов | `MAP/M1-ENC.md` |
| K1-N011 | normalize_pass | N | готов | `MAP/M1-ENC.md` |
| K1-N012 | emit_line | N | готов | `MAP/M1-ENC.md` |
| K1-P011 | parse_m | P | готов | `MAP/M1-ENC.md` |
| K1-P012 | split_operands | P | готов | `MAP/M1-ENC.md` |
| K1-P013 | parse_operand | P | готов | `MAP/M1-ENC.md` |
| K1-P014 | parse_mem | P | готов | `MAP/M1-ENC.md` |
| K1-P015 | parse_ref | P | готов | `MAP/M1-ENC.md` |
| K1-T011 | first_nws | T | готов | `MAP/M1-ENC.md` |
| K1-T012 | last_nws_end | T | готов | `MAP/M1-ENC.md` |
| K1-T013 | hex_digit | T | готов | `MAP/M1-ENC.md` |
| K1-T014 | parse_num | T | готов | `MAP/M1-ENC.md` |
| K1-T015 | is_name_char | T | готов | `MAP/M1-ENC.md` |
| K1-R011 | lookup_reg | R | готов | `MAP/M1-ENC.md` |
| K1-R012 | lookup_mnem | R | готов | `MAP/M1-ENC.md` |
| K1-R013 | lookup_sizekw | R | готов | `MAP/M1-ENC.md` |
| K1-E011 | emit2 | E | готов | `MAP/M1-ENC-E.md` |
| K1-E012 | emit_rex | E | готов | `MAP/M1-ENC-E.md` |
| K1-E013 | emit_slot | E | готов | `MAP/M1-ENC-E.md` |
| K1-E014 | emit_i32 | E | готов | `MAP/M1-ENC-E.md` |
| K1-E015 | enc_mem | E | готов | `MAP/M1-ENC-E.md` |
| K1-E016 | emit_rm | E | готов | `MAP/M1-ENC-E.md` |
| K1-E017 | emit_rr | E | готов | `MAP/M1-ENC-E.md` |
| K1-E018 | sel_imm | E | готов | `MAP/M1-ENC-E.md` |
| K1-E019 | emit_immres | E | готов | `MAP/M1-ENC-E.md` |
| K1-E020 | check_imm_range | E | готов | `MAP/M1-ENC-E.md` |
| K1-E021 | enc_alu | E | готов | `MAP/M1-ENC-E.md` |
| K1-E022 | enc_shift | E | готов | `MAP/M1-ENC-E.md` |
| K1-E023 | enc_jcc | E | готов | `MAP/M1-ENC-E.md` |
| K1-E024 | enc_mov | E | готов | `MAP/M1-ENC-E.md` |
| K1-E025 | enc_movzx | E | готов | `MAP/M1-ENC-E.md` |
| K1-E026 | enc_lea | E | готов | `MAP/M1-ENC-E.md` |
| K1-E027 | enc_test | E | готов | `MAP/M1-ENC-E.md` |
| K1-E028 | enc_call | E | готов | `MAP/M1-ENC-E.md` |
| K1-E029 | enc_unary | E | готов | `MAP/M1-ENC-E.md` |
| K1-E030 | enc_pushpop | E | готов | `MAP/M1-ENC-E.md` |
| K1-E031 | enc_jmp | E | готов | `MAP/M1-ENC-E.md` |
| K1-E032 | enc_simple | E | готов | `MAP/M1-ENC-E.md` |
| K1-E033 | enc_imul | E | готов | `MAP/M1-ENC-E.md` |
| K1-H011 | hex16_to_4 | H | готов | `MAP/M1-ENC-S.md` |
| K1-U011 | print_line | U | готов | `MAP/M1-ENC-S.md` |
| K1-F011 | open_file_read | F | готов | `MAP/M1-ENC-S.md` |
| K1-F012 | create_file_write | F | готов | `MAP/M1-ENC-S.md` |
| K1-F013 | close_file | F | готов | `MAP/M1-ENC-S.md` |
| K1-F014 | read_whole_dst | F | готов | `MAP/M1-ENC-S.md` |
| K1-F015 | write_all | F | готов | `MAP/M1-ENC-S.md` |
| K1-D011 | таблица цифр | D | готов | `MAP/M1-ENC-S.md` |
| K1-D012 | regtab | D | готов | `MAP/M1-ENC-S.md` |
| K1-D013 | mnemtab | D | готов | `MAP/M1-ENC-S.md` |
| K1-D014 | sizetab | D | готов | `MAP/M1-ENC-S.md` |
| K1-D015 | errtab | D | готов | `MAP/M1-ENC-S.md` |
| K1-D016 | строки вывода | D | готов | `MAP/M1-ENC-S.md` |
| K1-D017 | таблица импортов | D | готов | `MAP/M1-ENC-S.md` |
| K1-D018 | виртуальные нули | D | готов | `MAP/M1-ENC-S.md` |

## Правила реестра

1. Карточка нового кирпича пишется в файл его модуля (MAP/M<слой>-<имя>.md);
   строка добавляется в указатель выше.
2. Один файл реестра не превышает 500 строк — при достижении предела
   модуль выделяется в отдельный файл (как M0-SEED/M0-SEED2/M0-HXDUMP).
3. Поля «Состоит из» / «Используется в» заполняются у соседей при
   добавлении зависимости.
4. Удалённый кирпич помечается статусом `x`; строка и карточка
   сохраняются навсегда.

## Счётчики (обновлять при каждом изменении)

- Кирпичей в реестре: 221 (M0-SEED — 8, M0-SEED2 — 19, M0-HXDUMP — 23,
  M0-HEXGEN — 29, M0-PEGEN — 37, M1-BRICK — 42, M1-ENC — 63).
- Ветви кода: X, S, C, H, P, A, U, G, D, F, B, R + Q, E, M + T, N +
  E (кодирование), N (нормализация), P (разбор), R (поиск в таблицах),
  U (печать) — новые в M1-ENC.
- Модули: M0-* (слой L0), M1-BRICK и M1-ENC (слой L1).

| K1-X021 | prepare_stack | X | готов | `MAP/M1-SPLICE.md` |
| K1-X022 | exit_code | X | готов | `MAP/M1-SPLICE.md` |
| K1-C021 | get_cmdline | C | готов | `MAP/M1-SPLICE.md` |
| K1-C022 | skip_argv0 | C | готов | `MAP/M1-SPLICE.md` |
| K1-C023 | next_arg | C | готов | `MAP/M1-SPLICE.md` |
| K1-C024 | read_word | C | готов | `MAP/M1-SPLICE.md` |
| K1-C025 | copy_word_dst | C | готов | `MAP/M1-SPLICE.md` |
| K1-C026 | skip_seps | C | готов | `MAP/M1-SPLICE.md` |
| K1-G021 | dispatch | G | готов | `MAP/M1-SPLICE.md` |
| K1-G022 | print_error | G | готов | `MAP/M1-SPLICE.md` |
| K1-G023 | fail_format | G | готов | `MAP/M1-SPLICE.md` |
| K1-S011 | process_loop | S | готов | `MAP/M1-SPLICE.md` |
| K1-S012 | handle_line | S | готов | `MAP/M1-SPLICE.md` |
| K1-S013 | emit_line | S | готов | `MAP/M1-SPLICE.md` |
| K1-N011 | name_prefix | N | готов | `MAP/M1-SPLICE.md` |
| K1-H021 | hex16_to_4 | H | готов | `MAP/M1-SPLICE.md` |
| K1-U021 | print_line | U | готов | `MAP/M1-SPLICE.md` |
| K1-F021 | open_file_read | F | готов | `MAP/M1-SPLICE.md` |
| K1-F022 | create_file_write | F | готов | `MAP/M1-SPLICE.md` |
| K1-F023 | close_file | F | готов | `MAP/M1-SPLICE.md` |
| K1-F024 | read_whole_dst | F | готов | `MAP/M1-SPLICE.md` |
| K1-F025 | write_all | F | готов | `MAP/M1-SPLICE.md` |
| K1-D021 | таблица цифр | D | готов | `MAP/M1-SPLICE.md` |
| K1-D022 | errtab (9 записей) | D | готов | `MAP/M1-SPLICE.md` |
| K1-D023 | строки вывода | D | готов | `MAP/M1-SPLICE.md` |
| K1-D024 | таблица импортов | D | готов | `MAP/M1-SPLICE.md` |
| K1-D025 | виртуальные нули | D | готов | `MAP/M1-SPLICE.md` |

## M2-WALL (KERNEL/L2-WALL, карточки — MAP/M2-WALL.md)

| K2-X001 | prepare (кадр+регистры+3 прохода) | X | готов | `MAP/M2-WALL.md` |
| K2-X002 | exit_ok | X | готов | `MAP/M2-WALL.md` |
| K2-C001 | get_cmdline/skip_argv0 | C | готов | `MAP/M2-WALL.md` |
| K2-C002 | next_arg | C | готов | `MAP/M2-WALL.md` |
| K2-C003 | read_word/copy_word_dst | C | готов | `MAP/M2-WALL.md` |
| K2-C004 | skip_seps | C | готов | `MAP/M2-WALL.md` |
| K2-G002 | fail_format | G | готов | `MAP/M2-WALL.md` |
| K2-G003 | print_error | G | готов | `MAP/M2-WALL.md` |
| K2-G004 | stream_args | G | готов | `MAP/M2-WALL.md` |
| K2-H001 | hex16_to_4 | H | готов | `MAP/M2-WALL.md` |
| K2-U001 | print_line | U | готов | `MAP/M2-WALL.md` |
| K2-F001 | open_file_read | F | готов | `MAP/M2-WALL.md` |
| K2-F002 | create_file_write | F | готов | `MAP/M2-WALL.md` |
| K2-F003 | close_file | F | готов | `MAP/M2-WALL.md` |
| K2-F004 | read_whole_dst | F | готов | `MAP/M2-WALL.md` |
| K2-F005 | write_all | F | готов | `MAP/M2-WALL.md` |
| K2-N001 | line_next | N | готов | `MAP/M2-WALL.md` |
| K2-N002 | pass0 | N | готов | `MAP/M2-WALL.md` |
| K2-N003 | lex_line | N | готов | `MAP/M2-WALL.md` |
| K2-N004 | set_lastline | N | готов | `MAP/M2-WALL.md` |
| K2-L001 | lex_tok | L | готов | `MAP/M2-WALL.md` |
| K2-P001 | want_sym1 | P | готов | `MAP/M2-WALL.md` |
| K2-P002 | at_end_chk | P | готов | `MAP/M2-WALL.md` |
| K2-P003 | want_id | P | готов | `MAP/M2-WALL.md` |
| K2-P004 | kw_lookup | P | готов | `MAP/M2-WALL.md` |
| K2-P005 | chk_name | P | готов | `MAP/M2-WALL.md` |
| K2-P006 | names_find | P | готов | `MAP/M2-WALL.md` |
| K2-P007 | names_add | P | готов | `MAP/M2-WALL.md` |
| K2-P008 | local_find | P | готов | `MAP/M2-WALL.md` |
| K2-P009 | chain_count | P | готов | `MAP/M2-WALL.md` |
| K2-P010 | p_expr | P | готов | `MAP/M2-WALL.md` |
| K2-P011 | p_mul | P | готов | `MAP/M2-WALL.md` |
| K2-P012 | p_unary | P | готов | `MAP/M2-WALL.md` |
| K2-P01A | p_mdm | P | готов | `MAP/M2-WALL.md` |
| K2-P013 | p_prim | P | готов | `MAP/M2-WALL.md` |
| K2-P014 | p_args | P | готов | `MAP/M2-WALL.md` |
| K2-P015 | p_call_tail | P | готов | `MAP/M2-WALL.md` |
| K2-P016 | call_stats | P | готов | `MAP/M2-WALL.md` |
| K2-P017 | pa_stage | P | готов | `MAP/M2-WALL.md` |
| K2-P018 | p_cond | P | готов | `MAP/M2-WALL.md` |
| K2-S001 | pass1 | S | готов | `MAP/M2-WALL.md` |
| K2-S002 | p1_line | S | готов | `MAP/M2-WALL.md` |
| K2-S003 | p1_decl | S | готов | `MAP/M2-WALL.md` |
| K2-S004 | p1_funchdr | S | готов | `MAP/M2-WALL.md` |
| K2-S005 | names_find_ci | S | готов | `MAP/M2-WALL.md` |
| K2-S006 | p1s_var | S | готов | `MAP/M2-WALL.md` |
| K2-S007 | p1s_end | S | готов | `MAP/M2-WALL.md` |
| K2-S008 | p1s_else | S | готов | `MAP/M2-WALL.md` |
| K2-S009 | p1s_if | S | готов | `MAP/M2-WALL.md` |
| K2-S00A | p1s_while | S | готов | `MAP/M2-WALL.md` |
| K2-S00B | p1s_return | S | готов | `MAP/M2-WALL.md` |
| K2-S00C | p1s_setb | S | готов | `MAP/M2-WALL.md` |
| K2-S00D | p1_namestmt | S | готов | `MAP/M2-WALL.md` |
| K2-S00E | fh_param | S | готов | `MAP/M2-WALL.md` |
| K2-S00F | p1s_brk | S | готов | `MAP/M2-WALL.md` |
| K2-Y001 | pass2 | Y | готов | `MAP/M2-WALL.md` |
| K2-Y002 | p2_line | Y | готов | `MAP/M2-WALL.md` |
| K2-Y003 | p2s_var | Y | готов | `MAP/M2-WALL.md` |
| K2-Y004 | p2s_end | Y | готов | `MAP/M2-WALL.md` |
| K2-Y005 | p2s_else | Y | готов | `MAP/M2-WALL.md` |
| K2-Y006 | p2s_if | Y | готов | `MAP/M2-WALL.md` |
| K2-Y007 | p2s_while | Y | готов | `MAP/M2-WALL.md` |
| K2-Y008 | p2s_return | Y | готов | `MAP/M2-WALL.md` |
| K2-Y009 | p2s_setb | Y | готов | `MAP/M2-WALL.md` |
| K2-Y00A | p2_funchdr | Y | готов | `MAP/M2-WALL.md` |
| K2-Y00B | p2_namestmt | Y | готов | `MAP/M2-WALL.md` |
| K2-Y00C | p2s_break/p2s_continue | Y | готов | `MAP/M2-WALL.md` |
| K2-E001 | out_ch | E | готов | `MAP/M2-WALL.md` |
| K2-E002 | out_copy | E | готов | `MAP/M2-WALL.md` |
| K2-E003 | out_str | E | готов | `MAP/M2-WALL.md` |
| K2-E004 | out_line | E | готов | `MAP/M2-WALL.md` |
| K2-E005 | out_hex | E | готов | `MAP/M2-WALL.md` |
| K2-E006 | out_hex2 | E | готов | `MAP/M2-WALL.md` |
| K2-E007 | div10 | E | готов | `MAP/M2-WALL.md` |
| K2-E008 | out_dec | E | готов | `MAP/M2-WALL.md` |
| K2-E009 | emit_cmt | E | готов | `MAP/M2-WALL.md` |
| K2-E010 | emit_kadr/emit_vyhod | E | готов | `MAP/M2-WALL.md` |
| K2-E011 | emit_lab | E | готов | `MAP/M2-WALL.md` |
| K2-E012 | lower_copy | E | готов | `MAP/M2-WALL.md` |
| K2-E013 | str_dlen | E | готов | `MAP/M2-WALL.md` |
| K2-E014 | str_emit | E | готов | `MAP/M2-WALL.md` |
| K2-E015 | emit_header | E | готов | `MAP/M2-WALL.md` |
| K2-E016 | emit_entry | E | готов | `MAP/M2-WALL.md` |
| K2-E017 | calc_framesize | E | готов | `MAP/M2-WALL.md` |
| K2-E018 | emit_prologue | E | готов | `MAP/M2-WALL.md` |
| K2-E019 | emit_epilogue | E | готов | `MAP/M2-WALL.md` |
| K2-E020 | emit_alu | E | готов | `MAP/M2-WALL.md` |
| K2-E021 | emit_shift | E | готов | `MAP/M2-WALL.md` |
| K2-E034 | emit_imul | E | готов | `MAP/M2-WALL.md` |
| K2-E035 | emit_divmod | E | готов | `MAP/M2-WALL.md` |
| K2-E022 | emit_addr | E | готов | `MAP/M2-WALL.md` |
| K2-E023 | emit_len | E | готов | `MAP/M2-WALL.md` |
| K2-E024 | emit_load | E | готов | `MAP/M2-WALL.md` |
| K2-E025 | get_ext | E | готов | `MAP/M2-WALL.md` |
| K2-E026 | emit_imports | E | готов | `MAP/M2-WALL.md` |
| K2-E027 | emit_strdata | E | готов | `MAP/M2-WALL.md` |
| K2-E028 | emit_globdata | E | готов | `MAP/M2-WALL.md` |
| K2-E029 | emit_jcc_line | E | готов | `MAP/M2-WALL.md` |
| K2-E02A | emit_jmp_line | E | готов | `MAP/M2-WALL.md` |
| K2-E02B | emit_iflab | E | готов | `MAP/M2-WALL.md` |
| K2-E02C | emit_wlab | E | готов | `MAP/M2-WALL.md` |
| K2-E02D | emit_sstore | E | готов | `MAP/M2-WALL.md` |
| K2-D001 | digits | D | готов | `MAP/M2-WALL.md` |
| K2-D002 | kwtab | D | готов | `MAP/M2-WALL.md` |
| K2-D003 | jcctab | D | готов | `MAP/M2-WALL.md` |
| K2-D004 | alutab | D | готов | `MAP/M2-WALL.md` |
| K2-D005 | argtab | D | готов | `MAP/M2-WALL.md` |
| K2-D006 | errtab | D | готов | `MAP/M2-WALL.md` |
| K2-D007 | strblob | D | готов | `MAP/M2-WALL.md` |
| K2-D008 | strtab2 | D | готов | `MAP/M2-WALL.md` |
| K2-D010 | импорты | D | готов | `MAP/M2-WALL.md` |
| K2-D011 | bss | D | готов | `MAP/M2-WALL.md` |
