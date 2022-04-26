import sys
import traceback


def filter(path: str):
    """将文件中重复的基本块删掉

    Parameters
    ----------
    path : str
        存储循环BB名的文件路径

    Notes
    -----
    _description_
    """
    with open(path, mode="r") as f:
        loopBBs = f.readlines()
    loopBBs = sorted(set(loopBBs))

    f= open(path, mode="w")
    for loopBB in loopBBs:
        f.write(loopBB)
    f.close()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("还没有输入LoopBBs.txt的路径.")
    else:
        path = sys.argv[1]
        try:
            print("即将对文件%s进行过滤..." % path)
            filter(path)
            print("过滤完成!")
        except:
            print("出现错误:")
            traceback.print_exc()
