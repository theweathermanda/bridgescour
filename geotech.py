from __future__ import division

def connectToDB(cmd):
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
    cur.execute(cmd)
    return cnn, cur
    
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


def specificGravity(loc_id, tube_num, sn):
    calib_type = 302
    cmd = "SELECT * FROM calib WHERE calib_type = %d" % (calib_type,)
    cnn, cur = connectToDB(cmd)
    pcf = cur.fetchone()[1:]

    cmd = """SELECT mpync, mtot, mp, mps, temperature 
             FROM sgd 
             WHERE loc_id = %d
               AND tube_num = %d
               AND sn = %s""" % (loc_id, tube_num, sn)
    cur.execute(cmd)
    Mpync, Mtot, Mp, Mps, temp = cur.fetchone()

    M1 = Mtot
    M2 = pcf[0] + pcf[1]*temp + pcf[2]*temp**2
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

