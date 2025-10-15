import json

def calculate_compatibility(mentee, mentor):
    """
    Calculate compatibility score between mentee and mentor
    
    Returns a score between 0 and 100
    """
    score = 0
    max_score = 0
    
    # Parse JSON fields
    try:
        mentee_careers = json.loads(mentee.careers_interested_in) if mentee.careers_interested_in else []
        mentee_concentrations = json.loads(mentee.concentrations_interested_in) if mentee.concentrations_interested_in else []
        mentee_courses = json.loads(mentee.technical_courses_taken) if mentee.technical_courses_taken else []
        
        mentor_experiences = json.loads(mentor.professional_experiences) if mentor.professional_experiences else []
        mentor_courses = json.loads(mentor.technical_courses) if mentor.technical_courses else []
    except json.JSONDecodeError:
        # If JSON parsing fails, use empty lists
        mentee_careers = []
        mentee_concentrations = []
        mentee_courses = []
        mentor_experiences = []
        mentor_courses = []
    
    # 1. Career path alignment (40 points)
    if mentee.looking_for_career_advice and mentee_careers and mentor_experiences:
        max_score += 40
        # Check if mentor's experiences align with mentee's career interests
        career_matches = sum(1 for career in mentee_careers 
                           if any(career.lower() in exp.lower() for exp in mentor_experiences))
        if career_matches > 0:
            score += min(40, (career_matches / len(mentee_careers)) * 40)
    
    # 2. Concentration/Major alignment (30 points)
    if mentee.looking_for_major_advice and mentee_concentrations and mentor.info_concentration:
        max_score += 30
        # Check if mentor's concentration matches mentee's interests
        concentration_matches = sum(1 for conc in mentee_concentrations 
                                   if conc.lower() in mentor.info_concentration.lower())
        if concentration_matches > 0:
            score += min(30, (concentration_matches / len(mentee_concentrations)) * 30)
    
    # 3. Technical course overlap (30 points)
    if mentee_courses and mentor_courses:
        max_score += 30
        # Calculate Jaccard similarity for courses
        mentee_courses_set = set(course.lower() for course in mentee_courses)
        mentor_courses_set = set(course.lower() for course in mentor_courses)
        
        intersection = len(mentee_courses_set & mentor_courses_set)
        union = len(mentee_courses_set | mentor_courses_set)
        
        if union > 0:
            jaccard_score = intersection / union
            score += jaccard_score * 30
    
    # Normalize score to 0-100 range
    if max_score > 0:
        normalized_score = (score / max_score) * 100
    else:
        normalized_score = 50  # Default neutral score if no criteria matched
    
    return round(normalized_score, 2)


def get_top_matches(mentee, mentors, limit=10):
    """
    Get top N mentor matches for a mentee
    
    Args:
        mentee: Mentee object
        mentors: List of Mentor objects
        limit: Maximum number of matches to return
    
    Returns:
        List of tuples (mentor, score) sorted by score descending
    """
    matches = []
    
    for mentor in mentors:
        if mentor.availability_status == 'available':
            score = calculate_compatibility(mentee, mentor)
            matches.append((mentor, score))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:limit]

