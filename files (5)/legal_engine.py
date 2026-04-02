"""
Dharma Lens – Legal NLP Engine v3
Enhanced TF-IDF classifier with legal content validation
"""
import re, math
from collections import Counter

LEGAL_CATEGORIES = {
    "Criminal Law": {
        "keywords": [
            "murder","theft","robbery","assault","rape","kidnapping","fraud","bribery",
            "corruption","arson","extortion","blackmail","forgery","counterfeiting",
            "abetment","conspiracy","accused","prosecution","bail","fir","cognizable",
            "non-cognizable","chargesheet","conviction","acquittal","sentence","ipc",
            "mens rea","actus reus","culpable","homicide","grievous","hurt","offence",
            "crime","criminal","police","arrest","custody","imprisonment","death penalty",
            "life imprisonment","probation","parole","juvenile","witness","testimony",
            "evidence","investigation","challan","remand","discharge","culprit","suspect",
            "magistrate","sessions court","high court","supreme court","accused person",
            "complainant","victim","offender","penal","punishment","fine","sanction"
        ],
        "acts": [
            {"act":"Indian Penal Code (IPC), 1860","sections":"Sections 302 (Murder), 376 (Rape), 378 (Theft), 420 (Cheating), 120B (Criminal Conspiracy)"},
            {"act":"Code of Criminal Procedure (CrPC), 1973","sections":"Section 154 (FIR), Section 161 (Examination of witnesses), Section 437 (Bail)"},
            {"act":"Indian Evidence Act, 1872","sections":"Section 3 (Evidence), Section 45 (Expert Opinion), Section 65B (Electronic Evidence)"},
            {"act":"Bharatiya Nyaya Sanhita (BNS), 2023","sections":"Replaced IPC – covers all criminal offences with updated provisions"},
        ],
        "constitutional_articles": [
            {"article":"20","title":"Protection against ex post facto laws","relevance":"No person shall be convicted for an act not an offence when done"},
            {"article":"21","title":"Right to Life and Personal Liberty","relevance":"Right to fair trial, legal aid and due process"},
            {"article":"22","title":"Protection against arbitrary arrest","relevance":"Rights of arrested person including legal representation"},
        ],
        "color":"#E05C7A"
    },
    "Civil Law": {
        "keywords": [
            "plaintiff","defendant","suit","decree","injunction","damages","tortious",
            "negligence","nuisance","trespass","property","contract","breach","agreement",
            "specific performance","partition","possession","eviction","tenancy","lease",
            "mortgage","easement","succession","will","probate","intestate","heir",
            "inheritance","title","deed","registration","stamp duty","civil","jurisdiction",
            "limitation","appeal","revision","cpc","order","judgment","execution",
            "attachment","auction","receiver","interim","stay","caveat","plaint",
            "written statement","compensation","liability","tort","remedy","relief",
            "declaratory","mandatory","prohibitory","mesne profits","restitution"
        ],
        "acts": [
            {"act":"Code of Civil Procedure (CPC), 1908","sections":"Order VII (Plaint), Order VIII (Written Statement), Section 9 (Jurisdiction)"},
            {"act":"Indian Contract Act, 1872","sections":"Section 2 (Definitions), Section 10 (Valid Contract), Section 73 (Damages)"},
            {"act":"Transfer of Property Act, 1882","sections":"Section 5 (Transfer), Section 54 (Sale), Section 105 (Lease)"},
            {"act":"Limitation Act, 1963","sections":"Article 113 (General limitation period of 3 years for civil suits)"},
        ],
        "constitutional_articles": [
            {"article":"300A","title":"Right to Property","relevance":"No person shall be deprived of property save by authority of law"},
            {"article":"14","title":"Right to Equality","relevance":"Equal protection of laws in civil proceedings"},
            {"article":"21","title":"Right to Life","relevance":"Right to livelihood and protection from arbitrary civil action"},
        ],
        "color":"#3DB8D8"
    },
    "Cyber Law": {
        "keywords": [
            "hacking","cyber","internet","online","digital","data","breach","unauthorized",
            "access","phishing","malware","ransomware","virus","trojan","ddos","identity",
            "theft","social media","email","password","encrypt","decrypt","privacy",
            "surveillance","stalking","harassment","morphing","defamation","pornography",
            "obscene","financial fraud","atm","credit card","banking","otp","it act",
            "electronic","signature","certificate","authority","intermediary","platform",
            "website","domain","ip address","server","cloud","database","personal data",
            "gdpr","pdpb","information","technology","cybercrime","dark web","bitcoin",
            "cryptocurrency","blockchain","deepfake","spyware","keylogger","botnet",
            "data theft","account hacked","scam","phishing email","online fraud"
        ],
        "acts": [
            {"act":"Information Technology Act (ITA), 2000","sections":"Section 43 (Damage to computer), Section 66 (Hacking), Section 66C (Identity Theft), Section 66E (Privacy Violation)"},
            {"act":"IT (Amendment) Act, 2008","sections":"Section 66A (Offensive messages), Section 67 (Obscene material), Section 69 (Interception)"},
            {"act":"Personal Data Protection Bill (PDPB), 2023","sections":"Consent-based data processing, data principal rights, data fiduciary obligations"},
            {"act":"IPC Section 420 & 468","sections":"Cheating by personation and forgery – applicable to online fraud"},
        ],
        "constitutional_articles": [
            {"article":"21","title":"Right to Privacy (Puttaswamy 2017)","relevance":"Right to digital privacy is a fundamental right under Article 21"},
            {"article":"19(1)(a)","title":"Freedom of Speech and Expression","relevance":"Online speech restrictions must be reasonable and proportionate"},
            {"article":"19(2)","title":"Reasonable Restrictions","relevance":"State may restrict online content on grounds of decency, security or public order"},
        ],
        "color":"#9B6EE8"
    },
    "Corporate/Business Law": {
        "keywords": [
            "company","corporation","directors","shareholders","board","merger","acquisition",
            "takeover","insolvency","bankruptcy","liquidation","winding up","sebi","nse","bse",
            "ipo","shares","debentures","bonds","securities","insider trading","corporate",
            "governance","audit","accounts","balance sheet","profit loss","dividend","annual",
            "report","agm","egm","resolution","mca","registrar","incorporation","memorandum",
            "articles","partnership","llp","proprietorship","franchise","joint venture",
            "due diligence","compliance","penalty","fine","competition","monopoly",
            "cartel","predatory pricing","bid rigging","cci","promoter","allotment",
            "prospectus","rights issue","buyback","delisting","nclt","ibc","creditor"
        ],
        "acts": [
            {"act":"Companies Act, 2013","sections":"Section 166 (Directors duties), Section 447 (Fraud), Section 185 (Loans to directors)"},
            {"act":"SEBI Act, 1992","sections":"Section 11 (Powers of SEBI), SEBI (Insider Trading) Regulations 2015"},
            {"act":"Insolvency and Bankruptcy Code (IBC), 2016","sections":"Section 7 (Financial creditor), Section 9 (Operational creditor), Section 31 (Resolution Plan)"},
            {"act":"Competition Act, 2002","sections":"Section 3 (Anti-competitive agreements), Section 4 (Abuse of dominance)"},
        ],
        "constitutional_articles": [
            {"article":"19(1)(g)","title":"Freedom to practise any profession or business","relevance":"Right to carry on trade subject to reasonable restrictions"},
            {"article":"301","title":"Freedom of Trade and Commerce","relevance":"Trade and commerce shall be free throughout the territory of India"},
            {"article":"39(b)","title":"Directive Principle – Distribution of wealth","relevance":"State shall direct policy to prevent concentration of wealth"},
        ],
        "color":"#D4A843"
    },
    "Family Law": {
        "keywords": [
            "divorce","marriage","matrimonial","custody","child","alimony","maintenance",
            "adoption","guardianship","inheritance","succession","will","dowry","cruelty",
            "desertion","adultery","restitution","conjugal","rights","separation","annulment",
            "muslim","hindu","christian","personal law","iddat","mehr","talaq","triple talaq",
            "nikah","polygamy","bigamy","domestic violence","protection order","shared household",
            "stridhan","ancestral","joint family","coparcenary","karta","huf","minor","welfare",
            "best interests","visitation","foster","surrogacy","ivf","wife","husband","spouse",
            "matrimonial home","marital","wedlock","nuptial","conjugal rights","mutual consent"
        ],
        "acts": [
            {"act":"Hindu Marriage Act, 1955","sections":"Section 5 (Conditions), Section 13 (Divorce grounds), Section 24 (Maintenance pendente lite)"},
            {"act":"Hindu Succession Act, 1956","sections":"Section 6 (Coparcenary property), Section 8 (General rules of succession)"},
            {"act":"Protection of Women from Domestic Violence Act, 2005","sections":"Section 3 (Definition of domestic violence), Section 12 (Application to Magistrate)"},
            {"act":"Guardians and Wards Act, 1890","sections":"Section 7 (Power of court to make child custody orders)"},
        ],
        "constitutional_articles": [
            {"article":"14","title":"Right to Equality","relevance":"Equal rights in matrimonial property and succession"},
            {"article":"21","title":"Right to Life and Dignity","relevance":"Protection from domestic violence; child right to welfare"},
            {"article":"15","title":"Prohibition of discrimination on grounds of sex","relevance":"Special provisions for women and children in family disputes"},
        ],
        "color":"#3DC97A"
    },
    "Constitutional Law": {
        "keywords": [
            "fundamental rights","directive principles","parliament","legislature","judiciary",
            "executive","separation of powers","federalism","union","state","centre","governor",
            "president","prime minister","cabinet","loksabha","rajyasabha","election",
            "constitutional","amendment","preamble","sovereignty","democratic","republic",
            "secular","socialist","writ","habeas corpus","mandamus","certiorari","prohibition",
            "quo warranto","judicial review","basic structure","emergency","article 356",
            "president rule","freedom of speech","press","religion","conscience","assembly",
            "movement","profession","equality","discrimination","reservation","sc st obc",
            "affirmative action","citizenship","nrc","caa","right to education","rte",
            "fundamental duty","constitutional validity","ultra vires","unconstitutional"
        ],
        "acts": [
            {"act":"Constitution of India, 1950","sections":"Part III (Fundamental Rights Art.12-35), Part IV (DPSPs Art.36-51), Part IVA (Fundamental Duties Art.51A)"},
            {"act":"Representation of the People Act, 1951","sections":"Electoral laws, disqualification, election disputes"},
            {"act":"Right to Information Act, 2005","sections":"Section 3 (Right of citizens to information), Section 8 (Exemptions)"},
            {"act":"Right to Education Act, 2009","sections":"Article 21A – Free and compulsory education for children aged 6-14"},
        ],
        "constitutional_articles": [
            {"article":"12-35","title":"Fundamental Rights","relevance":"Core bundle of rights guaranteed to every citizen of India"},
            {"article":"32","title":"Right to Constitutional Remedies","relevance":"Dr. Ambedkar called this the heart and soul of the Constitution"},
            {"article":"226","title":"Power of High Courts to issue writs","relevance":"High Courts can issue writs for enforcement of fundamental rights"},
        ],
        "color":"#E08C3A"
    },
    "Labour/Employment Law": {
        "keywords": [
            "employee","employer","worker","workman","labour","employment","terminate","dismissal",
            "retrenchment","layoff","gratuity","provident fund","esic","epfo","bonus","wages",
            "salary","minimum wage","overtime","leave","maternity","paternity","union","strike",
            "lockout","collective bargaining","industrial dispute","conciliation","arbitration",
            "tribunal","labour court","standing orders","service rules","appointment","probation",
            "confirmation","promotion","transfer","suspension","misconduct","domestic enquiry",
            "show cause","sexual harassment","posh","vishakha","contract labour","apprentice",
            "child labour","migrant","factories act","shops establishment","wrongful termination",
            "unfair labour practice","voluntary retirement","golden handshake","severance"
        ],
        "acts": [
            {"act":"Industrial Disputes Act, 1947","sections":"Section 2(s) (Workman definition), Section 25F (Retrenchment), Section 25N (Prior permission)"},
            {"act":"Payment of Gratuity Act, 1972","sections":"Section 4 (Payment of gratuity after 5 years), Section 7 (Determination of gratuity)"},
            {"act":"Employees Provident Fund Act, 1952","sections":"Section 6 (Contribution), Section 7A (Determination of dues)"},
            {"act":"Sexual Harassment of Women at Workplace Act, 2013","sections":"Section 3 (Prevention of sexual harassment), Section 4 (Internal Complaints Committee)"},
        ],
        "constitutional_articles": [
            {"article":"21","title":"Right to Livelihood","relevance":"Wrongful termination without due process violates the right to livelihood"},
            {"article":"23","title":"Prohibition of forced labour","relevance":"Forced, bonded or compulsory labour is unconstitutional"},
            {"article":"43","title":"DPSP – Living wage for workers","relevance":"State shall endeavour to secure a living wage and decent standard of life for workers"},
        ],
        "color":"#D4D43A"
    },
    "Intellectual Property Law": {
        "keywords": [
            "copyright","trademark","patent","design","trade secret","intellectual property",
            "infringement","passing off","plagiarism","piracy","counterfeit","license","royalty",
            "assignment","ownership","creator","author","inventor","registrar","registry",
            "geographical indication","gi tag","traditional knowledge","biodiversity","plant variety",
            "semiconductor","mask work","fair use","public domain","creative commons",
            "open source","software patent","business method","injunction","anton piller",
            "mareva","disclosure","confidential","nda","trade mark","brand","logo","slogan",
            "domain name","cybersquatting","dilution","blurring","tarnishment","literary work",
            "artistic work","musical work","cinematographic","sound recording","broadcast"
        ],
        "acts": [
            {"act":"Copyright Act, 1957","sections":"Section 13 (Works protected), Section 51 (Infringement), Section 52 (Fair dealing exceptions)"},
            {"act":"Trade Marks Act, 1999","sections":"Section 29 (Infringement), Section 11 (Relative grounds for refusal), Section 135 (Relief in suits)"},
            {"act":"Patents Act, 1970","sections":"Section 2(m) (Invention), Section 48 (Rights of patentees), Section 64 (Revocation)"},
            {"act":"Designs Act, 2000","sections":"Section 2(d) (Design definition), Section 22 (Piracy of registered design)"},
        ],
        "constitutional_articles": [
            {"article":"300A","title":"Right to Property","relevance":"Intellectual property is property; deprivation requires authority of law"},
            {"article":"19(1)(g)","title":"Freedom to practise any profession","relevance":"Right to commercially exploit one creative or inventive work"},
            {"article":"21","title":"Right to Life","relevance":"Right to livelihood from one creative work falls under Article 21"},
        ],
        "color":"#3DC9C9"
    },
}

# Legal content detection – broad set of terms indicating legal context
LEGAL_INDICATOR_WORDS = {
    "court","judge","plaintiff","defendant","accused","petition","order","judgment","decree",
    "appeal","legal","law","act","section","article","rights","case","complaint","dispute",
    "lawyer","advocate","counsel","justice","hearing","trial","evidence","witness","bail",
    "arrest","fir","police","offence","crime","contract","agreement","party","clause",
    "amendment","constitution","statute","regulation","ordinance","notification","gazette",
    "affidavit","deposition","summons","notice","reply","rejoinder","pleading","jurisdiction",
    "liability","penalty","compensation","damages","relief","injunction","stay","writ",
    "habeas","mandamus","certiorari","tribunal","commission","authority","board","committee",
    "memorandum","articles","incorporation","director","shareholder","employee","employer",
    "marriage","divorce","custody","guardianship","succession","inheritance","will","property",
    "copyright","trademark","patent","infringement","license","royalty","assignment","brand",
    "murder","theft","fraud","rape","assault","kidnapping","extortion","bribery","corruption",
    "cyber","hacking","data","breach","privacy","digital","online","phishing","malware",
    "gratuity","provident","wages","salary","termination","retrenchment","union","strike",
    "company","insolvency","bankruptcy","sebi","merger","acquisition","shares","securities",
    "high court","supreme court","district court","sessions court","magistrate","tribunal",
    "ipc","cpc","crpc","ibc","ita","pf","esic","mca","cci","rbi","nclt","nclat"
}

