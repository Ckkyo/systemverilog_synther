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

这是测试版，您可以将 test_files/testX 替换为您自己的 SVA 语句文件，然后修改 main.py 中的 test_cases = [(xxx, xxx)] 来指定您想要综合的测试文件。  

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