from validation.schemas import ReviewerAnnotation

class HumanReviewWorkflow:
    """Hooks for researcher dashboard manual overrides."""
    
    def __init__(self):
        self.annotations = []
        
    def submit_review(self, annotation: ReviewerAnnotation):
        self.annotations.append(annotation)
        # TODO: Update Supabase report status
