"""
PathMatch Matching Algorithm Test Suite
========================================
Tests the matching algorithm with mock mentors and mentees to validate:
- Score distribution is meaningful
- Clear differentiation between good and poor matches
- Match explanations are coherent
"""

import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, calculate_compatibility, get_top_matches
from models import User, Mentor, Mentee

# =============================================================================
# MOCK DATA
# =============================================================================

MOCK_MENTORS = [
    {
        'name': 'Andrew Lin',
        'email': 'al123@cornell.edu',
        'net_id': 'al123',
        'graduating_year': 2025,
        'info_concentration': 'Interactive Technologies',
        'career_pursuing': 'Software Engineering',
        'advising_topics': ['job', 'internship'],
        'bio': 'Software engineer with experience at Google and Meta. Love building scalable systems and mentoring on technical interviews.',
        'experiences': 'Interned at Google, Meta. Built distributed systems. Strong in algorithms and system design.',
        'calendly_link': 'https://calendly.com/andrew-lin'
    },
    {
        'name': 'Chelsea Ho',
        'email': 'ch456@cornell.edu',
        'net_id': 'ch456',
        'graduating_year': 2025,
        'info_concentration': 'UX',
        'career_pursuing': 'UX Design',
        'advising_topics': ['job', 'major'],
        'bio': 'UX Designer passionate about human-centered design. Portfolio includes work for startups and Fortune 500 companies.',
        'experiences': 'Led UX redesign at startup. Conducted user research for enterprise products. Skilled in Figma and prototyping.',
        'calendly_link': 'https://calendly.com/chelsea-ho'
    },
    {
        'name': 'Hamid Rezaee',
        'email': 'hr789@cornell.edu',
        'net_id': 'hr789',
        'graduating_year': 2025,
        'info_concentration': 'Data Science',
        'career_pursuing': 'Data Science',
        'advising_topics': ['phd', 'masters-it', 'job'],
        'bio': 'Data scientist specializing in machine learning and AI research. Published papers on NLP and computer vision.',
        'experiences': 'Research assistant in ML lab. Internship at AI startup. Experience with deep learning frameworks.',
        'calendly_link': 'https://calendly.com/hamid-r'
    },
    {
        'name': 'Leina McLaughlin',
        'email': 'lm012@cornell.edu',
        'net_id': 'lm012',
        'graduating_year': 2025,
        'info_concentration': 'Behavioral Science',
        'career_pursuing': 'Academia',
        'advising_topics': ['phd', 'major'],
        'bio': 'Pursuing PhD in HCI research. Focus on how technology affects human behavior and social interactions.',
        'experiences': 'Published 3 peer-reviewed papers. TA for intro info science. Research on social media effects.',
        'calendly_link': 'https://calendly.com/leina-m'
    },
    {
        'name': 'Max Savona',
        'email': 'ms345@cornell.edu',
        'net_id': 'ms345',
        'graduating_year': 2025,
        'info_concentration': 'Networks, Crowds, and Markets',
        'career_pursuing': 'Entrepreneurship',
        'advising_topics': ['job', 'mba', 'internship'],
        'bio': 'Startup founder with experience in fintech. Raised seed funding and built a team of 10. Interested in product strategy.',
        'experiences': 'Founded two startups. Product manager at fintech company. Strong background in business development.',
        'calendly_link': 'https://calendly.com/max-s'
    }
]

MOCK_MENTEES = [
    {
        'name': 'Jessica Smith',
        'email': 'js111@cornell.edu',
        'net_id': 'js111',
        'graduating_year': 2027,
        'info_concentration': 'Data Science',
        'advising_needs': ['phd', 'job'],
        'careers_interested_in': ['Data Scientist', 'ML Engineer', 'Research Scientist'],
        'field_interests': ['data-science', 'academia-research'],
        'bio': 'Sophomore interested in machine learning and AI research. Want to pursue a PhD and work on cutting-edge ML problems.'
    },
    {
        'name': 'Michael Kim',
        'email': 'mk222@cornell.edu',
        'net_id': 'mk222',
        'graduating_year': 2026,
        'info_concentration': 'Interactive Technologies',
        'advising_needs': ['job', 'internship'],
        'careers_interested_in': ['Software Engineer', 'Full Stack Developer'],
        'field_interests': ['programming', 'it'],
        'bio': 'Junior looking for software engineering roles. Strong in Python and JavaScript. Want advice on tech interviews.'
    },
    {
        'name': 'Emma Rodriguez',
        'email': 'er333@cornell.edu',
        'net_id': 'er333',
        'graduating_year': 2027,
        'info_concentration': 'UX',
        'advising_needs': ['major', 'internship'],
        'careers_interested_in': ['UX Designer', 'Product Designer', 'UI Designer'],
        'field_interests': ['ux-ui', 'management'],
        'bio': 'Passionate about design and user experience. Building my portfolio and looking for design internships.'
    },
    {
        'name': 'David Chen',
        'email': 'dc444@cornell.edu',
        'net_id': 'dc444',
        'graduating_year': 2026,
        'info_concentration': 'Networks, Crowds, and Markets',
        'advising_needs': ['mba', 'job'],
        'careers_interested_in': ['Product Manager', 'Business Analyst', 'Consultant'],
        'field_interests': ['management', 'entrepreneurship', 'quant-finance'],
        'bio': 'Interested in the business side of tech. Considering MBA or going directly into product management.'
    },
    {
        'name': 'Sarah Johnson',
        'email': 'sj555@cornell.edu',
        'net_id': 'sj555',
        'graduating_year': 2028,
        'info_concentration': "I don't know",
        'advising_needs': ['major'],
        'careers_interested_in': ['Not sure yet'],
        'field_interests': ['not-sure'],
        'bio': 'Freshman exploring different areas of information science. Not sure what I want to do yet.'
    }
]


