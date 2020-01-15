import requests
import os
from zipfile import ZipFile
from bs4 import BeautifulSoup
import re
from io import BytesIO
from tqdm import tqdm
import pandas as pd
import numpy as np
import glob
import shutil


def assure_path_exists(path):
    if not os.path.exists(path):
            os.makedirs(path)
    # else:
    #     shutil.rmtree(os.path.join(os.path.dirname(__file__), 'SampleInputFiles'), ignore_errors=False)
    #     os.makedirs('SampleInputFiles', mode=0o777)


def extractZip(session_requests, monthlistdata, path):
    abc = tqdm(monthlistdata)
    for month in abc:
        abc.set_description("Downloading %s" % month)
        r = session_requests.get(month)
        z = ZipFile(BytesIO(r.content))
        z.extractall(path)


def makedirectories():

    if not os.path.exists('cleanFiles'):
        os.makedirs('cleanFiles', mode=0o777)
    else:
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'cleanFiles'), ignore_errors=False)
        os.makedirs('cleanFiles', mode=0o777)

    if not os.path.exists('cleanFilesWithSummaries'):
        os.makedirs('cleanFilesWithSummaries', mode=0o777)
    else:
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'cleanFilesWithSummaries'), ignore_errors=False)
        os.makedirs('cleanFilesWithSummaries', mode=0o777)


def fillNAN(df):
    df['cred_scr'] = df['cred_scr'].fillna(0)
    df['fst_hmebyr_flg'] = df['fst_hmebyr_flg'].fillna('Unknown')
    df['metro_stat_area'] = df['metro_stat_area'].fillna(0)
    df['mort_insur_pctg'] = df['mort_insur_pctg'].fillna(0)
    df['nbr_units'] = df['nbr_units'].fillna(0)
    df['occu_status'] = df['occu_status'].fillna('Unknown')
    df['orig_cmbnd_ln_to_value'] = df['orig_cmbnd_ln_to_value'].fillna(0)
    df['orig_dbt_to_incm'] = df['orig_dbt_to_incm'].fillna(0)
    df['orig_ln_to_value'] = df['orig_ln_to_value'].fillna(0)
    df['chnl'] = df['chnl'].fillna('Unknown')
    df['pre_pnl_mort_flg'] = df['pre_pnl_mort_flg'].fillna('Unknown')
    df['proptype'] = df['proptype'].fillna('Unknown')
    df['zipcode'] = df['zipcode'].fillna(0)
    df['ln_purps'] = df['ln_purps'].fillna('Unknown')
    df['nbr_brwrs'] = df['nbr_brwrs'].fillna(0)
    df['spr_confrm_flg'] = df['spr_confrm_flg'].fillna('N')
    return df


def changedatatype(df):
    #Change the data types for all column
    df[['cred_scr', 'metro_stat_area', 'mort_insur_pctg', 'nbr_units', 'orig_cmbnd_ln_to_value',
             'orig_dbt_to_incm', 'orig_upb', 'orig_ln_to_value', 'zipcode', 'orig_ln_trm',
             'nbr_units']] = df[
        ['cred_scr', 'metro_stat_area', 'mort_insur_pctg', 'nbr_units', 'orig_cmbnd_ln_to_value',
         'orig_dbt_to_incm', 'orig_upb', 'orig_ln_to_value', 'zipcode', 'orig_ln_trm',
         'nbr_units']].astype('int64')
    df[['spr_confrm_flg', 'srvcr_name', 'pre_hrp_ln_seq_nmbr']] = df[
        ['spr_confrm_flg', 'srvcr_name', 'pre_hrp_ln_seq_nmbr']].astype('str')
    return df


