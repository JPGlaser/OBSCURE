from collections import defaultdict

def get_ParameterRanges(InitializeCatalog):
    Parameter_Dict = defaultdict(lambda: defaultdict(dict))
    for system_name, system in zip(Astropy_Catalog.groups.keys.as_array(), Astropy_Catalog.groups):
        system_name = system_name[0] # Odd Formatting Due to How Group Keys Work
        system_params = Parameter_Dict[system_name]
        for planet in system:
            missing_value = False
            planet_params = system_params[planet['pl_name']]
            for base_param_name in ['pl_orbper', 'pl_bmassj', 'pl_orbeccen']: #, 'pl_orbincl']:
                if '--' not in [str(planet[base_param_name]), \
                                str(planet[base_param_name+'err1']), \
                                str(planet[base_param_name+'err2'])]:
                    max_param = planet[base_param_name]+planet[base_param_name+'err1']
                    min_param = planet[base_param_name]+planet[base_param_name+'err2']
                    planet_params.update({base_param_name : [min_param, max_param]})
                else:
                    missing_value = True
                    print("One of the parameters related to", base_param_name, "for", planet['pl_name'], \
                          "has missing values. Removing the full system from Parameter Dictionary")
                    break
            if missing_value:
                Parameter_Dict.pop(system_name, None)
                break
    return Parameter_Dict
