# -*- codeing = utf-8 -*-
# @Time : 2022/6/12 11:09
# @Author : Lowry
# @File : real_time_data.py
# @Software : PyCharm


from time import sleep
import matplotlib.pyplot as plt
import pandas as pd


def recordData(tmp=None, stats=None):
    totalTime = 120
    sleep(60)
    graphData = tmp + '/graphData.csv'
    x_axis_data = [0]  # x轴数据：时间
    y_axis_data = [0]  # y轴数据：覆盖路径数量
    i = 0
    # 字典中的key值即为csv中列名
    dataframe = pd.DataFrame({'时间': x_axis_data, '覆盖路径数量': y_axis_data})
    dataframe.to_csv(graphData, index=False)
    while i < 1440:
        i += 1
        sleep(60)  # 1min读取一次数据
        with open(stats) as f:
            num = int(f.readlines()[6].split(':')[1])
        y_axis_data.append(num)
        x_axis_data.append(i)
        dataframe = pd.DataFrame({'时间': x_axis_data, '覆盖路径数量': y_axis_data})
        dataframe.to_csv(graphData, index=False)

    plt.rcParams['savefig.dpi'] = 500  # 图片像素
    plt.rcParams['figure.dpi'] = 500  # 分辨率

    plt.figure(figsize=(8, 6))  # 定义图的大小
    plt.xlabel("time(s)")  # X轴标签
    plt.ylabel("totalPath")  # Y轴坐标标签
    plt.title("record per min")  # 曲线图的标题

    plt.plot(x_axis_data, y_axis_data)  # 绘制曲线图
    plt.savefig(tmp + '/path_pic.jpg')  # 保存该图片
