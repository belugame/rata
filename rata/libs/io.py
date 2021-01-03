from datetime import datetime
import os
import shutil
import subprocess
import tempfile

datetime_format = "%Y-%m-%d %H:%M:%S"


def is_inside_git_dir(file_name):
    cmd = 'cd {} && git rev-parse --is-inside-work-tree'.format(os.path.dirname(os.path.abspath(file_name)))
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return process.stdout.read() == b'true\n'


def read_file(file_name):
    tasks = {}
    with open(file_name, "r") as input_file:
        for line in input_file:
            if line.strip() in (":LOGBOOK:", ":END:"):
                continue
            elif line.startswith("*"):
                task = line.lstrip("* ").rstrip()
                if task not in tasks:
                    tasks[task] = []
            else:
                assert line.startswith("CLOCK:"), line
                # CLOCK: [2020-12-11 Fr 10:26]--[2020-12-11 Fr 12:00] => 01:34
                start, end = parse_line(line)
                tasks[task].append([start, end])
    return tasks


def write_file(tasks, file_name, message):
    tasks = tasks[:]
    tasks.sort(key=lambda t: t.name.lower())
    tmp_file = tempfile.NamedTemporaryFile("w+t", delete=False)
    for t in tasks:
        tmp_file.write("* {}\n".format(t.name))
        tmp_file.write(":LOGBOOK:\n")
        records = t.records[:]
        records.sort(key=lambda r: r.start, reverse=True)
        for start, end in [(r.start, r.end) for r in records]:
            tmp_file.write("CLOCK: {}\n".format(format_record(start, end)))
        tmp_file.write(":END:\n")
    tmp_file.close()
    shutil.copyfile(tmp_file.name, file_name)
    git_commit(file_name, message)
    os.unlink(tmp_file.name)


def format_record(start, end):
    end = end.strftime(datetime_format) if end else "running"
    return "[{}] -- [{}]".format(start.strftime(datetime_format), end)


def format_duration(my_timedelta):
    d = my_timedelta.total_seconds()
    duration = "{:02.0f}:{:02.0f}:{:02.0f}".format(d // 3600, d % 3600 // 60, d % 60)
    return duration


def parse_line(line):
    """
    Parse lines with a start/end timestamp to datetime records.
    CLOCK: [2020-12-11 Fr 10:26]--[2020-12-11 Fr 12:00] => 01:34
    or also: [2020-12-11 Fr 10:26]--[2020-12-11 Fr 12:00] => 01:34
    """
    _, start, end = line.split("[")
    start, _ = start.split("]")
    start = datetime.strptime(start, datetime_format)
    if "running" in end:
        end = None
    else:
        end, _ = end.split("]")
        end = datetime.strptime(end.strip(), datetime_format)
    return start, end


def git_commit(file_name, message):
    cmd = 'cd {} && git reset . && git add {} && git commit -m "rata: {}"'.format(
        os.path.dirname(os.path.abspath(file_name)), file_name, message)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    process.communicate()
