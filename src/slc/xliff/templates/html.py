HTML_HEAD = """<html>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<xliff version='1.2'
       xmlns='urn:oasis:names:tc:xliff:document:1.2'
       xmlns:tal="http://xml.zope.org/namespaces/tal"
       xmlns:metal="http://xml.zope.org/namespaces/metal">
{content}
</xliff>
</html>
"""

HTML_FILE_BODY = """<file original="{original}" oid="{oid}" source-language="{source_language}" target-language="{source_language}">
<body>
<group>
{attrs}
</group>
</body>
</file>
"""

HTML_ATTR_BODY = """    <trans-unit id="{id}">
        <source xml:lang='{source_language}'>
        <!-- {value} -->
        </source>
        <target xml:lang='{source_language}'>
        {value}
        </target>
    </trans-unit>
"""
