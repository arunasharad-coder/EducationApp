```python
# curfew_logic.py

from datetime import time, datetime
from models import SocialPost

# Define curfew period start and end times
CURFEW_START = time(22, 0)  # 22:00 or 10 PM
CURFEW_END = time(7, 0)     # 07:00 or 7 AM


def can_post(student_time: time) -> bool:
    """
    Check if the student is allowed to post at the given time.

    Returns False if time is within the curfew period (22:00 to 07:00),
    otherwise True.
    """
    # Curfew is from 22:00 to 07:00.
    # Because curfew crosses midnight, we handle accordingly:
    if CURFEW_START <= student_time or student_time < CURFEW_END:
        return False
    return True


def create_post(student_id: int, content: str) -> SocialPost:
    """
    Creates and saves a SocialPost if posting is allowed at the current time.

    Raises a PermissionError if curfew does not allow posting.

    Returns the saved SocialPost instance.
    """
    now = datetime.now().time()
    if not can_post(now):
        raise PermissionError(
            "Posting is not allowed during curfew hours (22:00 to 07:00)."
        )

    post = SocialPost(student_id=student_id, content=content, timestamp=datetime.now())
    post.save()  # Assuming SocialPost has a .save() method to commit to DB
    return post
```