# 维护与构建

当前版本 `v2026.11.11` 分发唯一 dst-mod-engineering.zip 与 SHA256SUMS.txt，247 条知识与 MCP 共用 knowledge/。用户入口见[README](../README.md)，来源维护见[专页](source-compatibility.md)。

```text
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s dst-kb-service/tests -v
python -B -m unittest discover -s knowledge/tests -v
python -B scripts/build_release.py
python -B scripts/build_release.py --check
```

生成器核对 `knowledge/PACKAGE-MANIFEST.json` 的每个文件、FAMILY-REGISTRY 生成的目录计数（当前 64 + 13 + 110 + 60 = 247 个唯一记录），以及单一证据环境，再从明确允许的文件构建 `dist/release/`。ZIP 内 `RELEASE-MANIFEST.json` 提供版本、记录计数和逐文件哈希；清单不对自身形成循环哈希。固定路径顺序、时间和 ZIP 元数据，使用 DEFLATE 压缩；相同 Python/压缩库下，同一源文件得到相同字节。跨压缩库比较时应以包内逐文件哈希核对内容。`build_web_bundle.py` 是同一命令的兼容入口，不再生成网页或独立 Skill 分包。

构建排除缓存、游戏源码、本地客户端配置、测试夹具、旧知识副本和构建产物。`dist/` 只放发行 ZIP 与校验文件，不复制源码树。不要把含本地恢复 Lua 的 `cache/` 提交或上传。已有生成物被修改或目录中有未知文件时，构建器拒绝覆盖；应先检查差异，或选择新的输出目录。

修改知识或证据必须保留事实、Scope、角色、类型、版本、更正与来源边界，重新绑定公开证据的真实哈希。来源槽必须由用户合法来源恢复；不能绕过原校验器或 Coding HOLD。更新来源另做版本差异维护，不能把历史证据改名为当前来源。

来源身份、逐引用状态与缺口处理统一见[源码维护](source-compatibility.md)，公开版自动检查入口见[更新助手](../references/source-update-assist.md)。

目录/完整模式、错误处理与会话切换见[安装说明](install-and-use.md)。恢复缓存的隔离材料和准备锁均为本地维护状态，打包时排除 cache/。

发布前核对数据、协议、链接与逐文件清单，并按[验证记录](validation.md)报告游戏覆盖范围。