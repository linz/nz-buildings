
.. _buildings_lds_schema:
{% filter upper %}
**Schema:** **{{ schema_gen_buildings_lds["name"] }}**
=======================================
{% endfilter %}
**Description:** **{{ schema_gen_buildings_lds["comment"] }}**

{% filter upper %}{{ schema_gen_buildings_lds["name"] }}{% endfilter %} Schema Details
-----------------------------------------


{% for item in schema_tab_buildings_lds  %}
.. _table-name-{{item.table_nam}}:

Table Name: {% filter upper %} {{ item.table_nam }} {% endfilter %}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
Description: {{ item.table_comment }}

		{% for table in item.table_columns %}{%  for column in table %}{{ column }}{% endfor %}
		{% endfor %}
	      
		

{% endfor %}