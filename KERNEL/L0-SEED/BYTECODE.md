# BYTECODE.md — байт-за-байтом разбор seed.exe

Паспорт файла: KERNEL/L0-SEED/BYTECODE.md | слой: L0 | роль: полный разбор образа.

Источник истины — `seed.hex`. Здесь каждый байт объяснён: что, почему и как
работает. Файл задуман как самодостаточный учебник «PE + x86-64 с нуля»
и как справочник для будущих изменений.

## 0. Сводка

| Свойство | Значение |
|---|---|
| Размер файла | 1024 байта (0x400) |
| SHA-256 | 615D3292CCDD08664F7ACFCF9EF39E55F37443D1BF5A5F3E40D1CC796E64DBDF |
| Точка входа | файл 0x200 (RVA 0x1000) |
| Вывод | `U-L0-SEED OK IMAGE=0x00002000` + CRLF (31 байт), код возврата 0 |
| Смещение -> RVA | заголовки: файл = RVA; секция: RVA = файл − 0x200 + 0x1000 |

## 1. DOS-заголовок (0x000–0x03F)

| Смещ. | Байты | Поле | Пояснение |
|---|---|---|---|
| 0x000 | `4D 5A` | сигнатура | 'MZ' — обязательна для загрузчика Windows |
| 0x002 | `90 00` | BytesOnLastPage | наследие DOS, не проверяется |
| 0x004 | `03 00` | Pages | то же |
| 0x006 | `00 00` | Relocations | 0 |
| 0x008 | `04 00` | HeaderSize | параграфы (устар.) |
| 0x00A | `00 00` | MinAlloc | 0 |
| 0x00C | `FF FF` | MaxAlloc | классика DOS-заголовка |
| 0x00E | `00 00` | SS | 0 |
| 0x010 | `B8 00` | SP | 0xB8 |
| 0x012 | `00 00` | Checksum | 0 |
| 0x014 | `00 00` | IP | 0 |
| 0x016 | `00 00` | CS | 0 |
| 0x018 | `40 00` | RelocTable | 0x40 |
| 0x01A | `00 00` | Overlay | 0 |
| 0x01C–0x03B | нули | зарезервировано | 32 байта |
| 0x03C | `80 00 00 00` | **e_lfanew** | адрес PE-сигнатуры: 0x80 |

Из всего DOS-заголовка Windows реально читает только `MZ` и `e_lfanew`.

## 2. DOS-заглушка (0x040–0x07F)

`55 6E 69 ... 24` — ASCII-текст «Universal L0 seed. No DOS support.\r\n$»
(37 байт), затем нули. В Windows никогда не исполняется; текст — дань
традиции. Байт `$` (0x24) — классический признак конца строки DOS.

## 3. PE-сигнатура и COFF (0x080–0x097)

| Смещ. | Байты | Поле | Пояснение |
|---|---|---|---|
| 0x080 | `50 45 00 00` | сигнатура | 'PE\0\0' |
| 0x084 | `64 86` | Machine | 0x8664 = AMD64 |
| 0x086 | `01 00` | NumberOfSections | 1 (.text) |
| 0x088 | `00 00 00 00` | TimeDateStamp | 0 (воспроизводимость) |
| 0x08C | `00 00 00 00` | PointerToSymbolTable | 0 |
| 0x090 | `00 00 00 00` | NumberOfSymbols | 0 |
| 0x094 | `F0 00` | SizeOfOptionalHeader | 240 = PE32+ |
| 0x096 | `22 00` | Characteristics | 0x22: EXECUTABLE_IMAGE + LARGE_ADDRESS_AWARE |

## 4. Опциональный заголовок PE32+ (0x098–0x187)

