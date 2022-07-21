# Scripts

- jasper
  - [jasper-fuzz.sh](#jasper-fuzz)

- libming
  - [libming-fuzz.sh](#libming-fuzz)

- libxml2
  - [libxml2-fuz.sh](#libxml2-fuzz)


### jasper-fuzz

- 文件名: jasper-fuzz.sh
- 功能: 下载jasper, 并进行模糊测试
- 参数
  - $1: 要使用的fuzzer
  - $2: 重复测试多少次 (数字)
- 前置条件
  - 确认是否需要更改被测项目的版本
  - 更改脚本中各fuzzer的路径
  - 更改测试时间
  - 更改afl-model中是否开启py
- 使用例
```shell
./jasper-fuzz.sh afl 5
```


### libming-fuzz

- 文件名: libming-fuzz.sh
- 功能: 下载libming, 并进行模糊测试
- 参数
  - $1: 要使用的fuzzer
  - $2: 重复测试多少次 (数字)
- 前置条件
  - 确认是否要更改被测项目的版本
  - 更改脚本中各fuzzer的路径
  - 更改测试时间
  - 更改afl-model中是否开启py
- 使用例
```shell
./libming-fuzz.sh afl 5
```


### libxml2-fuzz

- 文件名: libxml2-fuzz.sh
- 功能: 下载libxml2, 并进行模糊测试
- 参数
  - $1: 要使用的fuzzer
  - $2: 重复测试多少次 (数字)
- 前置条件
  - 确认是否要更改被测项目的版本
  - 更改脚本中各fuzzer的路径
  - 更改测试时间
  - 更改afl-model中是否开启py
- 使用例
```shell
./libxml2-fuzz.sh afl 5
```