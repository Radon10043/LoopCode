# 基于全连接神经网络的模糊测试关键字节选择器

## 实验记录

* 2022-04-25 手动实现整型和字符型的二进制编码转换。可将已知类型的数据转换为二进制比特数组
* 2022-04-25 基于二进制比特数组的模型，准确率可达到0.9以上
* 2022-04-25 将每8比特作为一个字节，尝试应用模型，失败，因为模型的每一个x内不能再划分数组
* 2022-04-25 采用NEUZZ代码中的方法，直接读取字符串，使用bytearray转换为字节串，再转换为字节数组，能够训练模型，准确率为0.3以下
* 2022-05-20 参数: `layer=(3,3,3,), top_k=None, max_feature=100, select_bb_size=2`.
  需要注意的是，现在选取bb的标准是**这批**数据里最少覆盖的`select_bb_size`个bb

|          | index | time limit | afl                                        | afl-model-guide                                | afl-no-havoc | afl-model-guide-no-havoc |
|----------|-------|------------|--------------------------------------------|------------------------------------------------|--------------|--------------------------|
| swftophp | 1     | -          | 49min with 1713 paths and 132 uniq crashes | 37min with 1937 paths / 109 uniq crashes / ?   |              |                          |
| swftophp | 2     | 30min      | 1466 paths / 101 uniq crashes              | 1685 paths / 101 uniq crashes / 14 train model |              |                          |
| swftophp | 3     | 30min      | 1414 paths / 95 uniq crashes               | 1719 paths / 115 uniq crashes / 24 train model |              |                          |
| swftophp | 4     | 60min      | 1841 paths / 125 uniq crashes              | 2581 paths / 182 uniq crashes / 49 train model |              |                          |
| swftophp | 5     | 30min      |                                            |                                                | 902 / 99     | 1078 / 78 / 24           |