'''
GEOTECH.PY
Performs all calculations related to the geotechnical aspects of samples tested in the tilting erosion flume at Georgia Tech's Hydraulic Laboratory in the 
School of Civil and Environmental Engineering and the stress-controlled 
rheometer in the Complex Fluids Laboratory.

Available functions include:
waterConent(loc_id, tube_num, sn)
specificGravity(loc_id, tube_num)
organicMatterContent(loc_id. tube_num)
grainSize(loc_id, tube_num)
atterbergLimits(loc_id, tube_num)

See individual docstrings for help.
-Paul M. Hobson
(pmhobson@gmail.com)

'''

from __future__ import division

def connectToDB(cmd=None):
    '''Connect to Erosiondatabase
    General function to connect to erosion database

    Inputs: NONE
    Outputs: cnn (pyscopg2 connection object)
    Usage:
        import geotech
        cnn = geotech.connectToDB()
    '''
    import psycopg2 as db
    f = open('puppies', 'r')
    puppies = f.readline()
    cnn = db.connect(host='localhost', user='paul', 
                     password=puppies, database='erosion')
    cur = cnn.cursor()
    if cmd:
        cur.execute(cmd)

    return cnn, cur
    
def getCalibFactors(calib_type):
    cmd = """SELECT * FROM calib
             WHERE calib_type = """ % (calib_type,)
    cnn, cur = connectToDB(cmd)
    CF = cur.fetchone()[1:]
    return CF
    cnn.close()
    

    
def waterContent(loc_id, tube_num, sn):
    '''Water Content
    Function to compute the water content of a sample
    Inputs:
        loc_id: Location ID in Erosion database ('locations' table)
        tube_num: tube number ('tubes' table)
        sn: sample number to computer WC ('wcs' table)
    Outputs: wc - decimal fraction water content of sample (float)
    Usage:
        import geotech
        wc = geotech(waterContent(11, 1, 1)
        print(wc)

    '''
    cmd = """SELECT mpsw, mps, mp 
             FROM wcs 
             WHERE loc_id = %d
               AND tube_num = %d
               AND sn = %s""" % (loc_id, tube_num, sn)
    cnn, cur = connetToDB(cmd)
    Mpsw, Mps, Mp = cur.fetchone()

    Mw = Mpsw - Mps
    Ms = Mps - Mp
    wc = Mw/Ms
    
    cnn.close()
    return wc


def specificGravity(loc_id, tube_num):
    pyncCF = getCalibFactors(302)
    cmd = """SELECT mpync, mtot, mp, mps, temperature 
             FROM sgd 
             WHERE loc_id = %d
               AND tube_num = %d""" % (loc_id, tube_num)
    cnn, cur = connectToDB(cmd)
    Mpync, Mtot, Mp, Mps, temp = cur.fetchone()

    M1 = Mtot
    M2 = pyncCF[0] + pyncCF[1]*temp + pyncCF[2]*temp**2
    Ms = Mps - Mp

    sg = Ms / (Ms - M1 + M2)
    cnn.close()
    return sg

def organicMatterConent(loc_id, tube_num):
    cmd = """SELECT mpsa, mps, mp 
             FROM omd 
             WHERE loc_id = %d 
               AND tube_num = %d""" % (loc_id, tube_num)
    cnn, cur = connectToDB(cmd)
    Mpsa, Mps, Mp = cur.fetchone()
    Ma = Mpsa - Mps
    Ms = Mps - Ms
    om = Ma/Ms

    cnn.close()
    return om

