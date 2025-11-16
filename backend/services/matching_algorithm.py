import json

def calculate_compatibility(mentee, mentor):
    """
    Calculate compatibility score between mentee and mentor based on the new models.
    
    Returns a score between 0 and 100, weighted as follows:
    - 50% for Advising Topics match
    - 30% for Career Path match
    - 20% for Concentration match
    """
    score = 0
    max_score = 0
    
    # 1. Parse JSON fields from Text columns
    try:
        # Mentee fields
        mentee_needs = json.loads(mentee.advising_needs) if mentee.advising_needs else []
        mentee_careers = json.loads(mentee.careers_interested_in) if mentee.careers_interested_in else []
        
        # Mentor fields
        mentor_topics = json.loads(mentor.advising_topics) if mentor.advising_topics else []
    except json.JSONDecodeError:
        # If JSON parsing fails, use empty lists
        mentee_needs = []
        mentee_careers = []
        mentor_topics = []

    # --- Matching Logic ---

    # 1. Advising Topics Alignment (Weight: 50 points)
    # Scores based on the % of the mentee's needs that the mentor can fulfill.
    if mentee_needs:
        max_score += 50
        
        # Use sets for efficient, case-insensitive comparison
        mentee_needs_set = set(need.lower().strip() for need in mentee_needs)
        mentor_topics_set = set(topic.lower().strip() for topic in mentor_topics)
        
        # Find how many of the mentee's needs the mentor can fulfill
        matches_found = mentee_needs_set.intersection(mentor_topics_set)
        
        # Calculate percentage of mentee's needs met
        if mentee_needs_set: # Avoid division by zero
            match_percentage = len(matches_found) / len(mentee_needs_set)
            score += match_percentage * 50

    # 2. Career Path Alignment (Weight: 30 points)
    # Matches mentee's list of interests (JSON) vs. mentor's single career (string)
    if mentee_careers and mentor.career_pursuing:
        max_score += 30
        
        mentor_career_lower = mentor.career_pursuing.lower().strip()
        mentee_careers_lower = [career.lower().strip() for career in mentee_careers]
        
        # Give full points if the mentor's career is in the mentee's list of interests
        if mentor_career_lower in mentee_careers_lower:
            score += 30 

    # 3. Concentration Alignment (Weight: 20 points)
    # Simple string match for Information Science concentration
    if mentee.info_concentration and mentor.info_concentration:
        max_score += 20
        mentee_conc = mentee.info_concentration.lower().strip()
        mentor_conc = mentor.info_concentration.lower().strip()

        # Give points if they match. This also handles "I don't know" matching "I don't know"
        if mentee_conc == mentor_conc:
            score += 20
    
    # --- Normalization ---
    # Normalize the final score to be out of 100
    if max_score > 0:
        normalized_score = (score / max_score) * 100
    else:
        # Default neutral score if no criteria matched (e.g., mentee left all fields blank)
        normalized_score = 50  
    
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
        # Only match with mentors who are available
        if mentor.availability_status == 'available':
            score = calculate_compatibility(mentee, mentor)
            matches.append((mentor, score))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:limit]