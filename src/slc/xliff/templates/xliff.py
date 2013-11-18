XLIFF_HEAD = """<xliff version='1.2'
       xmlns='urn:oasis:names:tc:xliff:document:1.2'
       xmlns:tal="http://xml.zope.org/namespaces/tal"
       xmlns:metal="http://xml.zope.org/namespaces/metal">
%(content)s
</xliff> 
"""

XLIFF_FILE_BODY = """<file original="%(original)s" oid="%(oid)s" source-language="%(source_language)s" target-language="">
<body>
<group>
%(attrs)s
</group>
</body>
</file>
"""

XLIFF_ATTR_BODY = """    <trans-unit id="%(id)s">
        <source xml:lang='%(source_language)s'>
        %(value)s
        </source>
        <target>
        </target>
    </trans-unit>
"""
