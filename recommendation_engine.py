
import numpy as np
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

class RecommendationEngine:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
        self.db = self.client["citizen_portal"]
        self.users_col = self.db["users"]
        self.eng_col = self.db["engagements"]
        self.ads_col = self.db["ads"]

    def get_user_segment(self, user_id):
        """Segment users based on demographics and behavior"""
        if not user_id:
            return "unknown"
        try:
            user = self.users_col.find_one({"_id": ObjectId(user_id)})
        except:
             return "unknown"
            
        if not user:
            return "unknown"
        
        profile = user.get('extended_profile', {})
        engagements = list(self.eng_col.find({"user_id": user_id}).sort("timestamp", -1).limit(50))
        
        # Demographic segmentation
        age = profile.get('family', {}).get('age') or user.get('profile', {}).get('basic', {}).get('age')
        education = profile.get('education', {}).get('highest_qualification', 'unknown')
        children = profile.get('family', {}).get('children', [])
        job = profile.get('career', {}).get('current_job', 'unknown')
        
        segment = []
        
        # Age-based segments
        if age:
            if age < 25:
                segment.append("young_adult")
            elif 25 <= age <= 35:
                segment.append("early_career")
            elif 36 <= age <= 45:
                segment.append("mid_career_family")
            elif 46 <= age <= 60:
                segment.append("established_professional")
            else:
                segment.append("senior")
        
        # Education-based segments
        if education in ['none', 'school', 'ol']:
            segment.append("needs_qualification")
        elif education in ['al', 'diploma']:
            segment.append("mid_education")
        elif education in ['degree', 'masters', 'phd']:
            segment.append("highly_educated")
            
        # Family-based segments
        if children:
            segment.append("parent")
            children_ages = profile.get('family', {}).get('children_ages', [])
            if any(age in [5, 6, 7, 8, 9, 10] for age in children_ages):
                segment.append("primary_school_parent")
            if any(age in [11, 12, 13, 14, 15, 16] for age in children_ages):
                segment.append("secondary_school_parent")
            if any(age in [17, 18, 19, 20] for age in children_ages):
                segment.append("university_age_parent")
                
        # Career-based segments
        job_lower = job.lower()
        if 'government' in job_lower:
            segment.append("government_employee")
        if any(word in job_lower for word in ['manager', 'director', 'head']):
            segment.append("management")
        if 'student' in job_lower or 'undergraduate' in job_lower:
            segment.append("student")
        if 'teacher' in job_lower or 'lecturer' in job_lower or 'professor' in job_lower:
            segment.append("teacher")
            
        return list(set(segment))

    def get_personalized_ads(self, user_id, limit=5):
        """Get personalized ads based on user segment and behavior"""
        if not user_id:
             return []
        
        segments = self.get_user_segment(user_id)
        user_engagements = list(self.eng_col.find({"user_id": user_id}))
        
        # Extract interests from engagements
        interests = []
        for eng in user_engagements:
            interests.extend(eng.get('desires', []))
            if eng.get('question_clicked'):
                interests.append(eng['question_clicked'])
            if eng.get('service'):
                interests.append(eng['service'])
                
        # Score ads based on relevance
        ads = list(self.ads_col.find({"active": True}))
        scored_ads = []
        
        for ad in ads:
            score = 0
            ad_tags = ad.get('tags', [])
            ad_segments = ad.get('target_segments', [])
            
            # Segment matching
            segment_match = len(set(segments) & set(ad_segments))
            score += segment_match * 10
            
            # Interest matching
            interest_match = len(set(interests) & set(ad_tags))
            score += interest_match * 5
            
            # Recency boost
            if ad.get('created'):
                # Handle simplified date format if needed
                if isinstance(ad['created'], str):
                     try:
                        created_dt = datetime.fromisoformat(ad['created'])
                        days_old = (datetime.utcnow() - created_dt).days
                     except:
                        days_old = 100
                else:
                    days_old = (datetime.utcnow() - ad['created']).days
                    
                if days_old < 7:
                    score += 5
                elif days_old < 30:
                    score += 2
            
            scored_ads.append((ad, score))
            
        # Sort by score and return top ones
        scored_ads.sort(key=lambda x: x[1], reverse=True)
        # Convert ObjectId to str for JSON serialization
        results = []
        for ad, score in scored_ads[:limit]:
            ad["_id"] = str(ad["_id"])
            results.append(ad)
        return results

    def generate_education_recommendations(self, user_id):
        """Generate education recommendations based on profile"""
        if not user_id:
             return []
        try:
             user = self.users_col.find_one({"_id": ObjectId(user_id)})
        except:
             return []

        if not user:
            return []
        
        profile = user.get('extended_profile', {})
        education = profile.get('education', {})
        career = profile.get('career', {})
        age = profile.get('family', {}).get('age')
        
        recommendations = []
        
        # Degree completion for government employees without degrees
        if (education.get('highest_qualification') in ['ol', 'al', 'diploma'] and 
            'government' in career.get('current_job', '').lower() and 
            age and 25 <= age <= 50):
            recommendations.append({
                "type": "education",
                "title": "Complete Your Degree",
                "message": "Enhance your career with a recognized degree program",
                "priority": "high",
                "tags": ["degree", "government", "career_advancement"]
            })
            
        # Children education recommendations
        children_ages = profile.get('family', {}).get('children_ages', [])
        children_education = profile.get('family', {}).get('children_education', [])
        
        for i, age in enumerate(children_ages):
            current_edu = children_education[i].lower() if i < len(children_education) else ""
            
            if 15 <= age <= 18 and 'ol' not in current_edu:
                recommendations.append({
                    "type": "child_education",
                    "title": "O/L Exam Preparation",
                    "message": "Special courses for your child's O/L exams",
                    "priority": "medium",
                    "tags": ["ol_exams", "tuition", "secondary_education"]
                })
                
            if 17 <= age <= 20 and 'al' not in current_edu:
                recommendations.append({
                    "type": "child_education",
                    "title": "A/L Stream Selection Guidance",
                    "message": "Expert guidance for A/L subject selection",
                    "priority": "medium",
                    "tags": ["al_exams", "career_guidance", "higher_education"]
                })
                
        return recommendations
