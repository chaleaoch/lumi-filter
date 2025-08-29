# lumi_filter

[![PyPI version](https://badge.fury.io/py/lumi-filter.svg)](https://badge.fury.io/py/lumi-filter)
[![Build Status](https://travis-ci.org/chaleaoch/lumi_filter.svg?branch=main)](https://travis-ci.org/chaleaoch/lumi_filter)
[![Coverage Status](https://coveralls.io/repos/github/chaleaoch/lumi_filter/badge.svg?branch=main)](https://coveralls.io/github/chaleaoch/lumi_filter?branch=main)

一个简单好用的 Python 过滤库。无论你的数据来自 Peewee、Pydantic 模型，还是普通的列表字典，都可以用同样的方式进行过滤和排序。

## 主要功能

- **统一的过滤接口**: 对 Peewee 查询、Pydantic 模型和列表字典使用相同的 API。
- **自动生成模型**: 使用 `AutoQueryModel` 从数据源自动生成过滤模型。
- **丰富的查询表达式**: 支持 `__gt`, `__in`, `__icontains` 等多种查询。
- **类型安全**: 内置过滤值的验证和类型转换。
- **易于扩展**: 可以轻松自定义 `FilterField`。
- **支持嵌套字段**: 使用点 `.` 表示法过滤嵌套字典。

## 安装

```bash
pip install lumi-filter
```

## 快速上手

### 1. 过滤 Peewee 查询

首先，定义 Peewee 模型和 `lumi_filter.Model`。

```python
import peewee
from lumi_filter import Model, StrField, IntField

# 1. 定义 Peewee 模型
class User(peewee.Model):
    name = peewee.CharField()
    age = peewee.IntegerField()
    email = peewee.CharField()

    class Meta:
        database = peewee.SqliteDatabase(':memory:')

# 2. 定义过滤模型
class UserFilter(Model):
    name = StrField()
    age = IntField()

    class Meta:
        schema = User

# 3. 应用过滤器
query = User.select()
request_args = {
    'name__contains': 'john',  # 包含 'john' (大小写敏感)
    'age__gte': 18           # age >= 18
}

filtered_query = UserFilter.cls_filter(query, request_args)

# 也可以链式调用
model_instance = UserFilter(query, request_args)
result = model_instance.filter().order().result()
```

### 2. 使用 `AutoQueryModel` 自动生成模型

如果不想手动定义 `Model`，可以用 `AutoQueryModel` 来快速过滤。

```python
from lumi_filter.shortcut import AutoQueryModel

# 适用于 Peewee 查询
query = User.select()
request_args = {'name__icontains': 'JOHN', 'age__lt': 30} # icontains 是大小写不敏感的查询

model = AutoQueryModel(query, request_args)
filtered_results = model.filter().order().result()
```

### 3. 过滤字典列表

`lumi_filter` 同样适用于普通的字典列表。

```python
from lumi_filter.shortcut import AutoQueryModel

users = [
    {'name': 'John Doe', 'age': 25, 'active': True},
    {'name': 'Jane Smith', 'age': 30, 'active': False},
    {'name': 'Bob Johnson', 'age': 35, 'active': True}
]

request_args = {
    'name__icontains': 'john',  # 包含 'john' (大小写不敏感)
    'active': True
}

model = AutoQueryModel(users, request_args)
filtered_users = model.filter().result()
# filtered_users 结果: [{'name': 'John Doe', 'age': 25, 'active': True}]
```

### 4. 结合 Pydantic 模型

你也可以用 Pydantic 模型作为 schema 定义。

```python
import pydantic
from lumi_filter import Model

class UserSchema(pydantic.BaseModel):
    name: str
    age: int
    email: str

class UserFilter(Model):
    class Meta:
        schema = UserSchema
        fields = ['name', 'age']  # 指定要过滤的字段

# 数据可以是匹配 schema 的字典列表
data = [{'name': 'John', 'age': 25, 'email': 'john@example.com'}]
filtered_data = UserFilter.cls_filter(data, {'name__icontains': 'john'})
```

## 查询表达式

在 `request_args` 中可以使用以下查询表达式：

| 表达式        | 描述                      | 示例                        |
|---------------|----------------------------------|--------------------------------|
| ` ` (无)      | 精确匹配                      | `{'name': 'John Doe'}`         |
| `!`           | 不等于                        | `{'status!': 'inactive'}`      |
| `__gt`        | 大于                     | `{'age__gt': 18}`              |
| `__gte`       | 大于等于         | `{'age__gte': 18}`             |
| `__lt`        | 小于                        | `{'age__lt': 65}`              |
| `__lte`       | 小于等于            | `{'age__lte': 65}`             |
| `__in`        | 在列表中 (用于数字类型)    | `{'id__in': '1,2,3'}`          |
| `__contains`  | 包含子字符串 (大小写敏感) | `{'email__contains': '@a.com'}` |
| `__icontains` | 包含子字符串 (大小写不敏感) | `{'name__icontains': 'john'}`  |

## 排序

使用 `ordering` 字段来控制排序。

- 多个字段用逗号 `,` 分隔。
- 降序在字段名前加 `-`。

```python
request_args = {
    'name__icontains': 'j',
    'ordering': 'age,-name'  # 按 age 升序, 再按 name 降序
}

model = AutoQueryModel(users, request_args)
ordered_users = model.filter().order().result()
```

## 高级用法

### 自定义过滤字段

你可以创建自己的 `FilterField` 来处理特殊的数据类型或验证逻辑。

```python
from lumi_filter.field import FilterField
import datetime

class CustomDateField(FilterField):
    """一个可以解析多种日期格式的自定义字段"""
    SUPPORTED_LOOKUP_EXPR = frozenset({'', '!', 'gt', 'lt', 'gte', 'lte'})

    def parse_value(self, value):
        if isinstance(value, datetime.date):
            return value, True
        try:
            # 支持多种格式
            for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y'):
                try:
                    return datetime.datetime.strptime(value, fmt).date(), True
                except ValueError:
                    continue
            return None, False
        except (ValueError, TypeError):
            return None, False

class MyFilter(Model):
    birth_date = CustomDateField()
    name = StrField()
```

### 嵌套字段过滤

对于嵌套字典，使用点 `.` 表示法。`lumi_filter` 会自动处理。

```python
users = [
    {
        'name': 'John',
        'profile': {
            'age': 25,
            'location': {'city': 'New York'}
        }
    }
]

request_args = {
    'profile.age__gte': 21,
    'profile.location.city__icontains': 'york'
}

model = AutoQueryModel(users, request_args)
result = model.filter().result()
```

## 支持的字段类型

- `IntField`: 整数
- `StrField`: 字符串
- `DecimalField`: `Decimal` 类型
- `BooleanField`: 布尔值 (接受 'true', 'false', '1', '0')
- `DateField`: 日期 (解析 'YYYY-MM-DD')
- `DateTimeField`: 日期时间 (解析 'YYYY-MM-DDTHH:MM:SS')

## 依赖

- Python 3.8+
- `peewee` >= 3.17.1
- `pydantic` >= 2.5.3

## 开发

### 运行测试

首先，安装开发依赖：

```bash
pip install -e .[dev]
```

然后，运行测试：

```bash
pytest
```

### 生成覆盖率报告

在 `htmlcov/` 目录下生成覆盖率报告：

```bash
pytest --cov=lumi_filter --cov-report=html
```

## 许可证

本项目基于 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Pull Request！

1. Fork 本仓库。
2. 创建你的功能分支 (`git checkout -b feature/amazing-feature`)。
3. 提交你的修改 (`git commit -m 'Add some amazing feature'`)。
4. 推送到分支 (`git push origin feature/amazing-feature`)。
5. 新建一个 Pull Request。
