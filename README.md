# FastAPI + Typesense Application

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Typesense](https://img.shields.io/badge/Typesense-0.25.2-orange.svg)](https://typesense.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, high-performance search and recommendation system built with FastAPI and Typesense. This application demonstrates real-time full-text search, filtering, faceted search, and basic recommendation algorithms - perfect for e-commerce, content discovery, and data exploration use cases.

## 🌟 Features

### Core Search Capabilities
- **Full-text Search**: Search across multiple fields with relevance ranking
- **Real-time Indexing**: Instant search on newly added data
- **Typo Tolerance**: Smart search that handles misspellings
- **Faceted Search**: Filter and group results by categories, price ranges, ratings
- **Advanced Filtering**: Complex queries with multiple conditions
- **Auto-complete**: Fast type-ahead suggestions

### Recommendation System
- **Content-based Filtering**: Similarity based on product attributes
- **Category Recommendations**: Related products within same category
- **Rating-based Suggestions**: Popular and highly-rated items
- **Configurable Algorithms**: Easy to extend with ML models

### Analytics & Admin
- **Collection Management**: View and manage Typesense collections
- **Search Analytics**: Performance metrics and search statistics
- **Health Monitoring**: Real-time health checks and status reporting
- **Interactive API Documentation**: Auto-generated Swagger/OpenAPI docs

## 🚀 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Search Engine**: Typesense 0.25.2
- **Data Validation**: Pydantic v2
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger UI / ReDoc
- **Development**: Uvicorn ASGI server

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Git** (for cloning the repository)

## 🛠️ Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fastapi-typesense-demo.git
   cd fastapi-typesense-demo
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health
   - **Typesense Dashboard**: http://localhost:8108

### Option 2: Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/fastapi-typesense-demo.git
   cd fastapi-typesense-demo
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start Typesense**
   ```bash
   docker run -p 8108:8108 -v /tmp/typesense-data:/data \
     typesense/typesense:0.25.2 \
     --data-dir /data --api-key=xyz --enable-cors
   ```

3. **Run FastAPI**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Typesense Configuration
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_API_KEY=your-secure-api-key-here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=info
DEBUG=true

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Production Configuration

For production deployment, use strong API keys and proper security settings:

```env
TYPESENSE_API_KEY=your-very-secure-random-api-key
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message and API info |
| `GET` | `/health` | Health check status |
| `GET` | `/docs` | Interactive API documentation |

### Product Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/` | List all products (paginated) |
| `POST` | `/products/` | Add a new product |
| `GET` | `/products/{id}` | Get product by ID |
| `PUT` | `/products/{id}` | Update product by ID |
| `DELETE` | `/products/{id}` | Delete product by ID |

### Search & Discovery

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search/` | Search products with filters |
| `GET` | `/categories/` | Get all available categories |
| `GET` | `/recommendations/{id}` | Get product recommendations |
| `GET` | `/similar/{id}` | Get similar products |

### Analytics & Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/collections` | List all collections |
| `GET` | `/admin/collection/{name}` | Get collection schema |
| `GET` | `/admin/collection/{name}/stats` | Collection statistics |
| `GET` | `/admin/typesense/stats` | Server statistics |
| `GET` | `/analytics/popular` | Popular products |
| `GET` | `/analytics/price-ranges` | Price analytics |

## 🔍 Usage Examples

### Search Products

```bash
# Basic search
curl -X POST "http://localhost:8000/search/" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "smartphone",
       "category": "Electronics",
       "min_price": 500,
       "max_price": 1200
     }'
```

### Add a Product

```bash
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "new-product-1",
       "name": "Gaming Laptop",
       "description": "High-performance gaming laptop with RTX graphics",
       "category": "Computers",
       "price": 1599.99,
       "rating": 4.5,
       "tags": ["gaming", "laptop", "RTX", "performance"]
     }'
```

### Get Recommendations

```bash
curl "http://localhost:8000/recommendations/1?limit=5"
```

### Search with Python

```python
import requests

# Search for products
response = requests.post("http://localhost:8000/search/", json={
    "query": "headphones",
    "category": "Audio",
    "min_price": 100
})

products = response.json()
print(f"Found {products['found']} products")
for hit in products['results']:
    product = hit['document']
    print(f"- {product['name']}: ${product['price']}")
```

### Search with JavaScript

```javascript
// Search for products
const searchProducts = async (query) => {
  const response = await fetch('http://localhost:8000/search/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      category: 'Electronics'
    })
  });
  
  const data = await response.json();
  return data.results;
};

// Usage
searchProducts('laptop').then(products => {
  console.log('Found products:', products);
});
```

## 🚢 Deployment

### Docker Production

1. **Build production image**
   ```bash
   docker build -t fastapi-typesense:latest .
   ```

2. **Use production compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```


## 🔧 Advanced Configuration

### Custom Collection Schema

```python
# Extend the schema for your use case
CUSTOM_SCHEMA = {
    'name': 'products',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'name', 'type': 'string'},
        {'name': 'description', 'type': 'string'},
        {'name': 'category', 'type': 'string', 'facet': True},
        {'name': 'price', 'type': 'float', 'facet': True},
        {'name': 'rating', 'type': 'float', 'facet': True},
        {'name': 'tags', 'type': 'string[]', 'facet': True},
        {'name': 'created_at', 'type': 'int64'},
        {'name': 'in_stock', 'type': 'bool', 'facet': True},
        {'name': 'brand', 'type': 'string', 'facet': True},
        {'name': 'weight', 'type': 'float'},
        {'name': 'dimensions', 'type': 'string'},
        {'name': 'colors', 'type': 'string[]', 'facet': True}
    ],
    'default_sorting_field': 'rating'
}
```

### Performance Tuning

```python
# Optimize search parameters
SEARCH_CONFIG = {
    'query_by': 'name,description,tags,brand',
    'query_by_weights': '4,2,1,3',
    'prefix': 'true,false,false,true',
    'num_typos': '2,1,0,1',
    'min_len_1typo': 3,
    'min_len_2typo': 5,
    'drop_tokens_threshold': 5,
    'typo_tokens_threshold': 1
}
```

## 🐛 Troubleshooting

### Common Issues

**1. Connection Refused Error**
```bash
# Check if Typesense is running
curl -H "X-TYPESENSE-API-KEY: xyz" http://localhost:8108/health

# Check container logs
docker-compose logs typesense
```

**2. Port Already in Use**
```bash
# Find and kill process using port
sudo lsof -t -i:8000 | xargs sudo kill -9
sudo lsof -t -i:8108 | xargs sudo kill -9
```

**3. Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear Docker cache
docker system prune -af
```

**4. Search Not Working**
```bash
# Check collection exists
curl -H "X-TYPESENSE-API-KEY: xyz" http://localhost:8108/collections

# Verify data import
curl -H "X-TYPESENSE-API-KEY: xyz" http://localhost:8108/collections/products/documents
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

```bash
# Monitor container resources
docker stats

# Check Typesense metrics
curl -H "X-TYPESENSE-API-KEY: xyz" http://localhost:8108/metrics.json
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Typesense](https://typesense.org/) - Open source search engine
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation library
- [Docker](https://www.docker.com/) - Containerization platform

