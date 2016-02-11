import re, requests, json
from bs4 import BeautifulSoup, NavigableString
locs = {"18" :"Berlin",
           "40" :"Nord",
           "16" :"Ost",
           "17" :"Süd",
           "39" :"West"}
bas = {'design': 'Bestes Design', 'world': 'Mit Code die Welt verbessern', 'audience': 'Publikumspreis', 'code': 'Bester Code', 'innovation': 'Aha Moment', 'special': 'Sonderpreis'}
ps = []
#with open("index.html") as projektefile: #debugging
projektreq = requests.get("http://www.jugendhackt.de/projekte/", headers={"user-agent":""}) # jugendhackt blockt python requests
page = BeautifulSoup(projektreq.text)
for projekt in page.findAll("div",{"class":"teaser-item"})[1:]:
	b = str(projekt)
	p = {}
	r = re.findall("badge-([a-z0-9]*)",b)
	if len(r) > 0:
		p["badges_raw"] = r
		p["badges"] = [bas[ba] for ba in r]
	r = re.findall("term-([0-9]{2})",b)
	loc = None
	for m in r:
		if m in locs:
			loc = locs[m]
	p["location"] = loc
	r = re.findall("(http|https)://(www.)?hackdash.org/embed/projects/([a-f0-9]*)",b)
	h = True
	if len(r) == 0:
		h = False
		r = re.findall("(http|https)://www.youtube.com/embed/[A-Za-z0-9_-]*",b)
		url = r[0]
	else:
		url = "https://hackdash.org/projects/%s" % r[0][1]
	p["url"] = url
	p["people"] = []
	p["description"] = ""
	p["title"] = ""
	if h:
		req = requests.get("https://hackdash.org/api/v2/projects/%s"%r[0][1])
		for f in req.json()['contributors']:
			if f['provider'] == "github":
				p["people"].append("https://github.com/%(username)s"%f)
			elif f['provider'] == "twitter":
				p["people"].append("https://twitter.com/%(username)s"%f)
			else:
				print("Provider not implemented: %s"%f["provider"])
		p["description"] = req.json()["description"]
		p["title"] = req.json()["title"]
	ps.append(p)
with open("projekte.json","w") as ofile:
	json.dump(ps, ofile)
