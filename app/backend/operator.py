from typing import Union
import utils.user_data_directory as udd
import os


operator: str = "No operator set"


def get_last_operator() -> Union[str, None]:
    operator_directory = udd.get_user_data_dir(["SaintsPay", "operator"])

    if not os.path.exists(operator_directory):
        os.makedirs(operator_directory)

    last_operator = os.path.join(operator_directory, f"last_operator.txt")

    if not os.path.exists(last_operator):
        return None

    with open(last_operator, "r") as last_operator_file:
        return last_operator_file.read()


def set_operator(new_operator: str):
    global operator
    operator = new_operator

    operator_directory = udd.get_user_data_dir(["SaintsPay", "operator"])

    if not os.path.exists(operator_directory):
        os.makedirs(operator_directory)

    operators_list = os.path.join(operator_directory, f"operators_list.txt")

    if not os.path.exists(operators_list):
        with open(operators_list, "w") as operators_list_file:
            operators_list_file.write(new_operator)
    else:
        with open(operators_list, "r") as operators_list_file:
            operators = operators_list_file.read().split("\n")

        if new_operator not in operators:
            operators.append(new_operator)

            with open(operators_list, "w") as operators_list_file:
                operators_list_file.write("\n".join(operators))

    last_operator = os.path.join(operator_directory, f"last_operator.txt")

    with open(last_operator, "w") as last_operator_file:
        last_operator_file.write(new_operator)


def get_operators() -> list[str]:
    operator_directory = udd.get_user_data_dir(["SaintsPay", "operator"])

    if not os.path.exists(operator_directory):
        os.makedirs(operator_directory)

    operators_list = os.path.join(operator_directory, f"operators_list.txt")

    if not os.path.exists(operators_list):
        return []

    with open(operators_list, "r") as operators_list_file:
        return [x for x in operators_list_file.read().split("\n") if x.strip() != ""]
