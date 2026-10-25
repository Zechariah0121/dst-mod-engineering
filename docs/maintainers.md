# 维护与构建

安装与使用见根README。`knowledge/`是当前187条公开知识；旧`dst-engineering-kb/`仅保留早期公开参考数据。
不要把`cache/`提交或打包：其中含用户本地恢复的游戏源码、准备凭据及派生索引。

```text
python -B -m unittest discover -s tests -v
python -B scripts/build_web_bundle.py
python -B scripts/build_web_bundle.py --check
python -B -m unittest discover -s dst-kb-service/tests -v
```

生成器按当前knowledge/PACKAGE-MANIFEST.json核对文件，将知识数据同时带入Skill和网页阅读ZIP；完整包另外带MCP与本地准备工具。
修改知识或证据必须保留事实、Scope、角色和来源边界，使用明确公开的证据重新绑定真实哈希，不能只改摘要消除校验错误。
源码槽必须由用户合法来源恢复；不为方便分发修改原validator或绕过HOLD。更新来源时另做版本差异维护。
旧64条导出器仅用于旧格式，不用于重建当前Native合集。历史服务测试另存compatibility/v0.1，不冒称当前API保持旧字段。
