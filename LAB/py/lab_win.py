"""lab_win.py — окружение Win32 для эмуляции: загрузка PE + kernel32.

Вход:  путь EXE, командная строка, host-файлы {имя: байты}.
Выход: готовый к запуску lab_cpu.CPU + результат (stdout, код, файлы).
Функция: отобразить образ в память (заголовки+секция+bss), заполнить
         IAT адресами заглушек kernel32, поставить стек и командную
         строку, исполнить от точки входа до ExitProcess.

Заглушки kernel32: GetStdHandle, WriteFile, ExitProcess,
GetCommandLineA, CreateFileA, ReadFile, CloseHandle; с E6.4c — куча:
GetProcessHeap, HeapAlloc, HeapFree (бамп-распределитель отдельного
региона; HeapFree — успешный no-op, документировано в SPEC/11).
С E6.4d-1 — CreateFile2 (WALL-программы слоя L2: контракт 5 аргументов
SPEC/11 п.3 не позволяет 7-аргументный CreateFileA; имя — LPCWSTR,
pCreateExParams — NULL, семантика disp 2/3 как у CreateFileA).
С E6.4d-2 — GlobalAlloc (только GMEM_FIXED=0; тот же бамп-регион,
что HeapAlloc; буферы каркаса wall.wall — вход 128 КиБ).
Файлы живут в виртуальной ФС (dict); stdout пишется в буфер bytes.
"""
import lab_pe
import lab_cpu

IMAGE_BASE = 0x140000000
STACK_BASE = 0x7FF700000000
STACK_SIZE = 0x100000          # 1 МиБ — резерв стека наших образов
CMDLINE_BASE = 0x7FF800000000
STUB_BASE = 0x7FF900000000     # адреса заглушек kernel32
RETGUARD = 0x7FF90000DEAD      # ловушка возврата из точки входа
HEAP_BASE = 0x7FFB00000000     # регион кучи HeapAlloc (E6.4c)
HEAP_SIZE = 0x800000           # 8 МиБ (E6.4d-2/3: srcbuf 131 К + карта
                               # текстов 1 М + таблицы прохода 1 3.4 М +
                               # будущий outbuf 2 М каркаса)
STD_OUTPUT_HANDLE = 0xFFFFFFF5  # -11
INVALID_HANDLE_VALUE = 0xFFFFFFFFFFFFFFFF

KERNEL32 = ["GetStdHandle", "WriteFile", "ExitProcess", "GetCommandLineA",
            "CreateFileA", "ReadFile", "CloseHandle", "GetProcessHeap",
            "HeapAlloc", "HeapFree", "CreateFile2", "GlobalAlloc"]


class VFile:
    """Файл виртуальной ФС: байты + позиция."""

    def __init__(self, data=b"", readonly_host=False):
        self.data = bytearray(data)
        self.pos = 0


class Result:
    def __init__(self):
        self.stdout = b""
        self.exit_code = None
        self.files = {}            # нормализованное имя -> bytes
        self.error = None          # строка если эмуляция сорвалась

    def __repr__(self):
        out = self.stdout.decode("latin1").replace("\r", "").replace(
            "\n", "\\n")
        return "Result(code=%s, stdout=%r, files=%s)" % (
            self.exit_code, out[:80], list(self.files))


