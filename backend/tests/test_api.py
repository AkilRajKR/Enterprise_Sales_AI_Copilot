import pytest
from api.schemas import QuestionRequest, QueryResponse


def test_question_request_validation():
    """Test QuestionRequest validation"""
    # Valid request
    req = QuestionRequest(question="What are total sales?")
    assert req.question == "What are total sales?"
    
    # Invalid: empty question
    with pytest.raises(ValueError):
        QuestionRequest(question="")


def test_query_response_structure():
    """Test QueryResponse structure"""
    response = QueryResponse(
        question="What are total sales?",
        answer="$50,000",
        sql_query="SELECT SUM(total_amount) FROM orders",
        evidence={"total": 50000},
        confidence=0.95,
        cache_hit=False,
        retry_count=0,
        validation_status="passed",
        execution_time_ms=245,
        token_usage={"input": 150, "output": 50}
    )
    
    assert response.question == "What are total sales?"
    assert response.confidence == 0.95
    assert response.validation_status == "passed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
