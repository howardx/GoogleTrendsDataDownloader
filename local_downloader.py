#!/usr/bin/env python
import cookielib
import csv
from StringIO import StringIO
import urllib
from time import sleep
import os
import mechanize # pip install mechanize
import random 
import getpass
import datetime

class Googler:
  def __init__(self, TermsInfoRows, us, world, DoneTermsFile, NotfirstRun):
    self.queryDict = {} # searchterm : query
    self.TempUS = us 
    self.TempWorld = world # for saving intermediate CSV files
    self.TermsInfoRows = TermsInfoRows
    self.DoneTermsFile = DoneTermsFile
    self.NotfirstRun = NotfirstRun 

  def QueryBuilder(self):
    Done = []
    if self.NotfirstRun:
      with open(self.DoneTermsFile) as DoneTerms:
        reader = csv.reader(DoneTerms, skipinitialspace = True)
        Done, DoneFiscal = zip(*reader)
        DoneTerms.close()
    for i in range(1, len(self.TermsInfoRows)):#skip first row
      if self.TermsInfoRows[i] != "":
        TermInfoList = self.TermsInfoRows[i].split(',') 
        SearchTerm = urllib.quote(TermInfoList[1])
        if TermInfoList[1] not in Done:
          Fiscal = TermInfoList[3]
          FiscalEnd = Fiscal.split('/') # month always is first element
          WorldQuery = "http://www.google.com/trends/viz?q=" + SearchTerm + "&cmpt=q&graph=all_csv"
          USQuery = "http://www.google.com/trends/viz?q=" + SearchTerm + "&cmpt=q&graph=all_csv&geo=US"
          WorldTempFile = os.path.join(self.TempWorld, TermInfoList[1]+" DataFile.csv")
          USTempFile = os.path.join(self.TempUS, TermInfoList[1] + " US DataFile.csv")
          self.queryDict[TermInfoList[1]] = [WorldQuery, USQuery, FiscalEnd[0], WorldTempFile, USTempFile]

  def SendRequestToGoogle(self, username, password):
    br = mechanize.Browser()
    # Create cookie jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    br.set_handle_robots(False)
    # Act like we're a real browser
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    response = br.open('https://accounts.google.com/ServiceLogin?hl=en&continue=https://www.google.com/')
    forms = mechanize.ParseResponse(response)
    form = forms[0]
    form['Email'] = username
    form['Passwd'] = password
    response = br.open(form.click())
  
    keyList = self.queryDict.keys()
    keyCount = len(keyList)
    i = 0
    TermsDone = open(self.DoneTermsFile,'ab')
    print "\n\n log-in success! \n\n"
    while i < keyCount:
      SearchTerm = keyList[i]
      Queries = self.queryDict[SearchTerm]
      WorldQuery = Queries[0]
      USQuery = Queries[1]
      FiscalEnd = Queries[2] # ending month of fiscal year
      sleep(random.uniform(40,70))
      WorldResponse = br.open(WorldQuery)
      WorldResult = csv.reader(StringIO(WorldResponse.read()))
      sleep(random.uniform(30,60))
      USResponse = br.open(USQuery) # searchterm : query
      USResult = csv.reader(StringIO(USResponse.read()))

      TempWorld = Queries[3] # temperary file pathes
      TempUS = Queries[4]
      # Send contents out for writing intermediate output CSV files
      W_Error = self.IntermediateCSV(WorldResult, TempWorld)
      US_Error = self.IntermediateCSV(USResult, TempUS)
      if W_Error == -1 or US_Error == -1:
        self.ErrorHandler(SearchTerm) # quota limit
      else:
        i = i + 1 
        # keep track of downloaded CSV files, prevetent repeats
        TermsDone.write(SearchTerm + ',' + FiscalEnd + '\n')
        print "%s\t\tDONE"%(SearchTerm) # for monitoring 
    TermsDone.close()
 
  def IntermediateCSV(self, content, TempFileName):
    self.SilentRemove(TempFileName)
    f = open(TempFileName, 'wb')
    writer = csv.writer(f) # create CSV file writer obj
    for row in content:
      writer.writerow(row)
      for cellNum in range(0, len(row)):
        if row[cellNum].find("An error has been detected") != -1:
          f.close()
          return -1 # You have reached your quota limit. Please try again later
    return 0

  def SilentRemove(self, filename):
    try:
      os.remove(filename)
    except OSError: # error = "no such file or directory"
      pass

  def ErrorHandler(self, Term):
    print Term
    print"\n\n\tA Slight Hiccup Has Occured:\n\nGoogle has detected that we are downloading data programatically\n\nThe program is pausing 10 seconds for a retry\n"
    for i in range(0, 10):
      print (10-i)
      sleep(1)
    print "Retry!\n"
    return

def main():
  print "\n\nPlease make sure to TURN OFF Google 2-step verification!\n"
  username = raw_input("Please enter gmail username: ").strip()
  password = getpass.getpass("Please enter password: ").strip()
  print "Your account credential information will NOT be disclosed in any way!\n"

  DoneTermsFileName = os.path.join('..','TermsDownloadedForWorldAndUS.csv')
  f = open(os.path.join('..','FullList.csv'), 'rb')
  lineList = f.readlines()
  f.close()
  usTempPath = os.path.join('..','Data','US')
  worldTempPath = os.path.join('..','Data','World')
  if not os.path.exists(usTempPath):
    os.makedirs(usTempPath)
  if not os.path.exists(worldTempPath):
    os.makedirs(worldTempPath)
  NotfirstRun = os.path.isfile(DoneTermsFileName)
  go = Googler(lineList, usTempPath, worldTempPath, DoneTermsFileName, NotfirstRun)
  go.QueryBuilder()

  go.SendRequestToGoogle(username, password)
if __name__ == "__main__":
  main()
