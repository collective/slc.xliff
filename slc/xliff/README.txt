How it works
============

please see the doc/ directory

TODO
----

Currently untested are:

- html compatibility export and import
   
    
HTML Compatibility
------------------

Unfortunately some translators still only can translate using html editors. For this case we supply an htmlized form of the xliff file which adds an html header. It also hides the source tags and adds the source language into the target tag so that it can be translated by replacing it. There is a flag to use compatibility mode.

There is a log output which explicitly states which languages have been uploaded and where parsing problems have occured. Note that in html compatibility mode you are responsible yourself to check if the results are good.

