#!/usr/bin/env python3

import main
import unittest


class TestClassifier(unittest.TestCase):

  def test_ClassifiesRecordIdLine(self):
    self.assertEqual(
      main.Classifier().classify('00002 HOOLI INC'),
      main.Event.RECORD_ID)
  
  def test_ClassifiesCusip(self):
    self.assertEqual(
      main.Classifier().classify('30303M102'),
      main.Event.CUSIP)

  def test_ClassifiesData(self):
    self.assertEqual(
      main.Classifier().classify(
          '1.0000 03/25/16 04/25/16 $1,166.00 $1,882.00'),
      main.Event.DATA)


class TestLineProcessor(unittest.TestCase):

  def test_DataRegexMatches(self):
    m = main.DATA_GROUPS_RE.search(
        '1.0000 03/25/16 04/25/16 $1,166.00 $1,882.00')
    self.assertEqual(m.group('quantity'), '1.0000')

  def test_EmitsOneRecord(self):
    def oneRecord(record):
      global test_record  # so we can verify it later
      test_record = record

    lp = main.LineProcessor(oneRecord)
    lp.ingest('00002 HOOLI INC')
    lp.ingest('30303M102')
    lp.ingest('1.0000 03/25/16 04/25/16 $1,166.00 $1,882.00')

    self.assertIsNotNone(test_record)
    

if __name__ == '__main__':
    unittest.main()
