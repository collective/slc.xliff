from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import pagetemplatefile
from Products.statusmessages.interfaces import IStatusMessage
from slc.xliff import HAVE_SHOPPINGLIST
from slc.xliff import XliffMessageFactory as _
from slc.xliff.interfaces import IExportParams
from slc.xliff.interfaces import IImportParams
from slc.xliff.interfaces import IXLIFFExporter
from slc.xliff.interfaces import IXLIFFImporter
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility


class ExportXliffForm(form.Form):
    """ Form for exporting xliff
    """
    fields = field.Fields(IExportParams)
    ignoreContext = True
    label = u'Export Xliff'
    form_name = _(u"Export Xliff")
    template = pagetemplatefile.ZopeTwoPageTemplateFile('templates/export_xliff.pt')

    def __call__(self):
        self.request.set('disable_border', 'on')
        return super(ExportXliffForm, self).__call__()

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        data = {}
        # make the recursive checked if context is folderish
        if self.context.isPrincipiaFolderish:
            data = {'recursive': True}
        self.widgets = setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, data=data, adapters=self.adapters, ignore_request=ignore_request)

    def have_shoppinglist(self):
        return HAVE_SHOPPINGLIST

    def shoppinglist(self):
        """ returns the titles of the items currently in the shoppinglist """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        pc = getToolByName(context, 'portal_catalog')
        member = mtool.getAuthenticatedMember()
        sl = member.getProperty('shoppinglist', tuple())
        brains = pc(UID=sl)

        mylist = list()
        for b in brains:
            if b is not None:
                mylist.append(dict(uid=b.UID, title=b.Title, url=b.getURL()))

        return mylist

    @button.buttonAndHandler(u'Export')
    def action_export(self, action):
        context = aq_inner(self.context)
        data, errors = self.extractData()

        recursive = bool(data.get('recursive'))
        single_file = bool(data.get('single_file'))
        zip = bool(data.get('zip'))
        html_compatibility = bool(data.get('html_copmpatibility'))
        # XXX
        export_shoppinglist = bool(data.get('export_shoppinglist'))

        if self.context.isPrincipiaFolderish:
            container = context
        else:
            container = context.aq_parent

        if recursive is True:
            xliffexporter = IXLIFFExporter(container)
        else:
            xliffexporter = IXLIFFExporter(context)

        xliffexporter.recursive = recursive
        xliffexporter.single_file = single_file
        xliffexporter.html_compatibility = html_compatibility
        xliffexporter.zip = zip
        xliffexporter.source_language = "en"
        xliffexporter.export_shoppinglist = export_shoppinglist

        if export_shoppinglist is True:
            xliffexporter.shoppinglist = [x['uid'] for x in self.shoppinglist()]

        data = xliffexporter.export()

        if zip is True:
            self.request.response.setHeader('Content-type', 'application/zip')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename=xliff_export_%s.zip' % DateTime().strftime('%Y-%m-%d'))
        elif html_compatibility and single_file:
            self.request.response.setHeader('Content-type', 'text/html')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename=%s_xliff.html' % context.getId())
        elif single_file:
            self.request.response.setHeader('Content-type', 'text/xml')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename=%s.xliff' % context.getId())
        else:
            pass    # Should not happen
        self.request.response.write(data)
        return self.request.response


class ImportXliffForm(form.Form):
    """ Form for importing xliff
    """
    fields = field.Fields(IImportParams)
    ignoreContext = True

    label = _(u"Import Xliff")

    @button.buttonAndHandler(_(u'Import'))
    def handleApply(self, action):
        data, errors = self.extractData()
        context = aq_inner(self.context)
        xliff_file = data['xliff_file']
        xliffimporter = getUtility(IXLIFFImporter)
        errors = xliffimporter.upload(
            xliff_file, html_compatibility=False, request=context.REQUEST)
        if errors != []:
            error = ["%s: %s" % x for x in errors]
            confirm = _(u"Error while importing Xliff.\n " + "\n".join(error))
            IStatusMessage(self.request).addStatusMessage(confirm, type='warn')
        else:
            confirm = _(u"Xliff import successful.")
            IStatusMessage(self.request).addStatusMessage(confirm, type='info')

        self.request.response.redirect(context.absolute_url() + '/@@xliffimport')

        return ''
