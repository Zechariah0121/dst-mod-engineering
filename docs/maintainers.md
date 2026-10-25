# 维护与构建

用户安装与使用见根 [README](../README.md)。当前发行只有一个 `dst-mod-engineering.zip` 和配套 `SHA256SUMS.txt`，Skill、187 条公开知识和 MCP 共用唯一 `knowledge/`。当前运行来源环境为 `759671`；历史版本在 Git 历史中保留。

```text
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s dst-kb-service/tests -v
python -B -m unittest discover -s knowledge/tests -v
python -B scripts/build_release.py
python -B scripts/build_release.py --check
```

生成器核对 `knowledge/PACKAGE-MANIFEST.json` 的每个文件、目录中的 64 + 13 + 110 个唯一记录，以及单一运行环境，再从明确允许的文件构建 `dist/release/`。ZIP 内 `RELEASE-MANIFEST.json` 提供版本、记录计数和逐文件哈希；清单不对自身形成循环哈希。固定路径顺序、时间和 ZIP 元数据，使用 DEFLATE 压缩；相同 Python/压缩库下，同一源文件得到相同字节。跨压缩库比较时应以包内逐文件哈希核对内容。`build_web_bundle.py` 是同一命令的兼容入口，不再生成网页或独立 Skill 分包。

构建排除缓存、游戏源码、本地客户端配置、测试夹具、旧知识副本和构建产物。`dist/` 只放发行 ZIP 与校验文件，不复制源码树。不要把含本地恢复 Lua 的 `cache/` 提交或上传。已有生成物被修改或目录中有未知文件时，构建器拒绝覆盖；应先检查差异，或选择新的输出目录。

修改知识或证据必须保留事实、Scope、角色、类型、版本、更正与来源边界，重新绑定公开证据的真实哈希。来源槽必须由用户合法来源恢复；不能绕过原校验器或 Coding HOLD。更新来源另做版本差异维护，不能把历史证据改名为当前来源。

公开发布前运行适当检查，并明确报告实际验证范围。单元测试、来源准备、MCP 连接与一次查询均不代表 DST 游戏、远端客户端、视觉或音频已通过。
