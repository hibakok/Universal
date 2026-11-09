"""lab_l2_lay.py — раскладка кадровых слотов WALL v1/v2 (SPEC/11 п.5).

Вход:  функция (AST из lab_l2.parse), таблица имён, число параметров
       функций, размеры глобальных переменных.
Выход: need(e) — потребность T-слотов выражения; Layout — базовые слоты
       (параметры; локали: скаляр 1 слот, массив a[n] — n слотов,
       a[0] самый глубокий: адрес a[i] = rbp-8*(p+n-i)), maxd/maxc,
       S-слоты (setb ИЛИ v2-astore), framesize = align16(8*nslots)+0x30.
Функция: кирпич раскладки бэкенда оракула WALL; вызывается
         lab_l2_gen.Gen._func. Разрез по лимиту 500 строк (E6.4c).
"""
from lab_l2_err import WallError            # noqa: F401


def _hex(v):
    return "%X" % v


def _align16(v):
    return (v + 15) & ~15


def need(e):
    """Число T-слотов выражения при генерации с текущей глубины."""
    t = e[0]
    if t == "neg":
        return need(e[1])
    if t == "bin":
        return 1 + max(need(e[2]), need(e[3]))
    if t == "index":                      # v2: база + индекс
        return 1 + max(need(e[1]), need(e[2]))
    if t == "getb":
        return 1 + max(need(e[1]), need(e[2]))
    if t == "call":
        return max([need(a) for a in e[2]] + [0])
    return 0                      # num, name, addr, len


class Layout:
    """Раскладка кадровых слотов функции (SPEC/11 п.5 + v2-массивы).

    Базовые слоты: параметры (по 1) + локали в порядке объявления
    (скаляр 1 слот, массив a[n] — n слотов; a[0] — самый глубокий).
    Адрес элемента i: rbp - 8*(p + n - i), где p — первый слот массива."""

    def __init__(self, fn, names, funcparams, gsizes):
        self.fn = fn
        self.names = names
        self.fp = funcparams
        self.gs = gsizes                   # глобальные: имя -> размер
        base, sizes = {}, {}
        idx = 0
        for n in fn["params"]:
            base[n], sizes[n] = idx, 1
            idx += 1
        for n, s in fn["locals"]:
            base[n], sizes[n] = idx, s
            idx += s
        self.base = base
        self.sizes = sizes
        self.nbase = idx
        self.maxd = self.maxc = 0
        self.setb = self.ext5 = self.astore = False
        self._scan(fn["body"])
        ns = (3 if (self.setb or self.astore) else 0) + \
            (1 if self.ext5 else 0)
        self.nslots = self.nbase + self.maxd + self.maxc + ns
        self.framesize = _align16(8 * self.nslots) + 0x30

    def _upd(self, d):
        self.maxd = max(self.maxd, d)

    def _call(self, name, args):
        kind = self.names.get(name)
        n = len(args)
        self.maxc = max(self.maxc, min(n, 4) if kind == "ext" else n)
        if kind == "ext" and n == 5:
            self.ext5 = True
        for a in args:
            self._scan_expr(a)

    def _scan_expr(self, e):
        """обход выражения: вызовы (в т.ч. вложенные) дают C-слоты"""
        t = e[0]
        if t == "call":
            self._call(e[1], e[2])
        elif t == "bin":
            self._scan_expr(e[2])
            self._scan_expr(e[3])
        elif t in ("neg",):
            self._scan_expr(e[1])
        elif t == "index":                 # v2
            self._scan_expr(e[1])
            self._scan_expr(e[2])
        elif t == "getb":
            self._scan_expr(e[1])
            self._scan_expr(e[2])

    def _scan_cond(self, c):
        for disj in c:                     # v2: цепочки && / ||
            for cmp in disj:
                self._scan_expr(cmp[1])
                self._scan_expr(cmp[2])
                self._upd(1 + max(need(cmp[1]), need(cmp[2])))

    def _scan(self, body):
        for st in body:
            t = st[0]
            if t == "lvar":
                continue
            if t == "assign":
                self._scan_expr(st[2])
                self._upd(need(st[2]))
            elif t == "return":
                if st[1] is not None:
                    self._scan_expr(st[1])
                    self._upd(need(st[1]))
            elif t == "call":
                self._call(st[1], st[2])
            elif t == "setb":
                self.setb = True
                for e in (st[1], st[2], st[3]):
                    self._scan_expr(e)
                    self._upd(need(e))
            elif t == "astore":            # v2: e[i] = v
                self.astore = True
                for e in (st[1][1], st[1][2], st[2]):   # база/индекс/знач.
                    self._scan_expr(e)
                    self._upd(need(e))
            elif t in ("break", "continue"):
                pass
            elif t == "if":
                self._scan_cond(st[1])
                self._scan(st[2])
                self._scan(st[3])
            elif t == "while":
                self._scan_cond(st[1])
                self._scan(st[2])

    # смещения слотов (rbp-относительные, 0-базовый индекс)
    def _off(self, idx):
        return 8 * (idx + 1)

    def local(self, name):
        return self._off(self.base[name])

    def arrbase(self, name):
        """смещение адреса a[0] локального массива (rbp-относительное)"""
        return 8 * (self.base[name] + self.sizes[name])

    def t(self, d):
        return self._off(self.nbase + d - 1)

    def c(self, i):
        return self._off(self.nbase + self.maxd + i - 1)

    def s(self, i):
        return self._off(self.nbase + self.maxd + self.maxc + i)


