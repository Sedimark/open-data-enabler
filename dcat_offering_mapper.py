import rdflib, json, jmespath

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
    
    rdf_dict = {}
    
    for s, p, o in g:
        subject = str(s)
        predicate = str(p)
        object_ = str(o)
        
        if subject not in rdf_dict:
            rdf_dict[subject] = {}
        
        if predicate not in rdf_dict[subject]:
            rdf_dict[subject][predicate] = []
        
        rdf_dict[subject][predicate].append(object_)
    
    return rdf_dict

def extract_params(rdf_dict):
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
    
    for subject, predicates in rdf_dict.items():
        
        if('/' not in subject): continue
        
        if subject.split('/')[-2] == 'dataset': # dataset level
            
            if 'http://purl.org/dc/terms/issued' in predicates:
                params_dict['offering']['dct_issued'] = predicates['http://purl.org/dc/terms/issued'][0]
            if 'http://purl.org/dc/terms/language' in predicates:
                params_dict['offering']['dct_language'] = predicates['http://purl.org/dc/terms/language'][0]
            if 'http://purl.org/dc/terms/title' in predicates:
                params_dict['offering']['dct_title'] = predicates['http://purl.org/dc/terms/title'][0]
            if 'http://purl.org/dc/terms/description' in predicates:
                params_dict['offering']['dct_description'] = predicates['http://purl.org/dc/terms/description'][0]
            if 'http://purl.org/dc/terms/publisher' in predicates:
                params_dict['offering']['dct_publisher'] = predicates['http://purl.org/dc/terms/publisher'][0]
            if 'http://purl.org/dc/terms/creator' in predicates:
                params_dict['offering']['dct_creator'] = predicates['http://purl.org/dc/terms/creator'][0]

            if 'http://www.w3.org/ns/dcat#theme' in predicates:
                params_dict['asset']['dct_theme'] = predicates['http://www.w3.org/ns/dcat#theme'][0]
            if 'http://www.w3.org/ns/dcat#keyword' in predicates:
                params_dict['asset']['dcat_keyword'] = predicates['http://www.w3.org/ns/dcat#keyword']
            if 'http://www.w3.org/ns/locn#geometry' in predicates:
                params_dict['asset']['dct_spatial'] = predicates['http://www.w3.org/ns/locn#geometry'][0]
            if 'http://purl.org/dc/terms/description' in predicates:
                params_dict['asset']['dct_description'] = predicates['http://purl.org/dc/terms/description'][0]
            if 'http://purl.org/dc/terms/issued' in predicates:
                params_dict['asset']['dct_issued'] = predicates['http://purl.org/dc/terms/issued'][0]
            if 'http://purl.org/dc/terms/creator' in predicates:
                params_dict['asset']['dct_creator'] = predicates['http://purl.org/dc/terms/creator'][0]
                
            if distribution_found:
                break

        elif subject.split('/')[-2] == 'resource': # distribution level
            
            if distribution_found:
                continue
            
            distribution_found = True
            
            if 'http://purl.org/dc/terms/license' in predicates:
                params_dict['offering']['dct_license'] = predicates['http://purl.org/dc/terms/license'][0]
            if 'http://purl.org/dc/terms/title' in predicates:
                params_dict['asset_provision']['dct_title'] = predicates['http://purl.org/dc/terms/title'][0]
            if 'http://purl.org/dc/terms/format' in predicates:
                params_dict['asset_provision']['dct_format'] = predicates['http://purl.org/dc/terms/format'][0]
            if 'http://purl.org/dc/terms/description' in predicates:
                params_dict['asset_provision']['dct_description'] = predicates['http://purl.org/dc/terms/description'][0]
            if 'http://purl.org/dc/terms/issued' in predicates:
                params_dict['asset_provision']['dct_issued'] = predicates['http://purl.org/dc/terms/issued'][0]
            if 'http://www.w3.org/ns/dcat#accessURL' in predicates:
                params_dict['asset_provision']['dcat_accessURL'] = predicates['http://www.w3.org/ns/dcat#accessURL'][0]
                
            params_dict['odrl'] = {
                'permission': [],
                'prohibition': [],
                'obligation': []
            }
    
    return params_dict

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
