.. _published_data:


Published Data
================================

The data described below represents building outlines data openly available on the LINZ Data Service (LDS):
https://data.linz.govt.nz/layer/101290-nz-building-outlines/

Data Model
--------------------------------

To assist you in understanding these datasets, the structure and details of the data fields is described in tables below. The relationship between tables and directly related datasets is provided in a `data model diagram <https://nz-buildings.readthedocs.io/en/latest/_images/nz-buildings-pgtap-db.png>`_

To enable changes between updates to be recorded and then queried using using LDS `changesets <https://www.linz.govt.nz/data/linz-data-service/guides-and-documentation/how-to-use-the-changeset-generator>`_, every table has a primary key. Primary keys in tables are shown by a field name with bold font.



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