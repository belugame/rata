from datetime import datetime, timedelta

import urwid

from .io import parse_line
from .exceptions import RecordOverlap


class TaskButtonWrap(urwid.WidgetWrap):
    """
    Button that adjusts label to terminal width
    https://stackoverflow.com/questions/41571349/change-button-label-on-screen-redraw-urwid
    """
    def __init__(self, task):
        self.task = task
        self.button = urwid.Button(task.label[0] + " " + task.label[1])
        super().__init__(self.button)

    def rows(self, *args, **kw):
        return 1

    def render(self, size, *args, **kw):
        cols = size[0]
        name, timestamp = self.task.label
        max_name_size = cols - 6 - len(timestamp)  # 6 = border size
        label_format = "{{:<{width}.{width}}} {{}}".format(width=max_name_size)
        label = label_format.format(name, timestamp)
        self.button.set_label(label)
        return super().render(size, *args, **kw)

    def set_label(self, label):
        self._w.set_label(label)


class NewTask(urwid.Edit):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application

    def keypress(self, size, key):
        if key == 'enter':
            self.application.add_new_task(self.get_edit_text())
        if key == 'esc':
            self.application.to_main_screen()
        super().keypress(size, key)


class RecordEdit(urwid.Edit):
    def __init__(self, application, record, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application
        self.record = record
        if not hasattr(self, "_original"):
            self._original = self.get_edit_text()

    def keypress(self, size, key):
        if key == 'enter':  # replace the edited time record
            self._submit_modification()
        if key == 'esc':
            self.application.to_main_screen()
        super().keypress(size, key)

    def _submit_modification(self):
        old = self._original
        new = self.get_edit_text()
        old_start, old_end = parse_line(old)
        new_start, new_end = self._clean(new)

        self.record.start = new_start
        self.record.end = new_end

        try:
            self.application.taskmanager.check_for_overlapping()
        except RecordOverlap as e:
            self.record.start = old_start
            self.record.end = old_end
            self.application.set_message("Failed to edit. {}".format(str(e)), error=True)
            return
        self.record.task.write("{}: Change record".format(self.record.task.name[:30]))
        self.application.to_main_screen()

    def _clean(self, line):
        try:
            new_start, new_end = parse_line(line)
            if new_end and new_start > new_end:
                self.application.set_message("Invalid input: end before start", error=True)
            return new_start, new_end
        except ValueError:
            self.application.set_message("Failed to parse!", error=True)
            return

    def _get_record_index(self, start, end):
        try:
            return self.task.records.index([start, end])
        except ValueError:
            self.application.set_message("Failed to edit record. Could not find it.", error=True)


class RecordButton(urwid.Button):
    def __init__(self, record, application, *args, **kwargs):
        super().__init__(record.label, *args, **kwargs)
        self.record = record
        self.application = application

    def keypress(self, size, key):
        if key == "h":
            self._move_by_timedelta("start", timedelta(minutes=1))
        if key == "j":
            self._move_by_timedelta("start", timedelta(minutes=-1))
        if key == "k" and self.record.end:
            self._move_by_timedelta("end", timedelta(minutes=1))
        if key == "l" and self.record.end:
            self._move_by_timedelta("end", timedelta(minutes=-1))
        if key == 'left':
            self.application.to_main_screen()
            return
        return super().keypress(size, key)

    def _move_by_timedelta(self, side, my_timedelta):
        assert side in ("start", "end")
        old_value = getattr(self.record, side)
        setattr(self.record, side, old_value + my_timedelta)
        end = self.record.end or datetime.now().replace(microsecond=0)
        if self.record.start > end:
            setattr(self.record, side, old_value)
            self.application.set_message("Failed to edit: Start time must be before end time.", error=True)
            return
        try:
            self.record.task.taskmanager.check_for_overlapping()
        except RecordOverlap as e:
            setattr(self.record, side, old_value)
            self.application.set_message("Failed to edit. {}".format(str(e)), error=True)
        else:
            self.set_label(self.record.label)
            self.record.task.write("{}: Change record".format(self.record.task.name[:30]))
            self.application.set_message("Edit saved.")


class RenameTask(urwid.Edit):
    def __init__(self, application, task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application
        self.task = task
        self.set_edit_text(task.name)

    def keypress(self, size, key):
        new_name = self.get_edit_text()
        if new_name:
            if key == 'enter':
                old_name = self.task.name
                self.task.name = new_name
                self.task.write("{}: Rename to '{}'".format(old_name, new_name))
                self.application.to_main_screen()
        if key == 'esc':
            self.application.to_main_screen()
        super().keypress(size, key)
