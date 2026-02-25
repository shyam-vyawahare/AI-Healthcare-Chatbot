# backend/routes/analytics.py
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import sqlite3
from collections import Counter, defaultdict

from config import settings
from utils.logger import setup_logger
from db.models import get_db_connection
from utils.helpers import validate_date_range, format_timestamp

# Initialize router
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize logger
logger = setup_logger(__name__)

class AnalyticsEngine:
    """Analytics engine for processing and aggregating data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_dashboard_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get dashboard summary analytics"""
        try:
            cache_key = f"dashboard_summary_{days}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_ttl:
                    return cached_data
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Total queries
            cursor.execute('''
                SELECT COUNT(*) FROM interactions 
                WHERE sender = 'user' AND timestamp >= ?
            ''', (start_date,))
            total_queries = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute('''
                SELECT COUNT(DISTINCT phone) FROM interactions 
                WHERE timestamp >= ?
            ''', (start_date,))
            unique_users = cursor.fetchone()[0]
            
            # Active users (users with interactions in last 7 days)
            cursor.execute('''
                SELECT COUNT(DISTINCT phone) FROM interactions 
                WHERE timestamp >= ?
            ''', (end_date - timedelta(days=7),))
            active_users = cursor.fetchone()[0]
            
            # Successful responses (queries with bot responses)
            cursor.execute('''
                SELECT COUNT(DISTINCT i1.id) FROM interactions i1
                JOIN interactions i2 ON i1.phone = i2.phone AND i2.sender = 'bot'
                WHERE i1.sender = 'user' AND i1.timestamp >= ?
            ''', (start_date,))
            successful_responses = cursor.fetchone()[0]
            
            # Response rate
            response_rate = (successful_responses / total_queries * 100) if total_queries > 0 else 0
            
            # Language distribution
            cursor.execute('''
                SELECT language, COUNT(*) as count FROM language_stats 
                WHERE last_updated >= ?
                GROUP BY language ORDER BY count DESC
            ''', (start_date,))
            language_stats = cursor.fetchall()
            
            # Top intents
            cursor.execute('''
                SELECT intent, COUNT(*) as count FROM intent_stats 
                WHERE last_updated >= ?
                GROUP BY intent ORDER BY count DESC LIMIT 10
            ''', (start_date,))
            intent_stats = cursor.fetchall()
            
            # Recent activity
            cursor.execute('''
                SELECT phone, last_active, query_count FROM user_activity 
                ORDER BY last_active DESC LIMIT 10
            ''')
            recent_activity = cursor.fetchall()
            
            # Channel distribution
            cursor.execute('''
                SELECT channel, COUNT(*) as count FROM interactions 
                WHERE timestamp >= ? GROUP BY channel
            ''', (start_date,))
            channel_stats = cursor.fetchall()
            
            conn.close()
            
            summary = {
                "total_queries": total_queries,
                "unique_users": unique_users,
                "active_users": active_users,
                "successful_responses": successful_responses,
                "response_rate": round(response_rate, 2),
                "language_distribution": [
                    {"language": lang, "count": count, "percentage": round((count / total_queries * 100), 2) if total_queries > 0 else 0}
                    for lang, count in language_stats
                ],
                "top_intents": [
                    {"intent": intent, "count": count, "percentage": round((count / total_queries * 100), 2) if total_queries > 0 else 0}
                    for intent, count in intent_stats
                ],
                "recent_activity": [
                    {
                        "phone": phone[:4] + "****" + phone[-3:] if len(phone) > 7 else phone,  # Anonymize
                        "last_active": format_timestamp(last_active),
                        "query_count": count
                    }
                    for phone, last_active, count in recent_activity
                ],
                "channel_distribution": [
                    {"channel": channel, "count": count}
                    for channel, count in channel_stats
                ],
                "period": f"last_{days}_days",
                "from_date": start_date.isoformat(),
                "to_date": end_date.isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = (summary, datetime.now())
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {str(e)}")
            raise
    
    async def get_query_metrics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get query metrics for a date range"""
        try:
            # Validate date range
            start_dt, end_dt = validate_date_range(start_date, end_date)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Daily query count
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count 
                FROM interactions 
                WHERE sender = 'user' AND timestamp BETWEEN ? AND ?
                GROUP BY DATE(timestamp) 
                ORDER BY date
            ''', (start_dt, end_dt))
            daily_queries = cursor.fetchall()
            
            # Hourly distribution
            cursor.execute('''
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count 
                FROM interactions 
                WHERE sender = 'user' AND timestamp BETWEEN ? AND ?
                GROUP BY hour 
                ORDER BY hour
            ''', (start_dt, end_dt))
            hourly_distribution = cursor.fetchall()
            
            # Query length analysis
            cursor.execute('''
                SELECT 
                    AVG(LENGTH(message)) as avg_length,
                    MAX(LENGTH(message)) as max_length,
                    MIN(LENGTH(message)) as min_length
                FROM interactions 
                WHERE sender = 'user' AND timestamp BETWEEN ? AND ?
            ''', (start_dt, end_dt))
            length_stats = cursor.fetchone()
            
            # Response time analysis (approximate)
            cursor.execute('''
                SELECT 
                    AVG((julianday(b.timestamp) - julianday(u.timestamp)) * 86400) as avg_response_time,
                    MAX((julianday(b.timestamp) - julianday(u.timestamp)) * 86400) as max_response_time
                FROM interactions u
                JOIN interactions b ON u.phone = b.phone AND b.sender = 'bot'
                WHERE u.sender = 'user' 
                AND u.timestamp BETWEEN ? AND ?
                AND b.timestamp > u.timestamp
            ''', (start_dt, end_dt))
            response_time_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                "daily_queries": [
                    {"date": date, "count": count}
                    for date, count in daily_queries
                ],
                "hourly_distribution": [
                    {"hour": int(hour), "count": count}
                    for hour, count in hourly_distribution
                ],
                "query_length": {
                    "average": round(length_stats[0] or 0, 2),
                    "maximum": length_stats[1] or 0,
                    "minimum": length_stats[2] or 0
                },
                "response_time": {
                    "average_seconds": round(response_time_stats[0] or 0, 2),
                    "maximum_seconds": round(response_time_stats[1] or 0, 2)
                },
                "date_range": {
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting query metrics: {str(e)}")
            raise
    
    async def get_user_analytics(self, user_type: str = "all", limit: int = 100) -> Dict[str, Any]:
        """Get user analytics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if user_type == "active":
                # Most active users
                cursor.execute('''
                    SELECT phone, query_count, last_active 
                    FROM user_activity 
                    ORDER BY query_count DESC 
                    LIMIT ?
                ''', (limit,))
            elif user_type == "recent":
                # Recently active users
                cursor.execute('''
                    SELECT phone, query_count, last_active 
                    FROM user_activity 
                    ORDER BY last_active DESC 
                    LIMIT ?
                ''', (limit,))
            else:
                # All users with pagination
                cursor.execute('''
                    SELECT phone, query_count, last_active 
                    FROM user_activity 
                    ORDER BY last_active DESC 
                    LIMIT ?
                ''', (limit,))
            
            users = cursor.fetchall()
            
            # User engagement stats
            cursor.execute('''
                SELECT 
                    AVG(query_count) as avg_queries_per_user,
                    MAX(query_count) as max_queries_per_user,
                    COUNT(*) as total_users
                FROM user_activity
            ''')
            engagement_stats = cursor.fetchone()
            
            # User retention (users active in consecutive weeks)
            cursor.execute('''
                WITH weekly_activity AS (
                    SELECT 
                        phone,
                        strftime('%Y-%W', timestamp) as week
                    FROM interactions 
                    WHERE timestamp >= ?
                    GROUP BY phone, week
                ),
                consecutive_weeks AS (
                    SELECT 
                        phone,
                        COUNT(DISTINCT week) as active_weeks
                    FROM weekly_activity
                    GROUP BY phone
                )
                SELECT 
                    active_weeks,
                    COUNT(*) as user_count
                FROM consecutive_weeks
                GROUP BY active_weeks
                ORDER BY active_weeks
            ''', (datetime.now() - timedelta(days=30),))
            retention_data = cursor.fetchall()
            
            conn.close()
            
            return {
                "users": [
                    {
                        "phone": phone[:4] + "****" + phone[-3:] if len(phone) > 7 else phone,
                        "query_count": count,
                        "last_active": format_timestamp(last_active),
                        "engagement_level": self._get_engagement_level(count)
                    }
                    for phone, count, last_active in users
                ],
                "engagement_stats": {
                    "average_queries_per_user": round(engagement_stats[0] or 0, 2),
                    "maximum_queries_per_user": engagement_stats[1] or 0,
                    "total_users": engagement_stats[2] or 0
                },
                "retention_analysis": [
                    {"active_weeks": weeks, "user_count": count}
                    for weeks, count in retention_data
                ],
                "user_type": user_type,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            raise
    
    async def get_language_analytics(self) -> Dict[str, Any]:
        """Get language usage analytics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Language distribution over time (last 30 days)
            cursor.execute('''
                SELECT 
                    language,
                    DATE(last_updated) as date,
                    SUM(query_count) as daily_count
                FROM language_stats 
                WHERE last_updated >= ?
                GROUP BY language, DATE(last_updated)
                ORDER BY date, language
            ''', (datetime.now() - timedelta(days=30),))
            language_trends = cursor.fetchall()
            
            # Current language distribution
            cursor.execute('''
                SELECT language, SUM(query_count) as total_count
                FROM language_stats 
                GROUP BY language 
                ORDER BY total_count DESC
            ''')
            current_distribution = cursor.fetchall()
            
            # Language by intent
            cursor.execute('''
                SELECT 
                    i.intent,
                    l.language,
                    COUNT(*) as count
                FROM interactions i
                JOIN language_stats l ON i.phone = l.language
                WHERE i.sender = 'user'
                GROUP BY i.intent, l.language
                ORDER BY i.intent, count DESC
            ''')
            language_intent_data = cursor.fetchall()
            
            conn.close()
            
            # Process language trends
            trends = defaultdict(list)
            for lang, date, count in language_trends:
                trends[lang].append({"date": date, "count": count})
            
            return {
                "current_distribution": [
                    {"language": lang, "count": count, "percentage": 0}  # Will calculate below
                    for lang, count in current_distribution
                ],
                "language_trends": [
                    {"language": lang, "trend": trend_data}
                    for lang, trend_data in trends.items()
                ],
                "language_by_intent": [
                    {"intent": intent, "language": lang, "count": count}
                    for intent, lang, count in language_intent_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting language analytics: {str(e)}")
            raise
    
    async def get_intent_analytics(self, top_n: int = 15) -> Dict[str, Any]:
        """Get intent analysis"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Top intents
            cursor.execute('''
                SELECT intent, SUM(query_count) as total_count
                FROM intent_stats 
                GROUP BY intent 
                ORDER BY total_count DESC
                LIMIT ?
            ''', (top_n,))
            top_intents = cursor.fetchall()
            
            # Intent trends (last 30 days)
            cursor.execute('''
                SELECT 
                    intent,
                    DATE(last_updated) as date,
                    SUM(query_count) as daily_count
                FROM intent_stats 
                WHERE last_updated >= ?
                GROUP BY intent, DATE(last_updated)
                ORDER BY date, intent
            ''', (datetime.now() - timedelta(days=30),))
            intent_trends = cursor.fetchall()
            
            # Intent success rate (approximate)
            cursor.execute('''
                SELECT 
                    i.intent,
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN r.message IS NOT NULL THEN 1 ELSE 0 END) as successful_responses
                FROM interactions i
                LEFT JOIN interactions r ON i.phone = r.phone AND r.sender = 'bot'
                WHERE i.sender = 'user'
                GROUP BY i.intent
            ''')
            intent_success = cursor.fetchall()
            
            # Intent by language
            cursor.execute('''
                SELECT 
                    i.intent,
                    l.language,
                    COUNT(*) as count
                FROM interactions i
                JOIN language_stats l ON i.phone = l.language
                WHERE i.sender = 'user'
                GROUP BY i.intent, l.language
                ORDER BY i.intent, count DESC
            ''')
            intent_language_data = cursor.fetchall()
            
            conn.close()
            
            # Process intent trends
            trends = defaultdict(list)
            for intent, date, count in intent_trends:
                trends[intent].append({"date": date, "count": count})
            
            # Calculate success rates
            success_rates = {}
            for intent, total, successful in intent_success:
                success_rate = (successful / total * 100) if total > 0 else 0
                success_rates[intent] = round(success_rate, 2)
            
            return {
                "top_intents": [
                    {
                        "intent": intent,
                        "count": count,
                        "success_rate": success_rates.get(intent, 0)
                    }
                    for intent, count in top_intents
                ],
                "intent_trends": [
                    {"intent": intent, "trend": trend_data}
                    for intent, trend_data in trends.items()
                ],
                "intent_by_language": [
                    {"intent": intent, "language": lang, "count": count}
                    for intent, lang, count in intent_language_data
                ],
                "total_intents_tracked": len(top_intents)
            }
            
        except Exception as e:
            logger.error(f"Error getting intent analytics: {str(e)}")
            raise
    
    async def get_geographic_analytics(self) -> Dict[str, Any]:
        """Get geographic distribution analytics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # User locations
            cursor.execute('''
                SELECT 
                    address,
                    COUNT(*) as user_count
                FROM user_locations 
                GROUP BY address
                ORDER BY user_count DESC
                LIMIT 50
            ''')
            location_data = cursor.fetchall()
            
            # State-wise distribution (approximate from address)
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN address LIKE '%Delhi%' THEN 'Delhi'
                        WHEN address LIKE '%Mumbai%' THEN 'Maharashtra'
                        WHEN address LIKE '%Chennai%' THEN 'Tamil Nadu'
                        WHEN address LIKE '%Bangalore%' THEN 'Karnataka'
                        WHEN address LIKE '%Kolkata%' THEN 'West Bengal'
                        WHEN address LIKE '%Hyderabad%' THEN 'Telangana'
                        WHEN address LIKE '%Pune%' THEN 'Maharashtra'
                        WHEN address LIKE '%Ahmedabad%' THEN 'Gujarat'
                        ELSE 'Other'
                    END as state,
                    COUNT(*) as user_count
                FROM user_locations 
                GROUP BY state
                ORDER BY user_count DESC
            ''')
            state_distribution = cursor.fetchall()
            
            # Urban vs Rural distribution (approximate)
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN address LIKE '%city%' OR address LIKE '%metro%' OR address IN ('Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad') THEN 'Urban'
                        WHEN address LIKE '%village%' OR address LIKE '%rural%' THEN 'Rural'
                        ELSE 'Unknown'
                    END as area_type,
                    COUNT(*) as user_count
                FROM user_locations 
                GROUP BY area_type
            ''')
            area_distribution = cursor.fetchall()
            
            conn.close()
            
            return {
                "top_locations": [
                    {"location": location, "user_count": count}
                    for location, count in location_data
                ],
                "state_distribution": [
                    {"state": state, "user_count": count}
                    for state, count in state_distribution
                ],
                "area_distribution": [
                    {"area_type": area_type, "user_count": count}
                    for area_type, count in area_distribution
                ],
                "total_locations_tracked": len(location_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting geographic analytics: {str(e)}")
            raise
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Response time percentiles
            cursor.execute('''
                SELECT 
                    AVG((julianday(b.timestamp) - julianday(u.timestamp)) * 86400) as avg_response_time,
                    MAX((julianday(b.timestamp) - julianday(u.timestamp)) * 86400) as max_response_time,
                    MIN((julianday(b.timestamp) - julianday(u.timestamp)) * 86400) as min_response_time
                FROM interactions u
                JOIN interactions b ON u.phone = b.phone AND b.sender = 'bot'
                WHERE u.sender = 'user' 
                AND u.timestamp >= ?
            ''', (datetime.now() - timedelta(days=7),))
            response_times = cursor.fetchone()
            
            # Error rates
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN metadata LIKE '%error%' THEN 1 ELSE 0 END) as error_queries
                FROM interactions 
                WHERE sender = 'bot' AND timestamp >= ?
            ''', (datetime.now() - timedelta(days=7),))
            error_stats = cursor.fetchone()
            
            # NLP confidence distribution
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN json_extract(metadata, '$.confidence') < 0.5 THEN 'Low (<0.5)'
                        WHEN json_extract(metadata, '$.confidence') < 0.8 THEN 'Medium (0.5-0.8)'
                        ELSE 'High (>0.8)'
                    END as confidence_level,
                    COUNT(*) as count
                FROM interactions 
                WHERE sender = 'bot' AND metadata IS NOT NULL
                GROUP BY confidence_level
            ''')
            confidence_distribution = cursor.fetchall()
            
            # Service availability (approximate)
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_hours,
                    SUM(CASE WHEN error_count = 0 THEN 1 ELSE 0 END) as available_hours
                FROM (
                    SELECT 
                        strftime('%Y-%m-%d %H', timestamp) as hour,
                        COUNT(CASE WHEN metadata LIKE '%error%' THEN 1 END) as error_count
                    FROM interactions 
                    WHERE timestamp >= ?
                    GROUP BY hour
                )
            ''', (datetime.now() - timedelta(days=7),))
            availability_stats = cursor.fetchone()
            
            conn.close()
            
            total_queries = error_stats[0] or 1
            error_queries = error_stats[1] or 0
            error_rate = (error_queries / total_queries * 100) if total_queries > 0 else 0
            
            total_hours = availability_stats[0] or 1
            available_hours = availability_stats[1] or 0
            availability_rate = (available_hours / total_hours * 100) if total_hours > 0 else 0
            
            return {
                "response_times": {
                    "average_seconds": round(response_times[0] or 0, 2),
                    "maximum_seconds": round(response_times[1] or 0, 2),
                    "minimum_seconds": round(response_times[2] or 0, 2)
                },
                "error_metrics": {
                    "total_queries": total_queries,
                    "error_queries": error_queries,
                    "error_rate": round(error_rate, 2)
                },
                "confidence_distribution": [
                    {"confidence_level": level, "count": count}
                    for level, count in confidence_distribution
                ],
                "availability": {
                    "available_hours": available_hours,
                    "total_hours": total_hours,
                    "availability_rate": round(availability_rate, 2)
                },
                "performance_score": self._calculate_performance_score(
                    response_times[0] or 0, 
                    error_rate, 
                    availability_rate
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            raise
    
    async def get_outbreak_analytics(self) -> Dict[str, Any]:
        """Get outbreak-related analytics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Outbreak query trends
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as outbreak_queries
                FROM interactions 
                WHERE sender = 'user' 
                AND (message LIKE '%outbreak%' OR message LIKE '%alert%' OR message LIKE '%disease%')
                AND timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (datetime.now() - timedelta(days=30),))
            outbreak_trends = cursor.fetchall()
            
            # Top disease queries
            cursor.execute('''
                SELECT 
                    message,
                    COUNT(*) as query_count
                FROM interactions 
                WHERE sender = 'user' 
                AND (message LIKE '%fever%' OR message LIKE '%covid%' OR message LIKE '%malaria%' 
                     OR message LIKE '%dengue%' OR message LIKE '%cholera%')
                GROUP BY message
                ORDER BY query_count DESC
                LIMIT 10
            ''')
            disease_queries = cursor.fetchall()
            
            # Location-based outbreak interest
            cursor.execute('''
                SELECT 
                    ul.address,
                    COUNT(*) as outbreak_queries
                FROM interactions i
                JOIN user_locations ul ON i.phone = ul.phone
                WHERE i.sender = 'user' 
                AND (i.message LIKE '%outbreak%' OR i.message LIKE '%alert%')
                GROUP BY ul.address
                ORDER BY outbreak_queries DESC
                LIMIT 15
            ''')
            location_interest = cursor.fetchall()
            
            conn.close()
            
            return {
                "outbreak_trends": [
                    {"date": date, "query_count": count}
                    for date, count in outbreak_trends
                ],
                "top_disease_queries": [
                    {"disease": self._extract_disease_name(message), "query_count": count}
                    for message, count in disease_queries
                ],
                "location_interest": [
                    {"location": location, "outbreak_queries": count}
                    for location, count in location_interest
                ],
                "total_outbreak_queries": sum(count for _, count in outbreak_trends)
            }
            
        except Exception as e:
            logger.error(f"Error getting outbreak analytics: {str(e)}")
            raise
    
    def _get_engagement_level(self, query_count: int) -> str:
        """Determine user engagement level"""
        if query_count >= 20:
            return "high"
        elif query_count >= 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_performance_score(self, avg_response_time: float, error_rate: float, availability_rate: float) -> float:
        """Calculate overall performance score"""
        # Normalize metrics (lower is better for response time and error rate)
        response_score = max(0, 100 - (avg_response_time * 10))  # Deduct 10 points per second
        error_score = max(0, 100 - error_rate)  # Deduct 1 point per % error
        availability_score = availability_rate  # Direct percentage
        
        # Weighted average
        return round((response_score * 0.3 + error_score * 0.4 + availability_score * 0.3), 2)
    
    def _extract_disease_name(self, message: str) -> str:
        """Extract disease name from query message"""
        diseases = ['covid', 'malaria', 'dengue', 'cholera', 'fever', 'flu', 'tuberculosis', 'typhoid']
        message_lower = message.lower()
        for disease in diseases:
            if disease in message_lower:
                return disease.capitalize()
        return "Other"

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

# Analytics endpoints
@router.get("/dashboard")
async def get_dashboard_analytics(days: int = Query(30, ge=1, le=365)):
    """Get comprehensive dashboard analytics"""
    try:
        summary = await analytics_engine.get_dashboard_summary(days)
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in dashboard analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard analytics")

@router.get("/queries")
async def get_query_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get query analytics for date range"""
    try:
        metrics = await analytics_engine.get_query_metrics(start_date, end_date)
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in query analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch query analytics")

@router.get("/users")
async def get_user_analytics(
    user_type: str = Query("all", regex="^(all|active|recent)$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get user analytics"""
    try:
        analytics = await analytics_engine.get_user_analytics(user_type, limit)
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user analytics")

@router.get("/languages")
async def get_language_analytics():
    """Get language analytics"""
    try:
        analytics = await analytics_engine.get_language_analytics()
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in language analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch language analytics")

@router.get("/intents")
async def get_intent_analytics(top_n: int = Query(15, ge=5, le=50)):
    """Get intent analytics"""
    try:
        analytics = await analytics_engine.get_intent_analytics(top_n)
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in intent analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch intent analytics")

@router.get("/geographic")
async def get_geographic_analytics():
    """Get geographic analytics"""
    try:
        analytics = await analytics_engine.get_geographic_analytics()
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in geographic analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch geographic analytics")

@router.get("/performance")
async def get_performance_analytics():
    """Get performance metrics"""
    try:
        metrics = await analytics_engine.get_performance_metrics()
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in performance analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance analytics")

@router.get("/outbreaks")
async def get_outbreak_analytics():
    """Get outbreak-related analytics"""
    try:
        analytics = await analytics_engine.get_outbreak_analytics()
        return {
            "status": "success",
            "data": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in outbreak analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch outbreak analytics")

@router.get("/export")
async def export_analytics(
    data_type: str = Query(..., regex="^(users|queries|intents|languages)$"),
    format: str = Query("json", regex="^(json|csv)$")
):
    """Export analytics data"""
    try:
        # This would generate and return a file in practice
        # For now, return a placeholder response
        return {
            "status": "success",
            "message": f"Export for {data_type} in {format} format would be generated here",
            "export_url": f"/exports/{data_type}_{datetime.now().strftime('%Y%m%d')}.{format}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export analytics")

# Health check for analytics service
@router.get("/health")
async def analytics_health():
    """Analytics service health check"""
    try:
        # Test database connection and basic analytics
        test_summary = await analytics_engine.get_dashboard_summary(1)
        
        return {
            "status": "healthy",
            "service": "analytics",
            "timestamp": datetime.now().isoformat(),
            "data_available": test_summary["total_queries"] > 0
        }
    except Exception as e:
        logger.error(f"Analytics health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }