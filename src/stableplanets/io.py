import pyvo as vo
from astropy.table import Table
import astropy.io.votable
from astropy.io.votable import parse

def InitializeCatalog(path_to_csv = None, OfflineMode = False):
    if OfflineMode:
        # In Offline Mode, we want users to be able to still load the tool. By default, provide
        # a copy of the exoplanet archive kept in the package. If the user wants, allow them to
        # specify a csv file via giving the direct path to said file.
        from astropy.io import ascii
        if path_to_csv != None:
            # Read in the user provided CSV
            table_data = [] # ascii.read(path_to_csv)
        else:
            # Read in the package provided CSV
            table_data = [] # load test catalog
    else:
        # In Online Mode (default), we will query the latest catalog from the Exoplanet Archive.
        service = vo.dal.TAPService("https://exoplanetarchive.ipac.caltech.edu/TAP")
        search_query = "SELECT pl_name,hostname,sy_snum,sy_pnum,pl_orbper, pl_orbpererr1,pl_orbpererr2,pl_orbperlim,pl_bmassj, \
                        pl_bmassjerr1,pl_bmassjerr2,pl_bmassjlim, pl_orbeccen,pl_orbeccenerr1,pl_orbeccenerr2, \
                        pl_orbeccenlim,st_spectype,st_rad,st_raderr1,st_raderr2, st_radlim,st_mass,st_masserr1, \
                        st_masserr2,st_masslim,st_age,st_ageerr1,st_ageerr2,st_agelim \
                        FROM pscomppars "
        results = service.search(search_query)
        table_data = vo.dal.TAPResults.to_table(results)
    # Now, try to group the table by hostname. If the CSV doesn't have that column, raise an exception and exit.
    try:
        global grouped_table
        grouped_table = table_data.group_by("hostname")
        print("ALERT: There are", len(grouped_table.groups.keys), "planetary systems found in the supplied data.")
    except:
        print("ERROR: Supplied Astropy Table does not have a column labeled hostname.")
        print("       Please edit your CSV and try again.")

    return grouped_table
