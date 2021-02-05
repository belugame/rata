# rata: raw time tracker

Painless interactive terminal time tracker with git versioning running on python 3 and urwid.

What I disliked in other terminal time trackers was that I had to use complicated key strokes or type commands to
start/stop and switch between tasks. I wanted single-key actions, fast switching and typing only for naming tasks.

## Demo screencast

See a demo screencast here: https://asciinema.org/a/uyiaMiwlXnZjSj12N8fTudIrt

## Screenshot

![alt text](https://user-images.githubusercontent.com/16137830/106795236-1e842a80-665a-11eb-992c-62ac94f7318d.png)

It suits people who only want to track the name, duration, start and end time of tasks they worked on, e.g. for billing
a project per hour. A simple to use replacement for emacs org-mode respectively vim-dotoo.

It's my first urwid project and there is no test coverage. Use at own risk, though it commits all changes directly to
git. So you should always be able to recover your entries.

## Features

- runs in the terminal and adjusts to terminal size
- track time per task in a single text-based file
- quickly change between, add and rename tasks
- shows when you started tracking, since when you are tracking and total duration tracked per task
- edit previous records with check for overlaps
- keep track of all changes through automatic git commits
- sort by duration/name/most recently worked on
- output file loosely based on org-mode, fully text-based. Though please do not try to add something other than time
  records to the file. Rata won't be able to read it.

## Installation

pip install rata

## Usage

rata requires a file name in a git-versioned folder. It will create a new commit for any change.

````
git init ~/timerecords
rata ~/timerecords/projectFoo.txt

or if you want to see how much you will have to bill:

RATE=<hourly rate> rata ~/timerecords/projectFoo.txt

````
I would strongly recommend to not keep other files than what rata creates in the repository as it runs `git reset` before committing and may mess with your git stage.

### Key-bindings

#### Main view

- Enter: Start/Stop tracking task under cursor
- up/down: Move cursor over task list
- right: Show and edit list of time records of task under cursor
- n: Add new task and start tracking it
- r: Rename task under cursor
- s: Start/Stop current/last track (independant of cursor position)
- o: Toggle sorting: by name, total task duration, most recently tracked
- q: Quit program

#### Edit mode

- Enter: Edit record under cursor (modify the timestamps and confirm with Enter again)
- h: Quick-edit: Move start time under cursor 1 minute ahead
- j: Quick-edit: Move start time under cursor 1 minute back
- k: Quick-edit: Move end time under cursor 1 minute ahead
- l: Quick-edit: Move end time under cursor 1 minute back
- Esc: Go back to main view

### New task mode

- Enter a name for your new task
- Enter: Confirm
- Esc: Go back to main view

## Sample output file

````
* Client support
:LOGBOOK:
CLOCK: [2020-12-27 10:22:10] -- [2020-12-27 11:30:11]
CLOCK: [2020-12-24 09:30:03] -- [2020-12-24 10:40:06]
:END:
* On-site meetings
:LOGBOOK:
CLOCK: [2020-12-20 13:44:11] -- [2020-12-20 16:50:14]
CLOCK: [2020-12-25 15:00:07] -- [2020-12-25 17:38:10]

````
