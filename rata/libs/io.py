from datetime import datetime
import json
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
        data = json.load(input_file)
    for task_name, records in data.items():
        tasks[task_name] = []
        for record in records:
            start = datetime.strptime(record["start"], datetime_format)
            end = datetime.strptime(record["end"], datetime_format) if record["end"] else None
            tasks[task_name].append([start, end])
    return tasks


def write_file(tasks, file_name, message):
    tasks = tasks[:]
    tasks.sort(key=lambda t: t.name.lower())
    data = {}
    for t in tasks:
        records = t.records[:]
        records.sort(key=lambda r: r.start, reverse=True)
        data[t.name] = [
            {
                "start": r.start.strftime(datetime_format),
                "end": r.end.strftime(datetime_format) if r.end else None
            }
            for r in records
        ]
    tmp_file = tempfile.NamedTemporaryFile("w+t", delete=False)
    json.dump(data, tmp_file, indent=2)
    tmp_file.close()
    shutil.copyfile(tmp_file.name, file_name)
    git_commit(file_name, message)
    os.unlink(tmp_file.name)


def format_duration(my_timedelta):
    d = my_timedelta.total_seconds()
    duration = "{:02.0f}:{:02.0f}:{:02.0f} / {:>4.1f}h".format(
            d // 3600, d % 3600 // 60, d % 60, float(d/3600))
    return duration


def parse_line(line):
    """
    Parse lines with a start/end timestamp to datetime records.
    Format: [2020-12-11 10:26:23] -- [2020-12-11 12:00:00]
    or: [2020-12-11 10:26:23] -- [running]
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
