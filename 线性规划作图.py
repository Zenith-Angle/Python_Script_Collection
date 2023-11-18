# 假设我们已经有了最优解 x1 和 x2
x1 = 150.0
x2 = 70.0

# 车间每天可用加工工时
workshop_hours = [300, 540, 440, 300]

# 车间加工能力利用情况
workshop_utilization = [
    2 * x1,  # 车间1
    3 * x2,  # 车间2
    2 * x1 + 2 * x2,  # 车间3
    1.2 * x1 + 1.5 * x2  # 车间4
]

# 对偶价格（根据您之前的信息）
dual_prices = [50.0, 0.0, 200.0, 0.0]

# 计算常数项变化范围
for i, (utilization, hours, dual_price) in enumerate(zip(workshop_utilization, workshop_hours, dual_prices)):
    if dual_price > 0:  # 如果对偶价格大于0，约束是紧的
        # 可增加的最大工时（理论上无上限，因为增加工时会增加利润，但实际上可能受到其他因素的限制）
        increase_range = float('inf')
    else:  # 如果对偶价格等于0，约束不是紧的
        # 可减少的最大工时（直到这个车间的工时利用率达到下一个整数生产单位）
        increase_range = hours - utilization

    print(f"车间{i + 1}:")
    print(f"    可增加的加工工时上限: {increase_range}")
    print(f"    可减少的加工工时下限: {utilization - (hours if utilization < hours else 0)}")
