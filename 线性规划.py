# 定义线性规划的参数 - 考虑3小时和4小时的班次
from scipy.optimize import linprog

c_combined = [4] * 12 + [3] * 12  # 4小时班次和3小时班次的成本系数

# 新的约束条件
A_combined = []
for i in range(12):
    row = []
    for j in range(10):  # 3小时班次的约束
        if i <= j <= i + 2 and j < 10:
            row.append(-1)
        else:
            row.append(0)
    for j in range(12):  # 4小时班次的约束
        row.append(-1 if i == j else 0)
    A_combined.append(row)

# 使用linprog函数求解
res_combined = linprog(c_combined, A_ub=A_combined, b_ub=required_workers, method='highs')
print(res_combined.x, res_combined.fun)