NON_LEGAL_INDICATORS = {
    # nature/scenery
    "sunset","sunrise","mountain","river","ocean","forest","flower","bird","tree","sky",
    "cloud","rain","snow","beach","valley","waterfall","landscape","wildlife","nature",
    # food
    "recipe","cooking","baking","ingredient","restaurant","cuisine","meal","breakfast",
    "lunch","dinner","snack","dessert","food","taste","flavour","spice","herb",
    # entertainment/sports (non-legal)
    "movie","film","song","music","dance","sport","cricket","football","game","play",
    "actor","actress","celebrity","singer","band","album","concert","festival",
    # fashion/lifestyle
    "fashion","clothing","dress","shirt","shoe","style","makeup","beauty","skincare",
    # technology products (not cyber law)
    "smartphone","laptop","tablet","gadget","app","software feature","update","version",
    "download","install","tutorial","review","unboxing","specs",
    # travel/tourism
    "travel","tour","trip","vacation","hotel","resort","ticket","flight","destination",
    # health/medical (non-legal)
    "medicine","doctor","hospital","treatment","symptom","diagnosis","health","fitness",
    "exercise","yoga","diet","nutrition","vitamin","supplement",
    # agriculture
    "farming","crop","harvest","seed","fertilizer","irrigation","soil","agriculture",
    # personal diary/casual
    "today","yesterday","morning","night","friend","family","happy","sad","feeling",
    "weather","shopping","market","price","buy","sell","product","item"
}

STOPWORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with","by","from",
    "is","are","was","were","be","been","being","have","has","had","do","does","did",
    "will","would","could","should","may","might","shall","not","no","nor","so","yet",
    "both","either","neither","each","every","any","all","some","few","more","most",
    "other","another","such","what","which","who","whom","this","that","these","those",
    "i","he","she","it","we","they","me","him","her","us","them","my","his","its","our",
    "their","as","if","then","than","also","into","through","during","before","after",
    "above","below","between","out","up","down","over","under","again","further","once",
    "here","there","when","where","why","how","said","page","para","hon","vs"
}


class TFIDFEngine:
    def __init__(self):
        self.corpus = [" ".join(d["keywords"]) for d in LEGAL_CATEGORIES.values()]

    def tokenize(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    def compute_tf(self, tokens):
        count = Counter(tokens)
        total = len(tokens) or 1
        return {w: f/total for w, f in count.items()}

    def compute_idf(self, word):
        n = len(self.corpus)
        df = sum(1 for doc in self.corpus if word in doc.lower())
        return math.log((n+1)/(df+1)) + 1

    def compute_tfidf(self, text):
        tokens = self.tokenize(text)
        tf = self.compute_tf(tokens)
        scores = {w: round(tf[w] * self.compute_idf(w), 4) for w in tf}
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]


