"""lab_pe.py — разбор PE32+ и инварианты SPEC/04-PE-MINIMAL.

Вход:  путь к .exe (str) или байты образа.
Выход: словарь PE (parse) / список строк-нарушений (check_spec04).
Функция: независимый от Windows разбор наших EXE: заголовки, секция,
         каталоги импорта, виртуальные нули; проверка инвариантов.
         С E9.4-3a разбор обобщён на ПРОИЗВОЛЬНЫЕ образы PE32+ (фундамент
         чужих EXE для PEG v2 — SPEC/15 п. 10): смещения полей вычисляются
         от e_lfanew (раньше неявно предполагался 0x80), таблица секций
         разбирается ЦЕЛИКОМ в pe["sections"], RVA отображается в файл
         по секции, которая его содержит (импорты многих DLL). Поля
         семейства (sec_*/body_rva/body/imports) сохраняют прежнюю
         семантику — ЗНАЧЕНИЯ ПЕРВОЙ СЕКЦИИ: для образов семейства
         результаты идентичны прежним (нейтральность — T-E9-28).
"""
import struct


def _u16(b, o):
    return struct.unpack("<H", b[o:o + 2])[0]


def _u32(b, o):
    return struct.unpack("<I", b[o:o + 4])[0]


def _u64(b, o):
    return struct.unpack("<Q", b[o:o + 8])[0]


def _slot(data, o):
    """Слот таблицы секций (40 Б) -> словарь (имя/размеры/свойства)."""
    return {"name": data[o:o + 8].rstrip(b"\x00").decode("latin1"),
            "vsize": _u32(data, o + 8), "vaddr": _u32(data, o + 12),
            "raw_size": _u32(data, o + 16), "raw_ptr": _u32(data, o + 20),
            "chars": _u32(data, o + 36)}


def parse(data):
    """Разобрать образ PE32+ (E9.4-3a: произвольный — e_lfanew, ВСЕ
    секции, импорты многих DLL). Возвращает словарь полей + импорты;
    поля sec_*/body/body_rva — ПЕРВАЯ секция (семантика семейства).
    Семья: e_lfanew == 0x80, один .text — значения как раньше."""
    pe = {"size": len(data)}
    pe["mz"] = data[0:2] == b"MZ"
    pe["e_lfanew"] = _u32(data, 0x3C)
    coff = pe["e_lfanew"] + 4               # COFF-заголовок (20 Б)
    opt = coff + 0x14                       # опциональный заголовок
    pe["pe_sig_ok"] = data[pe["e_lfanew"]:pe["e_lfanew"] + 4] \
        == b"PE\x00\x00"
    pe["machine"] = _u16(data, coff + 0x00)
    pe["num_sections"] = _u16(data, coff + 0x02)
    pe["size_opt_header"] = _u16(data, coff + 0x10)
    pe["characteristics"] = _u16(data, coff + 0x12)
    pe["magic"] = _u16(data, opt + 0x00)
    pe["addr_entry_point"] = _u32(data, opt + 0x10)
    pe["image_base"] = _u64(data, opt + 0x18)
    pe["sect_align"] = _u32(data, opt + 0x20)
    pe["file_align"] = _u32(data, opt + 0x24)
    pe["size_of_image"] = _u32(data, opt + 0x38)
    pe["size_of_headers"] = _u32(data, opt + 0x3C)
    pe["subsystem"] = _u16(data, opt + 0x44)
    pe["dd1_import_rva"] = _u32(data, opt + 0x78)   # DD[1] Import
    pe["dd1_import_size"] = _u32(data, opt + 0x7C)
    pe["dd12_iat_rva"] = _u32(data, opt + 0xD0)     # DD[12] IAT
    pe["dd12_iat_size"] = _u32(data, opt + 0xD4)
    # таблица секций: ВСЕ слоты -> pe["sections"] (E9.4-3a); слот 0
    # читается всегда и раздаёт легаси-поля семейства (sec_*)
    tbl = opt + pe["size_opt_header"]
    if tbl + 40 > len(data):          # как раньше: поле за пределами файла
        raise struct.error("таблица секций вне файла")
    s0 = _slot(data, tbl)
    pe["sec_name"] = s0["name"]
    pe["sec_vsize"] = s0["vsize"]
    pe["sec_vaddr"] = s0["vaddr"]
    pe["sec_raw_size"] = s0["raw_size"]
    pe["sec_raw_ptr"] = s0["raw_ptr"]
    pe["sec_chars"] = s0["chars"]
    secs = [s0]
    for i in range(1, pe["num_sections"]):
        o = tbl + 40 * i
        if o + 40 > len(data):
            break                    # битый образ: слоты за пределами файла
        secs.append(_slot(data, o))
    pe["sections"] = secs[:pe["num_sections"]]
    # тело первой секции (семантика семейства)
    raw = data[pe["sec_raw_ptr"]:pe["sec_raw_ptr"] + pe["sec_raw_size"]]
    pe["body"] = raw
    pe["body_rva"] = pe["sec_vaddr"]
    # импорты: обход IDT по DD[1] (сколько DLL записано — столько и будет)
    imports = []
    rva = pe["dd1_import_rva"]
    while True:
        desc = _read_rva(data, pe, rva, 20)
        if desc is None or desc == b"\x00" * 20:
            break
        oft, ts, fc, name_rva, ft = struct.unpack("<IIIII", desc)
        dll = _read_cstr_rva(data, pe, name_rva)
        funcs = []
        thunk = oft if oft else ft
        while True:
            ent = _read_rva(data, pe, thunk, 8)      # PE32+: 8 байт/элемент
            if ent is None or ent == b"\x00" * 8:
                break
            hint_rva = struct.unpack("<Q", ent)[0] & 0x7FFFFFFFFFFFFFFF
            fname = _read_cstr_rva(data, pe, hint_rva + 2)
            funcs.append((fname, hint_rva))
            thunk += 8
        imports.append({"dll": dll, "funcs": funcs, "iat_rva": ft,
                        "oft_rva": oft, "name_rva": name_rva})
        rva += 20
    pe["imports"] = imports
    return pe


