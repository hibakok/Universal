"""lab_t_wallself_emit_cases.py — источники тестов эмитции каркаса
(T-E6-55/56/57/58, срезы C-2/1..C-2/3 + C-3 этапа E6.4d-4/3c).

Только данные: списки (имя, исходник) для секций T-E6-55 (return-
выражения), T-E6-56 (вызовы/getb/индексация; канарейки дефекта №21),
T-E6-57 (статы-имена: присваивания/вызовы-утверждения/astore/
setb; канарейка дефекта №22) и T-E6-58 (guard-эмитция среза C-3:
if/while/else/break/continue, цепочки && / ||, инверсии jcc).
Прогонщик — lab_t_wallself.py.
"""

EXPR_CASES = [
    ("return число", "func main\n  return 42\nend\n"),
    ("return параметры + операции",
     "func add(a, b)\n  return a + b\nend\nfunc main\n  return 0\nend\n"),
    ("все 5 ALU + сдвиги + v2 * / %",
     "func f(a, b, c, d)\n"
     "  return a + b - c | d ^ a & b << 1 >> 2 * 3 / 4 % 5\nend\n"
     "func main\n  return 0\nend\n"),
    ("скобки и приоритеты",
     "func f(a, b, c, d)\n  return (a + b) * (c - d) / 2\nend\n"
     "func main\n  return 0\nend\n"),
    ("унарный минус в цепочке (дефект №20)",
     "func f(a, b)\n  return -a + -3 - --b * 2\nend\n"
     "func main\n  return 0\nend\n"),
    ("глобальные var + массив (load)",
     "var g\nvar h[3]\nfunc main\n  return g + 1\nend\n"),
    ("&локальный массив и &глобаль (addr)",
     "var g\nfunc f(x)\n  var a[4]\n  return &a\nend\n"
     "func main\n  return &g\nend\n"),
    ("len str + глобальный + локальный массив",
     "str s = 'abc'\nvar h[5]\nfunc f(x)\n  var a[7]\n"
     "  return len(s) + len(h) + len(a)\nend\n"
     "func main\n  return 0\nend\n"),
    ("длинная цепочка K=5 + вложенная смесь",
     "func f(a, b, c, d)\n  return a + b + c + d + 1 + 2\nend\n"
     "func g(a, b, c, d)\n"
     "  return ((a + b) * 2 - (c << 1)) % 7 ^ (d & (a - b))\nend\n"
     "func main\n  return 0\nend\n"),
    ("v1 без v2-конструкций (заголовок v1)",
     "func f(a, b)\n  return a & b | a ^ b\nend\n"
     "func main\n  return 1 + 2\nend\n"),
]
CALL_CASES = [
    ("вызов 1/0 аргументов в выражении",
     "func f(x)\n  return x + 1\nend\nfunc g\n  return 7\nend\n"
     "func main\n  return f(2) + g()\nend\n"),
    ("вызов 4 аргументов (ARGREG r9)",
     "func q(a, b, c, d)\n  return a + b + c + d\nend\n"
     "func main\n  return q(1, 2, 3, 4)\nend\n"),
    ("двойная вложенность вызовов (дефект №21)",
     "func h(x)\n  return x * 2\nend\nfunc g(x, y)\n  return x + y\nend\n"
     "func f(x, y)\n  return x - y\nend\n"
     "func main\n  return f(g(h(1), 2), h(g(3, h(4))))\nend\n"),
    ("ext 0/4/5 аргументов (S5 + [rsp+20])",
     "ext GetTickCount\next ReadFile\next WriteFile\n"
     "func main\n  return GetTickCount() + ReadFile(1, 2, 3, 4)"
     " + WriteFile(1, 2, 3, 4, 5)\nend\n"),
    ("getb с &str / массивом / выражениями",
     "str s = 'ABC'\nfunc f(x)\n  var a[4]\n"
     "  return getb(&s, 1) + getb(a, x + 1)\nend\n"
     "func main\n  return getb(&s, 2)\nend\n"),
    ("индексация: массив, цепочка p[0][1], индекс-выражение",
     "var m[3]\nvar g[4]\nfunc f(x)\n  var a[4]\n  var p[2]\n"
     "  return a[x] + p[0][1]\nend\nfunc h(x)\n  return x * 2\nend\n"
     "func main\n  return m[2] + f(1) + g[h(1) + 1]\nend\n"),
    ("вызов-база и скобочная база индексации (откат)",
     "var t[4]\nvar a[4]\nfunc f(x)\n  return t[x]\nend\n"
     "func main\n  return f(0)[1] + (a + 0)[2]\nend\n"),
    ("смесь: вызовы + индексация + getb + операции",
     "str s = 'Q'\nvar a[4]\nfunc f(x, y)\n  return x + y\nend\n"
     "func g(x)\n  return a[x]\nend\n"
     "func main\n  return f(g(1), getb(&s, 0)) * a[2] - f(1, 2)\nend\n"),
    ("глубокая вложенность: вызов в индексе вызова",
     "var a[4]\nfunc f(x)\n  return x + 1\nend\n"
     "func main\n  return a[f(f(a[0]))]\nend\n"),
    ("вызовы в аргументах getb и вложенных индексах",
     "str s = 'XY'\nvar a[4]\nfunc f(x)\n  return x\nend\n"
     "func main\n  return getb(&s, f(1)) + a[a[f(0)]]\nend\n"),
]
STMT_CASES = [
    ("присваивание локали и глобали",
     "var g\nfunc main\n  var i\n  i = 5\n  g = 7\n  return 0\nend\n"),
    ("присваивание с выражениями (вызовы/индексация/getb)",
     "str s = 'AB'\nvar g[4]\nfunc f(x)\n  return x * 2\nend\n"
     "func main\n  var i\n  i = f(3) + g[1] + getb(&s, 0)\n"
     "  g[2] = i + 1\n  return i\nend\n"),
    ("вызов-утверждение func 0..4 аргументов",
     "func a\n  return 1\nend\nfunc b(x)\n  return x\nend\n"
     "func q(x, y, z, w)\n  return x + y + z + w\nend\n"
     "func main\n  a()\n  b(9)\n  q(1, 2, 3, 4)\n  return 0\nend\n"),
    ("вызов-утверждение ext 0/4/5 аргументов",
     "ext GetTickCount\next ReadFile\next WriteFile\n"
     "func main\n  GetTickCount()\n  ReadFile(1, 2, 3, 4)\n"
     "  WriteFile(1, 2, 3, 4, 5)\n  return 0\nend\n"),
    ("astore локальный/глобальный массив (k = 1)",
     "var m[3]\nfunc main\n  var a[4]\n  a[0] = 11\n"
     "  a[1 + 1] = a[0] + 5\n  m[1] = a[2]\n  m[2] = m[1]\n"
     "  return a[0]\nend\n"),
    ("astore цепочка k=2/k=3 + индекс-выражения",
     "var g[4]\nfunc main\n  var p[2]\n  var q[2]\n"
     "  p[0][1] = 9\n  q[0][g[0]][1] = 8\n  g[1] = p[0][1]\n"
     "  return 0\nend\n"),
    ("setb простые и с выражениями/вызовами",
     "str s = 'AB'\nfunc f(x)\n  return x\nend\n"
     "func main\n  var a[4]\n  setb(&s, 0, 65)\n"
     "  setb(a, 1 + 1, 66)\n  setb(&s, f(1), f(2))\n  return 0\nend\n"),
    ("setb + astore + ext5 в одной функции (S + S5)",
     "ext WriteFile\nstr s = 'Q'\nvar g[2]\nfunc f(x)\n  return x\nend\n"
     "func main\n  var i\n  var a[4]\n  i = f(2)\n  a[i] = i + 1\n"
     "  g[0] = a[i]\n  setb(&s, f(0), 81)\n"
     "  WriteFile(1, 2, 3, 4, 5)\n  return i\nend\n"),
    ("канарейка №22 — astore локали не в последней функции",
     "func f(x)\n  var aaa[4]\n  var b\n  aaa[x] = x + 1\n  b = aaa[x]\n"
     "  return b\nend\n"
     "func main\n  var zzz[8]\n  zzz[3] = f(1)\n  return zzz[3]\nend\n"),
    ("смесь всего (присваивания + вызовы + astore + setb)",
     "ext ReadFile\nstr s = 'XYZ'\nvar g[4]\nvar v\n"
     "func f(x, y)\n  return x + y\nend\n"
     "func h(x)\n  var t[2]\n  t[0] = x\n  setb(&s, x, 65)\n"
     "  return t[0]\nend\n"
     "func main\n  var i\n  i = f(1, 2)\n  g[i] = h(i)\n"
     "  v = g[i] + len(s)\n  ReadFile(1, 2, 3, 4)\n  setb(&s, 1, 66)\n"
     "  return v\nend\n"),
]
GUARD_CASES = [
    ("if простой (m=1 — без d/t-меток)",
     "func main\n  var i\n  i = 0\n  if i == 0\n    i = 1\n"
     "  end\n  return i\nend\n"),
    ("if/else (lfalse = _if<k>)",
     "func main\n  var i\n  i = 0\n  if i < 2\n    i = 1\n"
     "  else\n    i = 2\n  end\n  return i\nend\n"),
    ("while простой (:_w<k> + обратный jmp)",
     "func main\n  var i\n  i = 0\n  while i < 3\n    i = i + 1\n"
     "  end\n  return i\nend\n"),
    ("while + break + continue (скан bstk)",
     "func main\n  var i\n  var s\n  i = 0\n  s = 0\n"
     "  while i < 10\n    i = i + 1\n    if i == 3\n"
     "      continue\n    end\n    if i == 8\n      break\n"
     "    end\n    s = s + i\n  end\n  return s\nend\n"),
    ("if с || m=2 (d/t-метки + jmp t)",
     "func main\n  var i\n  i = 0\n  if i == 1 || i == 0\n"
     "    i = 9\n  end\n  return i\nend\n"),
    ("if с || m=3 + конъюнкты &&",
     "func f(a, b, c, d)\n"
     "  if a == 1 && b == 2 || c == 3 && d == 4 || b == 5\n"
     "    return 1\n  end\n  return 0\nend\n"
     "func main\n  return f(1, 2, 0, 0)\nend\n"),
    ("while с || условием (m=2)",
     "func main\n  var i\n  var s\n  i = 10\n  s = 0\n"
     "  while i > 27 || s > 100\n    i = i - 1\n    s = s + 2\n"
     "  end\n  return i\nend\n"),
    ("все 6 операторов сравнения (инверсии jcc)",
     "func f(a, b)\n  if a == b\n    return 1\n  end\n"
     "  if a != b\n    return 2\n  end\n  if a < b\n    return 3\n"
     "  end\n  if a <= b\n    return 4\n  end\n  if a > b\n"
     "    return 5\n  end\n  if a >= b\n    return 6\n  end\n"
     "  return 0\nend\nfunc main\n  return f(1, 2)\nend\n"),
    ("вложенные if/while/if-else (сквозной счётчик k)",
     "func main\n  var i\n  var s\n  i = 0\n  s = 0\n"
     "  while i < 5\n    i = i + 1\n    if i == 2\n"
     "      s = s + 10\n    else\n      if i == 3\n"
     "        s = s + 100\n      end\n    end\n    s = s + 1\n"
     "  end\n  return s\nend\n"),
    ("условия с выражениями/вызовами/индексацией",
     "var g[4]\nfunc f(x)\n  return x * 2\nend\n"
     "func main\n  var a[2]\n  a[0] = 5\n  if a[0] + 1 == 6\n"
     "    if f(2) == g[0] + 4\n      return 1\n    end\n"
     "  end\n  return 0\nend\n"),
    ("&& цепочка m=1 (выход как v1)",
     "func f(a, b, c)\n  if a > 0 && b > 0 && c > 0\n"
     "    return 1\n  end\n  return 0\nend\n"
     "func main\n  return f(1, 2, 3)\nend\n"),
    ("if/else + while в теле if",
     "func main\n  var i\n  var s\n  s = 0\n"
     "  if s == 0\n    i = 0\n    while i < 3\n      s = s + 2\n"
     "      i = i + 1\n    end\n  else\n    s = 7\n  end\n"
     "  return s\nend\n"),
]