| Смещ. | Байты | Поле | Значение |
|---|---|---|---|
| 0x098 | `0B 02` | Magic | 0x020B (64-бит) |
| 0x09A | `01 00` | LinkerVersion | 1.0 |
| 0x09C | `00 02 00 00` | SizeOfCode | 0x200 |
| 0x0A0 | `00 00 00 00` | SizeOfInitializedData | 0 |
| 0x0A4 | `00 00 00 00` | SizeOfUninitializedData | 0 |
| 0x0A8 | `00 10 00 00` | **AddressOfEntryPoint** | RVA 0x1000 |
| 0x0AC | `00 10 00 00` | BaseOfCode | RVA 0x1000 |
| 0x0B0 | `00 00 00 40 01 00 00 00` | **ImageBase** | 0x140000000 |
| 0x0B8 | `00 10 00 00` | SectionAlignment | 0x1000 |
| 0x0BC | `00 02 00 00` | FileAlignment | 0x200 |
| 0x0C0 | `06 00 00 00` | OSVersion | 6.0 |
| 0x0C4 | `00 00 01 00` | ImageVersion | 0.1 |
| 0x0C8 | `06 00 00 00` | SubsystemVersion | 6.0 |
| 0x0CC | `00 00 00 00` | Win32VersionValue | 0 |
| 0x0D0 | `00 20 00 00` | **SizeOfImage** | 0x2000 |
| 0x0D4 | `00 02 00 00` | SizeOfHeaders | 0x200 |
| 0x0D8 | `00 00 00 00` | CheckSum | 0 |
| 0x0DC | `03 00` | **Subsystem** | 3 = консоль |
| 0x0DE | `00 00` | DllCharacteristics | 0 |
| 0x0E0 | `00 00 10 00 00 00 00 00` | StackReserve | 1 МиБ |
| 0x0E8 | `00 10 00 00 00 00 00 00` | StackCommit | 4 КиБ |
| 0x0F0 | `00 00 10 00 00 00 00 00` | HeapReserve | 1 МиБ |
| 0x0F8 | `00 10 00 00 00 00 00 00` | HeapCommit | 4 КиБ |
| 0x100 | `00 00 00 00` | LoaderFlags | 0 |
| 0x104 | `10 00 00 00` | NumberOfRvaAndSizes | 16 |
| 0x108 | нули | DD[0] Export | пусто |
| 0x110 | `00 11 00 00 28 00 00 00` | **DD[1] Import** | RVA 0x1100, размер 0x28 |
| 0x118–0x167 | нули | DD[2..11] | пусто |
| 0x168 | `30 11 00 00 20 00 00 00` | **DD[12] IAT** | RVA 0x1130, размер 0x20 |
| 0x170–0x187 | нули | DD[13..15] | пусто |

Little-endian на примере ImageBase: 0x140000000 = байты `00 00 00 40 01 00 00 00`
(младший байт первым).

## 5. Заголовок секции (0x188–0x1AF)

| Смещ. | Байты | Поле | Значение |
|---|---|---|---|
| 0x188 | `2E 74 65 78 74 00 00 00` | Name | «.text» |
| 0x190 | `C0 01 00 00` | VirtualSize | 0x1C0 |
| 0x194 | `00 10 00 00` | VirtualAddress | RVA 0x1000 |
| 0x198 | `00 02 00 00` | SizeOfRawData | 0x200 |
| 0x19C | `00 02 00 00` | PointerToRawData | файл 0x200 |
| 0x1A0 | `00 00 00 00` | PointerToRelocations | 0 |
| 0x1A4 | `00 00 00 00` | PointerToLinenumbers | 0 |
| 0x1A8 | `00 00 00 00` | Relocs/Lines | 0/0 |
| 0x1AC | `20 00 00 E0` | Characteristics | CODE+EXEC+READ+WRITE |

Флаг WRITE нужен: код пишет в собственные данные (hex-поле, written).
0x1B0–0x1FF — нулевое выравнивание до 0x200.

## 6. Код (файл 0x200–0x27E, RVA 0x1000–0x107E)

RVA = файл − 0x200 + 0x1000. Мнемоника в синтаксисе Intel.

