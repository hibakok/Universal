"""wall_self_data.py — генератор данных эмитции каркаса wall.wall (E6.4d-4/3a).

Вход:  KERNEL/L2-WALL/wall_data.b2 (блоб :strblob — 2046 байт канонических
       строк эмиттера SPEC/11 п.8; источник тот же, что у wall.exe).
Выход: KERNEL/L2-WALL/wall_self_blob.wall — часть каркаса ТОЛЬКО с
       объявлениями str: блоб дополнен нулями до 2048 байт и закодирован
       hex-строками (2 ЗАГЛАВНЫЕ hex-цифры на байт, 8 литералов по 512
       символов — предел литерала SPEC/11 п.9), плюс таблица смещений
       (имя -> off/len, ДЕСЯТИЧНЫЕ) в комментариях для авторов частей
       wall_self_y/e.wall.
Функция: каркас (WALL v2) не может держать байты >= 0x80 в str-литералах
         (SPEC/11 п.2: байты 0x20..0x7E + экраны), а канонические строки
         содержат кириллицу UTF-8 — поэтому блоб хранится hex-кодировкой и
         декодируется в кучу при старте (blob_dec -> окно sblob области
         outmem, см. wall_self_e.wall / корень wall.wall). Смещения строк
         в блобе каркаса == смещениям wall.exe (единый канон).
Запуск: python3 LAB/ai/wall_self_data.py  (из корня репозитория)
"""
import os
import re

SRC = os.path.join("KERNEL", "L2-WALL", "wall_data.b2")
OUT = os.path.join("KERNEL", "L2-WALL", "wall_self_blob.wall")

BLOB = 2046            # байт в :strblob wall_data.b2
PAD = 2048             # блоб каркаса: дополнен нулями до 2048 (8x256)
CHUNK = 512            # символов на литерал = 256 байт


def load_blob():
    lines = open(SRC, "r", encoding="latin-1").read().split("\n")
    inside = False
    blob = []
    for l in lines:
        if l.startswith(":strblob"):
            inside = True
            continue
        if inside:
            if l.startswith("DB "):
                blob += [int(x, 16) for x in l[3:].split()]
            else:
                break
    if len(blob) != BLOB:
        raise SystemExit("strblob: ожидалось %d байт, получено %d"
                         % (BLOB, len(blob)))
    return bytes(blob)


def load_tab():
    """strtab2: имя -> (off, len) — порядок DD-строк."""
    lines = open(SRC, "r", encoding="latin-1").read().split("\n")
    inside = False
    tab = []
    for l in lines:
        if l.startswith(":strtab2"):
            inside = True
            continue
        if inside:
            m = re.match(r"DD ([0-9A-F]+) ([0-9A-F]+) ; (\S+)", l)
            if m:
                tab.append((m.group(3), int(m.group(1), 16),
                            int(m.group(2), 16)))
            elif l and not l.startswith(";"):
                break
    return tab


def main():
    blob = load_blob() + b"\x00" * (PAD - BLOB)
    tab = load_tab()
    out = []
    out.append("; wall_self_blob.wall — данные эмитции каркаса (E6.4d-4/3a)")
    out.append("; Паспорт: KERNEL/L2-WALL/wall_self_blob.wall | слой L2 |")
    out.append("; роль: ДАННЫЕ канона эмиттера SPEC/11 п.8 — единый блоб")
    out.append("; строк (те же 2046 байт, что :strblob wall_data.b2, + 2")
    out.append("; нуля до 2048) в hex-кодировке: литералы sd0..sd7 по 512")
    out.append("; ЗАГЛАВНЫХ hex-символов (2 символа/байт, 256 байт на")
    out.append("; литерал — предел 512 байт SPEC/11 п.9). Кириллица канона")
    out.append("; (байты >= 0x80) невыразима в str-литерале WALL (SPEC/11")
    out.append("; п.2: байты 0x20..0x7E) — поэтому блоб хранится hex и")
    out.append("; декодируется при старте (blob_dec части wall_self_e.wall")
    out.append("; в окно sblob = outmem+0 области outmem, см. корень).")
    out.append("; ГЕНЕРАТОР: LAB/ai/wall_self_data.py (НЕ редактировать")
    out.append("; вручную); регенерация при изменении wall_data.b2.")
    out.append(";")
    out.append("; Таблица строк (смещения/длины — ДЕСЯТИЧНЫЕ, годятся для")
    out.append("; литералов WALL; вызовы: out_str/off/len, out_line — +LF):")
    for name, off, ln in tab:
        out.append(";   %-10s off=%-5d len=%d" % (name, off, ln))
    out.append("")
    for k in range(PAD // (CHUNK // 2)):         # 8 литералов по 256 байт
        part = blob[k * (CHUNK // 2):(k + 1) * (CHUNK // 2)]
        out.append("str sd%d = '%s'" % (k, part.hex().upper()))
    open(OUT, "w", encoding="utf-8", newline="\n").write(
        "\n".join(out) + "\n")
    print("OK: %s (%d строк, блоб %d Б, таблица %d записей)"
          % (OUT, len(out), PAD, len(tab)))


if __name__ == "__main__":
    main()
