from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# ----Review Model-----------------------------------------
class Review(models.Model):
    display_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Rating must be at least 1"),
            MaxValueValidator(5, message="Rating cannot be more than 5")
        ]
    )
    comment = models.TextField()
    profile = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name} - {self.rating} Stars"

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['rating']),
        ]

# --- Our Results Model-----------------------------------------
class OurResults(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'our_results'
        ordering = ['-created_at']

class OurResultImages(models.Model):
    result = models.ForeignKey(OurResults, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='our_results/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.result.title}"
    
    class Meta:
        db_table = 'our_result_images'
        ordering = ['-created_at']

# --- Request Quote Model-----------------------------------------
class RequestQuote(models.Model):
    name          = models.CharField(max_length=255)
    profession    = models.CharField(max_length=255)
    email         = models.EmailField()
    business_name = models.CharField(max_length=255)
    location      = models.CharField(max_length=1000)
    phone         = models.CharField(max_length=1000)
    description   = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name          = "Request Quote"
        verbose_name_plural   = "Request Quotes"
        ordering              = ['-created_at']

