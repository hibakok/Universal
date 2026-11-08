# UNIVERSAL — ядро и язык, растущие из машинного кода

[![verify](https://github.com/hibakok/Universal/actions/workflows/verify.yml/badge.svg)](https://github.com/hibakok/Universal/actions/workflows/verify.yml)

> Самодостаточная вычислительная система: язык программирования, виртуальная
> машина, библиотеки и проекты — построенные вручную из мельчайших кирпичей,
> без использования чужих языков, компиляторов, ассемблеров и библиотек.

**Статус: этапы E0–E6.4a выполнены.** Артефакты ядра:
`KERNEL/L0-SEED/seed.exe` (1024 Б), `KERNEL/L0-SEED2/seed2.exe`
(2048 Б, командная строка), `KERNEL/L0-HXDUMP/hxdump.exe`
(3584 Б, файловый ввод), `KERNEL/L0-HEXGEN/hexgen.exe` (2560 Б,
**первый компилятор**: ATOM-текст → тело образа байт-в-байт),
`KERNEL/L0-PEGEN/pegen.exe` (4096 Б, **обёртка**: тело + PEG-файл →
готовый EXE), `KERNEL/L1-BRICK/brick.exe` (3584 Б, **ассемблер
BRICK v1**: метки, имена, rip-смещения) и `KERNEL/L1-ENC/enc.exe`
(11776 Б, **кодировщик BRICK v2**: M-строки — мнемоники вместо ручных
байтов — канонические кодировки SPEC/09) и
`KERNEL/L1-SPLICE/splice.exe` (3584 Б, **склейщик include**: директива
`!include`, SPEC/10 — собирает разрезанные исходники в плоский текст).
**E6.2 завершён:** ручное назначение байтов кодировок прекращено.
**E6.3 завершён:** все исходники L1 разрезаны на части ≤ 500 строк
(enc.b2 — корень + 10 частей, brick.brick — корень + 3, splice.b2 —
корень + 3); конвейер `splice → enc → brick → pegen` ведёт от
разрезанных мнемоник до EXE, сборка байт-в-байт, все круги самохостинга
(E5, E6.2, E6.3) зелёные.
**E6.4a завершён:** язык слоя L2 назван **WALL** («стена»); SPEC/11 —
грамматика, соглашения вызова, раскладка кадров, канон эмиттера;
оракул `LAB/py/lab_l2*.py` компилирует .wall → .b2 (BRICK v2),
демо-круг WALL → EXE → эмуляция печатает «U-WALL-OK 37».
**Следующий этап E6.4b** — wall.exe на BRICK v2 с самохостингом.

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
| `KERNEL/`| ядро системы; слой L0: семя, семя-2, hxdump, hexgen (компилятор), pegen (обёртка EXE); слой L1: brick (ассемблер BRICK), enc (кодировщик v2), splice (склейка include) |
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
SHA-256:          5F7F9EFD3398B735E762B37610ED1F197C383DA7252A3CD0C73DD3EE31A5C857
Команды:          brick.exe <src.brick> <out.bin> (см. CARD.md)

Самохостинг BRICK (DoD этапа E5, из папки KERNEL):
L1-BRICK\brick.exe L1-BRICK\brick.brick t_self.bin
L0-HEXGEN\hexgen.exe L1-BRICK\brick.hex t_body.bin
Ожидаемо:         fc /b t_self.bin t_body.bin -> различий нет (2968 байт)
L0-PEGEN\pegen.exe t_self.bin L1-BRICK\brick.peg t_brick.exe
Ожидаемо:         fc /b t_brick.exe L1-BRICK\brick.exe -> различий нет

cmd -> KERNEL\L1-ENC\enc.exe
Ожидаемый вывод:  U-L1-ENC CMDS: ENC <SRC.B2> <OUT.BRICK>
Код возврата:     2
SHA-256:          93AD8E21FADE2D1EC173F8723CE6165D3C9681C18251486FD27789D0E7A54A45
Команды:          enc.exe <src.b2> <out.brick> (см. CARD.md)

cmd -> KERNEL\L1-SPLICE\splice.exe
Ожидаемый вывод:  U-L1-SPLICE CMDS: SPLICE <ROOT.SRC> <OUT.FLAT>
Код возврата:     2
SHA-256:          387B5B63650205E4B16D270CD91FE0EADCAD644E67087C61E11D22D32D27AF92
Команды:          splice.exe <корень.b2> <выход.плоско> (см. CARD.md)

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
Ожидаемо:         ИТОГ: 96/96 OK (~33 секунды) — SHA, PE-инварианты,
                  эмуляция сценариев TESTS/, оракулы ATOM/BRICK/PEG/ENC/
                  SPLICE, круги E4, самохостинг E5 (на разрезе),
                  равенство enc.exe оракулу (109 якорей + 21 ошибка),
                  самохостинг E6.2 (на разрезе), оракул и инструмент
                  SPLICE (14 якорей + 13 ошибок + большие исходники +
                  корни репозитория), самохостинг E6.3 (splice собирает
                  себя из собственного разреза), оракул WALL (10 якорей
                  + 26 ошибок + полный круг до эмуляции «U-WALL-OK 37»
                  + PE-инварианты SPEC/11 + big_source 1203 строки).
                  Та же батарея
                  запускается автоматически при каждом пуше (вкладка
                  Actions; файл .github/workflows/verify.yml).

Подробности: `KERNEL/L0-SEED/VERIFY.md`, `KERNEL/L0-SEED2/VERIFY.md`,
`KERNEL/L0-HXDUMP/VERIFY.md`, `KERNEL/L0-HEXGEN/VERIFY.md`,
`KERNEL/L0-PEGEN/VERIFY.md`, `KERNEL/L1-BRICK/VERIFY.md`,
`KERNEL/L1-ENC/VERIFY.md`, `KERNEL/L1-SPLICE/VERIFY.md`.
