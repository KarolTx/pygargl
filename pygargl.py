'''
# pygargl
Python3 implementation of Gargl template file parser

author: https://github.com/KarolTx

inspired by: https://github.com/jodoglevy/gargl


## Requirements
* python3
* python3-lxml
* python3-cssselect - if using cssSelector fields

## Differences to original Gargl generator in Java:
* written in script language => no need to compile and therefor rapid prototyping
* supports multiple template variables in the original Gargl format
* supports templating variables in the Python format mini-language => extends the GTF
* returns fields (selected by CSS) as lxml elements
* ignores httpVersion field and response headers from GTF
* does nothing with the description values and module name from GTF

## Example
download https://github.com/jodoglevy/gargl/raw/master/templates/yahoosearch.gtf

```
ARG_GTF = '/path/to/yahoosearch.gtf'
g = gargl(ARG_GTF)

print(g.Autocomplete({'term': 'current ti'}))
print(g.Autocomplete({'term': 'pygargl'}))

print(g.Search({'query': 'pygargl'}))
print(g.Search({'query': 'python'}))
```
'''


import re
import json
import urllib.parse
import urllib.request

from lxml import html

__all__ = ['gargl']


at_pattern = re.compile(r'[^@]*(@\w+@)[^@]*', re.IGNORECASE)

def replace_variables(template_dict, values):
    if not template_dict:
        return {}

    k_v = {}
    k_v_format = {}
    k_v_value = {}

    # name & value -> name: value
    for item in template_dict:
        k_v[item['name']] = item['value']

    # @@ -> {}
    for key in k_v:
        matches = at_pattern.findall(k_v[key])
        tpl_vars = {v: '{{{}}}'.format(v.strip('@')) for v in matches}

        tmp = k_v[key]
        for v_orig, v_new in tpl_vars.items():
            tmp = tmp.replace(v_orig, v_new)

        k_v_format[key] = tmp

    # {} -> <value>
    for key, value in k_v_format.items():
        k_v_value[key] = value.format(**values)

    return k_v_value



class gargl(object):
    def __init__(self, gtf, encoding='utf-8'):
        self.gtf = gtf
        self.conf = None
        self.encoding = 'utf-8'

        with open(self.gtf, 'r') as conf_file:
            self.conf = json.load(conf_file)


    def __getattr__(self, name):
        try:
            f_desc = [f for f in self.conf['functions'] if f['functionName'] == name][0]
        except IndexError:
            raise AttributeError('function {} is not defined in GTF'.format(name))

        # prepare method
        def function(var_dict):
            # prepare URL
            url = f_desc['request']['url']
            if f_desc['request'].get('queryString'):
                url = '?'.join([url, urllib.parse.urlencode(replace_variables(
                    f_desc['request']['queryString'], var_dict))])

            data = urllib.parse.urlencode(
                replace_variables(f_desc['request'].get('postData'), var_dict)
                ).encode(self.encoding)
            headers = replace_variables(
                f_desc['request']['headers'], var_dict)

            request = urllib.request.Request(url, data=data, headers=headers,
                method=f_desc['request']['method'])
            response = urllib.request.urlopen(request)

            if not f_desc['response'].get('fields'):
                return response.read().decode(self.encoding)

            res = []
            tree = html.parse(response)

            # compatibility with GTFv1.0
            body = tree.xpath('/html/body')[0]

            for item in f_desc['response']['fields']:
                res.append({item['name']: body.cssselect(item['cssSelector'])})
            return res

        # "cache it"
        if name not in dir(self):
            self.__setattr__(name, function)

        return function



if __name__ == '__main__':
    # download https://github.com/jodoglevy/gargl/raw/master/templates/yahoosearch.gtf
    ARG_GTF = 'yahoosearch.gtf'
    g = gargl(ARG_GTF)
    print(g.Autocomplete({'term': 'current ti'}))
    print(g.Autocomplete({'term': 'pygargl'}))
    print(g.Search({'query': 'pygargl'}))
    print(g.Search({'query': 'python'}))

