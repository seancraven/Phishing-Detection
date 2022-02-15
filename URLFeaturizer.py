import datetime 
import math
from pyquery import PyQuery
import numpy as np
from requests import get
import whois
class UrlFeaturizer(object):
    def __init__(self, url):
        self.url = url
        self.domain = url.split('//')[-1].split('/')[0]
        self.today = datetime.datetime.now()

        try:
            self.whois = whois.whois(self.domain)
        except:
            self.whois = None

        try:
            self.response = get(self.url)
            self.pq = PyQuery(self.response.text)
        except:
            self.response = None
            self.pq = None

    ## URL string Features
    def entropy(self):
        string = self.url.strip()
        prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
        entropy = sum([(p * math.log(p) / math.log(2.0)) for p in prob])
        return entropy

    def numDigits(self):
        digits = [i for i in self.url if i.isdigit()]
        return len(digits)

    def urlLength(self):
        return len(self.url)

    def numParameters(self):
        params = self.url.split('&')
        return len(params) - 1

    def numFragments(self):
        fragments = self.url.split('#')
        return len(fragments) - 1

    def numSubDomains(self):
        subdomains = self.url.split('http')[-1].split('//')[-1].split('/')
        return len(subdomains)-1

    def domainExtension(self):
        ext = self.url.split('.')[-1].split('/')[0]
        return ext

    ## URL domain features
    def hasHttp(self):
        return 'http:' in self.url

    def hasHttps(self):
        return 'https:' in self.url

    def urlIsLive(self):
        return self.response == 200

    def daysSinceRegistration(self):
        if self.whois and self.whois.get('creation_date'):
            cd = self.whois['creation_date']
            if type(cd) == list:
                cd = cd[0]
            if type(cd) == datetime.datetime:
                diff = self.today - cd
                return diff.days
        else:
            return 0

    def daysSinceExpiration(self):
        if self.whois and self.whois.get('expiration_date'):
            ed = self.whois['expiration_date']
            if type(ed) == list:
                ed = ed[0]
            if type(ed) == datetime.datetime:
                diff = ed - self.today
                return diff.days
        else:
            return 0
    def daysSinceUpdate(self):
        if self.whois and self.whois.get('updated_date'):
            ud = self.whois['updated_date']
            if type(ud) == list:
                ud = ud[0]
            if type(ud) == datetime.datetime:
                diff = self.today - ud
                return diff.days
        else:
            return 0

    ## URL Page Features
    def bodyLength(self):
        if self.pq is not None:
            return len(self.pq('html').text()) if self.urlIsLive else 0
        else:
            return 0

    def numTitles(self):
        if self.pq is not None:
            titles = ['h{}'.format(i) for i in range(7)]
            titles = [self.pq(i).items() for i in titles]
            return len([item for s in titles for item in s])
        else:
            return 0

    def numImages(self):
        if self.pq is not None:
            return len([i for i in self.pq('img').items()])
        else:
            return 0

    def numLinks(self):
        if self.pq is not None:
            return len([i for i in self.pq('a').items()])
        else:
            return 0

    def scriptLength(self):
        if self.pq is not None:
            return len(self.pq('script').text())
        else:
            return 0

    def specialCharacters(self):
        if self.pq is not None:
            bodyText = self.pq('html').text()
            schars = [i for i in bodyText if not i.isdigit() and not i.isalpha()]
            return len(schars)
        else:
            return 0

    def scriptToSpecialCharsRatio(self):
        if self.pq is not None:
            sscr = self.scriptLength()/(self.specialCharacters()+1)
        else:
            sscr = 0
        return sscr

    def scriptTobodyRatio(self):
        if self.pq is not None:
            sbr = self.scriptLength()/(self.bodyLength()+1)
        else:
            sbr = 0
        return sbr

    def bodyToSpecialCharRatio(self):
        if self.pq is not None:
            bscr = self.specialCharacters()/(self.bodyLength()+1)
        else:
            bscr = 0
        return bscr

    def run(self):
        data = {}
        data['entropy'] = self.entropy()
        data['numDigits'] = self.numDigits()
        data['urlLength'] = self.urlLength()
        data['numParams'] = self.numParameters()
        data['hasHttp'] = self.hasHttp()
        data['hasHttps'] = self.hasHttps()
        data['urlIsLive'] = self.urlIsLive()
        data['bodyLength'] = self.bodyLength()
        data['numTitles'] = self.numTitles()
        data['numImages'] = self.numImages()
        data['numLinks'] = self.numLinks()
        data['scriptLength'] = self.scriptLength()
        data['specialChars'] = self.specialCharacters()
        #data['ext'] = self.domainExtension()
        data['dsu'] = self.daysSinceUpdate()
        data['dsr'] = self.daysSinceRegistration()
        data['dse'] = self.daysSinceExpiration()
        data['sscr'] = self.scriptToSpecialCharsRatio()
        data['sbr'] = self.scriptTobodyRatio()
        data['bscr'] = self.bodyToSpecialCharRatio()
        return data
    def run_array(self):
        data = np.zeros(19)
        data[0] = self.entropy()
        data[1] = self.numDigits()
        data[2] = self.urlLength()
        data[3] = self.numParameters()
        data[4] = self.hasHttp()
        data[5] = self.hasHttps()
        data[6] = self.urlIsLive()
        data[7] = self.bodyLength()
        data[8] = self.numTitles()
        data[9] = self.numImages()
        data[10] = self.numLinks()
        data[11] = self.scriptLength()
        data[12] = self.specialCharacters()
        #data['ext'] = self.domainExtension()
        data[13] = self.daysSinceRegistration()
        data[14] = self.daysSinceExpiration()
        data[15] = self.daysSinceUpdate()
        data[16] = self.scriptToSpecialCharsRatio()
        data[17] = self.scriptTobodyRatio()
        data[18] = self.bodyToSpecialCharRatio()
        
        return data
    def run_array_no_pyquery(self):
        data = np.zeros(9)
        data[0] = self.entropy()
        data[1] = self.numDigits()
        data[2] = self.urlLength()
        data[3] = self.numParameters()
        data[4] = self.hasHttp()
        data[5] = self.hasHttps()
        data[6] = self.daysSinceRegistration()
        data[7] = self.daysSinceExpiration()
        data[8] = self.daysSinceUpdate()
        return data
        