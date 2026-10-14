# seed-data.json 字段说明

`data/seed-data.json` 是从麦当劳 MCP Server 实测抓取的种子数据（2026-10-12，门店 3390081 长沙五一路平和堂），已固化为看板内联 `SEED`，亦供 `scripts/planner.py` 离线分析。`scripts/build_menu_order.py` 可据官方分类顺序重建。

## 顶层结构

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `_meta` | object | 数据来源、门店、抓取时间、`imageCount`、`menuOrderSource` |
| `stores` | array | 门店列表（5 家长沙门店） |
| `menu` | object | 餐品表，键为商品 code，值见下 |
| `nutrition` | object | 营养库，键为餐品名，值为营养对象（全国静态库，无价格） |
| `pointsProducts` | array | 积分兑换商品（含面值与过期时间） |
| `coupons` | object | `{ claimed: string[], claimable: string[] }` 已领 / 可领券描述 |
| `account` | object | 积分账户 |
| `menuOrder` | array | 官方 15 大分类顺序，每项 `{ name, codes: string[] }` |
| `menuGlobalOrder` | array | 全局去重后的有序餐品 code 列表 |

## menu 项字段

```json
{
  "name": "培根安格斯厚牛堡",
  "currentPrice": 34.5,
  "originalPrice": 34.5,
  "cat": "安格斯MAX\n厚牛堡",
  "tags": ["单品", "100%安格斯牛肉"],
  "kcal": 707,
  "image": "https://menu-img.mcd.cn/.../MS_511781_320.png",
  "discountType": "促销优惠"   // 可选，取值：促销优惠 / 随单购麦金卡优惠
}
```

- `kcal` 为 `null` 时表示套餐类无单项营养数据（配餐模块自动排除）。
- `image` 来自麦当劳官方 CDN（`menu-img.mcd.cn`），该 CDN 不返回 CORS 头，不可直接做 WebGL 纹理。

## stores 项字段

```json
{
  "storeCode": "3390081",
  "storeName": "麦当劳长沙五一路平和堂餐厅",
  "address": "黄兴中路88号平和堂商厦负一楼",
  "distance": 196,
  "businessStatus": true,
  "businessStartTime": "00:00",
  "businessEndTime": "23:59",
  "reservation": true
}
```

## pointsProducts 项字段

```json
{ "spuId": 17073, "spuName": "6.9元可乐麦炫酷", "point": 50,
  "selling": "6.9元可乐麦炫酷1份", "downTime": "2026-12-30 23:59:59", "catName": "到店专用" }
```

- `selling` 为 `"X元…"` 文本，`scripts/planner.py` 用正则提取面值数字（与看板 JS 口径一致）。
- `downTime` 为过期时间，已过期项在积分折算 / 比价中自动排除。

## account 字段

```json
{ "availablePoint": 538.2, "accumulativePoint": 717.5, "usedPoint": 40,
  "expiredPoint": 139.3, "currency": "麦享会积分" }
```

## nutrition 项字段

```json
{ "kcal": 513, "protein": 27, "fat": 26, "carb": 42, "sodium": 961, "calcium": 171 }
```
