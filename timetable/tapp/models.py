from django.db import models

class Unit(models.Model):
    name = models.CharField(max_length=255)
    difficulty = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return f"{self.name} (D={self.difficulty})"


class Availability(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)

    def __str__(self):
        return self.get_day_display()


class AvailabilityBlock(models.Model):
    BLOCK_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]
    availability = models.ForeignKey(Availability, related_name="blocks", on_delete=models.CASCADE)
    block = models.CharField(max_length=10, choices=BLOCK_CHOICES)
    hours = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.availability.get_day_display()} {self.block} - {self.hours} hrs"
