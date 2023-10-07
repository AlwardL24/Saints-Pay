import utils.user_data_directory as udd
import os
import time
import urllib.parse
from datetime import datetime
from . import operator


class BlacklistEntry:
    def __init__(
        self, student_schoolbox_id: str, operator: str, time: int, reason: str
    ):
        self.student_schoolbox_id = student_schoolbox_id
        self.operator = operator
        self.time = time
        self.reason = reason


def is_student_blacklisted(student_schoolbox_id: str) -> bool:
    blacklist_directory = udd.get_user_data_dir(["SaintsPay", "blacklist"])

    if not os.path.exists(blacklist_directory):
        os.makedirs(blacklist_directory)

    blacklist_file_path = os.path.join(
        blacklist_directory, f"{student_schoolbox_id}.txt"
    )

    return os.path.exists(blacklist_file_path)


def get_blacklist_entry_for_student(
    student_schoolbox_id: str,
) -> BlacklistEntry:
    blacklist_directory = udd.get_user_data_dir(["SaintsPay", "blacklist"])

    if not os.path.exists(blacklist_directory):
        os.makedirs(blacklist_directory)

    blacklist_file_path = os.path.join(
        blacklist_directory, f"{student_schoolbox_id}.txt"
    )

    if os.path.exists(blacklist_file_path):
        with open(blacklist_file_path, "r") as blacklist_file:
            lines = blacklist_file.read().split("\n")

            try:
                return BlacklistEntry(
                    student_schoolbox_id=student_schoolbox_id,
                    operator=urllib.parse.unquote(
                        next(
                            (
                                x.split("=")[1]
                                for x in lines
                                if x.startswith("operator=")
                            ),
                            "Unknown",
                        )
                    ),
                    time=int(
                        next(
                            (x.split("=")[1] for x in lines if x.startswith("time=")),
                            0,
                        )
                    ),
                    reason=urllib.parse.unquote(
                        next(
                            (x.split("=")[1] for x in lines if x.startswith("reason=")),
                            "No%20reason%20specified",
                        )
                    ),
                )
            except (StopIteration, ValueError, IndexError, TypeError):
                return BlacklistEntry(
                    student_schoolbox_id=student_schoolbox_id,
                    operator="Unknown",
                    time=0,
                    reason="No reason specified",
                )

    else:
        return BlacklistEntry(
            student_schoolbox_id=student_schoolbox_id,
            operator="Unknown",
            time=0,
            reason="No reason specified",
        )


def add_student_to_blacklist(
    student_schoolbox_id: str, reason: str = "No reason specified"
):
    blacklist_directory = udd.get_user_data_dir(["SaintsPay", "blacklist"])

    if not os.path.exists(blacklist_directory):
        os.makedirs(blacklist_directory)

    blacklist_file_path = os.path.join(
        blacklist_directory, f"{student_schoolbox_id}.txt"
    )

    with open(blacklist_file_path, "w") as blacklist_file:
        blacklist_file.write(
            f"student_schoolbox_id={student_schoolbox_id}\noperator={urllib.parse.quote(operator.operator)}\ntime={int(time.time())}\nreason={urllib.parse.quote(reason)}"
        )


def remove_student_from_blacklist(student_schoolbox_id: str):
    blacklist_directory = udd.get_user_data_dir(["SaintsPay", "blacklist"])

    if not os.path.exists(blacklist_directory):
        os.makedirs(blacklist_directory)

    blacklist_file_path = os.path.join(
        blacklist_directory, f"{student_schoolbox_id}.txt"
    )

    if os.path.exists(blacklist_file_path):
        os.remove(blacklist_file_path)