def fillNA(df):
    df['curr_ln_delin_status'] = df['curr_ln_delin_status'].fillna(0)
    df['repurch_flag'] = df['repurch_flag'].fillna('Unknown')
    df['mod_flag'] = df['mod_flag'].fillna('N')
    df['zero_bal_cd'] = df['zero_bal_cd'].fillna(00)
    df['zero_bal_eff_dt'] = df['zero_bal_eff_dt'].fillna('999901')
    df['current_dupb'] = df['current_dupb'].fillna(0)
    df['lst_pd_inst_duedt'] = df['lst_pd_inst_duedt'].fillna('999901')
    df['mi_recoveries'] = df['mi_recoveries'].fillna(0)
    df['net_sale_proceeds'] = df['net_sale_proceeds'].fillna('U')
    df['non_mi_recoveries'] = df['non_mi_recoveries'].fillna(0)
    df['expenses'] = df['expenses'].fillna(0)
    df['legal_costs'] = df['legal_costs'].fillna(0)
    df['maint_pres_costs'] = df['maint_pres_costs'].fillna(0)
    df['taxes_and_insur'] = df['taxes_and_insur'].fillna(0)
    df['misc_expenses'] = df['misc_expenses'].fillna(0)
    df['actual_loss_calc'] = df['actual_loss_calc'].fillna(0)
    df['mod_cost'] = df['mod_cost'].fillna(0)
    return df


def changedtype(df):
    #Change the data types for all column
    df[
        ['curr_ln_delin_status', 'loan_age', 'remng_mon_to_leg_matur', 'zero_bal_cd', 'current_dupb',
         'actual_loss_calc', 'est_loan_to_vlv']] = df[
        ['curr_ln_delin_status', 'loan_age', 'remng_mon_to_leg_matur', 'zero_bal_cd', 'current_dupb',
         'actual_loss_calc', 'est_loan_to_vlv']].astype('float64')

    df[['mon_rpt_prd', 'zero_bal_eff_dt', 'lst_pd_inst_duedt', 'stp_mod_flg', 'def_pymnt_mod']] = df[
        ['mon_rpt_prd', 'zero_bal_eff_dt', 'lst_pd_inst_duedt', 'stp_mod_flg', 'def_pymnt_mod']].astype('str')
    return df


