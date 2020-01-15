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
from sklearn import metrics
import pandas as pd
import numpy as np
import glob
import csv
from configparser import ConfigParser
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import sys


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


def getFilesFromFreddieMacPerQuarter(payload,testquarter):
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
                if (testquarter in zipa.text):
                    if (fetchFile in zipa.text):
                        link = zipa.get('href')
                        foldername = 'HistoricalInputFiles'
                        Historicalpath = str(os.getcwd()) + "/" + foldername
                        assure_path_exists(Historicalpath)
                        finallink = 'https://freddiemac.embs.com/FLoan/Data/' + link
                        print(finallink)
                        historicaldata.append(finallink)
        extracrtZip(s, historicaldata, Historicalpath)

def  getTrainData(trainQ):
    print("Working on Train data")
    downloadPath='./HistoricalInputFiles/historical_data1_time_'+trainQ+'.txt'

    df = pd.read_csv(downloadPath, sep="|",
                     names=['id_loan','svcg_cycle','current_upb','delq_sts','loan_age','mths_remng',
                           'repch_flag','flag_mod', 'cd_zero_bal',
                           'dt_zero_bal','current_int_rt','non_int_brng_upb','dt_lst_pi','mi_recoveries',
                           'net_sale_proceeds','non_mi_recoveries','expenses', 'legal_costs',
                           'maint_pres_costs','taxes_ins_costs','misc_costs','actual_loss', 'modcost','step_mod_flag',
                            'def_py_mod', 'eltv'], skipinitialspace=True, error_bad_lines=False, index_col=False, dtype='unicode', nrows=1500000)
    print(df.shape)

    df.columns = ['id_loan', 'svcg_cycle', 'current_upb', 'delq_sts', 'loan_age', 'mths_remng',
                           'repch_flag', 'flag_mod', 'cd_zero_bal',
                           'dt_zero_bal', 'current_int_rt', 'non_int_brng_upb', 'dt_lst_pi', 'mi_recoveries',
                           'net_sale_proceeds', 'non_mi_recoveries', 'expenses', 'legal_costs',
                           'maint_pres_costs', 'taxes_ins_costs', 'misc_costs', 'actual_loss', 'modcost','step_mod_flag',
                            'def_py_mod', 'eltv']

    df.current_upb = df.current_upb.astype('float64')
    df.non_int_brng_upb = df.non_int_brng_upb.astype('float64')
    df.current_int_rt = df.current_int_rt.astype('float64')

    df[['svcg_cycle', 'loan_age', 'mths_remng']] = df[
        ['svcg_cycle', 'loan_age', 'mths_remng']].astype('int64')

    df[['id_loan', 'delq_sts']] = df[['id_loan', 'delq_sts']].astype('str')

    df['delq_sts'] = [999 if x == 'R' else x for x in (df['delq_sts'].apply(lambda x: x))]
    df['delq_sts'] = [0 if x == 'XX' else x for x in (df['delq_sts'].apply(lambda x: x))]

    df[['delq_sts']] = df[['delq_sts']].astype('int64')
    df['new_delinq'] = (df.delq_sts > 0).astype(int)

    df.drop('delq_sts', axis=1, inplace=True)

    traincols = ['svcg_cycle', 'current_upb', 'loan_age',
                 'mths_remng', 'current_int_rt', 'non_int_brng_upb']
    y_train = df['new_delinq']

    print("Training data cleaned and training variables created")

    return df


