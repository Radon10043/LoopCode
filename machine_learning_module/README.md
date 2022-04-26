# 基于全连接神经网络的模糊测试关键字节选择器

## 实验记录

* 2022-04-25 手动实现整型和字符型的二进制编码转换。可将已知类型的数据转换为二进制比特数组
* 2022-04-25 基于二进制比特数组的模型，准确率可达到0.9以上
* 2022-04-25 将每8比特作为一个字节，尝试应用模型，失败，因为模型的每一个x内不能再划分数组
* 2022-04-25 采用NEUZZ代码中的方法，直接读取字符串，使用bytearray转换为字节串，再转换为字节数组，能够训练模型，准确率为0.3以下