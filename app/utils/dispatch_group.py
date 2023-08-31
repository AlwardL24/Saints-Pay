from threading import Thread


class DispatchGroup:
    entranceCount = 0
    exitCount = 0
    callbacks = []

    def __init__(self):
        pass

    def enter(self):
        self.entranceCount += 1

    def leave(self):
        self.exitCount += 1

        if self.exitCount == self.entranceCount:
            for i, callback in enumerate(self.callbacks):
                Thread(target=callback).start()

                del self.callbacks[i]

    def notify(self, callback):
        if self.exitCount == self.entranceCount:
            Thread(target=callback).start()
            return

        self.callbacks.append(callback)
