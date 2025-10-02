from django.db import models


class Timetable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(blank=True, null=True)  # Store generated timetable as JSON

    def __str__(self):
        return f"Timetable {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Unit(models.Model):
    timetable = models.ForeignKey(
        Timetable, related_name="units", on_delete=models.CASCADE,
        null=True, blank=True   # Allow units without a timetable initially
    )
    name = models.CharField(max_length=255)
    difficulty = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return f"{self.name} (D={self.difficulty})"


class Availability(models.Model):
    timetable = models.ForeignKey(
        Timetable, related_name="availability", on_delete=models.CASCADE,
        null=True, blank=True   # Allow availability records before timetable is finalized
    )

    DAY_CHOICES = [
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)

    def __str__(self):
        return self.get_day_display()


class AvailabilitySlot(models.Model):
    availability = models.ForeignKey(
        Availability, related_name="slots", on_delete=models.CASCADE
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.availability.get_day_display()} "
            f"{self.start_time or '...'} - {self.end_time or '...'}"
        )
