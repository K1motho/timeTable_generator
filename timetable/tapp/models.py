from django.db import models

# Create your models here.
class Unit(models.Model):
    name =  models.CharField( max_length=255)
    difficulty = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return f"{self.name} (D={self.difficulty})"
    
class Availability(models.Model):
    DAY_CHOICES= {
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    }
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    hours_available = models.PositiveIntegerField(help_text="Hours available on this day")
    
    def __str__(self):
        return f"{self.get_day_display()} - {self.hours_available}hrs"