import rdflib, json, jmespath

def custom_get(value):
    """
    Custom function to handle different types of values.
    
    Args:
        value: The value to be processed.
        
    Returns:
        str: The string representation of the value.
    """
    if isinstance(value, dict):
        return value.get('@value', value.get('@id', ''))
    elif isinstance(value, list):
        return [custom_get(v) for v in value]
    else:
        return str(value)

def read_rdf_to_dict(rdf_file):
    """
    Reads an RDF file and converts it to a dictionary.
    
    Args:
        rdf_file (str): Path to the RDF file.
        
    Returns:
        dict: Dictionary representation of the RDF data.
    """
    g = rdflib.Graph()
    try:
        g.parse(rdf_file, format='xml')
    except Exception as e:
        raise ValueError(f"Error parsing RDF file: {e}")
    
    rdf_dict = g.serialize(format='json-ld', encoding='utf-8')
    rdf_dict = json.loads(rdf_dict)

    return rdf_dict

def extract_params(rdf_dict, access_url=None):
    """
    Extracts parameters from the RDF dictionary.
    
    Args:
        rdf_dict (dict): Dictionary representation of the RDF data.
        
    Returns:
        dict: Dictionary of parameters extracted from the RDF data.
    """
    params_dict = dict()
    params_dict['offering'] = dict()
    params_dict['asset'] = dict()
    params_dict['asset_provision'] = dict()
    distribution_found = False
    
    for entry in rdf_dict:
        
        entry_type = entry.get('@type', [])[0]
        
        if 'http://www.w3.org/ns/locn#geometry' in entry:
            params_dict['asset']['dct_spatial'] = custom_get(entry['http://www.w3.org/ns/locn#geometry'][0])
        
        if entry_type == 'http://www.w3.org/ns/dcat#Dataset':
            
            if 'http://purl.org/dc/terms/issued' in entry:
                params_dict['offering']['dct_issued'] = custom_get(entry['http://purl.org/dc/terms/issued'][0])
            if 'http://purl.org/dc/terms/language' in entry:
                params_dict['offering']['dct_language'] = custom_get(entry['http://purl.org/dc/terms/language'][0])
            if 'http://purl.org/dc/terms/title' in entry:
                params_dict['offering']['dct_title'] = custom_get(entry['http://purl.org/dc/terms/title'][0])
            if 'http://purl.org/dc/terms/description' in entry:
                params_dict['offering']['dct_description'] = custom_get(entry['http://purl.org/dc/terms/description'][0])
            if 'http://purl.org/dc/terms/publisher' in entry:
                params_dict['offering']['dct_publisher'] = custom_get(entry['http://purl.org/dc/terms/publisher'][0])
            if 'http://purl.org/dc/terms/creator' in entry:
                params_dict['offering']['dct_creator'] = custom_get(entry['http://purl.org/dc/terms/creator'][0])

            if 'http://www.w3.org/ns/dcat#theme' in entry:
                params_dict['asset']['dct_theme'] = custom_get(entry['http://www.w3.org/ns/dcat#theme'][0])
            if 'http://www.w3.org/ns/dcat#keyword' in entry:
                params_dict['asset']['dcat_keyword'] = [custom_get(kw) for kw in entry['http://www.w3.org/ns/dcat#keyword']]
            if 'http://purl.org/dc/terms/description' in entry:
                params_dict['asset']['dct_description'] = custom_get(entry['http://purl.org/dc/terms/description'][0])
            if 'http://purl.org/dc/terms/issued' in entry:
                params_dict['asset']['dct_issued'] = custom_get(entry['http://purl.org/dc/terms/issued'][0])
            if 'http://purl.org/dc/terms/creator' in entry:
                params_dict['asset']['dct_creator'] = custom_get(entry['http://purl.org/dc/terms/creator'][0])

            if distribution_found:
                break

        elif entry_type == 'http://www.w3.org/ns/dcat#Distribution':
            
            if distribution_found:
                continue
            
            if access_url is not None:
                if 'http://www.w3.org/ns/dcat#accessURL' in entry:
                    if entry['http://www.w3.org/ns/dcat#accessURL'][0]["@id"] == access_url:
                        pass
                    else:
                        continue
                else:
                    continue
            
            distribution_found = True
            
            if 'http://purl.org/dc/terms/license' in entry:
                params_dict['offering']['dct_license'] = custom_get(entry['http://purl.org/dc/terms/license'][0])
            if 'http://purl.org/dc/terms/title' in entry:
                params_dict['asset_provision']['dct_title'] = custom_get(entry['http://purl.org/dc/terms/title'][0])
            if 'http://purl.org/dc/terms/format' in entry:
                params_dict['asset_provision']['dct_format'] = custom_get(entry['http://purl.org/dc/terms/format'][0])
            if 'http://purl.org/dc/terms/description' in entry:
                params_dict['asset_provision']['dct_description'] = custom_get(entry['http://purl.org/dc/terms/description'][0])
            if 'http://purl.org/dc/terms/issued' in entry:
                params_dict['asset_provision']['dct_issued'] = custom_get(entry['http://purl.org/dc/terms/issued'][0])
            if 'http://www.w3.org/ns/dcat#accessURL' in entry:
                params_dict['asset_provision']['dcat_accessURL'] = custom_get(entry['http://www.w3.org/ns/dcat#accessURL'][0])

            params_dict['odrl'] = {
                'permission': [],
                'prohibition': [],
                'obligation': []
            }
    
    if not distribution_found:
        error = "No valid distribution found in the RDF data for the access URL given."
    else:
        error = None

    return params_dict, error

def create_offering(params_dict):
    """
    Creates an offering dictionary from the parameters dictionary.
    
    Args:
        params_dict (dict): Dictionary of parameters extracted from the RDF data.
        
    Returns:
        dict: Offering dictionary.
    """
    
    with open('offering.template.jmespath') as file: template = file.read()
    offering = jmespath.search(template, params_dict)
    
    #recursively check for any null value and delete the parent field containing it
    def remove_nulls(d):
        if isinstance(d, dict):
            return {k: remove_nulls(v) for k, v in d.items() if v is not None}
        elif isinstance(d, list):
            return [remove_nulls(i) for i in d if i is not None]
        else:
            return d
        
    offering = remove_nulls(offering)
    
    return offering