def grainSize(loc_id, tube_num, plot=False):
    import numpy as np
    import NumUtils as nu
    import matplotlib.pyplot as pl
    
    # set up tables for hydrometer analysis (ASTM D 422)
    Table1 = {'SG'    : np.arange(2.45, 3.00, 0.05),
              'alpha' : np.arange(1.04, 0.93, -0.01)}
    Table1['alpha'][0] = 1.05  # minor correction

    Table2 = {'AHyR' : np.arange(0,61),
              'EffD' : np.array([16.3, 16.1, 16.0, 15.8, 15.6, 15.5, 15.3, 15.2,
                        15.0, 14.8, 14.7, 14.5, 14.3, 14.2, 14.0, 13.8,
                        13.7, 13.5, 13.3, 13.2, 13.0, 12.9, 12.7, 12.5,
                        13.5, 13.3, 13.2, 13.0, 12.9, 12.7, 12.5, 12.4,
                        12.2, 12.0, 11.9, 11.7, 11.5, 11.4, 11.2, 11.1,
                        10.9, 10.7, 10.6, 10.4, 10.2, 10.1,  9.9,  9.7,
                         9.6,  9.4,  9.2,  9.1,  8.9,  8.6,  8.4,  8.3, 
                         8.1,  7.9,  7.8,  7.6,  7.4,  7.3,  7.1,  7.0,
                         6.8,  6.6, 6.5])}

    Table3 = {'SG' : np.arange(2.45,2.90,0.05),
              'T'  : np.arange(16.0,31.0,1.0),
              'K'  : np.array([[0.01530, 0.01505, 0.01481, 0.01457, 0.01435, 0.01414, 0.01394, 0.01374, 0.01356],
                               [0.01511, 0.01486, 0.01462, 0.01439, 0.01417, 0.01396, 0.01376, 0.01356, 0.01338],
                               [0.01492, 0.01467, 0.01443, 0.01421, 0.01399, 0.01378, 0.01359, 0.01339, 0.01321],
                               [0.01474, 0.01449, 0.01425, 0.01403, 0.01382, 0.01361, 0.01342, 0.01323, 0.01305],
                               [0.01456, 0.01431, 0.01408, 0.01386, 0.01365, 0.01344, 0.01325, 0.01307, 0.01289],
                               [0.01438, 0.01414, 0.01391, 0.01374, 0.01369, 0.01348, 0.01328, 0.01291, 0.01273],
                               [0.01421, 0.01397, 0.01374, 0.01353, 0.01332, 0.01312, 0.01294, 0.01276, 0.01258],
                               [0.01404, 0.01381, 0.01358, 0.01337, 0.01317, 0.01297, 0.01279, 0.01261, 0.01243],
                               [0.01388, 0.01365, 0.01342, 0.01321, 0.01301, 0.01282, 0.01264, 0.01246, 0.01229],
                               [0.01372, 0.01349, 0.01327, 0.01306, 0.01286, 0.01267, 0.01249, 0.01232, 0.01215],
                               [0.01357, 0.01334, 0.01312, 0.01291, 0.01272, 0.01253, 0.01235, 0.01218, 0.01201]])}
    
    # initialize output arrays
    Dsve = np.array([])
    Dhyd = np.array([])
    PFsve = np.array([])
    PFhyd = np.array([])
    
    Mret = np.array([])                         
    # get the sieve data
    cmd = """SELECT dsve, mtot-msve
             FROM sieve
             WHERE loc_id = %d AND tube_num = %d)""" % (loc_id, tube_num)
    cnn, cur = connectToDB(cmd)
    for row in cur:
        Dsve = np.hstack([Dsve, row[0]])
        Mret = np.hstack([Mret, row[1]])
   
    # read hydrometer data
    cmd = """SELECT * time, hydr, temperature 
             FROM hydrometer
             WHERE loc_id = %d AND tube_num = %d""" % (loc_id, tube_num)
    cur.execute(cmd)
    time = np.array([])
    hydr = np.array([])
    temp = np.array([])

    for row in cur:
        time = np.hstack([time, row[0]])
        hydr = np.hstack([hydr, row[1]])
        temp = np.hstack([temp, row[2]])
        
    # get info about that hydrometer test
    if len(time) == 0:
        cumFracRet = Mret.cumsum()/Mret.sum()
        PFsieve = (1 - cumFracRet[:-1]) * 100
    
    else:    
        cmd = """SELECT msw, wcs_sn 
                 FROM luhydrometer
                 WHERE loc_id = %d AND tube_num = %d""" % (loc_id, tube_num)
        cur.execute(cmd)
        msw, wcs_sn = cur.fetchone()
        
        cmd = """SELECT * FROM calib WHERE calib_type
                """

        # hygroscopic water content of hydrometer soil
        wcHygro = waterContent(loc_id, tube_id, wcs_sn)
        Ms = Msw / (1 + wcHygro)
        
        Mcoarse = Mret.sum()
        Mfine = Ms - Mcoarse
        n = len(Mret)
        cumFracRet = Mret.cumsum()/Ms
        PFsieve = (1 - cumFracRet[:-1]) * 100
        
        hydrCF = getCalibFactors(301)
        hydrCorrection = hydrCF[0] + hydrCF[1] * temp + hydrCF[2] * temp**2
        hydrFinal = hydr - hydrCorrection
        
        SG = specificGravity(loc_id, tube_num)
        
        alpha = nu.linInterp(Table1['SG'], Table1['alpha'], SG)
        PFhydro = hydroFinal * alpha / Ms * 100
        
        L = np.zeros(len(hydr))
        K = np.zeros(len(hydr))
        for n in range(len(hydr)):
            L[n] = np.linInterp(Table2['AHyR'], Table2['EffD'], R[n])
            K[n] = np.planeInterp(Table3['SG'], Table3['T'], Table3['K'], SG, temp[n])
            
        Dhyd = K * np.sqrt(L/time)
        
    D = np.hstack([Dsve, Dhyd])
    PF = np.hstack([PFsieve, PFhydro])
    
    cnn.close()
    return D, PF








