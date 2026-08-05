"""
Real student data ko hamare database format me import karne ke liye.
- ID format: S2026-XXXX (face recognition system isi format ko use karta hai)
- Password: safely hashed (plain text nahi)
- Existing sample students (S2026-0001 se S2026-0005) ke saath collision nahi hoga —
  naye students S2026-0006 se shuru honge.

Chalane ka tarika:
    python -m database.import_real_students
"""

from database.connection import Base, engine, SessionLocal
from database.models import Student
from utils.security import hash_password

# (roll_no, name, dob, gender, class, section, phone, email,
#  address, admission_date, father_name, mother_name, username, password)
raw_students_data = [
    ('R001', 'Aarav Jain', '2009-03-24', 'Male', '7', 'A', '9181960013', 'aarav.jain1@example.com', 'Jodhpur, Rajasthan', '2024-06-07', 'Manoj Jain', 'Sunita Jain', 'R001', 'ram@1'),
    ('R002', 'Ishita Reddy', '2006-01-25', 'Female', '10', 'B', '9265423511', 'ishita.reddy2@example.com', 'Ajmer, Rajasthan', '2024-05-20', 'Anil Reddy', 'Geeta Reddy', 'R002', 'ram@2'),
    ('R003', 'Ananya Reddy', '2006-07-03', 'Female', '10', 'A', '9849593103', 'ananya.reddy3@example.com', 'Udaipur, Rajasthan', '2024-04-13', 'Ramesh Reddy', 'Rekha Reddy', 'R003', 'ram@3'),
    ('R004', 'Tanya Chauhan', '2009-06-07', 'Female', '7', 'B', '9419283276', 'tanya.chauhan4@example.com', 'Udaipur, Rajasthan', '2024-05-27', 'Suresh Chauhan', 'Poonam Chauhan', 'R004', 'ram@4'),
    ('R005', 'Reyansh Verma', '2008-05-03', 'Male', '8', 'B', '9395376724', 'reyansh.verma5@example.com', 'Jodhpur, Rajasthan', '2024-06-09', 'Sanjay Verma', 'Anita Verma', 'R005', 'ram@5'),
    ('R006', 'Siya Joshi', '2008-03-17', 'Female', '8', 'A', '9710122691', 'siya.joshi6@example.com', 'Ajmer, Rajasthan', '2024-06-09', 'Manoj Joshi', 'Kavita Joshi', 'R006', 'ram@6'),
    ('R007', 'Aditya Bhatt', '2008-02-10', 'Male', '8', 'B', '9627048281', 'aditya.bhatt7@example.com', 'Udaipur, Rajasthan', '2024-04-12', 'Manoj Bhatt', 'Rekha Bhatt', 'R007', 'ram@7'),
    ('R008', 'Shaurya Menon', '2010-08-01', 'Male', '6', 'B', '9154303911', 'shaurya.menon8@example.com', 'Ajmer, Rajasthan', '2024-04-05', 'Ramesh Menon', 'Anita Menon', 'R008', 'ram@8'),
    ('R009', 'Navya Yadav', '2008-04-18', 'Female', '8', 'B', '9346578713', 'navya.yadav9@example.com', 'Jodhpur, Rajasthan', '2024-06-18', 'Anil Yadav', 'Sunita Yadav', 'R009', 'ram@9'),
    ('R010', 'Om Agarwal', '2010-12-21', 'Male', '6', 'A', '9031051834', 'om.agarwal10@example.com', 'Ajmer, Rajasthan', '2024-06-19', 'Manoj Agarwal', 'Rekha Agarwal', 'R010', 'ram@10'),
    ('R011', 'Ishita Nair', '2007-02-04', 'Female', '9', 'A', '9656670106', 'ishita.nair11@example.com', 'Udaipur, Rajasthan', '2024-04-18', 'Suresh Nair', 'Rekha Nair', 'R011', 'ram@11'),
    ('R012', 'Aadhya Pandey', '2009-08-08', 'Female', '7', 'B', '9178108013', 'aadhya.pandey12@example.com', 'Jodhpur, Rajasthan', '2024-04-28', 'Vinod Pandey', 'Kavita Pandey', 'R012', 'ram@12'),
    ('R013', 'Ananya Yadav', '2007-07-09', 'Female', '9', 'A', '9746872343', 'ananya.yadav13@example.com', 'Jaipur, Rajasthan', '2024-04-24', 'Sanjay Yadav', 'Anita Yadav', 'R013', 'ram@13'),
    ('R014', 'Ananya Verma', '2006-09-28', 'Female', '10', 'B', '9820812191', 'ananya.verma14@example.com', 'Jodhpur, Rajasthan', '2024-04-19', 'Rakesh Verma', 'Anita Verma', 'R014', 'ram@14'),
    ('R015', 'Dhruv Gupta', '2007-05-07', 'Male', '9', 'B', '9534624751', 'dhruv.gupta15@example.com', 'Jaipur, Rajasthan', '2024-04-03', 'Manoj Gupta', 'Anita Gupta', 'R015', 'ram@15'),
    ('R016', 'Ansh Jain', '2009-02-08', 'Male', '7', 'B', '9542784980', 'ansh.jain16@example.com', 'Kota, Rajasthan', '2024-04-09', 'Sanjay Jain', 'Sunita Jain', 'R016', 'ram@16'),
    ('R017', 'Aditya Bhatt', '2009-05-20', 'Male', '7', 'B', '9353487401', 'aditya.bhatt17@example.com', 'Ajmer, Rajasthan', '2024-05-25', 'Rakesh Bhatt', 'Sunita Bhatt', 'R017', 'ram@17'),
    ('R018', 'Ishaan Yadav', '2007-09-01', 'Male', '9', 'B', '9112805982', 'ishaan.yadav18@example.com', 'Ajmer, Rajasthan', '2024-05-26', 'Rakesh Yadav', 'Meena Yadav', 'R018', 'ram@18'),
    ('R019', 'Yash Mishra', '2009-06-25', 'Male', '7', 'A', '9869232260', 'yash.mishra19@example.com', 'Jodhpur, Rajasthan', '2024-06-28', 'Ramesh Mishra', 'Kavita Mishra', 'R019', 'ram@19'),
    ('R020', 'Ishaan Yadav', '2010-01-28', 'Male', '6', 'B', '9733754330', 'ishaan.yadav20@example.com', 'Jodhpur, Rajasthan', '2024-04-25', 'Anil Yadav', 'Meena Yadav', 'R020', 'ram@20'),
    ('R021', 'Sneha Menon', '2007-01-04', 'Female', '9', 'B', '9429401965', 'sneha.menon21@example.com', 'Udaipur, Rajasthan', '2024-04-13', 'Manoj Menon', 'Anita Menon', 'R021', 'ram@21'),
    ('R022', 'Ishaan Verma', '2007-09-26', 'Male', '9', 'A', '9835615951', 'ishaan.verma22@example.com', 'Udaipur, Rajasthan', '2024-05-11', 'Anil Verma', 'Poonam Verma', 'R022', 'ram@22'),
    ('R023', 'Anika Bhatt', '2009-07-22', 'Female', '7', 'A', '9629946804', 'anika.bhatt23@example.com', 'Udaipur, Rajasthan', '2024-06-20', 'Vinod Bhatt', 'Geeta Bhatt', 'R023', 'ram@23'),
    ('R024', 'Tanya Reddy', '2007-09-16', 'Female', '9', 'A', '9214895134', 'tanya.reddy24@example.com', 'Jodhpur, Rajasthan', '2024-04-08', 'Suresh Reddy', 'Sunita Reddy', 'R024', 'ram@24'),
    ('R025', 'Kritika Gupta', '2007-11-19', 'Female', '9', 'B', '9367632016', 'kritika.gupta25@example.com', 'Jodhpur, Rajasthan', '2024-06-15', 'Ramesh Gupta', 'Poonam Gupta', 'R025', 'ram@25'),
]


