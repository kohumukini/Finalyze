import time

from typing import Callable

from typing import Any

def retry(
    fn: Callable[[], Any], # [] = Input types, any = return type
    *, # Means that everything after this has to be keyword-arguments
    deadline: float, # By when the entire retry should be completed
    is_retryable: Callable[[Exception], bool], # Takes an exception, returns a boolean
    initial_backoff: float = 10.0,
    min_attempt_time: float = 5.0 
):
    backoff = initial_backoff
    
    while True:
        try: 
            return fn()
        except Exception as e:
            if not is_retryable(e): 
                raise e
            
            now = time.time()
            if now >= deadline: 
                raise e
            
            remaining_time = deadline - now
            
            sleep_time = min(backoff, remaining_time)
            time.sleep(sleep_time)