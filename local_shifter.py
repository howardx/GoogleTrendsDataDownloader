#!/usr/bin/env python
import csv
from StringIO import StringIO
import os

class FiscalYearShifter:
  def __init__(self, TermsDoneRows, us, world, usShifted, worldShifted):
    self.TermDict = {}  
    self.us = us 
    self.world = world # for saving intermediate CSV files
    self.usShifted = usShifted
    self.worldShifted = worldShifted
    self.TermsDoneRows = TermsDoneRows

  def FiscalInfoTracker(self):
    for i in range(0, len(self.TermsDoneRows)):
      if self.TermsDoneRows[i] != "":
        DoneList = self.TermsDoneRows[i].split(',') 
        SearchTerm = DoneList[0]
        FiscalEnd = DoneList[1]
        WorldFile = os.path.join(self.world, SearchTerm + " DataFile.csv")
        USFile = os.path.join(self.us, SearchTerm + " US DataFile.csv")
        s_WorldFile = os.path.join(self.worldShifted, SearchTerm + " DataFile.csv")
        s_USFile = os.path.join(self.usShifted, SearchTerm + " US DataFile.csv")
        # populating dictionary, pairing terms and their information
        self.TermDict[SearchTerm] = [FiscalEnd, WorldFile, USFile, s_WorldFile, s_USFile]

  def DetectForIntermediateCSV(self):
    for term in self.TermDict:
      valueList = self.TermDict[term]
      usCSVname = valueList[2]
      wCSVname = valueList[1]
      self.ReadRawCSVFormTwoLists(term, usCSVname, 0)
      self.ReadRawCSVFormTwoLists(term, wCSVname, 1)
      
  def ReadRawCSVFormTwoLists(self, term, CSV, worldFlag):
    try:
      f = open(CSV, 'rb')
    except:
      i = 1
      #print CSV + " file is empty or does not exist.\n"
    else:
      # adding placeholders for shifting
      dateList = [""]
      trendList = ["","","",""]
      shift = 0
      for iterline in f:
        line = iterline.strip() # get rid of \r\n
        if line == '':
          continue 
        elif not line.find("Top regions for ") != -1 and not line.find("Top subregions for ") != -1 and not line.find("An error has been detected") != -1 :
          lineList = line.split(',')
          if len(lineList) == 2:
            dateList.append(lineList[0])
            trendList.append(lineList[1])
          else:
            dateList.append(lineList[0]) 
        else:
          break
      self.AssociateFiscalEndWithTrends(dateList, trendList, term, worldFlag)
      
  def AssociateFiscalEndWithTrends(self, date, trend, term, worldFlag):
    flag = 0
    FiscalEnd = self.TermDict[term][0]
    if int(FiscalEnd) == 3 or int(FiscalEnd) == 6 or int(FiscalEnd) == 9 or int(FiscalEnd) == 12: # fiscal quarter end = calendar quarter end
      pass # do nothing
    elif int(FiscalEnd) == 2 or int(FiscalEnd) == 5 or int(FiscalEnd) == 8 or int(FiscalEnd) == 11:
      flag = 4 # trends data shift down 4 cells/rows
    elif int(FiscalEnd) == 1 or int(FiscalEnd) == 4 or int(FiscalEnd) == 7 or int(FiscalEnd) == 10:
      flag = -4 # trends data shift up 4 cells/rows
    self.FormatOutputString(term, date, trend, flag, worldFlag)
  
  def FormatOutputString(self, term, Date, Trends, flag, worldFlag):
    data = Trends[5:] # remove headers
    Shifted_Trends = self.shift_list(data, flag)
    final = Trends[:5] + Shifted_Trends
    OutputString = ''
    for d, t in zip(Date, final):
      OutputString = OutputString + d + ',' + t + '\n'
    self.writeCSV(term, OutputString, worldFlag)

  def shift_list(self, l, shift, empty=""):
    src_index = max(-shift, 0)
    dst_index = max(shift, 0)
    length = max(len(l) - abs(shift), 0)
    new_l = [empty] * len(l)
    new_l[dst_index:dst_index + length] = l[src_index:src_index + length]
    return new_l

  def writeCSV(self, term, Output, worldFlag):
    if worldFlag == 1:
      f = open(self.TermDict[term][3], 'wb')
    else:
      f = open(self.TermDict[term][4], 'wb')
    f.write(Output)
    f.close()
    
 
def main():
  f = open(os.path.join('..', 'TermsDownloadedForWorldAndUS.csv'), 'rb')
  lineList = f.readlines()
  f.close()
  usPath = os.path.join('..', 'Data', 'US')
  worldPath = os.path.join('..', 'Data', 'World')
  usPath_s = os.path.join('..', 'Data', 'US_shifted')
  worldPath_s = os.path.join('..', 'Data', 'World_shifted')
  if not os.path.exists(usPath_s):
    os.makedirs(usPath_s)
  if not os.path.exists(worldPath_s):
    os.makedirs(worldPath_s)
  fo = FiscalYearShifter(lineList, usPath, worldPath, usPath_s, worldPath_s)
  fo.FiscalInfoTracker()
  fo.DetectForIntermediateCSV()
if __name__ == "__main__":
  main()