class Machine:
    """Собранная машина: память + CPU + заглушки. Метод run()."""

    def __init__(self, exe_path, args, host_files=None, argv0=None):
        self.exe_path = exe_path
        self.pe = lab_pe.load(exe_path)
        imgsize = (self.pe["size_of_image"] + 0xFFF) & ~0xFFF
        self.image = bytearray(imgsize)
        raw = open(exe_path, "rb").read()
        # заголовки — с RVA 0; секция — со своего VirtualAddress
        self.image[0:self.pe["size_of_headers"]] = \
            raw[:self.pe["size_of_headers"]]
        va, ptr = self.pe["sec_vaddr"], self.pe["sec_raw_ptr"]
        srd = self.pe["sec_raw_size"]
        self.image[va:va + srd] = raw[ptr:ptr + srd]
        # хвост VirtualSize сверх SizeOfRawData (bss) уже нулевой
        self.cmdline = bytearray(0x1000)
        argv0 = argv0 or ('"C:\\UNI\\%s"' % exe_path.replace("/", "\\")
                          .split("\\")[-1])
        line = (argv0 + " " + " ".join(args)).encode("latin1") + b"\x00"
        self.cmdline[0:len(line)] = line
        self.stack = bytearray(STACK_SIZE)
        self.stdout = bytearray()
        self.heap = bytearray(HEAP_SIZE)      # куча HeapAlloc (E6.4c)
        self.heap_pos = 0                     # бамп-курсор
        self.host = {self._norm(k): bytes(v) for k, v in
                     (host_files or {}).items()}
        self.files = {}                       # имя -> VFile (созданные)
        self.handles = {}                     # хэндл -> VFile/строка
        self.next_handle = 0x1000
        self.result = Result()
        regions = [(IMAGE_BASE, self.image), (STACK_BASE, self.stack),
                   (CMDLINE_BASE, self.cmdline), (HEAP_BASE, self.heap)]
        self.cpu = lab_cpu.CPU(self.image, IMAGE_BASE, regions)
        self._bind_iat()
        self._boot()

    # --- подготовка ---
    def _bind_iat(self):
        stubaddr = {}
        for i, name in enumerate(KERNEL32):
            addr = STUB_BASE + i * 16
            stubaddr[name] = addr
            self.cpu.stubs[addr] = getattr(self, "_api_" + name.lower())
        # у нас одна DLL (проверено инвариантом); пишем адреса в IAT
        # (PE32+: элементы IAT — по 8 байт)
        imp = self.pe["imports"][0]
        for k, (fname, _hint) in enumerate(imp["funcs"]):
            if fname not in stubaddr:
                raise RuntimeError("нет заглушки для %s" % fname)
            iat = IMAGE_BASE + imp["iat_rva"] + 8 * k
            self.cpu.write(iat, 8, stubaddr[fname])

    def _boot(self):
        cpu = self.cpu
        cpu.retguard = RETGUARD
        rsp = STACK_BASE + STACK_SIZE - 0x100
        rsp &= ~0xF
        rsp += 8                      # RSP%16==8 как после call из kernel
        cpu.r[4] = rsp
        cpu.write(rsp, 8, RETGUARD)   # адрес возврата-ловушка
        cpu.rip = IMAGE_BASE + self.pe["addr_entry_point"]

    # --- API kernel32 ---
    def _api_getstdhandle(self, cpu):
        is_out = (cpu.r[1] & 0xFFFFFFFF) == STD_OUTPUT_HANDLE
        cpu.r[0] = 0xF00D0001 if is_out else 0xF00D0002

    def _api_writefile(self, cpu):
        # Win64: rcx, rdx, r8, r9, [rsp+0x20]
        h, buf, n, written = cpu.r[1], cpu.r[2], cpu.r[8], cpu.r[9]
        data = self._read_bytes(buf, n)
        if h == 0xF00D0001:
            self.stdout += data
        else:
            vf = self.handles.get(h)
            if vf is None:
                cpu.r[0] = 0
                return
            if vf.pos + n > len(vf.data):
                vf.data.extend(b"\x00" * (vf.pos + n - len(vf.data)))
            vf.data[vf.pos:vf.pos + n] = data
            vf.pos += n
        if written:
            cpu.write(written, 4, n)
        cpu.r[0] = 1

    def _read_bytes(self, addr, n):
        buf, off = self.cpu._region(addr, n)
        return bytes(buf[off:off + n])

    def _write_bytes(self, addr, data):
        buf, off = self.cpu._region(addr, len(data))
        buf[off:off + len(data)] = data

    def _api_exitprocess(self, cpu):
        self.result.exit_code = cpu.r[1] & 0xFFFFFFFF
        raise lab_cpu.ExitProcess(self.result.exit_code)

    def _api_getcommandlinea(self, cpu):
        cpu.r[0] = CMDLINE_BASE

    def _api_createfilea(self, cpu):
        # 7 аргументов: rcx, rdx, r8, r9, [rsp+0x20], [rsp+0x28], [rsp+0x30]
        name_ptr = cpu.r[1]
        disp = cpu.read(cpu.r[4] + 0x20, 4)     # dwCreationDisposition
        name = self._cstr(name_ptr)
        norm = self._norm(name)
        disp = disp & 0xFFFFFFFF
        if disp == 3:                       # OPEN_EXISTING
            data = self.host.get(norm)
            if data is None and norm in self.files:
                data = bytes(self.files[norm].data)
            if data is None:
                cpu.r[0] = INVALID_HANDLE_VALUE
                return
            h = self._new_handle(VFile(data))
        elif disp == 2:                     # CREATE_ALWAYS
            vf = VFile()
            self.files[norm] = vf
            h = self._new_handle(vf)
        else:
            cpu.r[0] = INVALID_HANDLE_VALUE
            return
        cpu.r[0] = h

    def _api_createfile2(self, cpu):
        # 5 аргументов (SPEC/11 п.3): rcx=имя (LPCWSTR), rdx=доступ,
        # r8=share, r9=disposition, [rsp+0x20]=pCreateExParams (NULL).
        # Семантика disp 2 (CREATE_ALWAYS) и 3 (OPEN_EXISTING) — как у
        # _api_createfilea; имя читается как UTF-16LE (ASCII-байты).
        name = self._cstrw(cpu.r[1])
        norm = self._norm(name)
        disp = cpu.r[9] & 0xFFFFFFFF
        if disp == 3:                       # OPEN_EXISTING
            data = self.host.get(norm)
            if data is None and norm in self.files:
                data = bytes(self.files[norm].data)
            if data is None:
                cpu.r[0] = INVALID_HANDLE_VALUE
                return
            cpu.r[0] = self._new_handle(VFile(data))
        elif disp == 2:                     # CREATE_ALWAYS
            vf = VFile()
            self.files[norm] = vf
            cpu.r[0] = self._new_handle(vf)
        else:
            cpu.r[0] = INVALID_HANDLE_VALUE

    def _api_readfile(self, cpu):
        h, buf, want, got = cpu.r[1], cpu.r[2], cpu.r[8], cpu.r[9]
        vf = self.handles.get(h)
        if vf is None:
            cpu.r[0] = 0
            return
        chunk = bytes(vf.data[vf.pos:vf.pos + want])
        self._write_bytes(buf, chunk)
        vf.pos += len(chunk)
        if got:
            cpu.write(got, 4, len(chunk))
        cpu.r[0] = 1

    def _api_closehandle(self, cpu):
        self.handles.pop(cpu.r[1], None)
        cpu.r[0] = 1

    # --- куча (E6.4c): бамп-распределитель; HeapFree — no-op ---
    def _api_getprocessheap(self, cpu):
        cpu.r[0] = 0xF00D0003               # условный хэндл процесса

    def _api_heapalloc(self, cpu):
        _h, _flags, size = cpu.r[1], cpu.r[2], cpu.r[8]
        size = (size + 15) & ~15            # выравнивание 16
        if size > len(self.heap) - self.heap_pos:
            cpu.r[0] = 0                    # нет памяти — NULL
            return
        ptr = HEAP_BASE + self.heap_pos
        self.heap_pos += size
        cpu.r[0] = ptr

    def _api_heapfree(self, cpu):
        cpu.r[0] = 1                        # успех (память не возвращается)

    def _api_globalalloc(self, cpu):
        # GlobalAlloc(uFlags, dwBytes): 2 аргумента; поддерживается только
        # GMEM_FIXED (uFlags == 0 — единственная форма у WALL-программ,
        # E6.4d-2): возвращается неподвижный указатель. Размещение — тем
        # же бамп-распределителем, что и HeapAlloc (регион HEAP_BASE);
        # исчерпание — NULL, как в Win32. Флаги игнорируются (GMEM_*
        # кроме FIXED в наших программах не используются).
        _flags, size = cpu.r[1], cpu.r[2]
        size = (size + 15) & ~15            # выравнивание 16
        if size > len(self.heap) - self.heap_pos:
            cpu.r[0] = 0                    # нет памяти — NULL
            return
        ptr = HEAP_BASE + self.heap_pos
        self.heap_pos += size
        cpu.r[0] = ptr

    # --- утилиты ---
    def _new_handle(self, vf):
        self.next_handle += 4
        self.handles[self.next_handle] = vf
        return self.next_handle

    def _cstr(self, addr):
        out = bytearray()
        while True:
            c = self.cpu.read(addr, 1)
            if c == 0:
                break
            out.append(c)
            addr += 1
        return out.decode("latin1")

    def _cstrw(self, addr):
        # то же, но UTF-16LE (CreateFile2): читаем слово, берём младший
        # байт; терминатор — слово 0
        out = bytearray()
        while True:
            w = self.cpu.read(addr, 2)
            if w == 0:
                break
            out.append(w & 0xFF)
            addr += 2
        return out.decode("latin1")

    def _norm(self, name):
        return name.replace("\\", "/").strip("/").lower()

    # --- запуск ---
    def run(self, max_steps=200_000_000):
        try:
            self.cpu.run(max_steps)
        except lab_cpu.ExitProcess as e:
            self.result.exit_code = e.code
        except Exception as e:                  # noqa: BLE001
            self.result.error = "%s: %s" % (type(e).__name__, e)
        self.result.stdout = bytes(self.stdout)
        self.result.files = {k: bytes(v.data)
                             for k, v in self.files.items()}
        self.result.steps = self.cpu.steps
        return self.result
