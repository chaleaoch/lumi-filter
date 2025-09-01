# Quick Start Guide

## Installation

Install lumi_filter using pip:

```bash
pip install lumi-filter
```

## Usage Patterns

lumi_filter supports multiple usage patterns depending on your needs and data sources.

### 1. Manual Filter Model (Peewee ORM)

Define a manual filter model that maps to your Peewee model:

```python
import peewee
from lumi_filter import Model, IntField, StrField

# Define your Peewee model
class User(peewee.Model):
    name = peewee.CharField()
    age = peewee.IntegerField()

# Define your filter model
class UserFilter(Model):
    name = StrField()
    age = IntField()

    class Meta:
        schema = User

# Apply filters using cls_filter method
query = User.select()
request_args = {
    'name__contains': 'john',
    'age__gte': 18
}
filtered_data = UserFilter.cls_filter(query, request_args)
```

This pattern uses the `Model` base class with explicit field definitions and a `Meta.schema` configuration pointing to your Peewee model.

### 2. AutoQueryModel Pattern

Use `AutoQueryModel` for automatic schema detection and filtering:

```python
from lumi_filter.shortcut import AutoQueryModel

# Works with Peewee queries
query = User.select()
request_args = {'name__contains': 'john', 'age__gte': 18}

model = AutoQueryModel(query, request_args)
result = model.filter().order().result()
```

The `AutoQueryModel` class automatically inspects your data source and creates appropriate filter fields, eliminating the need for manual model definition.

### 3. Iterable Data Filtering

Filter Python lists and dictionaries using the same interface:

```python
from lumi_filter.shortcut import AutoQueryModel

users = [
    {'name': 'John Doe', 'age': 25, 'active': True},
    {'name': 'Jane Smith', 'age': 30, 'active': False},
    {'name': 'Bob Johnson', 'age': 35, 'active': True}
]

request_args = {
    'name__iin': 'john',  # Case-insensitive contains
    'active': True
}

model = AutoQueryModel(users, request_args)
filtered_users = model.filter().result()
```

### 4. Pydantic Schema Integration

Define filter models that work with Pydantic schemas:

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
        fields = ['name', 'age']  # Only include specific fields

data = [{'name': 'John', 'age': 25, 'email': 'john@example.com'}]
filtered_data = UserFilter.cls_filter(data, {'name__iin': 'john'})
```

## Lookup Expressions

lumi_filter provides a comprehensive set of lookup expressions for filtering operations:

| Expression | Description | Example |
|------------|-------------|---------|
| `field` or `field__exact` | Exact match | `name: 'John Doe'` |
| `field__!` or `field__ne` | Not equal | `status__!: 'inactive'` |
| `field__gt` | Greater than | `age__gt: 18` |
| `field__gte` | Greater than or equal | `age__gte: 18` |
| `field__lt` | Less than | `age__lt: 65` |
| `field__lte` | Less than or equal | `age__lte: 65` |
| `field__contains` | Contains (case-sensitive) | `name__contains: 'john'` |
| `field__iin` | Contains (case-insensitive) | `name__iin: 'john'` |
| `field__nin` | Not contains | `email__nin: '@temp.com'` |
| `field__in` | In list of values | `status__in: ['active', 'pending']` |
| `field__startswith` | Starts with | `name__startswith: 'John'` |
| `field__endswith` | Ends with | `email__endswith: '.com'` |

### Usage Examples

```python
# String filtering
request_args = {
    'name__iin': 'john',           # Case-insensitive contains
    'email__endswith': '.com',     # Ends with
    'status__in': ['active', 'pending']  # In list
}

# Numeric filtering
request_args = {
    'age__gte': 18,     # Age >= 18
    'age__lt': 65,      # Age < 65
    'score__gt': 80     # Score > 80
}

# Boolean filtering
request_args = {
    'active': True,         # Exact boolean match
    'verified__!': False    # Not equal to False
}
```

## Ordering Results

Control result ordering using the ordering parameter in your request arguments:

```python
request_args = {
    'name__iin': 'john',
    'ordering': 'age,-name'  # Order by age ascending, then name descending
}

model = UserFilter(data, request_args)
result = model.filter().order().result()
```

The ordering parameter accepts a comma-separated list of field names. Prefix field names with `-` for descending order.

## Next Steps

- Explore the [Examples](https://github.com/chaleaoch/lumi_filter/tree/main/example) for more detailed usage patterns
- Check out the [API Reference](../api_reference.md) for comprehensive documentation
