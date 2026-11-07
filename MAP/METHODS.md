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

- Кирпичей в реестре: 116 (M0-SEED — 8, M0-SEED2 — 19, M0-HXDUMP — 23,
  M0-HEXGEN — 29, M0-PEGEN — 37).
- Ветви кода: X, S, C, H, P, A, U, G, D, F, B, R (разбор ATOM, E3) +
  Q (разбор PEG), E (заголовок EXE), M (математика) — новые в M0-PEGEN.
