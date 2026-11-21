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

## Слой L5 — мост M5-BRIDGE (E9.2-1/2: каркас + спуск bridge.exe — 42 кирпича)

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
| K5-P017 | print_facts | P | готов (E9.2-1/2) | `MAP/M5-BRIDGE.md` |
| K5-D001 | fb | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D002 | rel8 | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D003 | rel32 | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D004 | modrm_skip | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D005 | dec0f | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D006 | decalu | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D007 | decmod | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D008 | decimm | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D009 | decshift | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D010 | decgrp | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D011 | decgrp2 | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D012 | decbr | D | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-D013 | decode_ins | D | готов (E9.2-2/3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D014 | u32 | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D015 | u64 | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D016 | set_reg | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D017 | set_rm | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D018 | set_imm | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D019 | set_immu | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D020 | set_tgt | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D021 | set_cl | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D022 | set_cnt | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-D023 | alu_id | D | готов (E9.2-3a) | `MAP/M5-BRIDGE-D.md` |
| K5-W001 | walk_code | W | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-W002 | sweep_ins | W | готов (E9.2-2/3a) | `MAP/M5-BRIDGE-D.md` |
| K5-W003 | calc_target | W | готов (E9.2-2) | `MAP/M5-BRIDGE-D.md` |
| K5-X001 | main | X | готов (E9.2-1/2/3a) | `MAP/M5-BRIDGE.md` |
| K5-E001 | fill_offs | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E002 | init_tables | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E003 | tpl_dec | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E004 | app_ch | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E005 | app_name | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E006 | app_reg | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E007 | out_hexv | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E008 | out_hxs | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E009 | out_hxu64 | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E010 | out_hex2 | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E011 | out_hex4m | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E012 | out_sdec | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E013 | note_op | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E014 | emit_note | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E015 | emit_h | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E016 | emit_data | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E017 | app_tpl | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
| K5-E018 | emit_raw | E | готов (E9.2-3a) | `MAP/M5-BRIDGE-E.md` |
