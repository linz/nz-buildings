
.. _schema4tables:
{% filter upper %}
**Schema: {{ schema_gen4["name"] }}**
=======================================
{% endfilter %}
**Description: {{ schema_gen4["comment"] }}**

Additional Notes about this Schema #1
------------------------------------
* This schema is designed for specific purposes

{% filter upper %}{{ schema_gen4["name"] }}{% endfilter %} Schema Details
-----------------------------------------


{% for item in schema_tab4  %}

	**Table Name:** {% filter upper %} **{{ item.table_nam }}** {% endfilter %}
	
	**Description: {{ item.table_comment }}**

		{% for table in item.table_columns %}{%  for column in table %}{{ column }}{% endfor %}
		{% endfor %}
	      
		

{% endfor %}