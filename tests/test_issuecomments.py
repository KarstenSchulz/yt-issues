import textwrap
from datetime import datetime

from ytissues.ytlib import IssueComment


def test_issue_comment_str():
    comment = textwrap.dedent(
        """
        ---
        **Comment by Gustavo, created: 2022-01-01 00:00, updated: -**

        A little comment to the issue."""
    )
    i_comment = IssueComment(
        comment_id="AN_ID",
        author="Gustavo",
        created=datetime(2022, 1, 1, 0, 0, 0),
        text="A little comment to the issue.",
    )
    assert str(i_comment) == comment
