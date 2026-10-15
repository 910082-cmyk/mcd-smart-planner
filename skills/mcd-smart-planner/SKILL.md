---
name: 麦麦智配
description: 基于麦当劳官方 MCP 的消费决策助手。当用户咨询「麦当劳吃什么 / 套餐推荐 / 怎么点最划算 / 优惠券 / 积分兑换 / 热量配餐 / 附近门店 / 取餐方式」时触发。提供热量配餐、优惠最大化、点单建议、积分折算、食物查询与菜单浏览六大能力，并指导调用麦当劳 MCP 工具进行实时校验。
---

# 麦麦智配（McDonald's Smart Planner）

## 定位

把麦当劳中国官方 MCP 能力（菜单 / 价格 / 营养 / 门店）整合为一个面向「消费决策」的统一助手：吃什么、怎么搭配热量不超标、用哪张券最划算、哪家店现在营业、积分怎么花最值。它不是单纯罗列菜单，而是给出可执行的决策建议。

## 何时使用

- 用户问「麦当劳吃什么 / 有什么推荐 / 点什么套餐」
- 用户关心热量、减肥、健身饮食搭配
- 用户想省钱、比价、用优惠券、查积分兑换
- 用户问「附近哪家麦当劳营业 / 怎么去 / 自取还是外卖」
- 用户提供了麦当劳相关场景（聚餐、单人餐、出行途中）

## 决策工作流

1. **离线分析（默认）**：调用 `scripts/planner.py` 基于项目内已固化的 `data/seed-data.json` 快速给出方案，无需联网，响应即时。
2. **实时校验（可选）**：在 WorkBuddy「连接器」中启用 `mcd-mcp` 后，调用麦当劳 MCP 工具获取最新菜单 / 价格 / 营养 / 门店，重新生成 seed 后重算，保证数据时效。
3. **金额回验**：任何涉及真实下单金额的结论，必须用 `calculate-price` 官方回验，不要仅凭 `currentPrice` 推算。
4. **下单守卫**：`create-order` 会真实产生费用，必须在用户明确确认后才可调用；禁止主动下单。

## 调用的麦当劳 MCP 工具

| 工具 | 用途 | 本项目用法 |
| --- | --- | --- |
| `query-meals` | 菜单查询（名称/分类/价格/图/标签） | 抓取种子菜单、官方分类顺序 |
| `calculate-price` | 价格计算（返回**分**，需 ÷100） | 优惠比价、购物车实付回验 |
| `list-nutrition-foods` | 营养查询（热量等，全国静态库，无价格） | 热量配餐 |
| `query-stores` | 门店查询（地址/距离/营业状态） | 点单建议、出行方式 |

详细说明见 [references/mcp_tools.md](references/mcp_tools.md)；数据字段见 [references/seed_schema.md](references/seed_schema.md)。

## 脚本接口（scripts/planner.py）

所有命令输出 JSON，解析后用语自然转述给用户即可。

```bash
# 热量配餐：目标 800 千卡，容差 ±20%，按「每千卡单价」最优排序
python scripts/planner.py kcal --target 800 --tol 0.2 --sort per

# 优惠最大化：购物车（code:数量），叠加麦金卡与积分后的最优实付
python scripts/planner.py deal --cart 511781:1,9900005456:2

# 点单建议：2 人、1.5km 内、步行、到店自取
python scripts/planner.py advise --people 2 --maxd 1500 --tp walk --mode 1

# 积分当钱花：当前积分折算价值、距最低兑换档进度、可兑券种
python scripts/planner.py points

# 食物查询：按名称查价格/热量/营养/可兑积分券
python scripts/planner.py search --q 巨无霸

# 购物车结算：件数 / 已省 / 合计
python scripts/planner.py cart --cart 511781:1,9900005456:2

# 菜单浏览：按分类/关键词/价格排序列出在售餐品
python scripts/planner.py menu --cat 饮品 --sort price
```

输出示例见 [templates/example_outputs.md](templates/example_outputs.md)。

## 能力映射（给模型的建议）

- **「吃点低热量的」/「减脂期怎么点」** → `kcal`（目标热量 + 容差），取 `per` 最优方案，并提示单餐占比全天推荐。
- **「怎么点最划算」/「帮我比价」** → 先 `menu` 或 `search` 选定餐品加入购物车（即 `--cart` 参数），再 `deal` 给出分阶段比价；强调需用 `calculate-price` 回验。
- **「附近哪家店营业」/「带孩子去哪」** → `advise`（人数/距离/出行/取餐方式），给出最近门店 + 推荐理由 + 备选 + 边界声明。
- **「我积分能换什么」** → `points`，展示折算价值、最低兑换档进度、可兑列表，并提示「先领券再考虑积分」。
- **「巨无霸多少钱/多少热量」** → `search`，返回价格、热量、营养与可兑积分券。

## 合规与边界

- 配置仅使用环境变量占位符（`${MCD_MCP_TOKEN}`），禁止在仓库中写入真实 Token / 密钥。
- 麦当劳 MCP **不提供**门店实时客流、排队时长或繁忙度数据；门店推荐仅基于距离、营业状态、预约能力与取餐方式推导，不含实时路况与排队预估。
- 营养 / 热量仅供参考，不构成医疗或专业建议；餐品信息、价格及供应状态以麦当劳官方渠道实时结果为准。
- 本项目非麦当劳官方产品。

## 数据时效说明

`data/seed-data.json` 为 2026-10-12 从麦当劳 MCP 实测抓取的种子数据，仅供离线演示。若需时效数据，请在 WorkBuddy 中调用麦当劳 MCP 工具刷新后重新生成 seed。
