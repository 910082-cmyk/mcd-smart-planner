# planner.py 输出示例

以下为 `scripts/planner.py` 在真实种子数据上的输出节选，供模型理解返回结构后转述为用户语言。

## kcal —— 热量配餐（目标 800，±20%，最优每千卡单价）

```json
{
  "target": 800, "tol": 0.2, "count": 3665,
  "top": [
    { "rank": 1, "set": [
        {"name": "那么大鸡排（椒盐风味）", "kcal": 385, "currentPrice": 14},
        {"name": "圆筒冰淇淋", "kcal": 93, "currentPrice": 5},
        {"name": "派", "kcal": 232, "currentPrice": 8.5} ],
      "kcal": 710, "price": 27.5, "per": 0.0387, "dayRatio": 31 }
  ]
}
```
转述：「方案 1：那么大鸡排 + 圆筒冰淇淋 + 派，共 710 千卡、¥27.5，占全天推荐 31%，每千卡单价最低。」

## deal —— 优惠最大化（培根安格斯×1 + 麦辣三件套×2）

```json
{
  "stages": [
    {"stage": "菜单原价", "amount": 126.5},
    {"stage": "促销优惠后", "amount": 101.5},
    {"stage": "积分兑换叠加", "amount": -17.9, "basis": "17.9元板烧可乐组合（500 积分）"},
    {"stage": "最优实付", "amount": 83.6, "basis": "较原价省 ¥42.9（34%）"}
  ],
  "final": 83.6, "saved": 17.9
}
```

## advise —— 点单建议（2 人，1.5km 内，步行，到店自取）

```json
{
  "recommend": {"storeName": "麦当劳长沙五一路平和堂餐厅", "distance": 196,
                "etaMin": 2, "mode": "到店自取（beType=1）", "travel": "步行",
                "people": 2, "businessStatus": true, "reservation": true},
  "reasons": ["步行 196 米，约 2 分钟", "营业中", "支持预约下单", "2 人建议选三件套，菜单 14 款可选"],
  "boundary": "MCP 不提供实时客流/排队数据，推荐仅基于可核实数据。"
}
```

## points —— 积分当钱花

```json
{
  "availablePoint": 538.2, "availableCount": 9,
  "cheapestTier": {"spuName": "6.9元可乐麦炫酷", "point": 50},
  "bestValue": {"spuName": "21.9元巨无霸可乐组合", "perPoint": 0.027},
  "equivalentYuan": 14.7, "progressToCheapest": 100,
  "status": "已过最低兑换档（50 积分），当前可兑 8 张"
}
```
