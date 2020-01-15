import requests
import re
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import time
import datetime
import sys
from tqdm import tqdm
import pandas as pd
import numpy as np
import glob
import csv

url = 'https://freddiemac.embs.com/FLoan/secure/auth.php'
postUrl = 'https://freddiemac.embs.com/FLoan/Data/download.php'


def payloadCreation(user, passwd):
    creds = {'username': user, 'password': passwd}
    return creds


def assure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def extracrtZip(s, monthlistdata, path):
    abc = tqdm(monthlistdata)
    for month in abc:
        abc.set_description("Downloading %s" % month)
        r = s.get(month)
        z = ZipFile(BytesIO(r.content))
        z.extractall(path)


def getFilesFromFreddieMacPerQuarter(payload, quarter, testquarter):
    with requests.Session() as s:
        preUrl = s.post(url, data=payload)
        payload2 = {'accept': 'Yes', 'acceptSubmit': 'Continue', 'action': 'acceptTandC'}
        finalUrl = s.post(postUrl, payload2)
        linkhtml = finalUrl.text
        allzipfiles = BeautifulSoup(linkhtml, "html.parser")
        ziplist = allzipfiles.find_all('td')
        sampledata = []
        historicaldata = []
        count = 0
        # q =quarter[2:6]
        # t =testquarter[2:6]
        for li in ziplist:
            zipatags = li.findAll('a')
            for zipa in zipatags:
                fetchFile = 'historical_data1_'
                if (quarter in zipa.text):
                    if (fetchFile in zipa.text):
                        link = zipa.get('href')
                        foldername = 'HistoricalInputFiles'
                        Historicalpath = str(os.getcwd()) + "/" + foldername
                        assure_path_exists(Historicalpath)
                        finallink = 'https://freddiemac.embs.com/FLoan/Data/' + link
                        print(finallink)
                        historicaldata.append(finallink)
                elif (testquarter in zipa.text):
                    if (fetchFile in zipa.text):
                        link = zipa.get('href')
                        foldername = 'HistoricalInputFiles'
                        Historicalpath = str(os.getcwd()) + "/" + foldername
                        assure_path_exists(Historicalpath)
                        finallink = 'https://freddiemac.embs.com/FLoan/Data/' + link
                        print(finallink)
                        historicaldata.append(finallink)
        extracrtZip(s, historicaldata, Historicalpath)


def getFilesFromFreddieMac(payload, st, en):
    with requests.Session() as s:
        preUrl = s.post(url, data=payload)
        payload2 = {'accept': 'Yes', 'acceptSubmit': 'Continue', 'action': 'acceptTandC'}
        finalUrl = s.post(postUrl, payload2)
        linkhtml = finalUrl.text
        allzipfiles = BeautifulSoup(linkhtml, "html.parser")
        ziplist = allzipfiles.find_all('td')
        sampledata = []
        historicaldata = []
        count = 0
        slist = []
        for i in range(int(st), int(en) + 1):
            # print(i)
            slist.append(i)
        for li in ziplist:
            zipatags = li.findAll('a')
            for zipa in zipatags:
                for yr in slist:
                    if str(yr) in zipa.text:
                        if re.match('sample', zipa.text):
                            link = zipa.get('href')
                            foldername = 'SampleInputFiles'
                            Samplepath = str(os.getcwd()) + "/" + foldername
                            assure_path_exists(Samplepath)
                            finallink = 'https://freddiemac.embs.com/FLoan/Data/' + link
                            sampledata.append(finallink)
        extracrtZip(s, sampledata, Samplepath)


def main():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
    args = sys.argv[1:]
    print("Starting")

    user = input("Enter Username: ")
    passwd = input("Enter password: ")
    trainQ = input("Enter Quarter for trainQ: ")
    testQ = input("Enter Test Quarter: ")

    print("USERNAME=" + user)
    print("PASSWORD=" + passwd)
    print("TRAINQUARTER=" + (trainQ))
    print("TESTQUARTER=" + (testQ))

    payload = payloadCreation(user, passwd)
    getFilesFromFreddieMacPerQuarter(payload, trainQ, testQ)

    rx = []
    rx.append(trainQ)
    rx.append(testQ)

    with open("input.csv", "w") as resultFile:
        wr = csv.writer(resultFile, quoting=csv.QUOTE_NONE)
        wr.writerow(rx)


if __name__ == '__main__':
    main()