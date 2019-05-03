from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import pagetemplatefile
from Products.statusmessages.interfaces import IStatusMessage
from slc.xliff import XliffMessageFactory as _
from slc.xliff.interfaces import IExportParams
from slc.xliff.interfaces import IImportParams
from slc.xliff.interfaces import IXLIFFExporter
from slc.xliff.interfaces import IXLIFFImporter
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from Products.Five.browser import BrowserView


class ExportXliffForm(form.Form):
    """ Form for exporting xliff
    """
    fields = field.Fields(IExportParams)
    ignoreContext = True
    label = u'Export Xliff'
    form_name = _(u"Export Xliff")

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

    @button.buttonAndHandler(u'Export')
    def action_export(self, action):
        context = aq_inner(self.context)
        data, errors = self.extractData()
        recursive = int(bool(data.get('recursive')))
        single_file = int(bool(data.get('single_file')))
        zip = int(bool(data.get('zip')))
        html_compatibility = int(bool(data.get('html_compatibility')))

        return self.request.response.redirect(
            self.context.absolute_url() + '/@@export_xliff_contents?recursive={}&single_file={}&zip={}&html_compatibility={}'.format(
                recursive, single_file, zip, html_compatibility)
        )


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


class XliffExportView(BrowserView):
    def __call__(self):
        data = self.request.form
        recursive = bool(int(data.get('recursive')))
        single_file = bool(int(data.get('single_file')))
        zip = bool(int(data.get('zip')))
        html_compatibility = bool(int(data.get('html_compatibility')))

        context = aq_inner(self.context)
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

        data = xliffexporter.export()

        if zip is True:
            self.request.response.setHeader('Content-type', 'application/zip')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename=xliff_export_{0}.zip'.format(DateTime().strftime('%Y-%m-%d')))
        elif html_compatibility and single_file:
            self.request.response.setHeader('Content-type', 'text/html')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename={0}_xliff.html'.format(context.getId()))
        elif single_file:
            self.request.response.setHeader('Content-type', 'text/xml')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename={0}.xliff'.format(context.getId()))
        else:
            pass    # Should not happen
        self.request.response.write(data)
        return self.request.response