def getTestData(testQ,df):
    print("Working on Test data")
    downloadPath = './HistoricalInputFiles/historical_data1_time_' + testQ + '.txt'

    test_df = pd.read_csv(downloadPath, sep="|",
                                names=['id_loan','svcg_cycle','current_upb','delq_sts','loan_age','mths_remng',
                           'repch_flag','flag_mod', 'cd_zero_bal',
                           'dt_zero_bal','current_int_rt','non_int_brng_upb','dt_lst_pi','mi_recoveries',
                           'net_sale_proceeds','non_mi_recoveries','expenses', 'legal_costs',
                           'maint_pres_costs','taxes_ins_costs','misc_costs','actual_loss', 'modcost','step_mod_flag',
                            'def_py_mod', 'eltv'],
                            skipinitialspace=True, error_bad_lines=False, index_col=False, dtype='unicode',
                            nrows=500000)

    test_df.columns = ['id_loan', 'svcg_cycle', 'current_upb', 'delq_sts', 'loan_age', 'mths_remng',
                  'repch_flag', 'flag_mod', 'cd_zero_bal',
                  'dt_zero_bal', 'current_int_rt', 'non_int_brng_upb', 'dt_lst_pi', 'mi_recoveries',
                  'net_sale_proceeds', 'non_mi_recoveries', 'expenses', 'legal_costs',
                  'maint_pres_costs', 'taxes_ins_costs', 'misc_costs', 'actual_loss', 'modcost','step_mod_flag',
                  'def_py_mod', 'eltv']

    test_df.current_upb = test_df.current_upb.astype('float64')
    test_df.non_int_brng_upb = test_df.non_int_brng_upb.astype('float64')
    test_df.current_int_rt = test_df.current_int_rt.astype('float64')

    test_df[['svcg_cycle', 'loan_age', 'mths_remng']] = test_df[
        ['svcg_cycle', 'loan_age', 'mths_remng']].astype('int64')

    test_df[['id_loan', 'delq_sts']] = test_df[['id_loan', 'delq_sts']].astype('str')

    test_df['delq_sts'] = [999 if x == 'R' else x for x in (test_df['delq_sts'].apply(lambda x: x))]
    test_df['delq_sts'] = [0 if x == 'XX' else x for x in (test_df['delq_sts'].apply(lambda x: x))]

    test_df[['delq_sts']] = test_df[['delq_sts']].astype('int64')
    test_df['new_delinq'] = (test_df.delq_sts > 0).astype(int)

    traincols = ['svcg_cycle', 'current_upb', 'loan_age',
                 'mths_remng', 'current_int_rt', 'non_int_brng_upb']
    y_train = df['new_delinq']
    Train_DF = df[traincols]

    testcols = ['svcg_cycle', 'current_upb', 'loan_age',
                'mths_remng', 'current_int_rt', 'non_int_brng_upb']
    y_test = test_df['new_delinq']
    Test_DF = test_df[testcols]
    model = LogisticRegression()
    mod_fit = model.fit(Train_DF, y_train)
    pred = mod_fit.predict(Test_DF)
    metrics.accuracy_score(y_test, pred)
    print(metrics.accuracy_score(y_test, pred))

    cf = confusion_matrix(y_test, pred, labels=None, sample_weight=None)
    numDelinqProper = cf[1][1]
    numnondelinqimproper = cf[0][1]
    numRecordsInDataset = y_test.count()
    numPredictedDelinq = cf[1][0] + cf[1][1]
    numActualDelinq = y_test[y_test == 1].count()

    record = testQ + "," + str(numActualDelinq) + "," + str(numPredictedDelinq) + "," + str(numRecordsInDataset) + "," + str(numDelinqProper) + "," + str(numnondelinqimproper)
    from pathlib import Path
    FINALCSVPATH = "./ClassificationMetrics.csv"
    checkFile = Path(FINALCSVPATH)

    if checkFile.is_file():
        with open(FINALCSVPATH, "a") as fil:
            fil.write(record)
            fil.write("\n")
    else:
        with open(FINALCSVPATH, "a") as fil:
            fil.write(
                "Quarter,NumActualDelinquents,NumOfPredictedDelinquents,NumRecordsInDataset,NumDelinquentsProperlyClassified,NumNonDelinquentsImproperlyClassified")
            fil.write("\n")
            fil.write(record)
            fil.write("\n")

def main():

    user=input("Enter Username: ")
    passwd=input("Enter Password: ")
    trainQ=input("Enter quarter for training: ")
    testQ=input("Enter quarter for testing: ")

    print("USERNAME=" + user)
    print("PASSWORD=" + passwd)
    print("TRAINQUARTER=" + trainQ)
    print("TESTQUARTER=" + testQ)

    fromquarter = 'Q21999'
    toquarter = 'Q12016'

    startquarter = int(fromquarter[1])
    endquarter = int(toquarter[1])
    startyear = int(fromquarter[2:6])
    endyear = int(toquarter[2:6])

    payload = payloadCreation(user, passwd)
    getFilesFromFreddieMacPerQuarter(payload, trainQ)
    Train_DF=getTrainData(trainQ)

    currentquarter = startquarter
    currentyear = startyear

    breakloop = False
    breakloopprev = False

    while breakloop == False:

        analyzequarter = "Q" + str(currentquarter) + str(currentyear)
        getFilesFromFreddieMacPerQuarter(payload,analyzequarter)
        getTestData(analyzequarter,Train_DF)

        print(analyzequarter)
        if currentquarter < 4:
            currentquarter += 1
        elif currentquarter == 4:
            currentquarter = 1
            currentyear = currentyear + 1
        if breakloopprev == True:
            break
        if ((currentyear == endyear) & (endquarter == currentquarter)):
            breakloopprev = True


if __name__ == '__main__':
    main()