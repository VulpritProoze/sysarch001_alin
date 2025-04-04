COURSE_CHOICES = [
    ('BSIT', 'Bachelor of Science in Information Technology'),
    ('BSCS', 'Bachelor of Science in Computer Science'),
    ('BSCPE', 'Bachelor of Science in Computer Engineering'),
    ('BSIS', 'Bachelor of Science in Information Systems'),
    ('BSCE', 'Bachelor of Science in Civil Engineering'),
    ('BSEE', 'Bachelor of Science in Electrical Engineering'),
    ('BSECE', 'Bachelor of Science in Electronics and Communications Engineering'),
    ('BSME', 'Bachelor of Science in Mechanical Engineering'),
    ('BSBA', 'Bachelor of Science in Business Administration'),
    ('BSHRM', 'Bachelor of Science in Hospitality and Restaurant Management'),
    ('BSA', 'Bachelor of Science in Accountancy'),
    ('BSN', 'Bachelor of Science in Nursing'),
    ('BSED', 'Bachelor of Secondary Education'),
    ('BEED', 'Bachelor of Elementary Education'),
    ('BSP', 'Bachelor of Science in Psychology'),
    ('BSMT', 'Bachelor of Science in Marine Transportation'),
    ('BSMarE', 'Bachelor of Science in Marine Engineering'),
    ('BSTM', 'Bachelor of Science in Tourism Management'),
    ('BFA', 'Bachelor of Fine Arts'),
    ('BSArch', 'Bachelor of Science in Architecture'),
    ('BSPharma', 'Bachelor of Science in Pharmacy'),
]


LEVEL_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
]

PROGRAMMING_LANGUAGE_CHOICES = [
    ("Python", "Python"),
    ("Java", "Java"),
    ("C", "C"),
    ("C++", "C++"),
    ("C#", "C#"),
    ("JavaScript", "JavaScript"),
    ("PHP", "PHP"),
    ("HTML & CSS", "HTML & CSS"),
    ("SQL", "SQL"),
    ("Ruby", "Ruby"),
    ("Go", "Go"),
    ("Swift", "Swift"),
    ("Kotlin", "Kotlin"),
]

SITIN_PURPOSE_CHOICES = [
    ("Java Programming", "Java Programming"),
    ("C# Programming", "C# Programming"),
    ("Systems Integration & Architecture", "Systems Integration & Architecture"),
    ("Embedded Systems & IoT", "Embedded Systems & IoT"),
    ("Digital Logic & Design", "Digital Logic & Design"),
    ("Computer Application", "Computer Application"),
    ("Database", "Database"),
    ("Project Management", "Project Management"),
    ("Python Programming", "Python Programming"),
    ("Mobile Application", "Mobile Application"),
    ("Web Design", "Web Design"),
    ("Php Programming", "Php Programming"),
    ("Others", "Others"),
]

LAB_ROOM_CHOICES = [
    ('524', 'Room 524'),
    ('526', 'Room 526'),
    ('528', 'Room 528'),
    ('530', 'Room 530'),
    ('542', 'Room 542'),
    ('544', 'Room 544'),
    ('517', 'Room 517'),
]

SITIN_STATUS_CHOICES = [
    ('none', 'Not Sitin'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('finished', 'Finished'),
]

RATING_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3,),
    (4, 4),
    (5, 5),
]

QUESTION_CHOICES = [
    (1, "How satisfied are you with the overall sit-in process?"),
    (2, "How easy was it to book a sit-in slot?"),
    (3, "Did the system provide clear instructions and requirements for sit-ins?"),
    (4, "How satisfied are you with the response time for sit-in approvals?"),
    (5, "Would you recommend this system to other students?"),
]

SURVEY_STATUS_CHOICES = [
    ('not taken', 'Not yet taken'),
    ('taken', 'Taken'),
]