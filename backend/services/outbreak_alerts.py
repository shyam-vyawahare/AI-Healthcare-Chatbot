# backend/services/outbreak_alerts.py
import json
import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)

class OutbreakAlertSystem:
    """System for monitoring and alerting about disease outbreaks"""
    
    def __init__(self):
        self.alerts = []
        self.subscribers = {}
        self.api_url = settings.OUTBREAK_API_URL
        
    async def fetch_outbreak_data(self) -> List[Dict[str, Any]]:
        """Fetch current outbreak data from various sources"""
        outbreaks = []
        
        try:
            # Fetch COVID-19 data
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/countries",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    covid_data = response.json()
                    for country_data in covid_data[:10]:  # Top 10 countries
                        if country_data.get("cases", 0) > 1000:
                            outbreaks.append({
                                "disease": "COVID-19",
                                "location": country_data.get("country", "Unknown"),
                                "cases": country_data.get("cases", 0),
                                "deaths": country_data.get("deaths", 0),
                                "recovered": country_data.get("recovered", 0),
                                "severity": self._calculate_severity(country_data.get("cases", 0)),
                                "timestamp": datetime.now().isoformat(),
                                "prevention": "Wear masks, maintain social distance, get vaccinated"
                            })
            
            # Load local outbreak data from JSON
            try:
                with open("data/outbreaks.json", "r", encoding="utf-8") as f:
                    local_outbreaks = json.load(f)
                    outbreaks.extend(local_outbreaks.get("active_outbreaks", []))
            except FileNotFoundError:
                logger.warning("outbreaks.json not found")
            
        except Exception as e:
            logger.error(f"Error fetching outbreak data: {str(e)}")
            
            # Fallback to local data
            outbreaks = self._get_local_outbreaks()
        
        return outbreaks
    
    def _get_local_outbreaks(self) -> List[Dict[str, Any]]:
        """Get local outbreak data as fallback"""
        return [
            {
                "disease": "Dengue",
                "location": "Multiple districts",
                "cases": 500,
                "severity": "moderate",
                "prevention": "Use mosquito nets, remove stagnant water",
                "symptoms": "High fever, severe headache, joint pain"
            },
            {
                "disease": "Seasonal Flu",
                "location": "Statewide",
                "cases": 1200,
                "severity": "mild",
                "prevention": "Get flu shot, wash hands regularly",
                "symptoms": "Fever, cough, body aches"
            }
        ]
    
    def _calculate_severity(self, cases: int) -> str:
        """Calculate outbreak severity based on case count"""
        if cases < 1000:
            return "mild"
        elif cases < 10000:
            return "moderate"
        elif cases < 100000:
            return "severe"
        else:
            return "critical"
    
    def check_active_alerts(self) -> List[Dict[str, Any]]:
        """Check for active outbreak alerts"""
        active_alerts = []
        
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            if datetime.now() - alert_time < timedelta(days=7):  # Active for 7 days
                active_alerts.append(alert)
        
        return active_alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all currently active alerts"""
        return self.check_active_alerts()
    
    async def create_alert(self, outbreak_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new outbreak alert"""
        alert = {
            "alert_id": f"alert_{len(self.alerts) + 1}",
            "title": f"{outbreak_data.get('disease', 'Disease')} Outbreak Alert",
            "description": f"An outbreak of {outbreak_data.get('disease', 'disease')} has been reported in {outbreak_data.get('location', 'your area')}.",
            "severity": outbreak_data.get("severity", "moderate"),
            "prevention_measures": outbreak_data.get("prevention", "Follow health guidelines"),
            "symptoms": outbreak_data.get("symptoms", "Check with health authorities"),
            "location": outbreak_data.get("location", "Unknown"),
            "cases": outbreak_data.get("cases", 0),
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.alerts.append(alert)
        logger.info(f"Created outbreak alert: {alert['title']}")
        
        # Notify subscribers
        await self._notify_subscribers(alert)
        
        return alert
    
    async def _notify_subscribers(self, alert: Dict[str, Any]):
        """Notify subscribers about new alert"""
        for phone, preferences in self.subscribers.items():
            if preferences.get("alert_types", ["all"]) in ["all", "outbreak"]:
                # In production, send actual notification via WhatsApp/SMS
                logger.info(f"Notifying {phone} about outbreak: {alert['title']}")
    
    def subscribe(self, phone: str, preferences: Optional[Dict] = None):
        """Subscribe user to outbreak alerts"""
        self.subscribers[phone] = preferences or {
            "alert_types": ["all"],
            "location": "all",
            "language": "en"
        }
        logger.info(f"User {phone} subscribed to outbreak alerts")
    
    def unsubscribe(self, phone: str):
        """Unsubscribe user from outbreak alerts"""
        if phone in self.subscribers:
            del self.subscribers[phone]
            logger.info(f"User {phone} unsubscribed from outbreak alerts")
    
    def get_alert_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Get alerts specific to a location"""
        return [alert for alert in self.alerts 
                if location.lower() in alert.get("location", "").lower()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get outbreak statistics"""
        active_alerts = self.check_active_alerts()
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "subscribers": len(self.subscribers),
            "severity_breakdown": self._get_severity_breakdown(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown of alerts by severity"""
        breakdown = {"mild": 0, "moderate": 0, "severe": 0, "critical": 0}
        
        for alert in self.alerts:
            severity = alert.get("severity", "mild")
            if severity in breakdown:
                breakdown[severity] += 1
        
        return breakdown