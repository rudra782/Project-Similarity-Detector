PROJECTS=[
("Project Similarity Detection","Compares student project abstracts, reports and source code against an academic repository using TF-IDF cosine similarity, Jaccard, MinHash and LSH.","Explainable ranked retrieval for faculty review.",["tf-idf","cosine similarity","minhash","academic projects","source code"],"Natural Language Processing","2025-26"),
("Code Plagiarism Detector","A token based source code comparison tool that removes comments, normalizes identifiers and detects structural similarity across programming assignments.","Uses token n-grams and Jaccard scoring without executing uploaded code.",["code tokens","jaccard","normalization","similarity"],"Software Engineering","2024-25"),
("AI Resume Analyzer","Extracts skills and education from resumes and ranks candidates against job descriptions with natural language processing.","Recruitment decision support dashboard.",["nlp","resume","ranking","tf-idf"],"Machine Learning","2024-25"),
("Smart Attendance System","Records classroom attendance using face recognition and produces faculty attendance reports.","Computer vision attendance management.",["face recognition","attendance","opencv"],"Computer Vision","2023-24"),
("Library Management System","Manages catalogues, borrowing, returns and overdue notifications for a college library.","Role-based library operations portal.",["library","catalogue","database"],"Web Development","2023-24"),
("Crop Disease Detection","Classifies crop leaf diseases from images and gives treatment guidance to farmers.","CNN-assisted agriculture support.",["agriculture","cnn","image classification"],"Machine Learning","2024-25"),
("Campus Navigation App","Provides accessible indoor and outdoor routes between campus buildings.","Graph search and location-aware directions.",["navigation","maps","shortest path"],"Mobile Computing","2025-26"),
("Healthcare Appointment System","Schedules clinical appointments and manages doctor availability and reminders.","Secure patient scheduling workflow.",["healthcare","appointments","scheduling"],"Web Development","2023-24"),
("E-Commerce Recommendation System","Suggests products from browsing and purchase histories using collaborative filtering.","Personalized product discovery.",["recommendation","collaborative filtering","e-commerce"],"Machine Learning","2024-25"),
("Student Performance Predictor","Predicts academic outcomes from attendance and assessment records and explains risk factors.","Early academic intervention support.",["prediction","education","analytics"],"Data Science","2025-26")]
def seed(db, Project):
    if db.query(Project).count(): return
    for i,p in enumerate(PROJECTS):
        db.add(Project(title=p[0],abstract=p[1],description=p[2],keywords=p[3],category=p[4],academic_year=p[5],team_name=f"Demo Team {i+1}",report_text=f"{p[1]} {p[2]} {' '.join(p[3])}"))
    db.commit()
