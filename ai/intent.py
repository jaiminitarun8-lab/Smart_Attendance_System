def detect_intent(message):

    msg = message.lower()

    attendance_keywords = [
        "attendance",
        "present",
        "percentage",
        "kitna present",
        "meri attendance",
        "attendance kitni",
        "attendance percentage"
    ]

    leave_keywords = [
        "leave",
        "holiday",
        "chutti",
        "leave status",
        "pending leave"
    ]

    today_keywords = [
        "today",
        "aaj",
        "today attendance"
    ]

    subject_keywords = [
        "mathematics",
        "math",
        "maths"
    ]

    prediction_keywords = [
        "75",
        "predict",
        "future attendance",
        "reach",
        "attendance target",
        "75 attendance"
    ]

    # Attendance
    for word in attendance_keywords:
        if word in msg:
            return "attendance"

    # Leave
    for word in leave_keywords:
        if word in msg:
            return "leave"

    # Today
    for word in today_keywords:
        if word in msg:
            return "today"

    # Subject
    for word in subject_keywords:
        if word in msg:
            return "mathematics"

    # Prediction
    for word in prediction_keywords:
        if word in msg:
            return "prediction"

    return "unknown"