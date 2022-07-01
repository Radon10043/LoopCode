# -*- codeing = utf-8 -*-
# @Time : 2022/6/12 11:09
# @Author : Lowry
# @File : real_time_data.py
# @Software : PyCharm


from time import sleep
import matplotlib.pyplot as plt
import pandas as pd

i = 0


def recordData():
    totalTime = 12
    sleep(2)
    file = '/home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14/obj-afl/out1/fuzzer_stats'
    # file = '/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out/fuzzer_stats'
    # file = '/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out_afl_origin/fuzzer_stats'
    x_axis_data = [0]   # x轴数据：时间
    y_axis_data = [0]   # y轴数据：覆盖路径数量
    global i
    # 字典中的key值即为csv中列名
    dataframe = pd.DataFrame({'时间': x_axis_data, '覆盖路径数量': y_axis_data})
    dataframe.to_csv("/home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14/obj-afl/out1/graphData.csv", index=False)
    # dataframe.to_csv("/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out/graphData.csv", index=False)
    while i < totalTime:
        sleep(1800)    # 1800s/30min读取一次数据
        i += 0.5
        with open(file) as f:
            num = int(f.readlines()[6].split(':')[1])
        x_axis_data.append(i)
        y_axis_data.append(num)
        dataframe = pd.DataFrame({'时间': x_axis_data, '覆盖路径数量': y_axis_data})
        # 将DataFrame存储为csv,index表示是否显示行名，default=True
        dataframe.to_csv("/home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14/obj-afl/out1/graphData.csv", index=False)
        # dataframe.to_csv("/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out/graphData.csv", index=False)
        # dataframe.to_csv("/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out_afl_origin/graphData.csv", index=False)

    plt.rcParams['savefig.dpi'] = 500  # 图片像素
    plt.rcParams['figure.dpi'] = 500  # 分辨率

    plt.figure(figsize=(8, 6))  # 定义图的大小
    plt.xlabel("time")  # X轴标签
    plt.ylabel("totalPath")  # Y轴坐标标签
    plt.title("record half an hour")  # 曲线图的标题

    plt.plot(x_axis_data, y_axis_data)  # 绘制曲线图
    plt.savefig('/home/lowry/Documents/LoopCode/scripts/libxml2-2.9.14/obj-afl/out1/path_pic.jpg')  # 保存该图片
    # plt.savefig('/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out/path_pic.jpg')  # 保存该图片
    # plt.savefig('/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out_afl_origin/path_pic.jpg')  # 保存该图片
    plt.show()


time = []


def recordModelTime():
    time.append(i)
    # 字典中的key值即为csv中列名
    dataframe = pd.DataFrame({'时间': time})

    # 将DataFrame存储为csv,index表示是否显示行名，default=True
    dataframe.to_csv("/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out/modelTime.csv", index=False)


# recordData()
