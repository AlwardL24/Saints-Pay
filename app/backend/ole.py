from typing import Union, Callable
import requests
import utils.user_data_directory as udd
import urllib.parse
import re


class OLE:
    class Error(Exception):
        def __init__(self, message):
            self.message = message
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
    is_staff = False

    def __init__(
        self,
        username: str,
        password: str,
        warning_callback: Callable[[str, str], None] = None,
    ):
        self.username = username
        self.password = password

        self.login(warning_callback=warning_callback)

    def get_headers(self):
        return {
            "Accept": "text/html, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 SaintsPayBot/1.0 (+https://saintspay.lucasalward.com/bot)",
            "Cookie": self.cookie,
        }.copy()

    def login(self, warning_callback: Callable[[str, str], None] = None):
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

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code >= 400 and response.status_code < 500:
            raise OLE.Error(f"{response.text}")
        elif response.status_code not in [200, 302]:
            raise OLE.Error("An unknown error occurred while logging in.")

        self.cookie = response.headers["Set-Cookie"]

        data = response.json()
        if data["role"] != "staff" and warning_callback:
            warning_callback(
                "OLE Login Warning",
                f"You are currently logged in as a {data['role']}. A staff account is required to show student photos and tutor groups.",
            )

        is_staff = data["role"] == "staff"

    def search_students(self, query: str) -> list[Student]:
        def get_page(number: int) -> list[OLE.Student]:
            url = (
                "https://ole.saintkentigern.com/resource/user/search?keyword="
                + urllib.parse.quote(query)
                + f"&type=user&p={str(number)}"
            )

            payload = {}
            headers = self.get_headers()

            response = requests.request("GET", url, headers=headers, data=payload)

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

        return get_page(1)

    def student(self, student: Student) -> Student:
        return self.student_from_id(schoolbox_id=student.schoolbox_id)

    def student_from_id(self, schoolbox_id: str) -> Student:
        url = "https://ole.saintkentigern.com/search/user/" + schoolbox_id

        payload = {}
        headers = self.get_headers()

        response = requests.request("GET", url, headers=headers, data=payload)
        print("GOT RESPONSE")

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

        if self.is_staff:
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

        return student

    def get_student_image(self, student: Student) -> bytes:
        url = (
            "https://ole.saintkentigern.com/portrait.php?id="
            + student.schoolbox_id
            + "&size=constrain200"
        )

        payload = {}
        headers = self.get_headers()

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.content
