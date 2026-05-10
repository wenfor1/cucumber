from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    
    class Meta:
        ordering = ['-date']
    INCOME_CATEGORIES = [
        ('salary', 'Зарплата'),
        ('bonus', 'Бонус'),
        ('freelance', 'Фріланс'),
        ('other', 'Інше'),
    ]
    
    income = models.DecimalField(max_digits=10, decimal_places=2)
    income_category = models.CharField(max_length=50, choices=INCOME_CATEGORIES, default='salary')
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.balance = self.income - self.expenses
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_income_category_display()}: {self.income} грн ({self.date})"



class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    
    class Meta:
        ordering = ['-date']
    CATEGORY_CHOICES = [
        ('food', 'Харчування'),
        ('transport', 'Транспорт'),
        ('entertainment', 'Розваги'),
        ('other', 'Інше'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateField()
    time_added = models.DateTimeField(auto_now_add=True)  # Точний час додавання витрати

    def __str__(self):
        return f"{self.category} - {self.amount} грн"
    

class Profile(models.Model):
    GENDER_CHOICES = [
        ('not_selected', 'Не вибрано'),
        ('male', 'Чоловік'),
        ('female', 'Жінка'),
    ]
    
    LANGUAGE_CHOICES = [
        ('uk', 'Українська'),
        ('en', 'English'),
    ]
    full_name = models.CharField(max_length=100)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='uk')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='not_selected')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_registered = models.DateTimeField(auto_now_add=True)
    username_cache = models.CharField(max_length=150, blank=True)
    email_cache = models.EmailField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Оновлюємо кешовані поля перед збереженням
        if self.user:
            self.username_cache = self.user.username
            self.email_cache = self.user.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        Profile.objects.create(user=instance, full_name=full_name)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.full_name = f"{instance.first_name} {instance.last_name}".strip()
    instance.profile.save()
    
class UserCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=19)  # Зберігаємо з пробілами для відображення
    card_holder = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3)
    card_type = models.CharField(max_length=20, default='BANK')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']