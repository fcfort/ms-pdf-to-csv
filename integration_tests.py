#!/usr/bin/env python3

import argparse
import main
import io
import os
import sys
import unittest


class SavingStringIO(io.StringIO):
  def close(self):   
    self.value = self.getvalue()
    return super(SavingStringIO, self).close()


class IntegrationTests(unittest.TestCase):
  def test_me(self):
    for file in os.listdir(IntegrationTests.TEST_PDF_DIR):
      if file.endswith(".pdf"):
        with self.subTest():
          print(file)
          pdf_path = os.path.join(IntegrationTests.TEST_PDF_DIR, file)

          # Read expected CSV                    
          with open(pdf_path + '.csv', 'r') as expected_csv:
            expected_csv_str = expected_csv.read()
          
          # Read actual CSV
          actual_csv = SavingStringIO()
          pdf_path = os.path.join(IntegrationTests.TEST_PDF_DIR, file)
          main.fileBasedPdfParse(pdf_path, actual_csv)
              
          # Compare
          self.maxDiff = None
          self.assertEqualWithLineEndings(expected_csv_str, actual_csv.value)

  def toUnix(string):
    return string.replace('\r\n','\n')

  def assertEqualWithLineEndings(self, expected_str, actual_str):
    self.assertEqual(
      IntegrationTests.toUnix(expected_str.strip()),
      IntegrationTests.toUnix(actual_str.strip()))


if __name__ == '__main__':
  if len(sys.argv) > 1:
    IntegrationTests.TEST_PDF_DIR = sys.argv.pop()

  unittest.main()
