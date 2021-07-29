import pyvo as vo
from astropy.table import Table
import astropy.io.votable
from astropy.io.votable import parse


class ExoplanetCatalog:
    def __init__(self, OfflineMode = False, path_to_csv = None):
        self.OfflineMode = OfflineMode
        self.path_to_csv = path_to_csv
        self.Catalog = self.InitializeCatalog()
        self.wasCleaned = False

    def InitializeCatalog(self):
        """
        A function which initalizes an astropy.Table instance of either:
             - Queried Pull from the Composite Table provided by the
               NASA Exoplanet Archive (suplementing any missing values
               with a pull from the exoplanet.eu catalog).
             - [OfflineMode=True] allows for the user to use a static
               catalog provided by StablePlanets release -OR- provide
               their own CSV compliant catalog given setting [path_to_csv].
        """
        if self.OfflineMode:
            # In Offline Mode, we want users to be able to still load the tool. By default, provide
            # a copy of the exoplanet archive kept in the package. If the user wants, allow them to
            # specify a csv file via giving the direct path to said file.
            from astropy.io import ascii
            if self.path_to_csv != None:
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

    #---------------------------------------------------------------------------

    def clean(self, **kwargs):
        """
        This function 'cleans' an Astropy_Catalog created via InitializeCatalog()
        by searching for and then removing any rows where there are missing values
        in any of the key columns.
        """
        columns_to_check = kwargs.get("columns_to_check", self.Catalog.columns)
        # See here for why this works:
        # https://stackoverflow.com/questions/50256012/drop-rows-with-masked-elements-in-astropy-table
        print("Removing rows with missing values ...")
        import operator
        from functools import reduce
        self.Catalog = self.Catalog[reduce(operator.and_, [~self.Catalog[col].mask for col in columns_to_check])]
        self.Catalog = self.Catalog.group_by("hostname")
        print("Removal complete!")
        self.wasCleaned = True
        print("ALERT: There are", len(self.Catalog.groups.keys), "planetary systems found in the supplied data.")

    #---------------------------------------------------------------------------

    def get_ParameterRanges(self):
        if not self.wasCleaned:
            self.clean()
        from collections import defaultdict
        self.Parameter_Dict = defaultdict(lambda: defaultdict(dict))
        for system_name, system in zip(self.Catalog.groups.keys.as_array(), self.Catalog.groups):
            system_name = system_name[0] # Odd Formatting Due to How Group Keys Work
            system_params = self.Parameter_Dict[system_name]
            for planet in system:
                missing_value = False
                planet_params = system_params[planet['pl_name']]
                for base_param_name in ['pl_orbper', 'pl_bmassj', 'pl_orbeccen']: #, 'pl_orbincl']:
                    max_param = planet[base_param_name]+planet[base_param_name+'err1']
                    min_param = planet[base_param_name]+planet[base_param_name+'err2']
                    planet_params.update({base_param_name : [min_param, max_param]})
            example_planet = system[0]
            star_params = system_params[system_name]
            star_params.update({'st_spectype' : example_planet['st_spectype']})
            for base_param_name in ['st_mass', 'st_rad', 'st_age']:
                max_param = planet[base_param_name]+planet[base_param_name+'err1']
                min_param = planet[base_param_name]+planet[base_param_name+'err2']
                star_params.update({base_param_name : [min_param, max_param]})
        return self.Parameter_Dict
