# Lumi Filter Example Application

This directory contains a comprehensive Flask application demonstrating the various filtering capabilities of the lumi_filter library. The example showcases different filtering approaches, from basic model filtering to advanced automatic field introspection.

## Features Demonstrated

- **Basic Model Filtering**: Explicit field definitions with custom filter models
- **Automatic ORM Filtering**: Auto-generation of filter fields from Peewee ORM queries
- **Iterable Data Filtering**: Filtering of list/dictionary data structures
- **Advanced Meta Configuration**: Using Meta classes for automatic field generation
- **Complex Relationships**: Filtering across joined tables and foreign keys

## Setup and Installation

### Prerequisites

- Python 3.8+
- Flask
- Peewee ORM
- lumi_filter

### Installation

1. Install dependencies:

```bash
cd example
pip install -r requirements.txt
```

2. Set up the Flask application:

```bash
export FLASK_APP=example.py
export FLASK_ENV=development
```

3. Run the application:

```bash
flask run
```

The application will be available at `http://localhost:5000`

## API Endpoints

### 1. Basic Model Filtering (`/model/`)

Demonstrates explicit field definitions with custom filter models.

**Endpoint**: `GET /model/`

**Features**:

- Explicit field definitions
- Type-safe filtering
- Custom field configurations
- Relationship filtering

**Example Requests**:

```bash
# Get all products
curl -X GET "http://localhost:5000/model/"

# Filter by product name (case-insensitive contains)
curl -X GET "http://localhost:5000/model/?name__icontains=apple"

# Filter by price range
curl -X GET "http://localhost:5000/model/?price__gte=2.0&price__lte=5.0"

# Filter by active status
curl -X GET "http://localhost:5000/model/?is_active=true"

# Filter by category
curl -X GET "http://localhost:5000/model/?category_name=Fruit"

# Complex filtering with multiple conditions
curl -X GET "http://localhost:5000/model/?name__icontains=berry&is_active=true&price__lt=6.0"

# Ordering (ascending by price)
curl -X GET "http://localhost:5000/model/?ordering=price"

# Ordering (descending by creation date)
curl -X GET "http://localhost:5000/model/?ordering=-created_at"
```

### 2. Automatic ORM Filtering (`/auto/`)

Demonstrates automatic field generation from Peewee ORM queries.

**Endpoint**: `GET /auto/`

**Features**:

- Automatic field introspection
- Zero configuration required
- Type inference from ORM fields
- Relationship handling

**Example Requests**:

```bash
# Basic filtering
curl -X GET "http://localhost:5000/auto/?name=Apple"

# Advanced filtering with lookups
curl -X GET "http://localhost:5000/auto/?name__icontains=apple&price__gte=1.0"

# Filter by category
curl -X GET "http://localhost:5000/auto/?category_name=Fruit&is_active=true"

# Price range filtering
curl -X GET "http://localhost:5000/auto/?price__gte=2.0&price__lte=5.0"
```

### 3. Iterable Data Filtering (`/auto/iterable/`)

Demonstrates filtering of nested dictionary data structures.

**Endpoint**: `GET /auto/iterable/`

**Features**:

- Nested data structure support
- Dot notation for nested fields
- Automatic field generation from data
- Flexible data source handling

**Example Requests**:

```bash
# Filter nested product data
curl -X GET "http://localhost:5000/auto/iterable/?product_name=Banana"

# Filter by product ID
curl -X GET "http://localhost:5000/auto/iterable/?product_id=1"

# Filter by category information
curl -X GET "http://localhost:5000/auto/iterable/?category_name=Berry"

# Complex nested filtering
curl -X GET "http://localhost:5000/auto/iterable/?product_name__icontains=fruit&category_id=1"
```

### 4. Advanced Model Filtering (`/advanced-model/`)

Demonstrates Meta class configuration for hybrid approaches.

**Endpoint**: `GET /advanced-model/`

**Features**:

- Meta class configuration
- Hybrid explicit/automatic fields
- Schema-based field generation
- Advanced relationship handling

