import hashlib, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOP = {"a","an","and","are","as","at","be","by","for","from","in","is","it","of","on","or","that","the","this","to","using","with"}
def tokens(text): return [w for w in re.findall(r"[a-z0-9+#.-]+", (text or "").lower()) if w not in STOP and len(w)>1]
def preprocess(text): return " ".join(tokens(text))
def cosine(a,b):
    if not preprocess(a) or not preprocess(b): return 0.0
    matrix=TfidfVectorizer(ngram_range=(1,2)).fit_transform([preprocess(a),preprocess(b)])
    return float(cosine_similarity(matrix[0],matrix[1])[0,0])
def jaccard(a,b):
    x,y=set(tokens(a)),set(tokens(b)); return len(x&y)/len(x|y) if x|y else 0.0
def shingles(text,n=3):
    t=tokens(text); return {" ".join(t[i:i+n]) for i in range(max(0,len(t)-n+1))}
def minhash(text, permutations=64):
    values=shingles(text) or set(tokens(text))
    if not values:return []
    return [min(int(hashlib.sha1(f"{i}:{v}".encode()).hexdigest(),16) for v in values) for i in range(permutations)]
def minhash_similarity(a,b):
    x,y=minhash(a),minhash(b); return sum(i==j for i,j in zip(x,y))/len(x) if x and y else 0.0
def normalize_code(code):
    code=re.sub(r"/\*.*?\*/|//[^\n]*|#[^\n]*", " ", code or "", flags=re.S)
    raw=re.findall(r'"(?:\\.|[^"\\])*"|\b\d+(?:\.\d+)?\b|[A-Za-z_$][\w$]*|==|!=|<=|>=|&&|\|\||[-+*/%=<>!&|{}()[\];,.?:]',code)
    reserved={"if","else","for","while","return","class","def","function","import","from","new","try","catch","public","private","static","void","int","string","const","let","var","async","await"}
    return " ".join(t.lower() if t.lower() in reserved or not re.match(r"[A-Za-z_$]",t) else "ID" for t in raw)
def code_similarity(a,b):
    a,b=normalize_code(a),normalize_code(b)
    return (cosine(a,b)+jaccard(a,b))/2 if a and b else 0.0
def classify(score):
    return "Very High Similarity" if score>=.85 else "High Similarity" if score>=.70 else "Significant Similarity" if score>=.50 else "Moderate Similarity" if score>=.25 else "Low Similarity"
def compare_projects(query, candidate):
    title=cosine(query.get("title"),candidate.title)
    abstract=cosine(f'{query.get("abstract","")} {query.get("description","")}',f"{candidate.abstract} {candidate.description}")
    report=cosine(query.get("report_text"),candidate.report_text)
    keyword=jaccard(" ".join(query.get("keywords",[]))," ".join(candidate.keywords or []))
    approx=minhash_similarity(" ".join([query.get("abstract", ""),query.get("description", ""),query.get("report_text","")])," ".join([candidate.abstract,candidate.description or "",candidate.report_text or ""]))
    code=code_similarity(query.get("source_code"),candidate.source_code)
    signals={"title":title,"abstract":abstract,"report":report,"keywords":keyword,"minhash":approx,"code":code}
    weights={"title":.10,"abstract":.25,"report":.20,"keywords":.15,"minhash":.10,"code":.20}
    available={k:v for k,v in signals.items() if k not in {"report","code"} or (query.get("report_text" if k=="report" else "source_code") and getattr(candidate,"report_text" if k=="report" else "source_code"))}
    total=sum(weights[k] for k in available); score=sum(available[k]*weights[k] for k in available)/total
    shared=sorted(set(tokens(" ".join(query.get("keywords",[]))+" "+query.get("abstract",""))) & set(tokens(" ".join(candidate.keywords or [])+" "+candidate.abstract)))[:10]
    reasons=[]
    if abstract>.35: reasons.append("Related abstract and project-description language")
    if keyword>.25: reasons.append("Strong overlap in declared topics and keywords")
    if code>.35: reasons.append("Similar normalized source-code token structure")
    if approx>.3: reasons.append("MinHash found shared text shingles")
    return {"score":round(score,4),"classification":classify(score),"components":{k:round(v,4) for k,v in signals.items()},"shared_keywords":shared,"evidence":reasons or ["Ranked by the available similarity signals"]}
