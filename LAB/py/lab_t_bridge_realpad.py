"""lab_t_bridge_realpad.py — корпус данных секции 18k батареи
(мост BRIDGE v1, срез E9.5-3a).

Паспорт файла: LAB/py/lab_t_bridge_realpad.py | слой: внешний
инструмент | роль: крафт реального паддинга raw > vsize + якоря —
вынесен из lab_t_bridge_corpus.py по лимиту 500 строк (решение №4
сессии 74, прецедент lab_t_*_corpus.py; срез E9.5-3a, сессия 92).

Вход:  нет (самодостаточный крафт).
Выход: realpad_image() — чужой образ PE32+ с РЕАЛЬНЫМ паддингом
       (mingw/MSVC-макет); якоря REALPAD_SECTIONS/REALPAD_FACTS/
       REALPAD_INS. Потребитель — lab_t_bridge_real.py (T-E9-34).
Функция: держать данные среза E9.5-3a отдельно, чтобы каждый файл
       был <= 500 строк.
"""
import struct as _st


# --- E9.5-3a: реальный паддинг raw > vsize (T-E9-34, секция 18k) ---
# Чужой образ в МАКЕТЕ реальных компиляторов (mingw/MSVC): raw
# выровнен ВВЕРХ от vsize до FileAlignment (0x200), хвост — ПАДДИНГ
# 0xCC (int3-заливка), НЕ нули. До E9.5-3a nz-подъём target вытаскивал
# паддинг за vsize -> «длина тела больше VirtualSize» (ложный отказ);
# обобщение SPEC/15 п. 7 «вилка raw>bss»: тело — ВСЯ raw-область
# (target = raw - (fa-1) при несовпадении вилки; здесь 0x200),
# bss = max(0, vsize - target) = 0 (виртуальных нулей НЕТ — хвост
# реальный). Макет .text (смещения секции): 0x20 mov eax,11; 0x25
# call 0x38; 0x2A xor eax,eax; 0x2C ret; 0x38 add eax,7; 0x3B ret;
# 0x3C..0x4B данные-блоб; vsize 0x40, raw 0x200 — паддинг 0xCC с
# 0x40 до 0x200; файл = 0x600 — РОВНО край raw (как у реальных EXE:
# mingw/MSVC не пишут хвост за последней секцией; overlay-хвост —
# отдельная задача «Наработки/E9.5»). Спуск от входа 0x1020:
# 6 инструкций; импортов нет (минимальный макет одного конфликта;
# многим DLL/таблицам — REAL-срез E9.5-3b).
def realpad_image():
    """Собрать чужой образ PE32+ с РЕАЛЬНЫМ паддингом raw > vsize
    (E9.5-3a). Якоря — REALPAD_* ниже; проверяет T-E9-34
    (lab_t_bridge_real.py)."""
    b = bytearray(0x600)
    b[0:2] = b"MZ"
    _st.pack_into("<I", b, 0x3C, 0x100)             # e_lfanew
    b[0x40:0x62] = b"Foreign PE32+ realpad E9.5-3a.\r\r\n$"
    b[0x100:0x104] = b"PE\x00\x00"
    _st.pack_into("<HHIIIHH", b, 0x104, 0x8664, 1, 0, 0, 0, 0xF0,
                  0x0022)
    _st.pack_into("<H", b, 0x118, 0x020B)            # Magic PE32+
    _st.pack_into("<I", b, 0x128, 0x1020)           # вход (в .text)
    _st.pack_into("<Q", b, 0x130, 0x180000000)      # ImageBase (чужой)
    _st.pack_into("<I", b, 0x138, 0x1000)            # SectionAlignment
    _st.pack_into("<I", b, 0x13C, 0x200)            # FileAlignment
    _st.pack_into("<I", b, 0x150, 0x3000)           # SizeOfImage
    _st.pack_into("<I", b, 0x154, 0x400)            # SizeOfHeaders
    _st.pack_into("<H", b, 0x15C, 3)                # Subsystem console
    _st.pack_into("<II", b, 0x190, 0, 0)            # DD[1] — импортов нет
    b[0x208:0x210] = b".text\x00\x00\x00"           # слот 0 (имя 8 Б)
    # vsize 0x40 < raw 0x200 — РЕАЛЬНАЯ развилка паддинга mingw/MSVC
    # (поля слота: vsize, vaddr, raw_size, raw_ptr — как _slot lab_pe)
    _st.pack_into("<IIII", b, 0x210, 0x40, 0x1000, 0x200, 0x400)
    _st.pack_into("<I", b, 0x22C, 0x60000020)      # слот 0: CODE+EXEC+READ
    t = 0x400 + 0x20                    # .text: файл 0x400 + вход 0x20
    b[t + 0x00:t + 0x05] = bytes([0xB8, 0x0B, 0x00, 0x00, 0x00])
    b[t + 0x05:t + 0x0A] = bytes([0xE8, 0x0E, 0x00, 0x00, 0x00])
    b[t + 0x0A:t + 0x0C] = bytes([0x31, 0xC0])
    b[t + 0x0C:t + 0x0D] = bytes([0xC3])
    b[t + 0x18:t + 0x1B] = bytes([0x83, 0xC0, 0x07])
    b[t + 0x1B:t + 0x1C] = bytes([0xC3])
    b[t + 0x1C:t + 0x2C] = b"code tail blob\x00"   # данные после ret
    pad = 0x400 + 0x40                  # паддинг от vsize-края
    b[pad:0x400 + 0x200] = bytes([0xCC]) * (0x200 - 0x40)   # ПАДДИНГ
    return bytes(b)


# якоря realpad_image (выведены из макета; сверка — T-E9-34)
REALPAD_SECTIONS = [
    {"name": ".text", "vsize": 0x40, "vaddr": 0x1000, "raw_size": 0x200,
     "raw_ptr": 0x400, "chars": 0x60000020}]
REALPAD_FACTS = {"entry_off": 0x20, "vsize": 0x40, "raw": 0x200,
                 "target": 0x200, "bss": 0}
REALPAD_INS = [(0x20, "mov", 5), (0x25, "call", 5), (0x2A, "xor", 2),
               (0x2C, "ret", 1), (0x38, "add", 3), (0x3B, "ret", 1)]
