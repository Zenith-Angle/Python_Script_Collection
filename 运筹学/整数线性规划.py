import pandas as pd
from scipy.optimize import linprog

# 提供的数据
towns = ['城镇1', '城镇2']
methods = ['焚烧', '填海', '掩埋']
costs = {
    '运费': {'城镇1': [7.5, 5, 15], '城镇2': [5, 7.5, 12.5]},
    '固定成本': [3850, 1150, 1920],
    '变动成本': [12, 16, 6],
    '处理能力': [1000, 500, 1300],
    '应处理量': {'城镇1': 700, '城镇2': 1200}
}

# 目标函数系数
c = [costs['运费'][town][i] + costs['变动成本'][i] for town in towns for i in range(len(methods))]

# 约束条件
# 每个城镇废物处理量的约束
A_eq = [[1 if j // len(methods) == i else 0 for j in range(len(towns) * len(methods))] for i in range(len(towns))]
b_eq = [costs['应处理量'][town] for town in towns]

# 每种处理方式的能力约束
A_ub = [[1 if j % len(methods) == i else 0 for j in range(len(towns) * len(methods))] for i in range(len(methods))]
b_ub = costs['处理能力']

# 非负约束隐含在bounds中
bounds = [(0, None) for _ in range(len(towns) * len(methods))]

# 求解线性规划
result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

# 解析结果
if result.success:
    decision_vars = result.x.reshape((len(towns), len(methods)))
    solution = pd.DataFrame(decision_vars, index=towns, columns=methods)
    total_cost = result.fun
    print("最优解为：")
    print(solution)
    print("最小总费用为：", total_cost)
else:
    print("无法找到解决方案")
