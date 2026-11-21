# Реестр кирпичей — указатель, часть 2 (слои L4/L5: библиотека и мосты)

Паспорт файла: MAP/METHODS-2.md | слой: все | роль: указатель реестра
кирпичей слоёв L4/L5 (продолжение MAP/METHODS.md — разрез по лимиту
500 строк, прецедент MAP/M3-UNIVM-V.md; K0..K3 — в MAP/METHODS.md).
Формат карточки: `SPEC/01-METHOD-CARD.md`. Идентификаторы вечны и не
переиспользуются (правило R5).

## Слой L4 — библиотека (SPEC/14 LIB-1: 11 кирпичей C/N/S/M — E8.2a..2d)

| ID | Имя | Ветвь | Статус | Карточка |
|---|---|---|---|---|
| K4-C001 | chr_out | C | готов | `MAP/M4-LIB.md` |
| K4-C002 | crlf_out | C | готов | `MAP/M4-LIB.md` |
| K4-C003 | buf_out | C | готов | `MAP/M4-LIB.md` |
| K4-C004 | buf_out_rev | C | готов | `MAP/M4-LIB.md` |
| K4-N001 | u64_to_dec_rev | N | готов | `MAP/M4-LIB.md` |
| K4-N002 | print_u64 | N | готов | `MAP/M4-LIB.md` |
| K4-N003 | print_i64 | N | готов | `MAP/M4-LIB.md` |
| K4-S001 | str_len | S | готов | `MAP/M4-LIB.md` |
| K4-S002 | str_out | S | готов | `MAP/M4-LIB.md` |
| K4-M001 | mem_copy | M | готов | `MAP/M4-LIB.md` |
| K4-M002 | mem_fill | M | готов | `MAP/M4-LIB.md` |

## Слой L5 — мост M5-BRIDGE (E9.2-1: каркас bridge.exe — 26 кирпичей)

| ID | Имя | Ветвь | Статус | Карточка |
|---|---|---|---|---|
| K5-C001 | print_error | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C002 | skip0 | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C003 | read_arg | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C004 | check_end | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C005 | widen | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C006 | copy_str | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C007 | out_dec | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-C008 | out_hex | C | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P001 | rd16 | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P002 | rd32 | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P003 | fail_family | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P004 | guard | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P005 | check_head | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P006 | check_opt | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P007 | check_base | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P008 | check_sect | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P009 | check_size | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P010 | check_body | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P011 | stub_name | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P012 | rva_off | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P013 | walk_descs | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P014 | cstr_len | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P015 | check_dll | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P016 | walk_funcs | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-P017 | print_facts | P | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
| K5-X001 | main | X | готов (E9.2-1) | `MAP/M5-BRIDGE.md` |
