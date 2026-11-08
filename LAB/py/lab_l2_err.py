"""lab_l2_err.py — ошибка компиляции WALL (лист-кирпич, без зависимостей).

Вход:  сообщение (str) и номер строки исходника (int, с 1; 0 — вне строк).
Выход: исключение WallError с полем .line.
Функция: единый тип ошибки оракула lab_l2/lab_l2_gen и будущего wall.exe
         (контракт ошибок — SPEC/11 п.10).
"""


class WallError(Exception):
    def __init__(self, msg, line):
        super().__init__("строка %d: %s" % (line, msg))
        self.line = line
        self.msg = msg