def seed_test_data():
    """Seed the database with test data."""
    print("\n" + "="*60)
    print("SEEDING TEST DATA")
    print("="*60)
    
    # Create mentors
    mentors = []
    for m_data in MOCK_MENTORS:
        # Check if user exists
        existing = User.query.filter_by(net_id=m_data['net_id']).first()
        if existing:
            mentor = Mentor.query.filter_by(user_id=existing.id).first()
            if mentor:
                mentors.append(mentor)
                print(f"  [EXISTS] Mentor: {m_data['name']}")
                continue
        
        user = User(
            net_id=m_data['net_id'],
            email=m_data['email'],
            name=m_data['name'],
            role='mentor'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.flush()
        
        mentor = Mentor(
            user_id=user.id,
            graduating_year=m_data['graduating_year'],
            info_concentration=m_data['info_concentration'],
            career_pursuing=m_data['career_pursuing'],
            advising_topics=json.dumps(m_data['advising_topics']),
            bio=m_data['bio'],
            experiences=m_data.get('experiences', ''),
            calendly_link=m_data['calendly_link'],
            availability_status='available'
        )
        db.session.add(mentor)
        mentors.append(mentor)
        print(f"  [CREATED] Mentor: {m_data['name']}")
    
    # Create mentees
    mentees = []
    for m_data in MOCK_MENTEES:
        existing = User.query.filter_by(net_id=m_data['net_id']).first()
        if existing:
            mentee = Mentee.query.filter_by(user_id=existing.id).first()
            if mentee:
                mentees.append(mentee)
                print(f"  [EXISTS] Mentee: {m_data['name']}")
                continue
        
        user = User(
            net_id=m_data['net_id'],
            email=m_data['email'],
            name=m_data['name'],
            role='mentee'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.flush()
        
        mentee = Mentee(
            user_id=user.id,
            graduating_year=m_data['graduating_year'],
            info_concentration=m_data['info_concentration'],
            advising_needs=json.dumps(m_data['advising_needs']),
            careers_interested_in=json.dumps(m_data['careers_interested_in']),
            field_interests=json.dumps(m_data['field_interests']),
            bio=m_data['bio']
        )
        db.session.add(mentee)
        mentees.append(mentee)
        print(f"  [CREATED] Mentee: {m_data['name']}")
    
    db.session.commit()
    print(f"\nSeeded {len(mentors)} mentors and {len(mentees)} mentees")
    
    return mentors, mentees


def test_individual_matches():
    """Test specific mentee-mentor pairs for expected behavior."""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL MATCH PAIRS")
    print("="*60)
    
    # Get all mentors and mentees
    mentors = Mentor.query.all()
    mentees = Mentee.query.all()
    
    # Create lookup by name
    mentor_by_name = {m.user.name: m for m in mentors}
    mentee_by_name = {m.user.name: m for m in mentees}
    
    test_cases = [
        {
            'mentee': 'Jessica Smith',
            'mentor': 'Hamid Rezaee',
            'expected': 'high',
            'reason': 'Both interested in Data Science, ML, PhD'
        },
        {
            'mentee': 'Michael Kim',
            'mentor': 'Andrew Lin',
            'expected': 'high',
            'reason': 'Both in SWE/Interactive Tech'
        },
        {
            'mentee': 'Emma Rodriguez',
            'mentor': 'Chelsea Ho',
            'expected': 'high',
            'reason': 'Both in UX Design'
        },
        {
            'mentee': 'David Chen',
            'mentor': 'Max Savona',
            'expected': 'high',
            'reason': 'Both interested in business/entrepreneurship'
        },
        {
            'mentee': 'Jessica Smith',
            'mentor': 'Chelsea Ho',
            'expected': 'low',
            'reason': 'Different fields (DS vs UX)'
        },
        {
            'mentee': 'Sarah Johnson',
            'mentor': 'Leina McLaughlin',
            'expected': 'moderate',
            'reason': 'Mentee exploring, mentor can help with major advice'
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        mentee = mentee_by_name.get(test['mentee'])
        mentor = mentor_by_name.get(test['mentor'])
        
        if not mentee or not mentor:
            print(f"\n  [SKIP] {test['mentee']} -> {test['mentor']}: Data not found")
            continue
        
        result = calculate_compatibility(mentee, mentor)
        score = result['score']
        
        # Determine if test passed
        if test['expected'] == 'high' and score >= 60:
            status = "[PASS]"
        elif test['expected'] == 'moderate' and 30 <= score < 60:
            status = "[PASS]"
        elif test['expected'] == 'low' and score < 40:
            status = "[PASS]"
        else:
            status = "[FAIL]"
            all_passed = False
        
        print(f"\n  {status} {test['mentee']} -> {test['mentor']}")
        print(f"      Expected: {test['expected'].upper()} | Actual Score: {score}")
        print(f"      Reason: {test['reason']}")
        print(f"      Breakdown: {result['breakdown']}")
        print(f"      Match Reasons: {result['reasons']}")
    
    return all_passed


def test_ranking():
    """Test that mentees get sensible rankings."""
    print("\n" + "="*60)
    print("TESTING MENTOR RANKINGS FOR EACH MENTEE")
    print("="*60)
    
    mentors = Mentor.query.all()
    mentees = Mentee.query.all()
    
    for mentee in mentees:
        print(f"\n  MENTEE: {mentee.user.name}")
        print(f"  Concentration: {mentee.info_concentration}")
        print(f"  Looking for: {mentee.advising_needs}")
        print(f"  Careers: {mentee.careers_interested_in}")
        print(f"  Bio: {mentee.bio[:60]}...")
        print(f"\n  TOP MATCHES:")
        
        matches = get_top_matches(mentee, mentors, limit=5)
        
        for i, match in enumerate(matches, 1):
            mentor = match['mentor']
            print(f"    {i}. {mentor.user.name}")
            print(f"       Score: {match['score']} ({match['quality']})")
            print(f"       Reasons: {', '.join(match['reasons'][:2])}")
        
        print("-" * 50)


def test_score_distribution():
    """Ensure scores are well-distributed, not all clustered."""
    print("\n" + "="*60)
    print("TESTING SCORE DISTRIBUTION")
    print("="*60)
    
    mentors = Mentor.query.all()
    mentees = Mentee.query.all()
    
    all_scores = []
    
    for mentee in mentees:
        for mentor in mentors:
            result = calculate_compatibility(mentee, mentor)
            all_scores.append(result['score'])
    
    min_score = min(all_scores)
    max_score = max(all_scores)
    avg_score = sum(all_scores) / len(all_scores)
    
    # Count distribution
    low = sum(1 for s in all_scores if s < 30)
    moderate = sum(1 for s in all_scores if 30 <= s < 60)
    high = sum(1 for s in all_scores if s >= 60)
    
    print(f"\n  Total match pairs: {len(all_scores)}")
    print(f"  Score range: {min_score:.1f} - {max_score:.1f}")
    print(f"  Average score: {avg_score:.1f}")
    print(f"\n  Distribution:")
    print(f"    Low (< 30):      {low} ({100*low/len(all_scores):.1f}%)")
    print(f"    Moderate (30-60): {moderate} ({100*moderate/len(all_scores):.1f}%)")
    print(f"    High (>= 60):     {high} ({100*high/len(all_scores):.1f}%)")
    
    # Check for good distribution
    spread = max_score - min_score
    if spread < 30:
        print("\n  [WARN] Score spread is too narrow!")
        return False
    
    if low == 0 or high == 0:
        print("\n  [WARN] Scores are too clustered!")
        return False
    
    print("\n  [PASS] Score distribution looks healthy!")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "#"*60)
    print("#  PATHMATCH MATCHING ALGORITHM TEST SUITE")
    print("#"*60)
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Seed test data
        seed_test_data()
        
        # Run tests
        results = []
        
        results.append(("Individual Matches", test_individual_matches()))
        results.append(("Score Distribution", test_score_distribution()))
        
        # This one is informational
        test_ranking()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        all_passed = True
        for name, passed in results:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n  All tests passed! ✓")
        else:
            print("\n  Some tests failed. Review output above.")
        
        return all_passed


if __name__ == '__main__':
    run_all_tests()

