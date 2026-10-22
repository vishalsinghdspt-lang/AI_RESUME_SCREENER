def calculate_match(candidate_skills, job_skills):

    matched_skills = list(
        set(candidate_skills).intersection(
            set(job_skills)
        )
    )

    missing_skills = list(
        set(job_skills) - set(candidate_skills)
    )

    score = round(
        (len(matched_skills) / len(job_skills)) * 100,
        2
    )

    if score >= 80:
        recommendation = "Strong candidate. Shortlist for interview."

    elif score >= 50:
        recommendation = "Potential candidate. Needs skill improvement."

    else:
        recommendation = "Not a strong match for this role."
    
    
    course_suggestions = {
        "AWS": "AWS Cloud Practitioner",
        "SQL": "SQL for Beginners",
        "Python": "Advanced Python Programming",
        "React.js": "React Complete Guide",
        "Node.js": "Node.js Bootcamp",
        "Git": "Git & GitHub Masterclass"
    }

    recommended_courses = []

    for skill in missing_skills:

        if skill in course_suggestions:

            recommended_courses.append(
            course_suggestions[skill]
        )

    return {
    "matched_skills": matched_skills,
    "missing_skills": missing_skills,
    "match_score": score,
    "recommendation": recommendation,
    "recommended_courses": recommended_courses
}