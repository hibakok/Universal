"""lab_enc_isa.py — кирпич роста ISA оракула ENC (E6.4c, SPEC/09).

Вход:  операнды M-строки imul (как _Op из lab_enc).
Выход: _enc_imul(ops, ln) -> байты imul r64,r64 (REX.WRB 0F AF /r mod11,
       reg-поле = приёмник); ошибки — EncError("FORMAT AT=XXXX").
Функция: умножение для WALL v2 (idiv входит в общее семейство F7 /ext
       lab_enc._enc_f7; cqo — в SIMPLE) — вынесено из lab_enc.py по
       лимиту 500 строк. Вызывается таблицей ENCODERS lab_enc.
"""
class EncError(ValueError):
    pass


def _err(ln):
    raise EncError("FORMAT AT=%04X" % ln)


def _rex(w, r, x, b):
    v = (w << 3) | (r << 2) | (x << 1) | b
    return 0x40 | v if v else None


def _enc_imul(ops, ln):
    """imul r64, r64 (E6.4c): REX.W 0F AF /r mod11; reg-поле — приёмник."""
    dst, src = ops
    if dst.kind != "reg" or src.kind != "reg" or dst.size != 64 \
            or src.size != 64:
        _err(ln)
    rex = _rex(True, dst.code >= 8, 0, src.code >= 8)
    modrm = 0xC0 | (dst.code & 7) << 3 | (src.code & 7)
    return ([rex] if rex else []) + [0x0F, 0xAF, modrm]
