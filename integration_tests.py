#!/usr/bin/env python3

import argparse
import main
import os
import sys
import unittest



class IntegrationTests(unittest.TestCase):
  print('1')
  TEST_PDF_DIR = ""


  def test_me(self):
    print('4')
    testPdfFiles = []
    for file in os.listdir(IntegrationTests.TEST_PDF_DIR):
      if file.endsWith(".pdf"):


    with self.subTest():

      print(os.path.join(IntegrationTests.TEST_PDF_DIR, file))


if __name__ == '__main__':
  print('2')
  if len(sys.argv) > 1:
    print('3')
    IntegrationTests.TEST_PDF_DIR = sys.argv.pop()

  unittest.main()
