
.. _buildings_bulk_load_schema:
{% filter upper %}
**Schema: {{ schema_gen_buildings_bulk_load["name"] }}**
=======================================
{% endfilter %}
**Description: {{ schema_gen_buildings_bulk_load["comment"] }}**

Additional Notes about this Schema
------------------------------------
* This schema is designed for specific purposes

{% filter upper %}{{ schema_gen_buildings_bulk_load["name"] }}{% endfilter %} Schema Details
-----------------------------------------


{% for item in schema_tab_buildings_bulk_load  %}

	**Table Name:** {% filter upper %} **{{ item.table_nam }}** {% endfilter %}
	
	**Description: {{ item.table_comment }}**

		{% for table in item.table_columns %}{%  for column in table %}{{ column }}{% endfor %}
		{% endfor %}
	      
		

{% endfor %}