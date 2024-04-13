from sympy import symbols, Eq, solve

# 定义变量
x, y = symbols('x y')

# 设置等式
eq1 = Eq(x + y, 40)
eq2 = Eq(x, 2/3 * y)

# 解决等式
solution = solve((eq1,eq2), (x, y))

# 输出凯琳的钱
print(f"凯琳有 £{solution[x]}")