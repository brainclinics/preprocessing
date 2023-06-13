#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 16:11:11 2021

@author: hannekevandijk
"""
import os
import numpy as np

class FilepathFinder(object):
    """*---------------------------------------------------------------------*
    This object class collects all filepaths of data of interest defined by a pattern
    (such as an extension) that are within the root_dir, excluding folders or datatypes
    if necessary, for use in DataLoader which will in its turn be used in
    tensorflow.keras.Model.fit_generator

    use as filepaths = FilepathFinder(pattern, root_dir, exclude, test_size=0.1)
        * root_dir: string of the path the data is at (this could be any level
                                                         above specific datasets,
                                                         faster when closer to
                                                         actual filelocations)
        * pattern: specifics about the files you want to include
        * exclude: an array of specific folders or file patterns you don't want
        to include
        * test_size is optional if you want to do an sklearn.model_selection.GroupShuffleSplit
        sklearn.model_selection.GroupShuffleSplit is built into this object and takes
        in the IDcodes as groups and test_size as test_size

    !! Note that right now, this object explicitly only takes in first sessions
    *-----------------------------------------------------------------------*"""
    import os, pickle
    import numpy as np
    def __init__ (self, pattern, root_dir, exclude, session='all', test_size=None):
        self.pattern = pattern
        self.root_dir = root_dir
        self.exclude = exclude
        self.test_size = test_size
        self.session = session
    def get_filenames(self):
        """returns and array of all filepaths adhering to the selected pattern
        and root_dir  in <data>.selectedfiles"""
        datapaths = self.___find___()
        datafiles = [f for f in datapaths if not any([excl in f for excl in self.exclude])]
        selectedfiles = []

        if self.session == 'first':
            for f in datafiles:
                idcode = f.rsplit('/')[-3]
                sesdata = [sess for sess in os.listdir(os.path.split(os.path.split(os.path.abspath(f))[0])[0]) if not any([excl in sess for excl in self.exclude])]
                sessnr = []
                for sess in sesdata:#right now only taking in first sessions
                    sessnr = np.append(sessnr, np.int(sess.rsplit('.')[0][-1]))
                datapick = np.min(sessnr)
                sel = [files for files in datafiles if idcode+'-'+str(np.int(datapick)) in files]
                selectedfiles.append(np.array(sel))
            self.selectedfiles = np.unique(np.concatenate(selectedfiles))
        elif self.session == 'last':
            for f in datafiles:
                idcode = f.rsplit('/')[-3]
                sesdata = [sess for sess in os.listdir(os.path.split(os.path.split(os.path.abspath(f))[0])[0]) if not any([excl in sess for excl in self.exclude])]
                sessnr = []
                for sess in sesdata:#right now only taking in first sessions
                    sessnr = np.append(sessnr, np.int(sess.rsplit('.')[0][-1]))
                datapick = np.max(sessnr)
                sel = [files for files in datafiles if idcode+'-'+str(np.int(datapick)) in files]
                selectedfiles.append(np.array(sel))
            self.selectedfiles = np.unique(np.concatenate(selectedfiles))
        else:
            self.selectedfiles = datafiles

    def __groupsplit_filenames__(self, filepaths = None, test_size = None):
        """returns a dev dataset <data>.devfiles and a test dataset <data>.testfiles
        based on the test_size, using sklearn.model_selection.GroupShuffleSplit
        using idcodes (from the filenames) as the 'groups' variable)"""
        from sklearn.model_selection import GroupShuffleSplit
        idcodes = []
        try:
            if len(filepaths)>0:
                filepaths = filepaths
        except:
            filepaths = self.selectedfiles

        if not test_size: test_size = self.test_size
        for sl in filepaths:
            idcodes.append(sl.rsplit('/')[-3])

        gss = GroupShuffleSplit(n_splits=2,test_size=test_size, random_state = 17)

        for dev, test in gss.split(filepaths, groups=idcodes):
            self.devfiles = filepaths[dev];
            self.testfiles = filepaths[test]

    def ___find___(self):
        """subfunction walking through all levels of subfolders and finds files consistent
        with the pattern given """
        results = []
        for root, dirs, files in os.walk(self.root_dir):
            for name in files:
                if self.pattern in name:
                    results.append(os.path.join(root, name))
        result = [r for r in results if not any([excl in r for excl in self.exclude])]
        return result

