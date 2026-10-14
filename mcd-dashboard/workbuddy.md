# WorkBuddy 开发上下文（workbuddy.md）

> 本文件记录使用 WorkBuddy 开发「麦麦智配」参赛项目的对话上下文，用于核验是否符合 M-CODE 2026 联动活动奖励条件。
> 项目仓库：`https://github.com/910082-cmyk/mcd-smart-planner`

## 项目背景

参赛者希望通过麦当劳官方 MCP 能力，构建一个面向「消费决策」的实用产品，参加 M-CODE 2026 程序员创意开发大赛。核心诉求：把分散的菜单 / 价格 / 营养 / 门店数据整合为一个可视化、可交互的决策看板，并具备强传播力（差异化于榜单中大量纯脚本项目）。

## 与 WorkBuddy 的协作过程

### 阶段一：数据获取与基座搭建
- **用户**：从麦当劳 MCP 抓取真实菜单、营养、门店数据，作为看板数据源。
- **WorkBuddy**：调用麦当劳 MCP 工具（`query-meals` / `calculate-price` / `list-nutrition-foods` / `query-stores`）实测抓取，固化为 `data/seed-data.json`（121 项菜单 / 61 项营养 / 5 家长沙门店）；编写 `scripts/build_menu_order.py` 按官方 15 大分类顺序重构菜单。

### 阶段二：看板原型与品牌贴合
- **用户**：做 Web 可视化看板，要更像麦当劳官方设计。
- **WorkBuddy**：以官方品牌色（`#FFC72C` / `#DA291C`，已联网核验）与 App 6.0 大图卡片为基准，分批改进：票券形优惠券、全局悬浮结算条、emoji 图标替换为品牌 SVG、顶部导航图标化、深色主题、取餐方式分段控件等。

### 阶段三：3D 金拱门品牌舞台
- **用户**：M 标志要做 3D，菜单舞台用 Three.js 化。
- **WorkBuddy**：放弃手绘 SVG（几何不准），改用官方矢量 M 经 ExtrudeGeometry 挤出；构建金属反射舞台、体积光、粒子尘埃、拖拽旋转；并内置 WebGL 降级（失败则显示官方矢量 M + 2D 大图，绝不白屏）。Three.js 本地化 `vendor/`，摆脱 CDN 网络依赖。

### 阶段四：交互体验与无障碍优化
- **用户**：系统优化点击 / 悬停 / 滚动 / 表单 / 页面切换等交互。
- **WorkBuddy**：落地 Toast 轻提示、购物车徽标、按压 / 焦点态、搜索防抖、参数收敛、计算中态、WAI-ARIA Tabs、图片三级降级、prefers-reduced-motion 遵循、WCAG 对比度修正等 16 项优化，输出《交互体验优化报告》。

### 阶段五：稳定性修复
- **用户**：反馈页面偶发空白 / 3D 异常。
- **WorkBuddy**：定位并修复 hero IIFE 在真实浏览器抛错导致整段脚本中止的根因（Canvas2D 不可链式调用 `g2.arc(...).fill()`）；为初始化与 3D 构建加 try/catch 降级；在浏览器截图通道受限的环境下，用无头 Edge + DOM 回显探针替代完成验证。

### 阶段六：参赛交付物生成
- **用户**：补齐比赛必需的文档与 Skill 包。
- **WorkBuddy**：生成 `README.md` / `MCP_INTEGRATION.md` / `CONTEST_DECLARATION.md`（官方原文，一字不改）/ `mcp-config.example.json` / 本文件，并把空壳 Skill 目录填充为可用的 `mcd-smart-planner` Skill 包。

## WorkBuddy 在其中的作用

- **设计伙伴**：品牌色核验、视觉评审（P0 / P1 / P2 分级）、3D 视觉方案。
- **开发伙伴**：编写 / 重构前端与 Python 构建脚本，定位并修复 WebGL、CORS、图片裁切等真实 bug。
- **调试伙伴**：在浏览器截图通道受限的环境下，建立「本地服务 + 状态码 + 像素分析 + DOM 探针」的可靠验证体系。
- **交付伙伴**：按官方规则生成不可改的参赛声明与必需文档，封装 Skill 包。

## 使用的 WorkBuddy 能力

- 设计模式（UI / 视觉稿评审与落地）
- 代码生成与重构（HTML / JS / Python）
- 连接器（麦当劳 MCP 调用）
- 文档生成（Markdown 参赛文档）

## 合规声明

项目不含真实 Token / 密钥 / 凭证，配置仅使用环境变量占位符；所有数据均为参赛演示用途，以麦当劳官方渠道实时结果为准。
