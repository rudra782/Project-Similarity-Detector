from app.similarity.engine import classify, code_similarity, cosine, jaccard, normalize_code, preprocess
def test_preprocess(): assert preprocess("The QUICK, brown fox!")=="quick brown fox"
def test_identical_cosine(): assert cosine("project similarity detection","project similarity detection")>.99
def test_empty_cosine(): assert cosine("","")==0
def test_unrelated_cosine(): assert cosine("apple orange","database network")==0
def test_jaccard(): assert jaccard("alpha beta","beta gamma")==1/3
def test_code_normalization(): assert "comment" not in normalize_code("// comment\nfunction sum(a,b){ return a+b; }")
def test_code_similarity(): assert code_similarity("def add(a,b): return a+b","def plus(x,y): return x+y")>.7
def test_classification(): assert classify(.72)=="High Similarity"
