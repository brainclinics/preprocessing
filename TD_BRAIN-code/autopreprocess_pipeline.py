#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 09:45:43 2019

@author: hannekevandijk

copyright: Research Institute Brainclinics, Brainclinics Foundation, Nijmegen, the Netherlands

"""

from autopreprocessing_OA import dataset as ds
import os
import numpy as np
import copy

def autopreprocess_standard(varargsin, subject = None, startsubj =0):
    """ standard autopreprocessing pipeline
    varargsin is a dictionary required with fields:
        ['sourcepath']: path of the original datasets
        ['savepath']: folder where the data should be saved
        ['condition']: which condition should be preprocessed
    subject: (optional) if a specific subject should be processed, should be IDcode e.g. 12013456
            but can also be can be the nth file in a folder
        """
    # Defining the reading path
    if not varargsin['sourcepath']:
        print('sourcepath not defined, where is your data?')

    if not varargsin['preprocpath']:
        print('preprocpath not defined')
    sourcepath = varargsin['sourcepath']
    preprocpath = varargsin['preprocpath']
    print(sourcepath)
    print(preprocpath)

    #other variables
    if varargsin['condition']:
        reqconds = varargsin['condition']
    else:
        reqconds = ['EO','EC']
    rawreport = 'yes'

    #Inventory of all relevant subjects
    exclude = np.hstack((['Apple','DS','._', 'preprocessed','results'],varargsin['exclude'])); s=[]
    subs = [s for s in os.listdir(sourcepath) if os.path.isdir(os.path.join(sourcepath,s)) and not any([excl in s for excl in exclude])]
    subs = np.sort(subs)
    print(len(subs))
#    subs = [s for s in os.listdir(sourcepath+'/') if os.path.isdir(os.path.join(sourcepath,s)) and not '.' in s]
#    subs = np.sort(subs)
    k=startsubj
    if subject == None:
        subarray = range(k,len(subs))
    elif type(subject) ==int:
        subarray = [subject]
    elif type(subject) == str:
        subarray = np.array([np.where(subs==subject)[0]][0])
    sp = k
    for s in subarray:
        print(sp)
        sessions = [session for session in os.listdir(os.path.join(sourcepath,subs[s])) if not any([excl in session for excl in exclude]) and os.path.isdir(os.path.join(sourcepath,subs[s],session))]
        for sess in range(len(sessions)):
            conditions = []
            allconds = np.array([conds for conds in os.listdir(os.path.join(sourcepath,subs[s],sessions[sess])) if (('.csv' in conds) or ('.edf' in conds)) and not any([excl in conds for excl in exclude])])
            if reqconds == 'all':
                conditions = allconds
            else:
                conditions = np.array([conds for conds in allconds if any([a.upper() in conds for a in reqconds])])

            for c in range(len(conditions)):
                print(conditions[c])
                if len(conditions)>0:
                    inname = os.path.join(sourcepath, subs[s], sessions[sess],conditions[c])
                    #try:
                    tmpdat = ds(inname)
                    tmpdat.loaddata()
                    tmpdat.bipolarEOG()
                    tmpdat.apply_filters()
                    tmpdat.correct_EOG()
                    tmpdat.detect_emg()
                    tmpdat.detect_jumps()
                    tmpdat.detect_kurtosis()
                    tmpdat.detect_extremevoltswing()
                    tmpdat.residual_eyeblinks()
                    tmpdat.define_artifacts()

                    trllength = 'all'
                    npy = copy.deepcopy(tmpdat)
                    npy.segment(trllength = trllength, remove_artifact='no')
                    subpath = os.path.join(preprocpath,subs[s])
                    if not os.path.isdir(subpath):
                        os.mkdir(subpath)
                    sesspath = os.path.join(preprocpath,subs[s],sessions[sess])
                    if not os.path.isdir(sesspath):
                        os.mkdir(sesspath)
                    npy.save(sesspath)

                    if rawreport == 'yes':#for the raw data report
                        lengthtrl = 10
                        pdf = copy.deepcopy(tmpdat)
                        pdf.segment(trllength = lengthtrl, remove_artifact='no')
                        pdf.save_pdfs(sesspath)
                   # except:
                   #     print('processing of '+inname+ ' went wrong')
        sp=sp+1

