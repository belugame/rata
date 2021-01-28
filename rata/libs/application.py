import os
from itertools import cycle

import urwid

from .edit_tasks import make_edit_task_screen
from .io import format_duration
from .tasks import TaskManager
from .widgets import NewTask, TaskButtonWrap, RenameTask


order_modes = cycle(["duration", "most recent", "name"])
palette = [
    ('cyan-bg', 'black', 'light cyan'),
    ('cyan', 'light cyan', ''),
    ('normal', '', ''),
    ('red', 'dark red', ''),
]
refresh_interval = 1
help_line = " | ".join(["Enter: start/stop task", "Right: edit", "(n)ew task", "(s)tart/stop last task", "s(o)rt tasks",
                        "(r)ename task", "(q)uit"])


class Rata(object):
    sort_order = "name"
    message_box = urwid.AttrMap(urwid.Text(""), "error")
    view = "main"

    def __init__(self, file_name):
        self.file_name = file_name
        self.taskmanager = TaskManager(file_name)
        self.current_task = self.taskmanager.find_running_task()
        self.body = self.create_tasks_menu()
        self.loop = urwid.MainLoop(
            self.body,
            palette,
            unhandled_input=self.handle_input
        )
        self.loop.set_alarm_in(refresh_interval, self.refresh)
        self.loop.run()

    def refresh(self, loop, data):
        """Update clocks on the screen: current task duration & total task duration."""
        if self.view == "main":  # Don't do anything if not on main screen as widgets are different
            if self.current_task:
                self.current_task.button.base_widget.set_label(self.current_task.label)
                self.set_message("{}: {}".format(self.current_task.name,
                                                 self.current_task.running_record.label_with_duration))
            else:
                self.set_message("")
            if hasattr(self.body.base_widget, "body"):
                self.body.base_widget.body[0].set_text(self.title)
        loop.set_alarm_in(refresh_interval, self.refresh)

    def to_main_screen(self):
        """Replace what is on the screen and show the main screen again"""
        focus = None
        if self.view == "main":
            focus = self.body.original_widget.base_widget.get_focus()[0].base_widget
        self.view = "main"
        self.set_message("")
        self.body.original_widget = self.create_tasks_menu()
        # Move cursor to where it was before:
        if focus:
            for index, w in enumerate(self.body.original_widget.base_widget.body):
                if hasattr(w.base_widget, "button") and w.base_widget.task == focus.task:
                    self.body.original_widget.base_widget.set_focus(index)

    def set_message(self, message, error=False):
        if error:
            self.message_box.set_attr_map({None: 'red'})
        else:
            self.message_box.set_attr_map({None: 'cyan'})
        self.message_box.base_widget.set_text(message)

    @property
    def title(self):
        """Defines top line shown above the task table."""
        rate = os.getenv("RATE")
        total_duration = self.taskmanager.total_duration
        todays_duration = self.taskmanager.todays_duration
        total_earned = ""
        today_earned = ""
        if rate:
            total_earned = " | {:.2f} €".format(total_duration.total_seconds()/3600 * float(rate))
            today_earned = " | {:.2f} €".format(todays_duration.total_seconds()/3600 * float(rate))
        title = "Tasks {} - sorted by {} - Total {}{} - Today {}{}".format(
            self.file_name, self.sort_order, format_duration(total_duration), total_earned,
            format_duration(todays_duration), today_earned)
        return title

    def create_tasks_menu(self):
        """Renders title and bottom line and in the middle a scrollable table of tasks with their duration"""
        body = [urwid.Text(self.title), urwid.Divider()]
        for task in self.taskmanager.tasks_by(self.sort_order):
            button = TaskButtonWrap(task)
            urwid.connect_signal(button.button, "click", self.toggle_recording_task, task)
            if task == self.current_task:
                button = urwid.AttrMap(button, "cyan")
            else:
                button = urwid.AttrMap(button, "normal", "cyan-bg")
            task.button = button
            body.append(button)
        body += [urwid.Divider(),
                 self.message_box,
                 urwid.Divider(),
                 urwid.Text(help_line)]
        return urwid.Padding(urwid.ListBox(urwid.SimpleFocusListWalker(body)), left=0, right=0)

    def toggle_recording_task(self, button, task):
        """Event handler for Enter-key on a task line: start/stop recording"""
        if self.current_task:
            self.current_task.stop()
        if self.current_task == task:  # Enter was pressed on currently running task
            self.current_task = None
        else:
            self.current_task = task
            self.current_task.start()
        self.to_main_screen()

    def handle_input(self, key):
        """Main widget key press event handler."""
        if self.view == "main":  # Don't do anything if not on main screen as widgets are different
            if key == 's':  # stop tracking
                self._start_stop_tracking()
                return
            if key == 'r':  # rename task under cursor
                self._rename_task()
                return
            elif key == 'n':  # track new task
                self._new_task()
                return
            elif key == 'o':  # sort
                self._sort()
                return
            elif key == 'right':  # edit
                self._edit_task()
                return
        if key == 'q':  # quit
            self._quit()
            return
        if key == 'esc':
            self.to_main_screen()

    def _quit(self):
        if self.current_task:
            self.current_task.stop()
            self.current_task = None
        raise urwid.ExitMainLoop()

    def _start_stop_tracking(self):
        if not self.taskmanager.tasks:
            return
        if self.current_task:
            self.current_task.stop()
            self.current_task = None
        else:
            tasks = self.taskmanager.tasks[:]
            tasks.sort(key=lambda t: t.most_recent, reverse=True)
            self.current_task = tasks[0]
            tasks[0].start()
        self.to_main_screen()  # Will resort

    def _rename_task(self):
        if not self.taskmanager.tasks:
            return
        self.view = "rename"
        task = self.body.base_widget.focus.base_widget.task
        edit = RenameTask(self, task, u"Rename task:\n")
        fill = urwid.Filler(edit)
        self.body.original_widget = fill

    def _new_task(self):
        self.view = "new task"
        edit = NewTask(self, u"New task:\n")
        fill = urwid.Filler(edit)
        self.body.original_widget = fill

    def _sort(self):
        self.sort_order = next(order_modes)
        self.to_main_screen()  # Will resort

    def _edit_task(self):
        if not self.taskmanager.tasks:
            return
        self.body.original_widget = make_edit_task_screen(self)

    def add_new_task(self, name):
        """Event handler for when a new task name was entered: Adds and starts tracking it."""
        task = self.taskmanager.add(name)
        if self.current_task:
            self.current_task.stop()
        self.current_task = task
        self.to_main_screen()
        task.start()
