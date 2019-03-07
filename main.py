#!/usr/bin/env python3

import argparse
import contextlib
import csv
import enum
import re
import subprocess
import sys


RECORD_GROUPS_RE = re.compile(r"^(?P<id>\d{4,5}) (?P<name>.*)$")
# E.g.: 1.0000 03/25/16 04/25/16 $1,166.00 $1,882.00
DATA_GROUPS_RE = re.compile(r"""
    ^
    (?P<quantity>[\d.]+)\                       # number
    (?P<acquired_date>VARIOUS|\d\d/\d\d/\d\d)\  # date or string
    (?P<sold_date>\d\d/\d\d/\d\d)\              # date
    \$(?P<gross_proceeds>[\d.,]+)\              # amount
    \$(?P<cost_basis>[\d.,]+)                   # amount
    $
    """, re.VERBOSE)
CUSIP_RE = re.compile(r"^[A-Z0-9]{9}$")

_NULL_FUNCTION = lambda x: None


class State(enum.Enum):
  DEFAULT = 0
  AFTER_TICKER = 1
  AFTER_CUSIP = 2


class Event(enum.Enum):
  OTHER = 0
  RECORD_ID = 1
  CUSIP = 2
  DATA = 3


class Record(object):
  def __init__(self, record_dict):
    for k,v in record_dict.items():
      setattr(self, k, v)

  def __repr__(self):
    return (
      self.id + " " + self.name + " " +
      self.cusip + " " + self.quantity + " " +
      self.acquired_date + " " + self.sold_date + " " +
      self.gross_proceeds + " " + self.cost_basis)


class Classifier(object):
  def __init__(self):
    self._matchers = {
      RECORD_GROUPS_RE: Event.RECORD_ID,
      CUSIP_RE: Event.CUSIP,
      DATA_GROUPS_RE: Event.DATA,
    }

  def classify(self, line):
    for matcher, ev in self._matchers.items():
      if matcher.search(line):
        return ev
    return Event.OTHER


class LineProcessor(object):
  def __init__(self, on_record_callback):
    # Immutable state:
    self._transitions = {
      # When we get (this state, this event): call and goto (this function, this state)
      (State.DEFAULT, Event.RECORD_ID): (self._on_record_id, State.AFTER_TICKER),
      (State.DEFAULT, Event.OTHER): (_NULL_FUNCTION, State.DEFAULT),

      (State.AFTER_TICKER, Event.CUSIP): (self._on_cusip, State.AFTER_CUSIP),
      (State.AFTER_TICKER, Event.OTHER): (_NULL_FUNCTION, State.AFTER_TICKER),

      (State.AFTER_CUSIP, Event.DATA): (self._on_data, State.DEFAULT),
      (State.AFTER_CUSIP, Event.OTHER): (_NULL_FUNCTION, State.AFTER_CUSIP),
    }
    self._on_record_callback = on_record_callback
    self._classifier = Classifier()

    # Mutable state:
    self._state = State.DEFAULT
    self._partial_record = {}

  # Classify a line as given event
  def _classify(self, line):
    return self._classifier.classify(line)

  def ingest(self, line):
    stripped_line = line.strip()

    ev = self._classify(stripped_line)
    transition_fn, new_state = self._transitions[(self._state, ev)]

    # print(
    #   "In state" + str(self._state) + ' got event ' + str(ev) + 
    #   ' and line ' + stripped_line)

    transition_fn(stripped_line)

    self._state = new_state

  def _on_record_id(self, line):
    m = RECORD_GROUPS_RE.search(line);

    if not m:
      raise Exception('on_record_id')

    self._partial_record.update(m.groupdict())

  def _on_cusip(self, line):
    self._partial_record['cusip'] = line

  def _on_data(self, line):
    m = DATA_GROUPS_RE.search(line)

    if not m:
      raise Exception('on_data')

    self._partial_record.update(m.groupdict())

    self._on_record_complete()

  def _on_record_complete(self):
    self._on_record_callback(Record(self._partial_record))
    self._partial_record = {}


class RecordWriter(object):
  def __init__(self, writer):
    self._writer = writer

  def write_record(self, record):
    self._writer.writerow([
        record.id, record.name, record.cusip, record.quantity,
        record.acquired_date, record.sold_date, record.gross_proceeds,
        record.cost_basis
    ])


# From https://stackoverflow.com/a/17603000
@contextlib.contextmanager
def smart_open(filename):
  if not filename:
    fh = sys.stdout
  else:
    fh = open(args.o, 'w', newline='')

  try:
    yield fh
  finally: 
    if fh is not sys.stdout:
      fh.close()


# takes file handles and completes pdf parsing
# to output_fh. is responsible for closing 
# output fh
def fileBasedPdfParse(input_fn, output_fh):
  with output_fh as csvfile:
    writer = RecordWriter(csv.writer(csvfile))
    lp = LineProcessor(writer.write_record)

  for l in subprocess.check_output(
      ['pdftotext', '-raw', input_fn, '-'],
      universal_newlines=True).split('\n'):
    lp.ingest(l)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", help="Input PDF")
  parser.add_argument("-o", help="Output CSV")
  args = parser.parse_args()

  with smart_open(args.o) as csvfile:
    fileBasedPdfParse(args.i, csvfile)
