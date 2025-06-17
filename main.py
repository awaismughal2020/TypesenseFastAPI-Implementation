from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import typesense
import os
import time
from contextlib import asynccontextmanager


# Pydantic models
class Product(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float
    rating: float
    tags: List[str]


class SearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


# Typesense client
client = typesense.Client({
    'nodes': [{
        'host': os.getenv('TYPESENSE_HOST', 'localhost'),
        'port': os.getenv('TYPESENSE_PORT', '8108'),
        'protocol': 'http'
    }],
    'api_key': os.getenv('TYPESENSE_API_KEY', 'xyz'),
    'connection_timeout_seconds': 2
})

# Collection schema
COLLECTION_NAME = 'products'
COLLECTION_SCHEMA = {
    'name': COLLECTION_NAME,
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'name', 'type': 'string'},
        {'name': 'description', 'type': 'string'},
        {'name': 'category', 'type': 'string', 'facet': True},
        {'name': 'price', 'type': 'float', 'facet': True},
        {'name': 'rating', 'type': 'float', 'facet': True},
        {'name': 'tags', 'type': 'string[]', 'facet': True}
    ],
    'default_sorting_field': 'rating'
}


async def setup_typesense():
    """Initialize Typesense collection and add sample data"""
    max_retries = 10
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Test connection first
            client.collections.retrieve()
            print(f"Connected to Typesense on attempt {attempt + 1}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff
            else:
                print(f"Failed to connect to Typesense after {max_retries} attempts: {e}")
                return

    try:
        # Try to delete existing collection
        try:
            client.collections[COLLECTION_NAME].delete()
        except:
            pass

        # Create collection
        client.collections.create(COLLECTION_SCHEMA)

        # Add sample products
        sample_products = [
            {
                'id': '1',
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple smartphone with advanced camera system',
                'category': 'Electronics',
                'price': 999.99,
                'rating': 4.7,
                'tags': ['smartphone', 'apple', 'premium', 'camera']
            },
            {
                'id': '2',
                'name': 'Samsung Galaxy S24',
                'description': 'Flagship Android phone with AI features',
                'category': 'Electronics',
                'price': 899.99,
                'rating': 4.5,
                'tags': ['smartphone', 'samsung', 'android', 'AI']
            },
            {
                'id': '3',
                'name': 'MacBook Pro M3',
                'description': 'Professional laptop with M3 chip',
                'category': 'Computers',
                'price': 1999.99,
                'rating': 4.8,
                'tags': ['laptop', 'apple', 'professional', 'M3']
            },
            {
                'id': '4',
                'name': 'Dell XPS 13',
                'description': 'Ultrabook with premium design',
                'category': 'Computers',
                'price': 1299.99,
                'rating': 4.4,
                'tags': ['laptop', 'dell', 'ultrabook', 'portable']
            },
            {
                'id': '5',
                'name': 'Sony WH-1000XM5',
                'description': 'Noise-canceling wireless headphones',
                'category': 'Audio',
                'price': 399.99,
                'rating': 4.6,
                'tags': ['headphones', 'sony', 'wireless', 'noise-canceling']
            }
        ]

        # Import documents
        client.collections[COLLECTION_NAME].documents.import_(sample_products)
        print("Typesense setup completed successfully!")

    except Exception as e:
        print(f"Error setting up Typesense: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await setup_typesense()
    yield
    # Shutdown
    pass


# FastAPI app
app = FastAPI(
    title="Typesense Demo API",
    description="A simple FastAPI application demonstrating Typesense search capabilities",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Welcome to Typesense Demo API"}


@app.get("/health")
async def health_check():
    """Check if Typesense is accessible"""
    try:
        # Simple check - try to get collections
        collections = client.collections.retrieve()
        return {"status": "healthy", "typesense": True, "collections": len(collections)}
    except Exception as e:
        return {"status": "degraded", "typesense": False, "error": str(e)}


@app.get("/products/")
async def get_all_products(limit: int = 10, offset: int = 0):
    """Get all products with pagination"""
    try:
        search_params = {
            'q': '*',
            'per_page': limit,
            'page': (offset // limit) + 1
        }
        results = client.collections[COLLECTION_NAME].documents.search(search_params)

        return {
            "total": results['found'],
            "page": search_params['page'],
            "per_page": limit,
            "products": [hit['document'] for hit in results['hits']]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")


@app.post("/products/", response_model=dict)
async def add_product(product: Product):
    """Add a new product to Typesense"""
    try:
        result = client.collections[COLLECTION_NAME].documents.create(product.dict())
        return {"message": "Product added successfully", "product": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add product: {e}")


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get a specific product by ID"""
    try:
        product = client.collections[COLLECTION_NAME].documents[product_id].retrieve()
        return product
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Product not found: {e}")


@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product by ID"""
    try:
        client.collections[COLLECTION_NAME].documents[product_id].delete()
        return {"message": f"Product {product_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to delete product: {e}")


@app.post("/search/")
async def search_products(search_query: SearchQuery):
    """Search products with various filters"""
    try:
        # Build search parameters
        search_params = {
            'q': search_query.query,
            'query_by': 'name,description,tags',
            'sort_by': 'rating:desc,price:asc'
        }

        # Add filters
        filters = []
        if search_query.category:
            filters.append(f'category:={search_query.category}')
        if search_query.min_price is not None:
            filters.append(f'price:>={search_query.min_price}')
        if search_query.max_price is not None:
            filters.append(f'price:<={search_query.max_price}')

        if filters:
            search_params['filter_by'] = ' && '.join(filters)

        # Perform search
        results = client.collections[COLLECTION_NAME].documents.search(search_params)

        return {
            "query": search_query.query,
            "found": results['found'],
            "results": results['hits']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {e}")


@app.get("/admin/collections")
async def get_all_collections():
    """Get all Typesense collections"""
    try:
        collections = client.collections.retrieve()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get collections: {e}")


@app.get("/admin/collection/{collection_name}")
async def get_collection_info(collection_name: str):
    """Get detailed information about a specific collection"""
    try:
        collection = client.collections[collection_name].retrieve()
        return collection
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {e}")


@app.get("/admin/collection/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """Get collection statistics"""
    try:
        # Get collection info
        collection_info = client.collections[collection_name].retrieve()

        # Get document count by searching all documents
        search_result = client.collections[collection_name].documents.search({
            'q': '*',
            'per_page': 0  # Don't return documents, just count
        })

        return {
            "collection_name": collection_name,
            "schema": collection_info,
            "document_count": search_result['found'],
            "search_time_ms": search_result.get('search_time_ms', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get collection stats: {e}")


@app.get("/admin/typesense/stats")
async def get_typesense_stats():
    """Get overall Typesense server statistics"""
    try:
        # This endpoint might not be available in all versions
        # Try to get basic info instead
        collections = client.collections.retrieve()

        total_docs = 0
        collection_stats = []

        for collection in collections:
            try:
                search_result = client.collections[collection['name']].documents.search({
                    'q': '*',
                    'per_page': 0
                })
                doc_count = search_result['found']
                total_docs += doc_count

                collection_stats.append({
                    "name": collection['name'],
                    "document_count": doc_count,
                    "fields": len(collection.get('fields', []))
                })
            except:
                collection_stats.append({
                    "name": collection['name'],
                    "document_count": "unknown",
                    "fields": len(collection.get('fields', []))
                })

        return {
            "total_collections": len(collections),
            "total_documents": total_docs,
            "collections": collection_stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Typesense stats: {e}")


@app.get("/categories/")
async def get_categories():
    """Get all available categories"""
    try:
        search_params = {
            'q': '*',
            'facet_by': 'category'
        }
        results = client.collections[COLLECTION_NAME].documents.search(search_params)

        categories = []
        if 'facet_counts' in results:
            for facet in results['facet_counts']:
                if facet['field_name'] == 'category':
                    categories = [count['value'] for count in facet['counts']]

        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get categories: {e}")


@app.get("/recommendations/{product_id}")
async def get_recommendations(product_id: str, limit: int = 5):
    """Get product recommendations based on a product (simple similarity)"""
    try:
        # Get the source product
        source_product = client.collections[COLLECTION_NAME].documents[product_id].retrieve()

        # Search for similar products based on category and tags
        search_params = {
            'q': ' '.join(source_product['tags']),
            'query_by': 'tags,category,name',
            'filter_by': f'id:!={product_id}',  # Exclude the source product
            'per_page': limit,
            'sort_by': 'rating:desc'
        }

        results = client.collections[COLLECTION_NAME].documents.search(search_params)

        return {
            "source_product": source_product,
            "recommendations": results['hits']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get recommendations: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
