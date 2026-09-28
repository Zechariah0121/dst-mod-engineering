# 维护与贡献

本页供修改技能、知识库或打包器的贡献者使用。安装与使用见 [README](../README.md)。

## 检查与构建

在仓库根目录安装 `requirements.txt`，然后执行：

```text
python -B -m unittest discover -s tests -v
python -B scripts/build_web_bundle.py
python -B scripts/build_web_bundle.py --check
python -B dst-engineering-kb/tools/validate.py
```

进入 `dst-kb-service` 后运行 `python -B -m unittest discover -s tests -v`。CI 在 Windows/Linux 上执行这些检查，不运行 DST 游戏。

修改文档后从源文件重新生成 `dist/web/`，不要手改生成文件。完整网页阅读包和技能 ZIP 只包含使用资料与开发辅助工具；维护记录、整合历史和发布脚本留在源码仓库。

## 发布输入

只从审查过的仓库文件构建。`<!-- local-only -->` 是打包器的拒绝标记，不是自动脱敏器；发布前仍需检查文件与 ZIP 内容。不要提交凭证、存档或未经授权的第三方资源。

知识库公开派生包由 `scripts/build_public_kb.py` 接收显式来源生成。它保留证据等级和纠错关系，更新包内来源哈希、发布溯源与 Manifest；非空输出默认拒绝覆盖，`--replace-generated` 仅接受清单和哈希完整的既有生成包。导出不能替代内容与授权审查。

## 提交变更

说明具体问题、适用范围与验证结果。知识修订遵循知识库的 Governance 和 Correction 流程；测试候选不能改写为已执行结果。版本相关事实注明核验范围。历史验证见 [验证记录](validation.md)。