def minmax(perf_df):
    new1_df = perf_df.groupby(['ln_sq_nbr'])['current_aupb'].min().to_frame(name='min_current_aupb').reset_index()
    new2_df = perf_df.groupby(['ln_sq_nbr'])['current_aupb'].max().to_frame(name='max_current_aupb').reset_index()
    new3_df = perf_df.groupby(['ln_sq_nbr'])['curr_ln_delin_status'].min().to_frame(
        name='min_curr_ln_delin_status').reset_index()
    new4_df = perf_df.groupby(['ln_sq_nbr'])['curr_ln_delin_status'].max().to_frame(
        name='max_curr_ln_delin_status').reset_index()
    new5_df = perf_df.groupby(['ln_sq_nbr'])['zero_bal_cd'].min().to_frame(name='min_zero_bal_cd').reset_index()
    new6_df = perf_df.groupby(['ln_sq_nbr'])['zero_bal_cd'].max().to_frame(name='max_zero_bal_cd').reset_index()
    new7_df = perf_df.groupby(['ln_sq_nbr'])['mi_recoveries'].min().to_frame(name='min_mi_recoveries').reset_index()
    new8_df = perf_df.groupby(['ln_sq_nbr'])['mi_recoveries'].max().to_frame(name='max_mi_recoveries').reset_index()
    new11_df = perf_df.groupby(['ln_sq_nbr'])['non_mi_recoveries'].min().to_frame(
        name='min_non_mi_recoveries').reset_index()
    new12_df = perf_df.groupby(['ln_sq_nbr'])['non_mi_recoveries'].max().to_frame(
        name='max_non_mi_recoveries').reset_index()
    new13_df = perf_df.groupby(['ln_sq_nbr'])['expenses'].min().to_frame(name='min_expenses').reset_index()
    new14_df = perf_df.groupby(['ln_sq_nbr'])['expenses'].max().to_frame(name='max_expenses').reset_index()
    new15_df = perf_df.groupby(['ln_sq_nbr'])['legal_costs'].min().to_frame(name='min_legal_costs').reset_index()
    new16_df = perf_df.groupby(['ln_sq_nbr'])['legal_costs'].max().to_frame(name='max_legal_costs').reset_index()
    new17_df = perf_df.groupby(['ln_sq_nbr'])['maint_pres_costs'].min().to_frame(
        name='min_maint_pres_costs').reset_index()
    new18_df = perf_df.groupby(['ln_sq_nbr'])['maint_pres_costs'].max().to_frame(
        name='max_maint_pres_costs').reset_index()
    new19_df = perf_df.groupby(['ln_sq_nbr'])['taxes_and_insur'].min().to_frame(
        name='min_taxes_and_insur').reset_index()
    new20_df = perf_df.groupby(['ln_sq_nbr'])['taxes_and_insur'].max().to_frame(
        name='max_taxes_and_insur').reset_index()
    new21_df = perf_df.groupby(['ln_sq_nbr'])['misc_expenses'].min().to_frame(name='min_misc_expenses').reset_index()
    new22_df = perf_df.groupby(['ln_sq_nbr'])['misc_expenses'].max().to_frame(name='max_misc_expenses').reset_index()
    new23_df = perf_df.groupby(['ln_sq_nbr'])['actual_loss_calc'].min().to_frame(
        name='min_actual_loss_calc').reset_index()
    new24_df = perf_df.groupby(['ln_sq_nbr'])['actual_loss_calc'].max().to_frame(
        name='max_actual_loss_calc').reset_index()
    new25_df = perf_df.groupby(['ln_sq_nbr'])['mod_cost'].min().to_frame(name='min_mod_cost').reset_index()
    new26_df = perf_df.groupby(['ln_sq_nbr'])['mod_cost'].max().to_frame(name='max_mod_cost').reset_index()

    final_df = new1_df.merge(new2_df, on='ln_sq_nbr').merge(new3_df, on='ln_sq_nbr').merge(new4_df,
                                                                                           on='ln_sq_nbr').merge(
        new5_df, on='ln_sq_nbr').merge(new6_df, on='ln_sq_nbr').merge(new7_df, on='ln_sq_nbr').merge(new8_df,
                                                                                                     on='ln_sq_nbr').merge(
        new11_df, on='ln_sq_nbr').merge(new12_df, on='ln_sq_nbr').merge(new13_df, on='ln_sq_nbr').merge(new14_df,
                                                                                                        on='ln_sq_nbr').merge(
        new15_df, on='ln_sq_nbr').merge(new16_df, on='ln_sq_nbr').merge(new17_df, on='ln_sq_nbr').merge(new18_df,
                                                                                                        on='ln_sq_nbr').merge(
        new19_df, on='ln_sq_nbr').merge(new20_df, on='ln_sq_nbr').merge(new21_df, on='ln_sq_nbr').merge(new22_df,
                                                                                                        on='ln_sq_nbr').merge(
        new23_df, on='ln_sq_nbr').merge(new24_df, on='ln_sq_nbr').merge(new25_df, on='ln_sq_nbr').merge(new26_df,
                                                                                                        on='ln_sq_nbr')

    return final_df


def combined_origin(str):
    # print(str)
    writeHeader1 = True
    if "sample" in str:
        filename = "SampleOriginationCombined.csv"
    else:
        filename = "HistoricalOriginationCombined.csv"

    abc = tqdm(glob.glob(str))

    with open(filename, 'w', encoding='utf-8', newline="") as file:
        for f in abc:
            abc.set_description("Working on  %s" % f)
            sample_df = pd.read_csv(f, sep="|",
                                    names=['cred_scr', 'fst_paymnt_dte', 'fst_hmebyr_flg', 'maturty_dte',
                                            'metro_stat_area', 'mort_insur_pctg', 'nbr_units', 'occu_status',
                                            'orig_cmbnd_ln_to_value', 'orig_dbt_to_incm', 'orig_upb',
                                            'orig_ln_to_value', 'orig_intrst_rate', 'chnl', 'pre_pnl_mort_flg',
                                            'prodtype', 'propstate', 'proptype', 'zipcode', 'ln_sq_nbr',
                                            'ln_purps', 'orig_ln_trm', 'nbr_brwrs', 'slr_name', 'srvcr_name',
                                            'spr_confrm_flg','pre_hrp_ln_seq_nmbr'], skipinitialspace=True)
            sample_df = fillNAN(sample_df)
            sample_df = changedatatype(sample_df)
            sample_df['Year_Orig'] = ['19' + x if x == '99' else '20' + x for x in
                                 (sample_df['ln_sq_nbr'].apply(lambda x: x[2:4]))]
            if writeHeader1 is True:
                sample_df.to_csv(file, mode='a', header=True, index=False)
                writeHeader1 = False
            else:
                sample_df.to_csv(file, mode='a', header=False, index=False)


