# 工具回归测试

在仓库根目录运行：

```sh
python -m pip install -r requirements.txt
python -m compileall -q scripts tests
python -m unittest discover -s tests -v
```

测试会在临时目录创建 ZIP、Mod 副本和日志，并用短命 Python 子进程模拟日志流。
`fixtures/` 中的 Lua 是为测试自行编写的极简输入；`vanilla_stub` 仅表示测试替身，
不包含 Klei 游戏源码，也不定义真实 DST API。测试不下载、启动或修改游戏。

范围包括 ZIP 路径与覆盖保护、Lua 解析与主客机声明分离、唯一副本、配置序列化、
本轮结果标记、超时、进程提前退出和完成后的错误。它们验证工具行为，不能证明
某个 Mod 在 DST 中正确运行。真实无头验收须在 Windows 本机使用自己的游戏安装
单独执行；画面、声音和真实客户端联网仍需另外验收。
