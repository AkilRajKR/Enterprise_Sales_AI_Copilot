import pytest
import os
from pathlib import Path
from agents.planner import PlannerAgent
from agents.cache import CacheAgent

os.environ["GEMINI_API_KEY"] = "test-key"


def test_planner_agent_initialization():
    """Test planner agent initialization"""
    api_key = os.getenv("GEMINI_API_KEY")
    planner = PlannerAgent(api_key)
    assert planner is not None
    assert planner.llm is not None


def test_cache_agent_initialization():
    """Test cache agent initialization"""
    db_path = "test_cache.db"
    cache = CacheAgent(db_path)
    assert cache is not None
    
    if Path(db_path).exists():
        os.remove(db_path)


def test_question_normalization():
    """Test question normalization for caching"""
    db_path = "test_cache.db"
    cache = CacheAgent(db_path)
    
    question = "  What are Total SALES?  "
    normalized = cache.normalize_question(question)
    
    assert normalized == "what are total sales?"
    
    if Path(db_path).exists():
        os.remove(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
