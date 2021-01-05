from datetime import datetime, timedelta

from .io import datetime_format, format_duration, read_file, write_file
from .exceptions import RecordOverlap


class Record(object):

    def __init__(self, task, start=None, end=None):
        self.task = task
        if start and end:
            assert start <= end, "Assert {} <= {}".format(start, end)
        self.start = start or datetime.now().replace(microsecond=0)
        self.end = end

    def __repr__(self):
        return "<Record {}: {} -- {}>".format(self.task.name, self.start, self.end or "running")

    def stop(self):
        assert not self.end
        self.end = datetime.now().replace(microsecond=0)

    @property
    def duration(self):
        return (self.end or datetime.now().replace(microsecond=0)) - self.start

    @property
    def is_running(self):
        return self.end is None

    @property
    def label(self):
        end = self.end.strftime(datetime_format) if self.end else "running"
        return "[{}] -- [{}]".format(self.start.strftime(datetime_format), end)

    @property
    def label_with_duration(self):
        end = self.end.strftime(datetime_format) if self.end else "running since {}".format(
                format_duration(self.duration))
        return "[{}] -- [{}]".format(self.start.strftime(datetime_format), end)


class Task(object):
    button = None

    def __init__(self, taskmanager, name, timerecords=None):
        self.taskmanager = taskmanager
        self.name = name
        self.records = [Record(self, r[0], r[1]) for r in timerecords] or []

    def __radd__(self, other):
        if other == 0:
            return self.duration
        return other + self.duration

    def __repr__(self):
        return "<Task: {}>".format(self.name)

    def start(self):
        self.records.append(Record(self))
        self.write("{}: Start task".format(self.name[:30]))

    def stop(self):
        for r in self.records:
            if r.is_running:
                r.stop()
                break
        else:
            raise Exception("Not running")
        self.taskmanager.check_for_overlapping()
        self.write("{}: Stop task".format(self.name[:30]))
        self.button.attr_map = {None: "normal"}

    def write(self, message=""):
        self.taskmanager.write(message)

    @property
    def duration(self):
        return sum([r.duration for r in self.records], timedelta())

    @property
    def label(self):
        return self.name, format_duration(self.duration)

    @property
    def is_running(self):
        return any([r.is_running for r in self.records])

    @property
    def most_recent(self):
        default = datetime(year=9999, month=1, day=1)
        return max([r.end or default for r in self.records], default=datetime(year=1, month=1, day=1))

    @property
    def running_record(self):
        for r in self.records:
            if r.is_running:
                return r
        return None


class TaskManager(object):
    tasks = []

    def __init__(self, file_name):
        self.file_name = file_name
        try:
            raw_tasks = read_file(file_name)
        except FileNotFoundError:
            pass
        else:
            for name, timerecords in raw_tasks.items():
                self.tasks.append(Task(self, name, timerecords))
        self.check_for_overlapping()

    def tasks_by(self, sort_order="name"):
        if sort_order == "name":
            self.tasks.sort(key=lambda t: t.name.lower())
        elif sort_order == "duration":
            self.tasks.sort(key=lambda t: t.duration, reverse=True)
        elif sort_order == "most recent":
            self.tasks.sort(key=lambda t: t.most_recent, reverse=True)
        else:
            raise Exception("unexpected sort_order")
        return self.tasks

    def add(self, name):
        new_task = None
        for t in self.tasks:
            if t.name == name:
                new_task = t
                break
        if not new_task:
            new_task = Task(self, name, [])
            self.tasks.append(new_task)
        return new_task

    def check_for_overlapping(self):
        flattened_records = []
        # Flat list of all timerecords but with last item in each timerecord being the task so we can show which two
        # tasks collide.
        [flattened_records.extend([[r.start, r.end or datetime.now(), t]
                                  for r in t.records]) for t in self.tasks]
        for f in flattened_records:
            all_others = flattened_records[:]
            all_others.remove(f)
            for o in all_others:
                latest_start = max(f[0], o[0])
                earliest_end = min(f[1], o[1])
                delta = (earliest_end - latest_start)
                if delta.total_seconds() > 0:
                    raise RecordOverlap("Overlapping records:\n{:50.50s} {} -- {}\n{:50.50s} {} -- {}".format(
                        o[2].name, o[0], o[1], f[2].name, f[0], f[1]))

    def find_running_task(self):
        """Return task that has no end time. Helps when program crashed while tracking and was restarted."""
        for t in self.tasks:
            if t.is_running:
                return t
        return None

    def write(self, message=""):
        write_file(self.tasks, self.file_name, message)

    @property
    def total_duration(self):
        return sum(self.tasks) or timedelta(seconds=0)

    @property
    def todays_duration(self):
        today = datetime.today().date()
        today_duration = timedelta(seconds=0)
        for t in self.tasks:
            for r in t.records:
                if r.start.date() == today:
                    today_duration += r.duration
        return today_duration
