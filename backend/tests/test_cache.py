import pytest
import os
from database.schema import init_database
from agents.cache import CacheAgent


def test_cache_storage_and_retrieval():
    """Test cache storage and retrieval"""
    db_path = "test_sales.db"
    init_database(db_path)
    
    cache = CacheAgent(db_path)
    
    # Store a cached answer
    success = cache.store(
        original_question="What are total sales?",
        sql_query="SELECT SUM(total_amount) FROM orders",
        answer="Total sales were $50,000",
        evidence={"total": 50000},
        confidence=0.95,
        execution_time_ms=245,
        token_usage={"input": 150, "output": 50}
    )
    
    assert success
    
    # Retrieve cached answer
    cached = cache.get("What are total sales?")
    assert cached is not None
    assert cached["answer"] == "Total sales were $50,000"
    assert cached["confidence"] == 0.95
    
    # Cleanup
    import os
    if os.path.exists(db_path):
        os.remove(db_path)


def test_cache_miss():
    """Test cache miss scenario"""
    db_path = "test_sales.db"
    init_database(db_path)
    
    cache = CacheAgent(db_path)
    
    # Try to get non-existent question
    cached = cache.get("Non-existent question")
    assert cached is None
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
