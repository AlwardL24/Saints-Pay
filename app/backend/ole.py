from typing import Union, Callable
import requests
import utils.user_data_directory as udd
from utils.system_agnostic_datetime_format import sadf
import os
import urllib.parse
import re
from PIL import Image
import uuid
import time
from . import notes, operator
from datetime import datetime


# To allow the creation of custom, "manually entered" students that for whatever reason aren't found on the OLE, we use a schoolbox ID of 000_<random UUIDv4 as hex>. These students obviously won't be found on the OLE, only in the student cache, and they have no photo so a default for manually entered students is used. These will be called 'local students'


class OLE:
    class Error(Exception):
        def __init__(self, message, retry_in=None):
            self.message = message
            self.retry_in = retry_in
            super().__init__(self.message)

        pass

    class Student:
        id: Union[str, None] = None
        schoolbox_id: Union[str, None] = None
        name: Union[str, None] = None
        username: Union[str, None] = None
        email: Union[str, None] = None
        tutor: Union[str, None] = None
        year: Union[str, None] = None

        def __init__(
            self,
            id: Union[str, None] = None,
            schoolbox_id: Union[str, None] = None,
            name: Union[str, None] = None,
            username: Union[str, None] = None,
            email: Union[str, None] = None,
            tutor: Union[str, None] = None,
            year: Union[str, None] = None,
        ):
            self.id = id
            self.schoolbox_id = schoolbox_id
            self.name = name
            self.username = username
            self.email = email
            self.tutor = tutor
            self.year = year

    username = None
    password = None
    cookie = None
    name = None
    role = None

    def __init__(
        self,
        username: str,
        password: str,
        info_callback: Callable[[str, str], None] = None,
    ):
        self.username = username
        self.password = password

        self.login(info_callback=info_callback)

    def get_headers(self):
        return {
            "Accept": "text/html, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 SaintsPayBot/1.0 (+https://saintspay.lucasalward.com/bot)",
            "Cookie": self.cookie,
        }.copy()

    def login(self, info_callback: Callable[[str, str], None] = None):
        # Post request to /api/session
        # Request body
        # form data encoded
        # username: username
        # password: password

        url = "https://ole.saintkentigern.com/api/session"

        payload = {
            "username": self.username,
            "password": self.password,
        }

        headers = self.get_headers()
        headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
        )

        response = requests.request(
            "POST", url, headers=headers, data=payload, allow_redirects=False
        )

        if response.status_code >= 400 and response.status_code < 500:
            raise OLE.Error(f"{response.text}")
        elif response.status_code == 503:
            raise OLE.Error("The OLE is currently down for maintenance", retry_in=60)
        elif response.status_code not in [200, 302]:
            raise OLE.Error("An unknown error occurred while logging in.")

        self.cookie = response.headers["Set-Cookie"]

        data = response.json()
        if data["role"] != "staff" and info_callback:
            info_callback(
                "OLE Login Info",
                f"You are currently logged in as a {data['role']}. A staff account is required to show student photos and tutor groups.",
            )

        print(data)

        self.role = data["role"]

    def search_students(self, query: str) -> list[Student]:
        def get_page(number: int) -> list[OLE.Student]:
            url = (
                "https://ole.saintkentigern.com/resource/user/search?keyword="
                + urllib.parse.quote(query)
                + f"&type=user&p={str(number)}"
            )

            payload = {}
            headers = self.get_headers()

            response = requests.request(
                "GET", url, headers=headers, data=payload, allow_redirects=False
            )

            if (
                response.status_code == 302
                and response.is_redirect
                and response.next.url.startswith("https://ole.saintkentigern.com/login")
            ):
                # We've been logged out - login again

                self.login()

                return get_page(number)

            page = response.text

            def get_matches_for(page: str) -> list[OLE.Student]:
                matches = re.finditer(
                    r"<div class=\"list-item\">(?:.|\n)+?<a href='(.+?)'>(?:.|\n)+?<h3>(.+?)<\/h3>(?:.|\n)+?<p class=\"meta\">((?:.|\n)+?)<\/p>",
                    page,
                )

                students = []

                for match in matches:
                    if match.group(3).find("Students College") == -1:
                        continue

                    students.append(
                        OLE.Student(
                            schoolbox_id=match.group(1).split("/")[-1],
                            name=match.group(2),
                        )
                    )

                return students

            students = get_matches_for(page)

            # TODO: really need to do something better here to ensure not the last page

            if (
                re.search(
                    r"<ul class=\"pagination\" data-search-pagination=.+?>(?:\s|\n)+?<\/ul>",
                    page,
                )
                is None
                and len(students) != 0
            ):
                students.extend(get_page(number + 1))

            return students

        return self.search_local_students(query) + get_page(1)

    def search_local_students(self, query: str) -> list[Student]:
        student_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache", "students"]
        )

        if not os.path.exists(student_cache_directory):
            return []

        students = []

        for student_filename in os.listdir(student_cache_directory):
            if not student_filename.endswith(".txt"):
                continue

            if not student_filename.startswith("000_"):
                continue

            with open(
                os.path.join(student_cache_directory, student_filename), "r"
            ) as student_file:
                student_data = student_file.read().split("\n")

                # try:
                name = urllib.parse.unquote(
                    next(x.split("=")[1] for x in student_data if x.startswith("name="))
                )

                print(name.lower().find(query.lower()))

                if name.lower().find(query.lower()) != -1:
                    students.append(
                        OLE.Student(
                            id=next(
                                (
                                    x.split("=")[1]
                                    for x in student_data
                                    if x.startswith("id=")
                                ),
                                None,
                            ),
                            schoolbox_id=next(
                                x.split("=")[1]
                                for x in student_data
                                if x.startswith("schoolbox_id=")
                            ),
                            name=name,
                            username=urllib.parse.unquote(
                                next(
                                    (
                                        x.split("=")[1]
                                        for x in student_data
                                        if x.startswith("username=")
                                    ),
                                    "None",
                                )
                            ),
                            email=urllib.parse.unquote(
                                next(
                                    (
                                        x.split("=")[1]
                                        for x in student_data
                                        if x.startswith("email=")
                                    ),
                                    "None",
                                )
                            ),
                            tutor=urllib.parse.unquote(
                                next(
                                    (
                                        x.split("=")[1]
                                        for x in student_data
                                        if x.startswith("tutor=")
                                    ),
                                    "None",
                                )
                            ),
                            year=urllib.parse.unquote(
                                next(
                                    (
                                        x.split("=")[1]
                                        for x in student_data
                                        if x.startswith("year=")
                                    ),
                                    "None",
                                )
                            ),
                        )
                    )
                # except (StopIteration, IndexError, TypeError):
                #     continue

        print(students)

        return students

    def student(self, student: Student) -> Student:
        return self.student_from_id(schoolbox_id=student.schoolbox_id)

    def student_from_id(self, schoolbox_id: str, try_cache: bool = True) -> Student:
        if try_cache or schoolbox_id.startswith("000_"):
            cached_student = self.student_from_id_from_cache(schoolbox_id)
            if cached_student is not None:
                return cached_student

        if schoolbox_id.startswith("000_"):
            return OLE.Student(
                schoolbox_id=schoolbox_id,
                name="Unknown",
                username="Unknown",
                email="Unknown",
                tutor="Unknown",
                year="Unknown",
            )

        url = "https://ole.saintkentigern.com/search/user/" + schoolbox_id

        payload = {}
        headers = self.get_headers()

        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )

        if (
            response.status_code == 302
            and response.is_redirect
            and response.next.url.startswith("https://ole.saintkentigern.com/login")
        ):
            # We've been logged out - login again

            self.login()

            return self.student_from_id(schoolbox_id)

        page = response.text

        student = OLE.Student(schoolbox_id=schoolbox_id)

        name_id_match = re.search(
            r"<script type=\"text\/javascript\">(?:\s|\n)+?let baseConfig(?:.|\n)+?student: {\"id\":(.+?),\"externalId\":\"(\d+)\",\"title\":.+?,\"firstname\":\"(.+?)\",\"preferredName\":.+?,\"givenName\":.+?,\"lastname\":\"(.+?)\",\"fullName\":\"(.+?)\"",
            page,
        )

        if name_id_match is not None:
            student.schoolbox_id = name_id_match.group(1)
            student.id = name_id_match.group(2)
            student.name = name_id_match.group(5)

        email_username_match = re.search(
            r"<a href=\"\/mail\/create\?replyto=((.+?)@(?:student\.)?saintkentigern\.com)\"",
            page,
        )

        if email_username_match is not None:
            student.email = email_username_match.group(1)
            student.username = email_username_match.group(2)

            year_match = re.search(
                r"<dt class=\".+?\">Year Level:<\/dt>(?:\s|\n)+?<dd class=\".+?\">(.+?)<\/dd>",
                page,
            )

            if year_match is not None:
                student.year = year_match.group(1)

            tutor_match = re.search(
                r"<dt class=\".+?\">Tutor Group:<\/dt>(?:\s|\n)+?<dd class=\".+?\">(.+?)<\/dd>",
                page,
            )

            if tutor_match is not None:
                student.tutor = tutor_match.group(1)

        # Write to cache

        student_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache", "students"]
        )

        if not os.path.exists(student_cache_directory):
            os.makedirs(student_cache_directory)

        student_filename = f"{schoolbox_id}.txt"

        student_path = os.path.join(student_cache_directory, student_filename)

        with open(student_path, "w") as handler:
            handler.write(
                ""
                + (f"id={student.id}\n" if student.id is not None else "")
                + (
                    f"schoolbox_id={student.schoolbox_id}\n"
                    if student.schoolbox_id is not None
                    else ""
                )
                + (
                    f"name={urllib.parse.quote(student.name)}\n"
                    if student.name is not None
                    else ""
                )
                + (
                    f"username={urllib.parse.quote(student.username)}\n"
                    if student.username is not None
                    else ""
                )
                + (
                    f"email={urllib.parse.quote(student.email)}\n"
                    if student.email is not None
                    else ""
                )
                + (
                    f"tutor={urllib.parse.quote(student.tutor)}\n"
                    if student.tutor is not None
                    else ""
                )
                + (
                    f"year={urllib.parse.quote(student.year)}"
                    if student.year is not None
                    else ""
                )
            )

        return student

    def student_from_id_from_cache(self, schoolbox_id: str) -> Student:
        student_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache", "students"]
        )

        if not os.path.exists(student_cache_directory):
            os.makedirs(student_cache_directory)

        student_filename = f"{schoolbox_id}.txt"

        student_path = os.path.join(student_cache_directory, student_filename)

        if os.path.exists(student_path):
            with open(student_path, "r") as student_file:
                student_data = student_file.read().split("\n")

                try:
                    name_quoted = next(
                        (
                            x.split("=")[1]
                            for x in student_data
                            if x.startswith("name=")
                        ),
                        None,
                    )

                    username_quoted = next(
                        (
                            x.split("=")[1]
                            for x in student_data
                            if x.startswith("username=")
                        ),
                        None,
                    )

                    email_quoted = next(
                        (
                            x.split("=")[1]
                            for x in student_data
                            if x.startswith("email=")
                        ),
                        None,
                    )

                    tutor_quoted = next(
                        (
                            x.split("=")[1]
                            for x in student_data
                            if x.startswith("tutor=")
                        ),
                        None,
                    )

                    year_quoted = next(
                        (
                            x.split("=")[1]
                            for x in student_data
                            if x.startswith("year=")
                        ),
                        None,
                    )

                    return OLE.Student(
                        id=next(
                            (
                                x.split("=")[1]
                                for x in student_data
                                if x.startswith("id=")
                            ),
                            None,
                        ),
                        schoolbox_id=next(
                            (
                                x.split("=")[1]
                                for x in student_data
                                if x.startswith("schoolbox_id=")
                            ),
                            None,
                        ),
                        name=urllib.parse.unquote(name_quoted)
                        if name_quoted is not None
                        else None,
                        username=urllib.parse.unquote(username_quoted)
                        if username_quoted is not None
                        else None,
                        email=urllib.parse.unquote(email_quoted)
                        if email_quoted is not None
                        else None,
                        tutor=urllib.parse.unquote(tutor_quoted)
                        if tutor_quoted is not None
                        else None,
                        year=urllib.parse.unquote(year_quoted)
                        if year_quoted is not None
                        else None,
                    )
                except (StopIteration, IndexError, TypeError):
                    return None
        else:
            return None

    def get_student_image(
        self, student: Student, try_cache: bool = True
    ) -> Image.Image:
        if try_cache:
            cached_image = self.get_student_image_from_cache(student)
            if cached_image is not None:
                return cached_image

        if student.schoolbox_id.startswith("000_"):
            return Image.open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "../assets/local_user_image.png",
                )
            )

        url = (
            "https://ole.saintkentigern.com/portrait.php?id="
            + student.schoolbox_id
            + "&size=constrain200"
        )

        payload = {}
        headers = self.get_headers()

        response = requests.request("GET", url, headers=headers, data=payload)

        if (
            response.status_code == 302
            and response.is_redirect
            and response.next.url.startswith("https://ole.saintkentigern.com/login")
        ):
            # We've been logged out - login again

            self.login()

            return self.get_student_image(student, try_cache=try_cache)

        # Write to cache

        image_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache", "images"]
        )

        if not os.path.exists(image_cache_directory):
            os.makedirs(image_cache_directory)

        image_filename = f"{student.schoolbox_id}.png"

        image_path = os.path.join(image_cache_directory, image_filename)

        with open(image_path, "wb") as handler:
            handler.write(response.content)

        return Image.open(image_path)

    def get_student_image_from_cache(
        self, student: Student
    ) -> Union[Image.Image, None]:
        if student.schoolbox_id.startswith("000_"):
            return None

        image_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache", "images"]
        )

        if not os.path.exists(image_cache_directory):
            os.makedirs(image_cache_directory)

        image_filename = f"{student.schoolbox_id}.png"

        image_path = os.path.join(image_cache_directory, image_filename)

        if os.path.exists(image_path):
            return Image.open(image_path)
        else:
            return None

    def create_local_student(self, student: Student) -> Student:
        # Assign a schoolbox ID of 000_<random UUIDv4 as hex>, and set ID to a random UUIDv4 as int

        student.schoolbox_id = "000_" + uuid.uuid4().hex
        student.id = uuid.uuid4().int

        # Write to cache

        student_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache", "students"]
        )

        if not os.path.exists(student_cache_directory):
            os.makedirs(student_cache_directory)

        student_filename = f"{student.schoolbox_id}.txt"

        student_path = os.path.join(student_cache_directory, student_filename)

        with open(student_path, "w") as handler:
            handler.write(
                f"id={student.id}\nschoolbox_id={student.schoolbox_id}\nname={urllib.parse.quote(student.name)}\nusername={urllib.parse.quote(student.username)}\nemail={urllib.parse.quote(student.email)}\ntutor={urllib.parse.quote(student.tutor)}\nyear={urllib.parse.quote(student.year)}\nlocal_student=True\nlocal_student__operator={urllib.parse.quote(operator.operator)}\nlocal_student__time={int(time.time())}"
            )

        # Save a note

        notes.set_notes_for_student(
            student.schoolbox_id,
            f"Manually created student\nCreated by {operator.operator} at {datetime.now().strftime(sadf('%a %-d %b %Y %-I:%M:%S %p'))}",
        )

        return student

    def clear_student_cache(self):
        student_cache_directory = udd.get_user_data_dir(
            ["SaintsPay", "student-data-cache"]
        )

        def for_dir(dir):
            if os.path.exists(dir):
                for filename in os.listdir(dir):
                    if filename.startswith("000_"):
                        continue
                    elif filename.endswith(".txt"):
                        os.remove(os.path.join(dir, filename))
                    elif filename.endswith(".png"):
                        os.remove(os.path.join(dir, filename))
                    elif os.path.isdir(os.path.join(dir, filename)):
                        for_dir(os.path.join(dir, filename))

        for_dir(student_cache_directory)
