# lumi_filter

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/chaleaoch/lumi_filter)

A powerful and flexible data filtering library for Python that provides a unified interface for filtering and ordering data across different sources.

## Features

- **Universal Filtering Interface**: Work with Peewee ORM queries, Pydantic models, and iterable data structures using the same API
- **Automatic Field Detection**: Automatically map field types from your data sources to appropriate filter fields
- **Rich Lookup Expressions**: Support for complex filtering operations including equality, comparison, and text matching
- **Type Safety**: Built-in validation and type conversion for filter values
- **Extensible**: Easy to extend with custom field types and operators
- **Backend Agnostic**: Seamlessly switch between different data backends

## Installation

```bash
pip install lumi-filter
```

## Quick Start

### Basic Usage with Peewee ORM

```python
import peewee
from lumi_filter import Model, IntField, StrField

# Define your Peewee model
class User(peewee.Model):
    name = peewee.CharField()
    age = peewee.IntegerField()
    email = peewee.CharField()

# Define your filter model
class UserFilter(Model):
    name = StrField()
    age = IntField()
    
    class Meta:
        schema = User

# Apply filters
query = User.select()
request_args = {
    'name__in': 'john',  # Contains 'john'
    'age__gte': 18       # Age >= 18
}

filtered_data = UserFilter.cls_filter(query, request_args)
```

### Automatic Model Generation

```python
from lumi_filter.shortcut import AutoQueryModel

# Automatically generate filter model from data
query = User.select()
request_args = {'name__in': 'john', 'age__gte': 18}

# AutoQueryModel inspects the query and creates appropriate filters
model = AutoQueryModel(query, request_args)
result = model.filter().order().result()
```

### Working with Dictionaries

```python
from lumi_filter.shortcut import AutoQueryModel

# Sample data
users = [
    {'name': 'John Doe', 'age': 25, 'active': True},
    {'name': 'Jane Smith', 'age': 30, 'active': False},
    {'name': 'Bob Johnson', 'age': 35, 'active': True}
]

request_args = {
    'name__in': 'john',  # Case-insensitive contains
    'active': True
}

model = AutoQueryModel(users, request_args)
filtered_users = model.filter().result()
```

### Pydantic Integration

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

# Use with any iterable data that matches the schema
data = [{'name': 'John', 'age': 25, 'email': 'john@example.com'}]
filtered_data = UserFilter.cls_filter(data, {'name__in': 'john'})
```

## Lookup Expressions

lumi_filter supports various lookup expressions for fine-grained filtering:

- **Exact match**: `field` or `field__exact`
- **Not equal**: `field__!` or `field__ne`
- **Comparison**: `field__gt`, `field__gte`, `field__lt`, `field__lte`
- **Contains**: `field__in` (case-sensitive), `field__iin` (case-insensitive)
- **Not contains**: `field__nin`

### Examples

```python
request_args = {
    'name': 'John Doe',           # Exact match
    'age__gte': 18,               # Age >= 18
    'age__lt': 65,                # Age < 65
    'email__in': '@gmail.com',    # Contains '@gmail.com'
    'status__!': 'inactive'       # Not equal to 'inactive'
}
```

## Ordering

Control result ordering using the `ordering` parameter:

```python
request_args = {
    'name__in': 'john',
    'ordering': 'age,-name'  # Order by age ascending, then name descending
}

model = UserFilter(data, request_args)
result = model.filter().order().result()
```

## Advanced Usage

### Custom Filter Fields

```python
from lumi_filter.field import FilterField
import datetime

class CustomDateField(FilterField):
    """Custom date field with flexible parsing"""
    
    SUPPORTED_LOOKUP_EXPR = frozenset({'', '!', 'gt', 'lt', 'gte', 'lte'})
    
    def parse_value(self, value):
        if isinstance(value, datetime.date):
            return value, True
        try:
            # Support multiple date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y']:
                try:
                    return datetime.datetime.strptime(value, fmt).date(), True
                except ValueError:
                    continue
            return None, False
        except (ValueError, TypeError):
            return None, False

class UserFilter(Model):
    birth_date = CustomDateField()
    name = StrField()
```

### Nested Field Support

For nested data structures, use dot notation:

```python
# Data structure
users = [
    {
        'name': 'John',
        'profile': {
            'age': 25,
            'location': {'city': 'New York'}
        }
    }
]

# Filter nested fields
request_args = {
    'profile__age__gte': 21,
    'profile__location__city__in': 'york'
}

model = AutoQueryModel(users, request_args)
result = model.filter().result()
```

## Supported Field Types

- **IntField**: Integer values with comparison operations
- **StrField**: String values with text matching operations
- **DecimalField**: Decimal values for precise arithmetic
- **BooleanField**: Boolean values with flexible string parsing
- **DateField**: Date values with format parsing
- **DateTimeField**: DateTime values with format parsing

## Requirements

- Python 3.12+
- peewee >= 3.18.2
- pydantic >= 2.11.7

## Development

### Running Tests

```bash
pytest
```

### Coverage Report

```bash
pytest --cov=lumi_filter --cov-report=html
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