def import_real_students():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Existing S2026-XXXX IDs se collision avoid karne ke liye already-used numbers dekh lo
    existing_ids = {s.student_id for s in db.query(Student).all()}
    next_number = 1
    added, skipped = 0, 0

    for (roll_no, name, dob, gender, class_, section, phone, email,
         address, admission_date, father_name, mother_name, username, password) in raw_students_data:

        # Naya unique S2026-XXXX ID dhundo
        while f"S2026-{next_number:04d}" in existing_ids:
            next_number += 1
        new_student_id = f"S2026-{next_number:04d}"
        next_number += 1

        already = db.query(Student).filter(Student.roll_no == roll_no).first()
        if already:
            skipped += 1
            continue

        student = Student(
            student_id=new_student_id,
            roll_no=roll_no,
            name=name,
            password_hash=hash_password(password),
            email=email,
            phone=phone,
            section=section,
            class_name=class_,
            dob=dob,
            gender=gender,
            address=address,
            admission_date=admission_date,
            father_name=father_name,
            mother_name=mother_name,
        )
        db.add(student)
        existing_ids.add(new_student_id)
        added += 1

    db.commit()
    db.close()

    print(f"✅ Import complete: {added} students added, {skipped} skipped (already existed).")
    print("Naye students ka login ID format: S2026-XXXX, password same rakha gaya hai jo pehle tha (jaise 'ram@1').")


if __name__ == "__main__":
    import_real_students()