class LegalContentValidator:
    """Validates whether uploaded text is legal/case-related content."""

    def validate(self, text):
        """Returns (is_legal: bool, confidence: float, reason: str)"""
        if not text or len(text.strip()) < 30:
            return False, 0.0, "Text is too short to analyse."

        text_lower = text.lower()
        words = set(re.findall(r'\b[a-z]{3,}\b', text_lower))

        legal_hits = len(words & LEGAL_INDICATOR_WORDS)
        non_legal_hits = len(words & NON_LEGAL_INDICATORS)

        total_words = len(text.split())
        legal_density = legal_hits / max(total_words * 0.1, 1)

        # Hard reject: image/binary/base64 content
        if len(re.findall(r'[^\x00-\x7F]', text)) > len(text) * 0.3:
            return False, 0.0, "File appears to contain binary or image data, not legal text."

        # Check for legal phrases (strong positive signals)
        strong_phrases = [
            "in the court","before the hon","filed a case","filed an fir",
            "the petitioner","the respondent","the accused","section ",
            "under the act","article ","fundamental right","case no",
            "order dated","judgment dated","whereas","hereby","hereinafter",
            "party of the","suit for","plaintiff has","defendant has",
            "this agreement","terms and conditions","in witness whereof",
            "legal notice","cause of action","relief sought","prayer"
        ]
        phrase_hits = sum(1 for p in strong_phrases if p in text_lower)

        # Decision logic
        if phrase_hits >= 2:
            return True, min(95.0, 60 + phrase_hits * 5), "Strong legal phrases detected."

        if legal_hits >= 5 and non_legal_hits <= 3:
            score = min(90.0, 50 + legal_hits * 4)
            return True, score, f"Legal terminology detected ({legal_hits} indicators)."

        if legal_hits >= 3 and non_legal_hits == 0:
            return True, 65.0, "Moderate legal content detected."

        if non_legal_hits > legal_hits * 1.5 and non_legal_hits >= 4:
            return False, 0.0, (
                f"This file does not appear to contain legal case content. "
                f"Detected non-legal content (e.g. nature, food, entertainment, personal diary). "
                f"Please upload legal documents such as FIRs, court orders, contracts, "
                f"legal notices, case files or law-related text."
            )

        if legal_hits >= 2:
            return True, 50.0, "Some legal content detected."

        return False, 0.0, (
            "No recognisable legal content found in this file. "
            "Please upload a legal document – court orders, FIRs, contracts, petitions, "
            "legal notices, agreements, judgments or case-related text files."
        )


