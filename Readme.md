# SVA Synther

## 语言转换与综合

将 SystemVerilog 断言(SVA)转换为可综合的状态机(Verilog)
支持 NFA (非确定性有限自动机) 和 DFA (确定性有限自动机) 的生成

## 可以对生成的状态机进行自动化测试验证
支持多种测试模式：  
原始 SVA 仿真测试 <-> NFA 运行测试  
原始 SVA 仿真测试 <-> DFA 运行测试  
原始 SVA 仿真测试 <-> Verilog FSM(通过 SSH 连接到安装了 VCS 的虚拟机仿真)  

## 如何使用

本工具为测试版，您可以参考 test_files 目录下的 SVA 文件格式，编写或替换为您自己的 SVA 语句文件。  
使用方法如下（命令行参数说明见下）：  
- 通过 `-f` 或 `--file_` 指定一个或多个待综合的 SVA 文件路径（可用空格分隔多个文件），如：  
  ```
  python main.py -f test_files/ok_files/test0.sv -o output_dir
  ```
- 通过 `-F` 或 `--folder_` 指定一个或多个包含 SVA 文件的文件夹（可用空格分隔多个文件夹），如：  
  ```
  python main.py -F test_files/ok_files -o output_dir
  ```
- `-o` 或 `--output_` 必须指定输出目录，若不存在会自动创建。  
- `--suffix_` 可指定需要解析的文件后缀，默认为 `.sv .svh .svp .v`。  
- `--img_format` 可选，指定生成图片的格式（svg、png、jpg），默认为 svg。  
- 参考： python main.py -o output/ -F test_files/mini_test_files

输入文件格式请参考 test_files 目录下的示例。  
详细参数说明可通过 `-h` 查看帮助。  

## demo 文件夹  

展示了一些 SVA 语句示例及其 Verilog FSM  

如果感兴趣，欢迎通过 GitHub 或邮箱与我联系：
📧 1169149623@qq.com
💻（或在 GitHub 上提问）

我会乐意解答您的问题或探讨相关内容。 

## 环境  

需要安装以下包：  

```
networkx  
matplotlib  
IPython
pydot // 用于图片生成
paramiko
ply
jinja2
```  

```
graphviz // 用于图片生成
```