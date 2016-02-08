
# pygargl
Python3 implementation of Gargl template file parser

author: https://github.com/KarolTx

inspired by: https://github.com/jodoglevy/gargl


## Requirements
* python3
* python3-lxml
* python3-cssselect - if using cssSelector fields
* python3-requests


## Differences to original Gargl generator in Java:
* written in script language => no need to compile and therefor rapid prototyping
* supports multiple template variables in the original Gargl format
* supports templating variables in the [Python format mini-language](https://docs.python.org/3/library/string.html#formatspec) => extends the GTF
* support selecting fields also by using XPath expessions (see sample GTF)
* returns fields (selected by CSS or XPath) as lxml elements
* ignores httpVersion field and response headers from GTF
* does nothing with the description values and module name from GTF


## Example

```
ARG_GTF = 'sample/yahoosearch.gtf'
g = gargl(ARG_GTF)
print(g.Search({'query': 'pygargl'}))
print(g.Search({'query': 'python'}))
```

