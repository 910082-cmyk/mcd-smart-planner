# 麦当劳 MCP 工具说明

麦麦智配的所有数据底座均为麦当劳中国官方 MCP Server。在 WorkBuddy「连接器」中配置 `mcd-mcp` 后即可由模型实时调用。

## 连接器配置（streamablehttp）

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": { "Authorization": "Bearer ${MCD_MCP_TOKEN}" }
    }
  }
}
```

Token 通过麦当劳 MCP 控制台申请；配置仅使用环境变量占位符，禁止写入真实 Token。

## 本项目实际使用的四个工具

### 1. `query-meals` —— 菜单查询
- **输入**：`storeCode`（门店编码，如 `3390081`）。
- **返回**：在售餐品列表（名称、分类 `categories`、价格、商品图、促销标签）。
- **用途**：抓取种子菜单、固化官方 15 大分类顺序（`menuOrder`）。
- **看板字段**：`name` / `currentPrice` / `originalPrice` / `cat` / `tags` / `kcal` / `image`。

### 2. `calculate-price` —— 价格计算
- **输入**：餐品组合。
- **返回**：最终实付金额，**单位为人民市分**，使用前须 ÷100。
- **用途**：优惠比价、购物车实付的官方回验（看板 `currentPrice` 推算仅为参考）。

### 3. `list-nutrition-foods` —— 营养查询
- **返回**：餐品营养成分（热量等），**全国静态营养库，不含价格**。
- **用途**：热量配餐。与 `query-meals` 的价格分属两套数据，配餐采用交集策略（仅对有热量数据的单品参与，套餐类自动排除）。

### 4. `query-stores` —— 门店查询
- **返回**：附近门店的地址、距离、营业状态、营业时间、是否支持预约。
- **用途**：点单建议、出行方式推导。
- **边界**：该工具**不提供**实时客流、排队时长或繁忙度，门店推荐不含实时路况与排队预估。

## 调用约定

- 涉及真实下单金额，必须使用 `calculate-price` 回验。
- `create-order` 会真实产生费用，**须在用户明确确认后**调用，禁止主动下单。
- 数据时效：种子数据为离线演示用途，实际消费以麦当劳官方渠道实时结果为准。
