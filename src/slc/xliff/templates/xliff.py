XLIFF_HEAD = """<xliff version='1.2'
       xmlns='urn:oasis:names:tc:xliff:document:1.2'
       xmlns:tal="http://xml.zope.org/namespaces/tal"
       xmlns:metal="http://xml.zope.org/namespaces/metal">
{content}
</xliff>
"""

XLIFF_FILE_BODY = """<file original="{original}" oid="{oid}" source-language="{source_language}" target-language="">
<body>
<group>
{attrs}
</group>
</body>
</file>
"""

XLIFF_ATTR_BODY = """    <trans-unit id="{id}">
        <source xml:lang='{source_language}'>
        {value}
        </source>
        <target>
        </target>
    </trans-unit>
"""
