import pydot
import sys
import traceback
import os

import networkx as nx


def coloring(path: str):
    """对path下的dot-files里的图进行染色

    Parameters
    ----------
    path : str
        路径下应包含dot-files文件夹, loop_recorded, LoopBBs.txt

    Notes
    -----
    _description_
    """
    loopBBs = list()    # 存储所有循环BB名字的list
    loopRecord = list() # 存储覆盖到循环BB测试用例数量的list, 与loopBBs的下标是对应的
    loopBBDict = dict() # <str, int>: key是循环BB名字, value是覆盖到key的测试用例数量
    with open(os.path.join(path, "LoopBBs.txt")) as f:
        loopBBs = f.readlines()
    with open(os.path.join(path, "loop_recorded")) as f:
        loopRecord = f.readlines()
    for i in range(min(len(loopBBs), len(loopRecord))): # 将loopBBs和loopRecord相应地存储到loopBBDict
        loopBBs[i] = loopBBs[i].rstrip("\n")
        loopBBDict[loopBBs[i]] = list()
        loopBBDict[loopBBs[i]] = [int(num) for num in loopRecord[i].split("-")]

    dotPaths = list()   # 存储所有dot图绝对路径的list
    for file in os.listdir(os.path.join(path, "dot-files")):
        if os.path.splitext(file)[1] != ".dot" or file == "callgraph.dot": # 跳过非dot文件和callgraph.dot文件
            continue
        dotPaths.append(os.path.join(path, "dot-files", file))

    # 创建输出文件夹
    outPath = os.path.join(path, "dot-files-coloring")
    if not os.path.exists(outPath):
        os.makedirs(outPath)

    # 对dot图进行染色, 并填入相关信息
    colorRes = str()    # 染色结果, 表示哪些文件染了色
    for dotPath in dotPaths:

        # 先获取dot图的所有节点(引用)
        filename = os.path.basename(dotPath)
        print("coloring %s ..." % filename)
        hasColored = False
        graph = pydot.graph_from_dot_file(dotPath)[0]
        nodes = graph.get_nodes()

        # 获得节点的label, 并进行染色操作
        for node in nodes:
            nodeLabel = node.obj_dict["attributes"]["label"].lstrip("\"{").rstrip(":}\"")
            if nodeLabel in loopBBs:  # 如果节点是循环BB, 且覆盖次数大于0, 就进行染色与添加覆盖次数
                if loopBBDict[nodeLabel][0] > 0:
                    node.obj_dict["attributes"]["fillcolor"] = "cyan"
                else:
                    node.obj_dict["attributes"]["fillcolor"] = "cyan3"
                node.obj_dict["attributes"]["style"] = "filled"
                node.obj_dict["attributes"]["label"] = "\"{" + nodeLabel + ":|" + str(loopBBDict[nodeLabel][0]) + "-" + str(loopBBDict[nodeLabel][1]) + "}\""
                hasColored = True

        # 如果这张图染色了, 就记录一下, 将染色后的图输出到文件夹中
        if hasColored:
            colorRes += "对%s进行了染色\n" % filename
            graph.write_raw(os.path.join(outPath, filename))

    # 染色结果也输出
    with open(os.path.join(path, "colorRes.txt"), mode="w") as f:
        f.write(colorRes)

    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请输入包含dot-files, loop_recorded和LoopBBs.txt的文件夹路路径")
    else:
        path = sys.argv[1]
        try:
            print("即将进行染色...")
            coloring(path)
        except:
            print("出现错误:")
            traceback.print_exc()