**Example Requests**:

```bash
# Basic filtering
curl -X GET "http://localhost:5000/advanced-model/?name=Apple"

# Price range filtering
curl -X GET "http://localhost:5000/advanced-model/?price__gte=2.0&price__lte=5.0"

# Category filtering
curl -X GET "http://localhost:5000/advanced-model/?category_name=Fruit"

# Complex filtering with multiple conditions
curl -X GET "http://localhost:5000/advanced-model/?name__icontains=berry&is_active=true&category_id=1"
```

## Available Filter Operators

The lumi_filter library supports various filter operators that can be used with any field:

- **Exact match**: `field=value`
- **Case-insensitive contains**: `field__icontains=value`
- **Case-sensitive contains**: `field__contains=value`
- **Greater than**: `field__gt=value`
- **Greater than or equal**: `field__gte=value`
- **Less than**: `field__lt=value`
- **Less than or equal**: `field__lte=value`
- **In list**: `field__in=value1,value2,value3`
- **Case-insensitive in**: `field__iin=value1,value2,value3`
- **Not equal**: `field!=value`
- **Range**: `field__range=min,max`

## Sample Data

The application is pre-populated with 25 fruit products across different categories:

- **Categories**: Fruit, Citrus, Tropical, Berry, Stone, Melon
- **Products**: Apple, Orange, Banana, Watermelon, Grape, etc.
- **Price Range**: $0.55 - $7.90
- **Active Status**: Most products are active, some inactive for testing

## File Structure

```
example/
├── README.md                           # This file
├── example.py                          # Main Flask application
├── extentions.py                       # Database configuration
├── requirements.txt                    # Python dependencies
├── db.db                              # SQLite database (auto-generated)
├── app/
│   ├── __init__.py
│   ├── db_model.py                    # Database models (Category, Product)
│   ├── schema.py                      # Pydantic schemas
│   └── api/
│       ├── auto_filter.py             # Automatic filtering demos
│       ├── model_filter.py            # Basic model filtering
│       ├── anvanced_model_filter.py   # Advanced filtering features
│       ├── auto_filter_peewee.py      # Peewee-specific auto filtering
│       └── extra_field_ordering_extra_field.py  # Extra features demo
```

## Testing the API

You can test the API using curl, Postman, or any HTTP client. Here are some comprehensive examples:

### Complex Filtering Examples

```bash
# Find all active berry products under $6
curl -X GET "http://localhost:5000/model/?category_name=Berry&is_active=true&price__lt=6.0"

# Find products with names containing 'fruit' and price between $2-$4
curl -X GET "http://localhost:5000/model/?name__icontains=fruit&price__gte=2.0&price__lte=4.0"

# Find citrus products, ordered by price descending
curl -X GET "http://localhost:5000/model/?category_name=Citrus&ordering=-price"

# Find products created after a specific date
curl -X GET "http://localhost:5000/model/?created_at__gte=2024-01-01T00:00:00"
```

### Response Format

All endpoints return JSON responses in the following format:

```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "name": "Apple",
            "price": 1.20,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00",
            "category_id": 1,
            "category_name": "Fruit"
        }
    ]
}
```

## Learning Path

1. **Start with Basic Model Filtering** (`/model/`) to understand explicit field definitions
2. **Explore Automatic Filtering** (`/auto/`) to see zero-configuration options
3. **Try Iterable Filtering** (`/auto/iterable/`) for complex data structures
4. **Experiment with Advanced Features** (`/advanced-model/`) for hybrid approaches

Each endpoint includes comprehensive examples in the source code docstrings and demonstrates different aspects of the lumi_filter library.

## Troubleshooting

### Common Issues

1. **Database not initialized**: Make sure to run the Flask app once to initialize the database with sample data
2. **Import errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
3. **Port conflicts**: Use `flask run --port=8080` to run on a different port

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

## Extension Ideas

- Add pagination support
- Implement authentication
- Add more complex relationships
- Create a frontend interface
- Add API documentation with Swagger/OpenAPI