| Файл | RVA | Байты | Мнемоника | Кирпич |
|---|---|---|---|---|
| 0x200 | 0x1000 | `48 83 EC 28` | `sub rsp,0x28` | K0-X001 |
| 0x204 | 0x1004 | `48 8D 1D F5 EF FF FF` | `lea rbx,[rip-0x100B]` | K0-S001 |
| 0x20B | 0x100B | `8B 43 3C` | `mov eax,[rbx+0x3C]` | K0-S002 |
| 0x20E | 0x100E | `8B 44 03 50` | `mov eax,[rbx+rax+0x50]` | K0-S002 |
| 0x212 | 0x1012 | `48 98` | `cdqe` | K0-S002 |
| 0x214 | 0x1014 | `48 8D 35 65 00 00 00` | `lea rsi,[rip+0x65]` | K0-H001 |
| 0x21B | 0x101B | `48 83 C6 15` | `add rsi,0x15` | K0-H001 |
| 0x21F | 0x101F | `4C 8D 05 79 00 00 00` | `lea r8,[rip+0x79]` | K0-H001 |
| 0x226 | 0x1026 | `B9 08 00 00 00` | `mov ecx,8` | K0-H001 |
| 0x22B | 0x102B | `C1 C0 04` | `rol eax,4` | K0-H001 |
| 0x22E | 0x102E | `48 89 C2` | `mov rdx,rax` | K0-H001 |
| 0x231 | 0x1031 | `83 E2 0F` | `and edx,0xF` | K0-H001 |
| 0x234 | 0x1034 | `41 0F B6 14 10` | `movzx rdx,byte [r8+rdx]` | K0-H001 |
| 0x239 | 0x1039 | `88 16` | `mov [rsi],dl` | K0-H001 |
| 0x23B | 0x103B | `48 FF C6` | `inc rsi` | K0-H001 |
| 0x23E | 0x103E | `FF C9` | `dec ecx` | K0-H001 |
| 0x240 | 0x1040 | `75 E9` | `jnz 0x102B` | K0-H001 |
| 0x242 | 0x1042 | `48 C7 C1 F5 FF FF FF` | `mov rcx,-11` | K0-P001 |
| 0x249 | 0x1049 | `FF 15 E1 00 00 00` | `call [rip+0xE1]` GetStdHandle | K0-P001 |
| 0x24F | 0x104F | `48 89 C1` | `mov rcx,rax` | K0-P001 |
| 0x252 | 0x1052 | `48 8D 15 27 00 00 00` | `lea rdx,[rip+0x27]` | K0-P001 |
| 0x259 | 0x1059 | `41 B8 1F 00 00 00` | `mov r8d,0x1F` | K0-P001 |
| 0x25F | 0x105F | `4C 8D 0D 49 00 00 00` | `lea r9,[rip+0x49]` | K0-P001 |
| 0x266 | 0x1066 | `48 C7 44 24 20 00 00 00 00` | `mov qword [rsp+0x20],0` | K0-P001 |
| 0x26F | 0x106F | `FF 15 C3 00 00 00` | `call [rip+0xC3]` WriteFile | K0-P001 |
| 0x275 | 0x1075 | `48 31 C9` | `xor ecx,ecx` | K0-X002 |
| 0x278 | 0x1078 | `FF 15 C2 00 00 00` | `call [rip+0xC2]` ExitProcess | K0-X002 |
| 0x27E | 0x107E | `CC` | `int3` | страховка |

### Расчёт rip-смещений (формула: цель − конец инструкции)

| Инструкция | Конец (RVA) | Цель (RVA) | disp32 | Байты |
|---|---|---|---|---|
| lea rbx | 0x100B | 0x0000 (база) | −0x100B = 0xFFFFEFF5 | `F5 EF FF FF` |
| lea rsi | 0x101B | 0x1080 (строка) | +0x65 | `65 00 00 00` |
| lea r8 | 0x1026 | 0x109F (цифры) | +0x79 | `79 00 00 00` |
| call GSH | 0x104F | 0x1130 (IAT[0]) | +0xE1 | `E1 00 00 00` |
| lea rdx | 0x1059 | 0x1080 (строка) | +0x27 | `27 00 00 00` |
| lea r9 | 0x1066 | 0x10AF (written) | +0x49 | `49 00 00 00` |
| call WF | 0x1075 | 0x1138 (IAT[1]) | +0xC3 | `C3 00 00 00` |
| call EP | 0x107E | 0x1140 (IAT[2]) | +0xC2 | `C2 00 00 00` |

Внимание на lea rbx: −0x100B в little-endian — это `F5 EF FF FF`
(НЕ `F5 FF FF FF`, что было бы −0xB). Эта ошибка была допущена и поймана
эмуляцией на этапе E0 — см. TESTS/POLICY.md.

### Разбор ключевых кодировок

- `48 83 EC 28`: REX.W(48) + группа 83 /5(ib) = sub r64, imm8; modrm EC =
  mod11(регистр) reg101(sub) rm100(rsp).
- `8B 44 03 50`: mov eax, [rbx+rax+disp8]. modrm 44 = mod01(байт смещ.)
  reg000(eax) rm100(далее SIB); SIB 03 = scale0 index000(rax) base011(rbx);
  disp8 0x50. Адрес = rbx + rax + 0x50 = база + 0x80 + 0x50 = SizeOfImage.
