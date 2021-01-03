import urwid

from .widgets import RecordEdit, RecordButton


def make_edit_task_screen(application):
    application.view = "edit"
    body = [urwid.Text("Edit records"), urwid.Divider()]
    task = application.body.base_widget.focus.base_widget.task
    task.records.sort(key=lambda r: r.start, reverse=True)
    for r in task.records:
        button = RecordButton(r, application)
        urwid.connect_signal(button, 'click', _edit_record, (application, r))
        body.append(button)
    body += [urwid.Divider(),
             urwid.Text("Enter: edit | h/j: Move start up/down | k/l: Move end up/down | Esc: cancel"),
             urwid.Divider(),
             application.message_box]
    return urwid.Padding(urwid.ListBox(urwid.SimpleFocusListWalker(body)), left=0, right=0)


def _edit_record(button, record_tuple):
    application, record = record_tuple
    application.set_message("")
    application.body.original_widget = urwid.ListBox([
            RecordEdit(application, record, edit_text=record.label),
            urwid.Divider(),
            application.message_box])
