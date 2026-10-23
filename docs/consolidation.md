# 旧技能入口迁移

仅使用过下列旧技能的用户需要本页。新用户直接按 [接入指南](../references/agent-setup.md) 安装 `dst-mod-engineering`。

| 旧名称 | 当前内容去向 |
|---|---|
| `dst-mod-development` / `dst-mod-devkit` | [统一入口](../SKILL.md)及现有核心专题、三个开发验证脚本 |
| `dst-add-cooker-dish` | [独立料理流程](../references/cooker-dishes.md)、[物品与植物](../references/items-food-plants.md) |
| `dst-add-spell` / `dst-custom-stat` | [法术与数值](../references/spells-and-custom-stats.md)、动作、网络和生命周期专题 |
| `dst-character-build` / `dst-swap-build` | [角色与装备美术](../references/character-and-equipment-art.md)、[资源结构](../references/assets-animation.md)、角色与动作专题 |
| `gif-to-dst-anim` | [帧序列与法阵制作](../references/animation-recipes.md)、资源结构与工具专题 |
| `dst-sound-fmod` | [音频与粒子](../references/audio-particles.md) |

## 从旧技能迁移

1. 备份旧安装及用户自定义内容，按上表确认所需专题已覆盖。
2. 安装统一技能并验证 Agent 能读取入口和参考文件。
3. 将不再使用的旧技能移出 Agent 的技能发现目录，更新项目中对旧名称的引用，避免同时加载两套规则。

安装本技能不会自动迁移或删除已有技能。迁移只涉及技能文件，不涉及游戏、Mod 源码、素材或存档。
