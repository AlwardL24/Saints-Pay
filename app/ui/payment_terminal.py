import backend.ole
from . import new_transaction
from . import student_search


class Window(student_search.Window):
    def __init__(self, master, ole: backend.ole.OLE):
        student_search.Window.__init__(
            self,
            master,
            ole,
            title="Payment Terminal",
            select_command=lambda student: new_transaction.Window(
                master=self.master, student=student, ole=self.ole
            ),
        )
