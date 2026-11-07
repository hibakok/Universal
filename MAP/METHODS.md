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

- Кирпичей в реестре: 50 (M0-SEED — 8, M0-SEED2 — 19, M0-HXDUMP — 23).
- Ветви кода: X, S, C, H, P, A, U, G, D (M0-SEED/M0-SEED2) + F, B (M0-HXDUMP).
