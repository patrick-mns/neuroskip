import random
from celery_app.config import celery_app
from models.Segment import Segment
import requests
from core.config import settings


@celery_app.task
def classify_advertisement_content(segments_id):
    """
    Classify video segments to identify advertisement content using AI.
    
    Args:
        segments_id: List of segment IDs to classify
    
    This function processes segments sequentially, using context from previous
    segments to improve classification accuracy.
    """
    previous_segment = None
    previous_class = None
    
    for i, id in enumerate(segments_id):
        segment = Segment.get_or_none(Segment.id == id)
        
        if segment is None:
            continue
        
        payload = {
            "previousSegment": previous_segment.text if previous_segment else None,
            "previousClass": previous_class,
            "currentSegment": segment.text if segment else None,
            "nextSegment": None
        }
        previous_class = segment
        
        try:
            response = requests.post(settings.ad_ai_url, json=payload)
            response.raise_for_status()
            result = response.json()
            current_class = result.get("response")
            previous_class = current_class
            
            print("response", response)
            # current_class = random.choice(["0", "1"])  # Temporary random assignment
            # Mark segment as advertisement if classified as such
            if current_class == "1":
                if segment:
                    segment.type = "ad"
                    segment.save()

            return current_class
        except Exception as e:
            previous_class = None