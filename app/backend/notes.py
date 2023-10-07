import utils.user_data_directory as udd
import os


def get_notes_for_student(student_schoolbox_id: str) -> str:
    notes_directory = udd.get_user_data_dir(["SaintsPay", "notes"])

    if not os.path.exists(notes_directory):
        os.makedirs(notes_directory)

    notes_file_path = os.path.join(notes_directory, f"{student_schoolbox_id}.txt")

    if os.path.exists(notes_file_path):
        with open(notes_file_path, "r") as notes_file:
            return notes_file.read()

    return "No Notes"


def set_notes_for_student(student_schoolbox_id: str, notes: str):
    notes_directory = udd.get_user_data_dir(["SaintsPay", "notes"])

    if not os.path.exists(notes_directory):
        os.makedirs(notes_directory)

    notes_file_path = os.path.join(notes_directory, f"{student_schoolbox_id}.txt")

    with open(notes_file_path, "w") as notes_file:
        notes_file.write(notes)
