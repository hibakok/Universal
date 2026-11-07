"""lab_pe.py — разбор PE32+ и инварианты SPEC/04-PE-MINIMAL.

Вход:  путь к .exe (str) или байты образа.
Выход: словарь PE (parse) / список строк-нарушений (check_spec04).
Функция: независимый от Windows разбор наших EXE: заголовки, секция,
         каталоги импорта, виртуальные нули; проверка инвариантов.
"""
import struct

PE_FIELDS = [
    # (имя, смещение, размер, формат-подсказка)
    ("e_lfanew", 0x3C, 4, "u32"),
    ("machine", 0x84 + 0, 2, "u16"),
    ("num_sections", 0x84 + 2, 2, "u16"),
    ("size_opt_header", 0x84 + 16, 2, "u16"),
    ("characteristics", 0x84 + 18, 2, "u16"),
    ("magic", 0x98, 2, "u16"),
    ("addr_entry_point", 0xA8, 4, "u32"),
    ("image_base", 0xB0, 8, "u64"),
    ("sect_align", 0xB8, 4, "u32"),
    ("file_align", 0xBC, 4, "u32"),
    ("size_of_image", 0xD0, 4, "u32"),
    ("size_of_headers", 0xD4, 4, "u32"),
    ("subsystem", 0xDC, 2, "u16"),
    ("dd1_import_rva", 0x110, 4, "u32"),
    ("dd1_import_size", 0x114, 4, "u32"),
    ("dd12_iat_rva", 0x168, 4, "u32"),
    ("dd12_iat_size", 0x16C, 4, "u32"),
    ("sec_name", 0x188, 8, "bytes"),
    ("sec_vsize", 0x190, 4, "u32"),
    ("sec_vaddr", 0x194, 4, "u32"),
    ("sec_raw_size", 0x198, 4, "u32"),
    ("sec_raw_ptr", 0x19C, 4, "u32"),
    ("sec_chars", 0x1AC, 4, "u32"),
]


def parse(data):
    """Разобрать образ PE32+. Возвращает словарь полей + импорты."""
    pe = {"size": len(data)}
    pe["mz"] = data[0:2] == b"MZ"
    for name, off, size, fmt in PE_FIELDS:
        raw = data[off:off + size]
        if fmt == "u16":
            val = struct.unpack("<H", raw)[0]
        elif fmt == "u32":
            val = struct.unpack("<I", raw)[0]
        elif fmt == "u64":
            val = struct.unpack("<Q", raw)[0]
        else:
            val = raw.rstrip(b"\x00").decode("latin1")
        pe[name] = val
    pe["pe_sig_ok"] = data[pe["e_lfanew"]:pe["e_lfanew"] + 4] == b"PE\x00\x00"
    # тело секции
    raw = data[pe["sec_raw_ptr"]:pe["sec_raw_ptr"] + pe["sec_raw_size"]]
    pe["body"] = raw
    pe["body_rva"] = pe["sec_vaddr"]
    # импорты: обход IDT по DD[1]
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


def _read_rva(data, pe, rva, n):
    """Байты по RVA внутри файловой части секции (иначе None)."""
    off = rva - pe["sec_vaddr"] + pe["sec_raw_ptr"]
    if off < 0 or off + n > len(data):
        return None
    return data[off:off + n]


def _read_cstr_rva(data, pe, rva):
    off = rva - pe["sec_vaddr"] + pe["sec_raw_ptr"]
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
