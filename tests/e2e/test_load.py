import pytest
import asyncio
import time

@pytest.mark.asyncio
async def test_simulated_load():
    """Simulates multiple concurrent agents interacting with memory."""
    start = time.time()
    # Mocking 50 concurrent validation checks
    tasks = [asyncio.sleep(0.01) for _ in range(50)]
    await asyncio.gather(*tasks)
    duration = time.time() - start
    
    # Ensure parallel execution happened under 1 second
    assert duration < 1.0 
