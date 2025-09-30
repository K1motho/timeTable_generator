from django.db import models


class Timetable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # Store timetable result as JSON (works with PostgreSQL JSONField)
    data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Timetable {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Unit(models.Model):
    timetable = models.ForeignKey(
        Timetable, related_name="units", on_delete=models.CASCADE,
        null=True, blank=True   # 👈 allow units without timetable
    )
    name = models.CharField(max_length=255)
    difficulty = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return f"{self.name} (D={self.difficulty})"


class Availability(models.Model):
    timetable = models.ForeignKey(
        Timetable, related_name="availability", on_delete=models.CASCADE
    )

    DAY_CHOICES = [
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)

    def __str__(self):
        return self.get_day_display()


class AvailabilityBlock(models.Model):
    availability = models.ForeignKey(
        Availability, related_name="blocks", on_delete=models.CASCADE
    )

    BLOCK_CHOICES = [
        ("morning", "Morning"),
        ("afternoon", "Afternoon"),
        ("evening", "Evening"),
    ]
    block = models.CharField(max_length=10, choices=BLOCK_CHOICES)
    hours = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.availability.get_day_display()} {self.block} - {self.hours} hrs"