def combined_performance(str):
    print(str)
    writeHeader2 = True
    if "sample" in str:
        filename = "SamplePerformanceCombinedSummary.csv"
    else:
        filename = "HistoricalPerformanceCombinedSummary.csv"

    abc = tqdm(glob.glob(str))

    with open(filename, 'w', encoding='utf-8', newline="") as file:
        for f in abc:
            abc.set_description("Working on  %s" % f)
            perf_df = pd.read_csv(f, sep="|",
                                  names=['ln_sq_nbr', 'mon_rpt_prd', 'current_aupb', 'curr_ln_delin_status',
                                                 'loan_age', 'remng_mon_to_leg_matur', 'repurch_flag', 'mod_flag',
                                                 'zero_bal_cd', 'zero_bal_eff_dt', 'current_int_rte', 'current_dupb',
                                                 'lst_pd_inst_duedt', 'mi_recoveries', 'net_sale_proceeds',
                                                 'non_mi_recoveries', 'expenses', 'legal_costs', 'maint_pres_costs',
                                                 'taxes_and_insur', 'misc_expenses', 'actual_loss_calc', 'mod_cost',
                                                 'stp_mod_flg','def_pymnt_mod','est_loan_to_vlv'],
                                  skipinitialspace=True)
            perf_df['curr_ln_delin_status'] = [999 if x == 'R' else x for x in (perf_df['curr_ln_delin_status'].apply(lambda x: x))]
            perf_df['curr_ln_delin_status'] = [0 if x == 'XX' else x for x in (perf_df['curr_ln_delin_status'].apply(lambda x: x))]
            perf_df = fillNA(perf_df)
            perf_df = changedtype(perf_df)
            filtered_df = minmax(perf_df)

            filtered_df['Year_Perf'] = ['20' + x for x in (filtered_df['ln_sq_nbr'].apply(lambda x: x[2:4]))]

            if writeHeader2 is True:
                filtered_df.to_csv(file, mode='a', header=True, index=False)
                writeHeader2 = False
            else:
                filtered_df.to_csv(file, mode='a', header=False, index=False)


USERNAME = input("Enter Username: ")
PASSWORD = input("Password: ")

payload = {
        "username": USERNAME,
        "password": PASSWORD
}

session_requests = requests.session()

login_url = "https://freddiemac.embs.com/FLoan/secure/auth.php"

result = session_requests.post(
    login_url,
    data=payload,
    headers=dict(referer=login_url)
)

url = 'https://freddiemac.embs.com/FLoan/Data/download.php'
agreement_payload = {
    "accept": "Yes",
    "action": "acceptTandC",
    "acceptSubmit": "Continue"
}
result = session_requests.post(
    url,
    agreement_payload,
    headers=dict(referer=url)
)

yearlist = []
sampledata = []

for i in range(2005, 2018):
    yearlist.append(i)


allfiles = BeautifulSoup(result.text, "html.parser")

atags = allfiles.find_all('a')

for a in atags:
                for yr in yearlist:
                    if str(yr) in a.text:
                        if re.match('sample', a.text):
                            link = a.get('href')
                            foldername = 'SampleInputFiles'
                            samplepath = str(os.getcwd())+"/"+foldername
                            assure_path_exists(samplepath)
                            finallink ='https://freddiemac.embs.com/FLoan/Data/' + link
                            sampledata.append(finallink)

#extractZip(session_requests, sampledata, samplepath)

#makedirectories()

foldername = 'SampleInputFiles'
sample_origin_folder = str(os.getcwd())+"/"+foldername+"/sample_orig_*.txt"
sample_performance_folder = str(os.getcwd())+"/"+foldername+"/sample_svcg_*.txt"

combined_origin(sample_origin_folder)
combined_performance(sample_performance_folder)

# makedirectories()

print("Done")