- `41 0F B6 14 10`: movzx rdx, byte [r8+rdx]. REX.B(41) расширяет базу SIB
  до r8; 0F B6 — movzx; modrm 14: mod00 reg010(rdx) rm100(SIB); SIB 10:
  scale0 index010(rdx) base000+r8.
- `48 C7 44 24 20 00 00 00 00`: mov qword [rsp+0x20], 0. Порядок байтов
  инструкции: opcode(C7) modrm(44) SIB(24) disp8(20) imm32(00000000).
  SIB 24: index=100 (индекса нет), base=rsp.
- `FF 15 ...`: call косвенный. modrm 15 = mod00 reg010(/2 = call) rm101
  (rip-относительно). Читает адрес функции из IAT и переходит.
- `48 C7 C1 F5 FF FF FF`: mov rcx, −11. imm32 = 0xFFFFFFF5 (знакорасширяется
  до 64 бит) — константа STD_OUTPUT_HANDLE Windows.

### Логика исполнения по шагам

1. Точка входа 0x1000: тень 0x20 + выравнивание (rsp%16==0 на вызовах).
2. rbx = база образа (rip-относительно, работает при любом адресе загрузки).
3. eax = [rbx+0x3C] = e_lfanew = 0x80.
4. eax = [rbx+rax+0x50] = [0xD0] = SizeOfImage = 0x2000.
5. rsi = строка+21 (hex-поле), r8 = таблица цифр, ecx = 8.
6. Цикл 8 раз: rol eax,4 выталкивает старшую тетраду вниз; and 0xF — номер
   цифры; movzx берёт ASCII-символ; запись в поле; rsi++; ecx--; jnz назад.
   После 8 сдвигов по 4 бита eax восстанавливается. Для 0x2000 вывод:
   0,0,0,0,2,0,0,0.
7. GetStdHandle(−11) -> rax; WriteFile(хэндл, строка, 31, &written, NULL).
8. ExitProcess(0). Страховочный int3 ниже никогда не исполняется.

## 7. Данные (файл 0x280–0x2B6, RVA 0x1080–0x10B6)

| Файл | RVA | Байты | Смысл |
|---|---|---|---|
| 0x280 | 0x1080 | `U-L0-SEED OK IMAGE=0x` | префикс, 21 байт |
| 0x295 | 0x1095 | `00 × 8` | hex-поле (заполняет цикл K0-H001) |
| 0x29D | 0x109D | `0D 0A` | CRLF |
| 0x29F | 0x109F | `0123456789ABCDEF` | таблица цифр, 16 байт |
| 0x2AF | 0x10AF | `00 × 8` | written — счётчик WriteFile |

0x2B7–0x2FF — нули (выравнивание до границ по 0x10 для области импортов).

## 8. Импорты (файл 0x300–0x3B9, RVA 0x1100–0x11B9)

### Описатель IDT (RVA 0x1100)

| Файл | Поле | Значение |
|---|---|---|
| 0x300 | OriginalFirstThunk | RVA 0x1160 (INT) |
| 0x304 | TimeDateStamp | 0 |
| 0x308 | ForwarderChain | 0 |
| 0x30C | Name | RVA 0x1180 («kernel32.dll») |
| 0x310 | FirstThunk | RVA 0x1130 (IAT) |
| 0x314–0x327 | терминатор | 20 нулевых байт |

### IAT (RVA 0x1130) и INT (RVA 0x1160)

До загрузки обе таблицы содержат одни и те же RVA hint-записей;
загрузчик Windows перепишет IAT адресами функций:

| Индекс | Значение | Функция |
|---|---|---|
| [0] | 0x1190 | GetStdHandle |
| [1] | 0x11A0 | WriteFile |
| [2] | 0x11AC | ExitProcess |
| [3] | 0 | терминатор |

### Имена (RVA 0x1180+)

| Файл | RVA | Содержимое |
|---|---|---|
| 0x380 | 0x1180 | «kernel32.dll\0» |
| 0x390 | 0x1190 | hint `00 00` + «GetStdHandle\0» (выровнено на чётное RVA) |
| 0x3A0 | 0x11A0 | hint `00 00` + «WriteFile\0» |
| 0x3AC | 0x11AC | hint `00 00` + «ExitProcess\0» |

## 9. Хвост

0x3BA–0x3FF — нули до размера 0x400. Полное покрытие файла байтами
проверяется скриптом сборки (наложений и дыр нет).
