from Acquisition import aq_inner, aq_base
from zope.formlib import form
from five.formlib import formbase
from zope.interface import implements
from zope.component import adapts, getUtility
from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import pagetemplatefile
from Products.LinguaPlone.interfaces import ITranslatable
from Products.statusmessages.interfaces import IStatusMessage


from slc.xliff.interfaces import IExportParams, IImportParams
from slc.xliff.interfaces import IXLIFFExporter, IXLIFFImporter
from slc.xliff import HAVE_SHOPPINGLIST, XliffMessageFactory as _
from zope.formlib.form import setUpWidgets

class ExportXliffForm(formbase.PageForm):
    """ Form for exporting xliff
    """
    form_fields = form.FormFields(IExportParams)
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

    @form.action(u'Export')
    def action_export(self, action, data):
        context = aq_inner(self.context)

        recursive = not not self.request.get('form.recursive')
        single_file = not not self.request.get('form.single_file')
        zip = not not self.request.get('form.zip')
        html_compatibility = not not self.request.get('form.html_compatibility')
        export_shoppinglist = not not self.request.get('form.export_shoppinglist')

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

        return data


class ImportXliffForm(formbase.PageForm):
    """ Form for importing xliff
    """
    form_fields = form.FormFields(IImportParams)
    label = u'Import Xliff'
    form_name = _(u"Import Xliff")

    template = pagetemplatefile.ZopeTwoPageTemplateFile('templates/import_xliff.pt')

    def __call__(self):
        self.request.set('disable_border', True)
        return super(ImportXliffForm, self).__call__()

    @form.action(u'Import')
    def action_import(self, action, data):
        context = aq_inner(self.context)
        file = self.request.get('form.file')
        xliffimporter = getUtility(IXLIFFImporter)
        errors = xliffimporter.upload(file, html_compatibility=False)
        if errors != []:
            error = ["%s: %s" % x for x in errors]
            confirm = _(u"Error while importing Xliff.\n " + "\n".join(error))
            IStatusMessage(self.request).addStatusMessage(confirm, type='warn')
        else:
            confirm = _(u"Xliff import successful.")
            IStatusMessage(self.request).addStatusMessage(confirm, type='info')

        self.request.response.redirect(context.absolute_url() + '/@@xliffimport')

        return ''






