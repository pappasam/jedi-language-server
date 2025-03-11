import threading
import time
from collections import Counter

from jedi_language_server.constants import MAX_CONCURRENT_DEBOUNCE_CALLS
from jedi_language_server.jedi_utils import debounce


def test_debounce() -> None:
    """Test that the debounce decorator delays and limits the number of concurrent calls."""
    # Create a function that records call counts per URI.
    counter = Counter[str]()
    cond = threading.Condition()

    def f(uri: str) -> None:
        with cond:
            counter.update(uri)
            cond.notify_all()

    # Call the debounced function more than the max allowed concurrent calls.
    debounced = debounce(interval_s=1, keyed_by="uri")(f)
    for _ in range(3):
        debounced("0")
    for i in range(1, MAX_CONCURRENT_DEBOUNCE_CALLS + 10):
        debounced(str(i))

    # Wait for at least the max allowed concurrent timers to complete.
    with cond:
        assert cond.wait_for(
            lambda: sum(counter.values()) >= MAX_CONCURRENT_DEBOUNCE_CALLS
        )

    # Check the counter after 0.5 seconds to ensure that no additional timers
    # were started and have completed.
    time.sleep(0.5)
    assert sum(counter.values()) == MAX_CONCURRENT_DEBOUNCE_CALLS

    # For uri "0", only one timer should have been started despite 3 calls.
    assert counter["0"] == 1
