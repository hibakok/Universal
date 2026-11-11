# UNIVERSAL — ядро и язык, растущие из машинного кода

[![verify](https://github.com/hibakok/Universal/actions/workflows/verify.yml/badge.svg)](https://github.com/hibakok/Universal/actions/workflows/verify.yml)

> Самодостаточная вычислительная система: язык программирования, виртуальная
> машина, библиотеки и проекты — построенные вручную из мельчайших кирпичей,
> без использования чужих языков, компиляторов, ассемблеров и библиотек.

**Статус: этапы E0–E6.4b, E6.4c (части 1–2), E6.4c-3 (срезы 1–2),
E6.4e-1, E6.4e-2 и E6.4e-3 выполнены; эпик E6.4e (рост пределов
конвейера 128 -> 256 КиБ) завершён.** Артефакты ядра:
`KERNEL/L0-SEED/seed.exe` (1024 Б), `KERNEL/L0-SEED2/seed2.exe`
(2048 Б, командная строка), `KERNEL/L0-HXDUMP/hxdump.exe`
(3584 Б, файловый ввод), `KERNEL/L0-HEXGEN/hexgen.exe` (2560 Б,
**первый компилятор**: ATOM-текст → тело образа байт-в-байт),
`KERNEL/L0-PEGEN/pegen.exe` (4096 Б, **обёртка**: тело + PEG-файл →
готовый EXE), `KERNEL/L1-BRICK/brick.exe` (3584 Б, **ассемблер
BRICK v1**: метки, имена, rip-смещения), `KERNEL/L1-ENC/enc.exe`
(12288 Б, **кодировщик BRICK v2**: M-строки — мнемоники вместо ручных
байтов; с E6.4c кодирует и **imul/idiv/cqo** — рост ISA для WALL v2)
и `KERNEL/L1-SPLICE/splice.exe` (3584 Б, **склейщик include**:
директива `!include`, SPEC/10; с E6.4e-2 — пределы файла и выхода
256 КиБ, буферы уровней 8×256 КиБ).
**E6.4c-1 завершён:** умножение/деление прошли весь вертикальный срез —
SPEC/05 + SPEC/09 + декодер/эмулятор LAB + оракул enc (117 якорей, 27
ошибок) + enc.exe (новый кирпич K1-E033 enc_imul, mnemtab 44 записи;
самохостинг и все круги зелёные).
**E6.4c-2 завершён:** язык **WALL v2** — SPEC/11 v2 (массивы `var a[n]`,
qword-индексация `e[i]`/`e[i] = v`, `* / %`, break/continue, цепочки
`&&`/`||`, куча HeapAlloc) + оракул (lab_l2/lab_l2_gen) + 9 якорей
вручную (lab_l2_cases2) + 13 ошибок + DEMO_WALL2: полный круг
wall-оракул → enc → brick → pegen → эмуляция печатает
**«U-WALL2-OK 85»**; программы v1 компилируются байт-в-байт как прежде.
Батарея 105 → **111** проверок.
**E6.4c-3, срез 1 завершён:** инструмент wall.exe понимает операторы
`* / %` (уровень p_mdm между конъюнкцией и унарным; эмиттеры imul и
rax/cqo/idiv) и печатает заголовок «WALL v1/v2» по флагу v2;
попутно исправлен дефект E6.4b №12 (chain_count) и снят предел меток
brick 512 (bss-метки → смещения r13+X). Батарея 111/111; dev-тест
27/27; круг DEMO_MDM печатает **«U-MDM-OK 52»**.
**E6.4c-3, срез 2 завершён:** wall.exe понимает **break/continue**
(только в while; kwtab 14; эмитция `jmp $_w<k>[e]`); попутно пойман и
исправлен ПРЕДСУЩЕСТВУЮЩИЙ дефект №15 (bstk 24 → 32 Б: push if
затирал lineidx объемлющего while) и синхронизирован генератор
wall_data.b2. Батарея 111/111; dev-тесты 27/27 + **17/17**;
круг DEMO_BC печатает **«U-BC-OK 25»** (s=37=0x25 — сумма 1..20 без
кратных 3, break при s > 30).
**E6.4e-1 завершён:** предел входа enc поднят 128 -> **256 КиБ**
(outbuf 0x44010 -> 0x88020; тело и размер файла не изменились,
vsize 0xCDEF4; новый тест T-E6-10b; самохостинг и все круги
зелёные). Это первый из трёх под-шагов эпика E6.4e — роста
пределов конвейера для срезов 3-5 и E6.4d; далее splice
(E6.4e-2 — выполнен, см. ниже) и brick (E6.4e-3: filebuf).
**E6.4e-2 завершён:** пределы splice **FILECAP/OUTCAP и буферы уровней
128 → 256 КиБ** (9 байтов кода: imm ×5, shl 11→12 ×3 — адресация
уровней ×0x40000, rip-смещение $outbuf; тело/файл не изменились, bss
0x240630, vsize 0x241102). Якоря BIG SRC/BIG OUT перевыпущены,
новый тест T-E6-16b, T-E6-17 расширен корнем wall.b2 (выход 130217 Б);
пересборка `LAB/ai/splice_build_lim.py` — dev 14/14 (корень/включение
132 КиБ приняты, 256 КиБ отвергнуто, максимум 0x3FFFF, выход 132 КиБ,
самохостинг, регресс enc/brick/wall). Батарея 112 → **113** проверок.
**E6.4e-3 завершён (эпик E6.4e закрыт):** предел исходника brick
128 → **256 КиБ** и таблица меток 512 → **1024 записи** (максимум
1023 пользовательских; wall.brick — 507): изменены 3 imm32 + 5 disp32
(ссылки на filebuf/imagebuf сдвинулись за ростом labtab/filebuf),
тело 0xB98 и файл 3584 Б НЕ изменились; bss 0x42178 → 0x84178
(labtab 16 КиБ, filebuf/imagebuf 256 КиБ), vsize 0x84D10. Круги E5
(самохостинг + pegen) зелёные; новый тест T-E6-36 (132 КиБ и 513
меток приняты / 256 КиБ отвергнут); попутно найден и зафиксирован
в очередь дефект №15 (DZ после DBZ в пассаже 2 пишет за пределы
файловой длины). Батарея 113 → **114** проверок; весь конвейер
splice → enc → brick → pegen принимает 256 КиБ на каждом уровне.
**Следующий шаг — срез 3 (E6.4c-3/3):** цепочки `&&`/`||` в wall.exe
(оракул и SPEC/11 v2 уже поддерживают; все пределы конвейера свободны),
затем срезы 4–5 и E6.4d — самохостинг wall.wall. Бюджет исходника
wall.b2: 130217 Б — запас 2× до пределов инструментов; см. журнал
LAB/ai, сессии 10–13.

## С чего начать (обязательно прочитать по порядку)

1. `DOCS/00-MANIFEST.md` — миссия, границы и принципы проекта.
2. `DOCS/02-AI-NAVIGATION.md` — как ориентироваться в репозитории
   (этот файл обязателен к прочтению для любого ИИ и нового участника).
3. `MAP/INDEX.md` — карта всех файлов репозитория.
4. `DOCS/03-ROADMAP.md` — план развития и текущий этап.

## Карта верхнего уровня

| Папка    | Назначение                                              |
|----------|---------------------------------------------------------|
| `DOCS/`  | манифест, методология, навигация, дорожная карта, правила изменений |
| `SPEC/`  | формальные спецификации: карточки методов, слои, форматы, PE, x86 |
| `MAP/`   | карта репозитория, указатель кирпичей, реестры модулей, слои |
| `KERNEL/`| ядро системы; слой L0: семя, семя-2, hxdump, hexgen (компилятор), pegen (обёртка EXE); слой L1: brick (ассемблер BRICK), enc (кодировщик v2), splice (склейка include); слой L2: wall (компилятор WALL v1) |
| `PROJECTS/` | внешние проекты — программы, исполняемые ядром          |
| `LAB/` | внешняя лаборатория ИИ (Python): эмулятор, оракулы, батарея |
| `TESTS/` | политика тестирования и тест-планы                        |

## Непреложные правила (полный список — `DOCS/01-METHODOLOGY.md`)

- Слой N зависит только от слоёв с номерами меньше N.
- Один файл — не более 500 строк.
- Любое изменение сопровождается обновлением реестров в `MAP/`.
- Запрещены сторонние языки, компиляторы, ассемблеры и библиотеки.
- Каждый байт каждого артефакта объясняется документацией.

## Быстрая проверка (Windows x64)

```
cmd -> KERNEL\L0-SEED\seed.exe
Ожидаемый вывод:  U-L0-SEED OK IMAGE=0x00002000
Код возврата:     0
SHA-256:          615D3292CCDD08664F7ACFCF9EF39E55F37443D1BF5A5F3E40D1CC796E64DBDF

cmd -> KERNEL\L0-SEED2\seed2.exe entry
Ожидаемый вывод:  U-L0-SEED2 ENTRY=0x00001000
Код возврата:     0
SHA-256:          190DE94E3F3227D421B6779B34985FD1762E127EC50EF864C4ED84814B05EE87
Команды:          entry | image | align | sect | args (см. CARD.md)

cmd -> KERNEL\L0-HXDUMP\hxdump.exe KERNEL\L0-SEED\seed.exe
Ожидаемый вывод (1-я строка):
  00000000: 4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00  MZ..............
Строк:            64 (файл 1024 байта / 16)
Код возврата:     0
SHA-256:          F0CEE97E45B1399FF13151BF4587BA2A02465E793FB9C92F525CDD69A7B4A8E3
Команды:          hxdump.exe <файл> (см. CARD.md)

Из папки KERNEL (конвейер E4 — полный круг «текст → EXE»):
L0-HEXGEN\hexgen.exe L0-SEED\seed.hex t_body.bin
L0-PEGEN\pegen.exe t_body.bin L0-SEED\seed.peg t_seed.exe
Ожидаемо:         вывод пуст; коды 0;
                  fc /b t_seed.exe L0-SEED\seed.exe -> различий нет
                  (DoD E4: конвейер воспроизводит артефакт из текстов)
L0-PEGEN\pegen.exe
Ожидаемый вывод:  U-L0-PEGEN CMDS: PEGEN <IMAGE.BIN> <CTRL.PEG> <OUT.EXE>
Код возврата:     2
SHA-256 pegen.exe: 39B7D78C344B2FAC0000AD929764EBF418D9EF98D394457826E5B8C806F1906C
Команды:          pegen.exe <образ.bin> <управляющий.peg> <выход.exe> (см. CARD.md)

Самосборка pegen (круг E4):
L0-HEXGEN\hexgen.exe L0-PEGEN\pegen.hex t_pb.bin
L0-PEGEN\pegen.exe t_pb.bin L0-PEGEN\pegen.peg t_pegen.exe
Ожидаемо:         fc /b t_pegen.exe L0-PEGEN\pegen.exe -> различий нет

cmd -> KERNEL\L1-BRICK\brick.exe
Ожидаемый вывод:  U-L1-BRICK CMDS: BRICK <SRC.BRICK> <OUT.BIN>
Код возврата:     2
SHA-256:          FEDA2B1A0E3F8EFD5D0E4FEEEF3C0B4AB06E729CCFC1A97B7DCC6C4B0C15EC74
Команды:          brick.exe <src.brick> <out.bin> (см. CARD.md)
Пределы:          исходник < 256 КиБ, метки <= 1024 записи (E6.4e-3)

Самохостинг BRICK (DoD этапа E5, из папки KERNEL):
L1-BRICK\brick.exe L1-BRICK\brick.brick t_self.bin
L0-HEXGEN\hexgen.exe L1-BRICK\brick.hex t_body.bin
Ожидаемо:         fc /b t_self.bin t_body.bin -> различий нет (2968 байт)
L0-PEGEN\pegen.exe t_self.bin L1-BRICK\brick.peg t_brick.exe
Ожидаемо:         fc /b t_brick.exe L1-BRICK\brick.exe -> различий нет

cmd -> KERNEL\L1-ENC\enc.exe
Ожидаемый вывод:  U-L1-ENC CMDS: ENC <SRC.B2> <OUT.BRICK>
Код возврата:     2
SHA-256:          18E6F2FDFA45FAEDA1E50D99483D9DBC05D71181089B7240926894C7264E4CA5
Команды:          enc.exe <src.b2> <out.brick> (см. CARD.md)
Предел входа:     256 КиБ (E6.4e-1; было 128 КиБ)
Рост ISA (E6.4c): echo M imul r10, r11> t.b2 && enc.exe t.b2 t.brick
                  -> t.brick: H 4D 0F AF D3

cmd -> KERNEL\L1-SPLICE\splice.exe
Ожидаемый вывод:  U-L1-SPLICE CMDS: SPLICE <ROOT.SRC> <OUT.FLAT>
Код возврата:     2
SHA-256:          E5C974173A7028A664A44DDC572D182B7855497694217F35EB810057AF6CD5C2
Команды:          splice.exe <корень.b2> <выход.плоско> (см. CARD.md)
Пределы:          файл < 256 КиБ, выход ≤ 256 КиБ (E6.4e-2)

cmd -> KERNEL\L2-WALL\wall.exe
Ожидаемый вывод:  U-L2-WALL CMDS: WALL <SRC.WALL> <OUT.B2>
Код возврата:     2
SHA-256:          A40A5FF668CE010BF6042D8D59E7F2589AE92F9500302A4D0A4E44D92724181D
Размер:           24064 байта (0x5E00); тело 23370; метки исходника 507/1024
Команды:          wall.exe <вход.wall> <выход.b2> (см. CARD.md)

Компиляция программы на WALL (из папки KERNEL):
L2-WALL\wall.exe   <прог>.wall <прог>.b2
L1-ENC\enc.exe     <прог>.b2   <прог>.brick
L1-BRICK\brick.exe <прог>.brick <прог>-body.bin
L0-PEGEN\pegen.exe <прог>-body.bin walldemo.peg <прог>.exe
Ожидаемо:         коды 0; <прог>.exe печатает результат программы

Самохостинг ENC на разрезе (DoD E6.2+E6.3, из папки KERNEL):
L1-SPLICE\splice.exe L1-ENC\enc.b2 t_flat.b2
L1-ENC\enc.exe t_flat.b2 t_v1.brick
L1-BRICK\brick.exe t_v1.brick t_body.bin
L0-PEGEN\pegen.exe t_body.bin L1-ENC\enc.peg t_enc.exe
Ожидаемо:         fc /b t_v1.brick L1-ENC\enc.brick -> различий нет
                  fc /b t_enc.exe L1-ENC\enc.exe -> различий нет

Самохостинг SPLICE через собственный include (DoD E6.3):
L1-SPLICE\splice.exe L1-SPLICE\splice.b2 t.b2
L1-ENC\enc.exe t.b2 t.brick
L1-BRICK\brick.exe t.brick t_body.bin
L0-PEGEN\pegen.exe t_body.bin L1-SPLICE\splice.peg t.exe
Ожидаемо:         fc /b t.brick L1-SPLICE\splice.brick -> различий нет
                  fc /b t.exe L1-SPLICE\splice.exe -> различий нет

Разрез brick воспроизводит тело (DoD E6.3):
L1-SPLICE\splice.exe L1-BRICK\brick.brick t_flat.brick
L1-BRICK\brick.exe t_flat.brick t_self.bin
L0-HEXGEN\hexgen.exe L1-BRICK\brick.hex t_body.bin
Ожидаемо:         fc /b t_self.bin t_body.bin -> различий нет (2968 байт)

Полный конвейер слоя L1 (модуль на BRICK v2 с разрезом):
L1-SPLICE\splice.exe <модуль>.b2 <модуль>-flat.b2
L1-ENC\enc.exe <модуль>-flat.b2 <модуль>.brick
L1-BRICK\brick.exe <модуль>.brick <модуль>-body.bin
L0-PEGEN\pegen.exe <модуль>-body.bin <модуль>.peg <модуль>.exe
```

Автоматическая батарея (без Windows, нужен Python 3.8+):
python3 LAB/py/lab_verify.py
Ожидаемо:         ИТОГ: 114/114 OK (~70 секунд) — SHA, PE-инварианты,
                  эмуляция сценариев TESTS/, оракулы ATOM/BRICK/PEG/ENC/
                  SPLICE, круги E4, самохостинг E5 (на разрезе),
                  равенство enc.exe оракулу (117 якорей + 27 ошибок),
                  самохостинг E6.2 (на разрезе), оракул и инструмент
                  SPLICE (14 якорей + 13 ошибок + большие исходники +
                  корни репозитория, вкл. wall.b2 + пределы 256 КиБ
                  T-E6-16b), самохостинг E6.3 (splice собирает
                  себя из собственного разреза), оракул WALL v1 (10 якорей
                  + 26 ошибок + полный круг до эмуляции «U-WALL-OK 37»
                  + PE-инварианты SPEC/11 + big_source 1203 строки),
                  оракул WALL v2 (T-E6-31..35: 9 якорей + 13 ошибок +
                  полный круг DEMO_WALL2 до эмуляции «U-WALL2-OK 85» —
                  массивы, * / %, break/continue, && / ||, куча +
                  big_source2 705 строк), инструмент wall.exe (T-E6-25..30:
                  == оракулу на якорях v1 и big_source, отвержение,
                  полный круг, SHA, PE; с E6.4c-3/1 — и операторы * / %:
                  dev-тест LAB/ai/wall_test_v2.py 27/27, круг
                  «U-MDM-OK 52»), инструмент brick.exe (T-E6-36, E6.4e-3:
                  исходник 132 КиБ и 513 меток приняты — старые пределы
                  128 КиБ/512 записей отвергли бы; 256 КиБ отвергнут
                  ERR=BIG SRC). Та же батарея
                  запускается автоматически при каждом пуше (вкладка
                  Actions; файл .github/workflows/verify.yml).

Подробности: `KERNEL/L0-SEED/VERIFY.md`, `KERNEL/L0-SEED2/VERIFY.md`,
`KERNEL/L0-HXDUMP/VERIFY.md`, `KERNEL/L0-HEXGEN/VERIFY.md`,
`KERNEL/L0-PEGEN/VERIFY.md`, `KERNEL/L1-BRICK/VERIFY.md`,
`KERNEL/L1-ENC/VERIFY.md`, `KERNEL/L1-SPLICE/VERIFY.md`,
`KERNEL/L2-WALL/VERIFY.md`.
