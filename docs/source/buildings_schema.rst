
.. _buildings_schema:
{% filter upper %}
**Schema: {{ schema_gen_buildings["name"] }}**
=======================================
{% endfilter %}
**Description: {{ schema_gen_buildings["comment"] }}**


{% filter upper %}{{ schema_gen_buildings["name"] }}{% endfilter %} Schema Details
-----------------------------------------


{% for item in schema_tab_buildings  %}
.. _table-name-{{item.table_nam}}:

Table Name: {% filter upper %} {{ item.table_nam }} {% endfilter %}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	
Description: {{ item.table_comment }}

		{% for table in item.table_columns %}{%  for column in table %}{{ column }}{% endfor %}
		{% endfor %}
	      
		

{% endfor %}