def _sec_of(pe, rva):
    """Секция, содержащая RVA в файловой части (иначе None). E9.4-3a:
    отображение по ВСЕМ секциям (раньше — единственная, sec_*)."""
    for s in pe["sections"]:
        if s["vaddr"] <= rva < s["vaddr"] + s["raw_size"]:
            return s
    return None


def _read_rva(data, pe, rva, n):
    """Байты по RVA внутри файловой части секции (иначе None)."""
    s = _sec_of(pe, rva)
    if s is None:
        return None
    off = rva - s["vaddr"] + s["raw_ptr"]
    if off < 0 or off + n > len(data):
        return None
    return data[off:off + n]


def _read_cstr_rva(data, pe, rva):
    s = _sec_of(pe, rva)
    if s is None:
        return "?"
    off = rva - s["vaddr"] + s["raw_ptr"]
    if off < 0 or off >= len(data):
        return "?"
    end = data.find(b"\x00", off)
    return data[off:end].decode("latin1")


def check_spec04(pe):
    """Инварианты SPEC/04. Возвращает список строк-нарушений."""
    bad = []

    def need(cond, msg):
        if not cond:
            bad.append(msg)

    def align_up(x, a):
        return (x + a - 1) & ~(a - 1)

    need(pe["mz"], "нет сигнатуры MZ")
    need(pe["pe_sig_ok"], "нет сигнатуры PE\\0\\0")
    need(pe["machine"] == 0x8664, "Machine != 0x8664")
    need(pe["num_sections"] == 1, "NumberOfSections != 1")
    need(pe["size_opt_header"] == 0xF0, "SizeOfOptionalHeader != 0xF0")
    need(pe["characteristics"] == 0x0022, "Characteristics != 0x0022")
    need(pe["magic"] == 0x020B, "Magic != 0x020B (PE32+)")
    need(pe["image_base"] == 0x140000000, "ImageBase != 0x140000000")
    need(pe["sect_align"] == 0x1000, "SectionAlignment != 0x1000")
    need(pe["file_align"] == 0x200, "FileAlignment != 0x200")
    need(pe["subsystem"] == 3, "Subsystem != 3 (console)")
    need(pe["sec_vaddr"] == 0x1000, "VirtualAddress != 0x1000")
    need(pe["sec_chars"] == 0xE0000020, "секция: не CODE+EXEC+READ+WRITE")
    need(pe["sec_name"] == ".text", "имя секции != .text")
    # инвариант 1: SizeOfImage = конец секции, округлённый до SectAlign
    end = align_up(pe["sec_vaddr"] + pe["sec_vsize"], pe["sect_align"])
    need(pe["size_of_image"] == end,
         "SizeOfImage %X != align_up(vaddr+vsize) %X" %
         (pe["size_of_image"], end))
    # инвариант 2: SizeOfHeaders = смещение первой секции, кратно FileAlign
    need(pe["size_of_headers"] == pe["sec_raw_ptr"] and
         pe["sec_raw_ptr"] % pe["file_align"] == 0,
         "SizeOfHeaders/PointerToRawData не выровнены")
    # инвариант 4: SizeOfRawData кратно FileAlign. Соотношение с VirtualSize
    # двоякое по SPEC/04: E0–E2 — raw >= virtual (файл дополнен до
    # выравнивания), с E3 — raw <= virtual (виртуальные нули bss в хвосте).
    need(pe["sec_raw_size"] % pe["file_align"] == 0,
         "SizeOfRawData не кратно 0x200")
    # инвариант 5: точка входа в секции с EXECUTE
    need(pe["sec_vaddr"] <= pe["addr_entry_point"] <
         pe["sec_vaddr"] + pe["sec_vsize"],
         "точка входа вне секции")
    need(pe["sec_chars"] & 0x20000000, "в секции нет EXECUTE")
    # размер файла = 0x200 + SizeOfRawData
    need(pe["size"] == pe["size_of_headers"] + pe["sec_raw_size"],
         "размер файла != SizeOfHeaders + SizeOfRawData")
    # точка входа традиционно 0x1000 (все наши модули)
    need(pe["addr_entry_point"] == 0x1000, "точка входа != 0x1000")
    # импорты: один kernel32.dll; имена по чётным RVA (инвариант 7)
    need(len(pe["imports"]) == 1, "число DLL импорта != 1")
    if pe["imports"]:
        imp = pe["imports"][0]
        need(imp["dll"].lower() == "kernel32.dll", "импортируется не kernel32")
        for fname, hint_rva in imp["funcs"]:
            need(hint_rva % 2 == 0, "hint %s: RVA %X нечётное" %
                 (fname, hint_rva))
        # размер DD[1] покрывает IDT (2 дескриптора: рабочий + терминатор)
        need(pe["dd1_import_size"] >= 40, "DD[1] size < 40")
    return bad


def load(path):
    with open(path, "rb") as f:
        return parse(f.read())


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        p = load(arg)
        problems = check_spec04(p)
        print("%s: %s | entry=%X vsize=%X raw=%X img=%X | %s" %
              (arg, "OK" if not problems else "FAIL",
               p["addr_entry_point"], p["sec_vsize"], p["sec_raw_size"],
               p["size_of_image"],
               ",".join(i["dll"] for i in p["imports"])))
        for msg in problems:
            print("  !", msg)