class LegalClassifier:
    def __init__(self):
        self.engine = TFIDFEngine()
        self.validator = LegalContentValidator()

    def classify(self, text):
        tokens = set(self.engine.tokenize(text))
        text_lower = text.lower()
        scores = {}
        for category, data in LEGAL_CATEGORIES.items():
            kw_list = data["keywords"]
            single_kw = set(kw for kw in kw_list if " " not in kw)
            multi_kw  = [kw for kw in kw_list if " " in kw]
            overlap       = len(tokens & single_kw)
            phrase_matches = sum(1 for p in multi_kw if p in text_lower)
            tfidf_scores   = dict(self.engine.compute_tfidf(text))
            tfidf_sum      = sum(tfidf_scores.get(kw, 0) for kw in single_kw if kw in tfidf_scores)
            scores[category] = overlap * 2.5 + phrase_matches * 4.5 + tfidf_sum * 12

        if not any(scores.values()):
            for cat, data in LEGAL_CATEGORIES.items():
                for kw in data["keywords"]:
                    if kw in text.lower():
                        scores[cat] = scores.get(cat, 0) + 1

        total  = sum(scores.values()) or 1
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top    = ranked[0][0] if ranked else "Civil Law"
        raw_conf = (scores[top] / total) * 100 * 1.8
        confidence = round(max(55.0, min(98.0, raw_conf)), 1)
        return {
            "category":   top,
            "confidence": confidence,
            "all_scores": {k: round(v/total*100, 1) for k, v in ranked},
            "data":       LEGAL_CATEGORIES[top]
        }

    def extract_summary(self, text, max_sentences=3):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if len(s.split()) > 5]
        return " ".join(sentences[:max_sentences]) if sentences else text[:400]

    def full_analysis(self, text):
        c = self.classify(text)
        return {
            "category":               c["category"],
            "confidence":             c["confidence"],
            "all_scores":             c["all_scores"],
            "summary":                self.extract_summary(text),
            "tfidf_keywords":         self.engine.compute_tfidf(text)[:12],
            "applicable_acts":        c["data"]["acts"],
            "constitutional_articles":c["data"]["constitutional_articles"],
            "color":                  c["data"]["color"],
            "severity":               self._severity(text),
            "recommended_action":     self._action(c["category"])
        }

    def _severity(self, text):
        high = {"murder","rape","kidnapping","terrorism","fraud","death","violent","assault",
                "critical","urgent","immediate","emergency","heinous","capital","aggravated"}
        low  = {"minor","small","trivial","simple","ordinary","routine","basic","dispute","property","civil"}
        tokens = set(self.engine.tokenize(text))
        if tokens & high: return "High"
        if tokens & low:  return "Low"
        return "Medium"

    def _action(self, cat):
        return {
            "Criminal Law":          "File an FIR at your nearest police station immediately. Engage a criminal defence lawyer. Preserve all evidence including witnesses.",
            "Civil Law":             "Consult a civil advocate to file a plaint in the appropriate civil court within the limitation period. Gather all documentary evidence.",
            "Cyber Law":             "File a complaint at cybercrime.gov.in or your nearest Cyber Cell. Preserve all digital evidence (screenshots, emails, logs).",
            "Corporate/Business Law":"Consult a company law specialist. File complaints with MCA, SEBI, or NCLT as applicable. Preserve all corporate documents.",
            "Family Law":            "Approach a family court or district court. Consider mediation first. Consult a family law advocate for the personal law applicable to you.",
            "Constitutional Law":    "File a Writ Petition (Article 32 before Supreme Court or Article 226 before High Court). Engage a constitutional law expert.",
            "Labour/Employment Law": "File a complaint with the Labour Commissioner or approach the Labour Court / Industrial Tribunal. Gather all employment documents.",
            "Intellectual Property Law":"Send a cease and desist notice immediately. File for injunction in the IP Division of the High Court. Register your IP if not already done.",
        }.get(cat, "Consult a qualified legal practitioner for advice specific to your situation.")


classifier = LegalClassifier()
