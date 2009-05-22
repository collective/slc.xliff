from zope.i18nmessageid import MessageFactory

try:
    import slc.shoppinglist
    HAVE_SHOPPINGLIST = True
except:
    HAVE_SHOPPINGLIST = False

XliffMessageFactory = MessageFactory('slc.xliff')



def initialize(context):
    """Initializer called when used as a Zope 2 product."""
