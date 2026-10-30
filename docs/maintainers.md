# 维护与构建

用户安装与使用见根 [README](../README.md)。当前版本 `v2026.10.30.1` 只有一个 `dst-mod-engineering.zip` 和配套 `SHA256SUMS.txt`，Skill、210 条登记知识和 MCP 共用唯一 `knowledge/`。`source_epoch=759671` 保留为证据基线，本次核验的来源输入为 `760944 / build 26306684`；历史版本在 Git 历史中保留。

```text
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s dst-kb-service/tests -v
python -B -m unittest discover -s knowledge/tests -v
python -B scripts/build_release.py
python -B scripts/build_release.py --check
```

生成器核对 `knowledge/PACKAGE-MANIFEST.json` 的每个文件、FAMILY-REGISTRY 生成的目录计数（当前 64 + 13 + 110 + 23 = 210 个唯一记录），以及单一证据环境，再从明确允许的文件构建 `dist/release/`。ZIP 内 `RELEASE-MANIFEST.json` 提供版本、记录计数和逐文件哈希；清单不对自身形成循环哈希。固定路径顺序、时间和 ZIP 元数据，使用 DEFLATE 压缩；相同 Python/压缩库下，同一源文件得到相同字节。跨压缩库比较时应以包内逐文件哈希核对内容。`build_web_bundle.py` 是同一命令的兼容入口，不再生成网页或独立 Skill 分包。

构建排除缓存、游戏源码、本地客户端配置、测试夹具、旧知识副本和构建产物。`dist/` 只放发行 ZIP 与校验文件，不复制源码树。不要把含本地恢复 Lua 的 `cache/` 提交或上传。已有生成物被修改或目录中有未知文件时，构建器拒绝覆盖；应先检查差异，或选择新的输出目录。

修改知识或证据必须保留事实、Scope、角色、类型、版本、更正与来源边界，重新绑定公开证据的真实哈希。来源槽必须由用户合法来源恢复；不能绕过原校验器或 Coding HOLD。更新来源另做版本差异维护，不能把历史证据改名为当前来源。

本版来源准备面向单份合法 `760944 / build 26306684 scripts.zip`，不要求旧版源码。核心必需载荷槽保持严格；机制研究从整 ZIP 身份锁改为逐引用报告文件/范围匹配、变化或缺失，研究缺口保留未知。历史比较节点以 `metadata_only` 保留原快照、哈希、行范围与上游引用，不作为当前已恢复源码证明。210 条记录的原知识陈述、Scope 和 HOLD 不因来源准备策略改变而自动升级。具体目标身份、必要范围收窄及验证边界见 [源码维护](source-compatibility.md)。

公开目录模式只提供导航与显式审阅，不承担完整模式的 Coding 上下文、源码恢复或原版 Source/Identity Guards。`auto` 对来源未准备或 `PACKAGE_CHANGED`，完整核验公开文件清单后选择两工具审阅并报告原因；已准备缓存损坏、无效激活及公开数据不可信仍保持可见错误。维护入口及依赖未知边界见 [源码维护](source-compatibility.md)。两工具与九工具在服务启动时选定，准备后需重启会话。损坏的恢复构建在 `cache/runtime/` 内隔离保留，准备锁随进程退出自动释放；不要把隔离材料加入发行包。

公开发布前运行适当检查，并明确报告实际验证范围。单元测试、来源准备、MCP 连接与一次查询均不代表 DST 游戏、远端客户端、视觉或音频已通过。
