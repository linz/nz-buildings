<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" styleCategories="AllStyleCategories" simplifyAlgorithm="0" version="3.16.8-Hannover" simplifyDrawingHints="0" simplifyLocal="1" minScale="100000000" maxScale="0" simplifyMaxScale="1" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal mode="0" fixedDuration="0" endExpression="" startField="" accumulate="0" startExpression="" durationUnit="min" durationField="" enabled="0" endField="last_modified">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="singleSymbol" enableorderby="0" forceraster="0" symbollevels="0">
    <symbols>
      <symbol type="fill" alpha="1" name="0" clip_to_extent="1" force_rhr="0">
        <layer pass="0" class="SimpleFill" locked="0" enabled="1">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="243,166,178,0" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,127,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.66" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory spacing="5" lineSizeScale="3x:0,0,0,0,0,0" sizeType="MM" penAlpha="255" height="15" width="15" scaleBasedVisibility="0" showAxis="1" backgroundColor="#ffffff" penWidth="0" diagramOrientation="Up" penColor="#000000" minimumSize="0" sizeScale="3x:0,0,0,0,0,0" rotationOffset="270" enabled="0" spacingUnitScale="3x:0,0,0,0,0,0" barWidth="5" backgroundAlpha="255" maxScaleDenominator="1e+08" lineSizeType="MM" labelPlacementMethod="XHeight" spacingUnit="MM" opacity="1" direction="0" minScaleDenominator="0" scaleDependency="Area">
      <fontProperties description="Ubuntu,11,-1,5,50,0,0,0,0,0" style=""/>
      <axisSymbol>
        <symbol type="line" alpha="1" name="" clip_to_extent="1" force_rhr="0">
          <layer pass="0" class="SimpleLine" locked="0" enabled="1">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" dist="0" obstacle="0" placement="1" zIndex="0" showAll="1" priority="0">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option type="Map" name="QgsGeometryGapCheck">
        <Option value="0" type="double" name="allowedGapsBuffer"/>
        <Option value="false" type="bool" name="allowedGapsEnabled"/>
        <Option value="" type="QString" name="allowedGapsLayer"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="facility_id" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="source_facility_id" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="name" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="source_name" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="use" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="use_type" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="use_subtype" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="estimated_occupancy" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="last_modified" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="internal" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="internal_comments" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="facility_id"/>
    <alias index="1" name="" field="source_facility_id"/>
    <alias index="2" name="" field="name"/>
    <alias index="3" name="" field="source_name"/>
    <alias index="4" name="" field="use"/>
    <alias index="5" name="" field="use_type"/>
    <alias index="6" name="" field="use_subtype"/>
    <alias index="7" name="" field="estimated_occupancy"/>
    <alias index="8" name="" field="last_modified"/>
    <alias index="9" name="" field="internal"/>
    <alias index="10" name="" field="internal_comments"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" expression="" field="facility_id"/>
    <default applyOnUpdate="0" expression="" field="source_facility_id"/>
    <default applyOnUpdate="0" expression="" field="name"/>
    <default applyOnUpdate="0" expression="" field="source_name"/>
    <default applyOnUpdate="0" expression="" field="use"/>
    <default applyOnUpdate="0" expression="" field="use_type"/>
    <default applyOnUpdate="0" expression="" field="use_subtype"/>
    <default applyOnUpdate="0" expression="" field="estimated_occupancy"/>
    <default applyOnUpdate="0" expression="" field="last_modified"/>
    <default applyOnUpdate="0" expression="" field="internal"/>
    <default applyOnUpdate="0" expression="" field="internal_comments"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" constraints="3" unique_strength="1" notnull_strength="1" field="facility_id"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="source_facility_id"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="name"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="source_name"/>
    <constraint exp_strength="0" constraints="1" unique_strength="0" notnull_strength="1" field="use"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="use_type"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="use_subtype"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="estimated_occupancy"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="last_modified"/>
    <constraint exp_strength="0" constraints="1" unique_strength="0" notnull_strength="1" field="internal"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" notnull_strength="0" field="internal_comments"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="facility_id"/>
    <constraint exp="" desc="" field="source_facility_id"/>
    <constraint exp="" desc="" field="name"/>
    <constraint exp="" desc="" field="source_name"/>
    <constraint exp="" desc="" field="use"/>
    <constraint exp="" desc="" field="use_type"/>
    <constraint exp="" desc="" field="use_subtype"/>
    <constraint exp="" desc="" field="estimated_occupancy"/>
    <constraint exp="" desc="" field="last_modified"/>
    <constraint exp="" desc="" field="internal"/>
    <constraint exp="" desc="" field="internal_comments"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" name="facility_id" hidden="0" width="-1"/>
      <column type="field" name="source_facility_id" hidden="0" width="-1"/>
      <column type="field" name="name" hidden="0" width="-1"/>
      <column type="field" name="source_name" hidden="0" width="-1"/>
      <column type="field" name="use" hidden="0" width="-1"/>
      <column type="field" name="use_type" hidden="0" width="-1"/>
      <column type="field" name="use_subtype" hidden="0" width="-1"/>
      <column type="field" name="estimated_occupancy" hidden="0" width="-1"/>
      <column type="field" name="last_modified" hidden="0" width="-1"/>
      <column type="field" name="internal" hidden="0" width="-1"/>
      <column type="field" name="internal_comments" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="estimated_occupancy"/>
    <field editable="1" name="facility_id"/>
    <field editable="1" name="internal"/>
    <field editable="1" name="internal_comments"/>
    <field editable="1" name="last_modified"/>
    <field editable="1" name="name"/>
    <field editable="1" name="source_facility_id"/>
    <field editable="1" name="source_name"/>
    <field editable="1" name="use"/>
    <field editable="1" name="use_subtype"/>
    <field editable="1" name="use_type"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="estimated_occupancy"/>
    <field labelOnTop="0" name="facility_id"/>
    <field labelOnTop="0" name="internal"/>
    <field labelOnTop="0" name="internal_comments"/>
    <field labelOnTop="0" name="last_modified"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="source_facility_id"/>
    <field labelOnTop="0" name="source_name"/>
    <field labelOnTop="0" name="use"/>
    <field labelOnTop="0" name="use_subtype"/>
    <field labelOnTop="0" name="use_type"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
