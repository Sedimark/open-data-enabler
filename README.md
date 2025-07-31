# Open Data Enabler

The Open Data Enabler is a toolbox component designed to simplify the process of accessing, transforming, and sharing datasets from Open Data portals.

## Features

- RDF-based dataset import from a URL
- Custom parameter extraction
- Transformation to SEDIMARK offering
- Friendly API

## Files

- open_data_enabler.py: Main script
- dcat_offering_mapper.py: Utilities
- offering.template.jmespath: Template used to generate the offering
- test_open_data_enabler.py: Quick test to check the functionality

## Usage

The `test_open_data_enabler.py` file provides an example of how to use the Open Data Enabler. The service listens for HTTP POST requests at a specified URL (default: `http://localhost:4020/newoffering`). Each POST request should include a JSON object in the body with the following parameters:

- **dcatRDF** (required): The URL of the DCAT RDF describing the dataset to be processed and transformed into a SEDIMARK offering.
- **accessURL** (optional): The identifier for a specific distribution within the dataset. If multiple distributions exist and a particular one is desired, specify its `accessURL`. This parameter is used because it is both mandatory and unique in DCAT Distributions. If not provided, the first available distribution is selected by default.