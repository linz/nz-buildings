.. _published_data:


Published Data
================================

The data described below represents building outlines data openly available on the LINZ Data Service:
https://data.linz.govt.nz/layer/53413-nz-building-outlines-pilot/

Data Model
--------------------------------

To assist you in understanding these datasets, the structure and details of the data fields is described in tables below. The relationship between tables and directly related datasets is provided in a data model diagram. No attempt has been made to indicate cardinality, however, the arrows drawn between datasets point from the dataset containing the unique record, to the dataset that may contain one or more references to that record (i.e. primary key -> foreign key). 

To enable changes between updates to be recorded and then queried using using LINZ Data Service `changesets <https://www.linz.govt.nz/data/linz-data-service/guides-and-documentation/how-to-use-the-changeset-generator>`_, every table has a primary key. Primary keys in tables are shown by a field name with bold font.

This data model has been designed to manage building data with multiple representations, allowing for future enhancements in building data management. Not all of this data is currently available and data capture for these new fields will occur over time.



Schema: {{ schema_gen_buildings_lds["name"] }}
--------------------------------------------------------

Description: {{ schema_gen_buildings_lds["comment"] }}


{% for item in schema_tab_buildings_lds  %}
.. _table-name-{{item.table_nam}}:

Table: {{ item.table_nam }}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
Description: {{ item.table_comment }}

		{% for table in item.table_columns %}{%  for column in table %}{{ column }}{% endfor %}
		{% endfor %}
	      
		

{% endfor %}