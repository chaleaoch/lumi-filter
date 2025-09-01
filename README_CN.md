# lumi_filter

> 具体用例请参考示例：
[示例代码](https://github.com/chaleaoch/lumi_filter/tree/main/example)

lumi_filter 是一个强大而灵活的数据过滤库，旨在简化您在 Python 应用程序中跨不同数据源过滤和排序数据的方式。无论您处理的是数据库查询、API 响应还是内存数据结构，lumi_filter 都能提供统一、直观的接口，使复杂的过滤操作变得轻而易举。lumi_filter 受 Django REST Framework 的过滤系统启发，但进行了重新设计，以支持多种后端和数据源。对 Flask 友好兼容。

lumi_filter 是一个基于模型的过滤库，它弥合了不同数据源和过滤需求之间的差距。其核心是为以下数据源过滤提供一致的 API：

- **Peewee ORM 查询** - 通过自动生成 SQL 直接进行数据库过滤
- **Pydantic 模型** - 使用类型验证过滤结构化数据
- **可迭代数据结构** - 过滤列表、字典和其他 Python 集合

该库消除了为每个数据源编写不同过滤逻辑的需要，允许您一次定义过滤需求并普遍应用。

## 为什么选择 lumi_filter？

### 统一的过滤接口

假设您需要在整个应用程序中实现过滤功能，该功能需要同时处理数据库记录和 API 响应。没有 lumi_filter 的话，您通常需要为每个数据源编写单独的过滤逻辑：

#### 数据库过滤（Peewee）

```python
query = Product.select().where(Product.name.contains("apple") & Product.price >= 100)
```

#### 列表过滤（Python）

```python
filtered_products = [p for p in products if "apple" in p["name"] and p["price"] >= 100]
```

使用 lumi_filter，您只需定义一次过滤模型，就可以在任何地方使用它：

```python
class FilterProduct(Model):
    name = StrField(source="name")
    price = DecimalField(source="price")
```

#### 适用于数据库查询

```python
db_filter = FilterProduct(Product.select(), request.args)
filtered_query = db_filter.filter().result()
```

#### 适用于可迭代数据

```python
list_filter = FilterProduct(products_list, request.args)
filtered_list = list_filter.filter().result()
```

## 丰富的过滤表达式

lumi_filter 支持一套全面的过滤运算符，超越了简单的相等性检查：

| 运算符 | 描述 | 示例 |
|--------|------|------|
| (无) | 精确匹配 | name=Apple |
| __in | 在值列表中 | name__in=Apple,Orange |
| __nin | 不在值列表中 | name__nin=Apple,Orange |
| __gte | 大于或等于 | price__gte=100 |
| __lte | 小于或等于 | price__lte=500 |
| __contains | 包含子字符串 | name__contains=apple |
| __startswith | 以...开头 | name__startswith=A |
| __endswith | 以...结尾 | name__endswith=e |

## 自动类型检测和映射

该库能智能检测字段类型并将其映射到适当的过滤字段，支持：

- 带模式匹配的字符串字段
- 带范围比较的数字字段
- 带时间过滤的日期/时间字段
- 带真值过滤的布尔字段
- 支持点表示法的嵌套字段

## TODO

- [ ] 支持分页
- [ ] 支持字段级别的权限控制
- [ ] 支持字段级别的自定义过滤
- [ ] 支持更多 ORM（如 SQLAlchemy）
