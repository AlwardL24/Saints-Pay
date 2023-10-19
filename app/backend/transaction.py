import utils.user_data_directory as udd
import os
import time
import uuid
import datetime
import urllib.parse
from . import ole as backend_ole
from typing import Union
from utils.system_agnostic_datetime_format import sadf


class Transaction:
    def __init__(
        self,
        id: str,
        student_schoolbox_id: str,
        amount: float,
        time: int,
        operator: str,
    ):
        self.id = id
        self.student_schoolbox_id = student_schoolbox_id
        self.amount = amount
        self.time = time
        self.operator = operator


class TransactionFilter:
    def __init__(
        self,
        from_start_of: Union[datetime.date, None] = None,
        to_end_of: Union[datetime.date, None] = None,
        student_schoolbox_id: Union[str, None] = None,
        operator: Union[str, None] = None,
        from_start_of_time: Union[int, None] = None,
    ):
        self.from_start_of = from_start_of
        self.to_end_of = to_end_of
        self.student_schoolbox_id = student_schoolbox_id
        self.operator = operator
        self.from_start_of_time = from_start_of_time

    def transaction_matches(self, transaction: Transaction) -> bool:
        if self.from_start_of is not None:
            if transaction.time < int(
                datetime.datetime.combine(
                    self.from_start_of, datetime.time.min
                ).timestamp()
            ):
                return False

        if self.from_start_of_time is not None:
            if transaction.time < self.from_start_of_time:
                return False

        if self.to_end_of is not None:
            if transaction.time > int(
                datetime.datetime.combine(self.to_end_of, datetime.time.max).timestamp()
            ):
                return False

        if self.student_schoolbox_id is not None:
            if transaction.student_schoolbox_id != self.student_schoolbox_id:
                return False

        if self.operator is not None:
            if transaction.operator != self.operator:
                return False

        return True

    def user_readable_string(self, ole: backend_ole.OLE) -> str:
        string = "transactions"

        if self.student_schoolbox_id is not None:
            string = f"{ole.student_from_id(self.student_schoolbox_id).name}'s {string}"

        if self.from_start_of_time is not None:
            string + f"This session's {string}"

        if self.operator is not None:
            string += f" made by {self.operator}"

        if self.from_start_of is not None:
            string += f" from {self.from_start_of.strftime(sadf('%d/%m/%Y'))}"

        if self.to_end_of is not None:
            string += f" to {self.to_end_of.strftime(sadf('%d/%m/%Y'))}"

        if string == "transactions":
            string = "all transactions"

        return string


def new_transaction(
    student_schoolbox_id: str,
    amount: float,
    time: int = int(time.time()),
    operator: str = "Unknown",
):
    transaction_directory = udd.get_user_data_dir(["SaintsPay", "transactions"])

    if not os.path.exists(transaction_directory):
        os.makedirs(transaction_directory)

    id = uuid.uuid4().hex

    transaction_file_path = os.path.join(transaction_directory, f"{id}.txt")

    with open(transaction_file_path, "w") as transaction_file:
        transaction_file.write(
            f"id={id}\nstudent_schoolbox_id={student_schoolbox_id}\namount={int(amount * 100)}\ntime={time}\noperator={urllib.parse.quote(operator)}"
        )


def get_transactions() -> list[Transaction]:
    transaction_directory = udd.get_user_data_dir(["SaintsPay", "transactions"])

    if not os.path.exists(transaction_directory):
        os.makedirs(transaction_directory)

    transactions = []

    for filename in os.listdir(transaction_directory):
        if not filename.endswith(".txt"):
            continue

        transaction_file_path = os.path.join(transaction_directory, filename)

        with open(transaction_file_path, "r") as transaction_file:
            try:
                transaction_data = transaction_file.read().split("\n")
            except UnicodeDecodeError:
                continue

            try:
                transactions.append(
                    Transaction(
                        id=next(
                            x.split("=")[1]
                            for x in transaction_data
                            if x.startswith("id=")
                        ),
                        student_schoolbox_id=next(
                            x.split("=")[1]
                            for x in transaction_data
                            if x.startswith("student_schoolbox_id=")
                        ),
                        amount=int(
                            next(
                                x.split("=")[1]
                                for x in transaction_data
                                if x.startswith("amount=")
                            )
                        )
                        / 100,
                        time=int(
                            next(
                                x.split("=")[1]
                                for x in transaction_data
                                if x.startswith("time=")
                            )
                        ),
                        operator=urllib.parse.unquote(
                            next(
                                (
                                    x.split("=")[1]
                                    for x in transaction_data
                                    if x.startswith("operator=")
                                ),
                                "Unknown",
                            )
                        ),
                    )
                )
            except (StopIteration, IndexError, TypeError, ValueError):
                continue

    return transactions


def get_transactions_filtered(by_filter: TransactionFilter) -> list[Transaction]:
    return list(filter(by_filter.transaction_matches, get_transactions()))


def delete_transactions_with_ids(ids: list[str]):
    transaction_directory = udd.get_user_data_dir(["SaintsPay", "transactions"])

    if not os.path.exists(transaction_directory):
        os.makedirs(transaction_directory)

    for filename in os.listdir(transaction_directory):
        if not filename.endswith(".txt"):
            continue

        transaction_file_path = os.path.join(transaction_directory, filename)

        with open(transaction_file_path, "r") as transaction_file:
            try:
                transaction_data = transaction_file.read().split("\n")
            except UnicodeDecodeError:
                continue

        try:
            if (
                next(x.split("=")[1] for x in transaction_data if x.startswith("id="))
                in ids
            ):
                os.remove(transaction_file_path)
        except (StopIteration, IndexError, TypeError, ValueError):
            continue


def edit_transaction(transaction: Transaction):
    transaction_directory = udd.get_user_data_dir(["SaintsPay", "transactions"])

    if not os.path.exists(transaction_directory):
        os.makedirs(transaction_directory)

    transaction_file_path = os.path.join(transaction_directory, f"{transaction.id}.txt")

    with open(transaction_file_path, "w") as transaction_file:
        transaction_file.write(
            f"id={transaction.id}\nstudent_schoolbox_id={transaction.student_schoolbox_id}\namount={int(transaction.amount * 100)}\ntime={transaction.time}\noperator={urllib.parse.quote(transaction.operator)}"
        )
