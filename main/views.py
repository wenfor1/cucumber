from sqlite3 import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import BudgetForm
from .models import Budget, Expense
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as EmailValidationError
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserCard
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


# Функція для реєстрації
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Перевірка валідності email
                email = form.cleaned_data['email']
                # Замість стандартного validate_email
                try:
                    validate_email(email)
                except EmailValidationError:
                    form.add_error('email', 'Будь ласка, введіть коректну email адресу')
                    return render(request, 'registration.html', {'form': form})
                
                # Перевірка унікальності email
                if User.objects.filter(email=email).exists():
                    form.add_error('email', 'Ця електронна адреса вже зареєстрована')
                    return render(request, 'registration.html', {'form': form})
                
                # Перевірка складності пароля
                password = form.cleaned_data['password']
                try:
                    validate_password(password, user=form.instance)
                except ValidationError as e:
                    for error in e.messages:
                        form.add_error('password', error)
                    return render(request, 'registration.html', {'form': form})
                
                # Перевірка збігу паролів
                if password != form.cleaned_data['password_confirmation']:
                    form.add_error('password_confirmation', 'Паролі не збігаються')
                    return render(request, 'registration.html', {'form': form})
                
                # Перевірка умов використання
                if not form.cleaned_data.get('terms'):
                    form.add_error('terms', 'Ви повинні погодитись з умовами використання')
                    return render(request, 'registration.html', {'form': form})
                
                # Створення користувача
                user = form.save(commit=False)
                user.set_password(password)
                user.save()
                
                login(request, user)
                messages.success(request, 'Реєстрація успішна! Ласкаво просимо!')
                return redirect('home')
                
            except IntegrityError:
                form.add_error('username', 'Користувач з таким ім\'ям вже існує')
        
        return render(request, 'registration.html', {'form': form})
    
    return render(request, 'registration.html', {'form': UserRegistrationForm()})

# Функція для входу
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Невірне ім\'я користувача або пароль')
        else:
            # Кастомні повідомлення про помилки
            for field, errors in form.errors.items():
                for error in errors:
                    if 'username' in field:
                        messages.error(request, 'Будь ласка, введіть коректне ім\'я користувача')
                    elif 'password' in field:
                        messages.error(request, 'Будь ласка, введіть пароль')
                    else:
                        messages.error(request, error)
    
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

# Функція для профілю
@login_required
def profile(request):
    return render(request, 'profile.html')

# Інші функції
@login_required
def createPlan(request):
    return render(request, 'createPlan.html')

@login_required
def chart(request):
    return render(request, 'chart.html')

@login_required
def costs(request):
    return HttpResponse('<h4>Перевірка "Оцінка витрат"</h4>')

@login_required
def analytics(request):
    return HttpResponse('<h4>Перевірка "Аналітика перевиконання бюджету"</h4>')

@login_required
def createBudget(request):
    user = request.user
    # Отримуємо дані тільки для поточного користувача
    total_income = Budget.objects.filter(user=user).aggregate(total=Sum('income'))['total'] or 0
    last_income_record = Budget.objects.filter(user=user).order_by('-date', '-created_at').first()
    
    if request.method == 'POST':
        try:
            income = float(request.POST.get('income', 0))
            income_category = request.POST.get('income_category', 'salary')
            date = request.POST.get('date') or timezone.now().date()
            
            if income <= 0:
                messages.error(request, "Сума доходу має бути більше нуля")
                return render(request, 'createBudget.html', {
                    'total_income': total_income,
                    'last_income': last_income_record.income if last_income_record else 0,
                    'current_date': timezone.now().date()
                })
            
            # Додаємо поточного користувача до запису
            Budget.objects.create(
                user=user,
                income=income,
                income_category=income_category,
                date=date,
                expenses=0,
                balance=income
            )
            
            messages.success(request, f"Дохід {income} грн успішно додано!")
            # Просте перенаправлення на ту саму сторінку
            return redirect('createBudget')  # Видалено reverse
            
        except ValueError:
            messages.error(request, "Будь ласка, введіть коректну суму доходу")
        except Exception as e:
            messages.error(request, f"Помилка при додаванні доходу: {str(e)}")
    
    return render(request, 'createBudget.html', {
        'total_income': total_income,
        'last_income': last_income_record.income if last_income_record else 0,
        'current_date': timezone.now().date()
    })
    
@login_required
def add_expense(request):
    user = request.user
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        date = request.POST.get('date')

        if amount and category and date:
            expense = Expense.objects.create(
                user=user,
                amount=amount,
                category=category,
                date=date,
            )
            return JsonResponse({'status': 'success', 'message': 'Витрату додано!', 'expense_id': expense.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'Будь ласка, заповніть всі поля.'})

    # GET-запит - показуємо тільки витрати поточного користувача
    expenses = Expense.objects.filter(user=user).order_by('-date')
    return render(request, 'createPlan.html', {'expenses': expenses})

@login_required
def delete_expense(request, expense_id):
    if request.method == 'POST':
        try:
            expense = Expense.objects.get(id=expense_id, user=request.user)
            expense.delete()
            return JsonResponse({'status': 'success', 'message': 'Витрату видалено!'})
        except Expense.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Витрата не знайдена або вам не належить.'})
    return JsonResponse({'status': 'error', 'message': 'Недійсний метод запиту.'})

@login_required
def report_api(request):
    user = request.user
    period = request.GET.get('period', 'month')
    date_str = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        date = timezone.now().date()
    
    # Отримуємо дані тільки для поточного користувача
    if period == 'day':
        expenses = Expense.objects.filter(user=user, date=date)
        budgets = Budget.objects.filter(user=user, date=date)
        labels = [date.strftime('%d.%m.%Y')]
        xAxisTitle = "День"
        
    elif period == 'month':
        start_date = date.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        expenses = Expense.objects.filter(user=user, date__range=[start_date, end_date])
        budgets = Budget.objects.filter(user=user, date__range=[start_date, end_date])
        labels = []
        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%d.%m'))
            current_date += timedelta(days=1)
        xAxisTitle = "Дні місяця"
        
    else:  # year
        start_date = date.replace(month=1, day=1)
        end_date = date.replace(month=12, day=31)
        expenses = Expense.objects.filter(user=user, date__range=[start_date, end_date])
        budgets = Budget.objects.filter(user=user, date__range=[start_date, end_date])
        labels = ['Січ', 'Лют', 'Бер', 'Кві', 'Тра', 'Чер', 'Лип', 'Сер', 'Вер', 'Жов', 'Лис', 'Гру']
        xAxisTitle = "Місяці року"
    
    # Підготовка даних для графіка
    if period == 'day':
        income = [float(budgets.aggregate(total=Sum('income'))['total'] or 0)]
        expenses_data = [float(expenses.aggregate(total=Sum('amount'))['total'] or 0)]
        
    elif period == 'month':
        income = [0] * end_date.day
        expenses_data = [0] * end_date.day
        
        # Розподіл доходів по днях
        for budget in budgets:
            day = budget.created_at.day - 1
            income[day] += float(budget.income)
        
        # Розподіл витрат по днях
        for expense in expenses:
            day = expense.date.day - 1
            expenses_data[day] += float(expense.amount)
            
    else:  # year
        income = [0] * 12
        expenses_data = [0] * 12
        
        # Розподіл доходів по місяцях
        for budget in budgets:
            month = budget.created_at.month - 1
            income[month] += float(budget.income)
        
        # Розподіл витрат по місяцях
        for expense in expenses:
            month = expense.date.month - 1
            expenses_data[month] += float(expense.amount)
    
    # Підготовка даних для таблиці
    transactions = []
    
    # Додаємо витрати
    for expense in expenses:
        transactions.append({
            'date': expense.date.strftime('%d.%m.%Y'),
            'type': 'Витрати',
            'amount': expense.amount,
            'category': expense.get_category_display()
        })
    
    # Додаємо доходи з їх датами
    for budget in budgets:
        transactions.append({
            'date': budget.created_at.strftime('%d.%m.%Y'),
            'type': 'Доходи',
            'amount': budget.income,
            'category': 'Зарплата'  # Можна додати поле категорії для доходів у моделі
        })
    
    # Сортуємо транзакції по даті
    transactions.sort(key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)
    
    return JsonResponse({
        'labels': labels,
        'income': income,
        'expenses': expenses_data,
        'xAxisTitle': xAxisTitle,
        'transactions': transactions
    })

def logout_view(request):
    logout(request)  # Викликає функцію для виходу користувача
    return redirect('login')  # Перенаправлення на сторінку логіну

@login_required
def profile_view(request):
    """Відображення профілю користувача"""
    user = request.user
    context = {
        'user': user,
        'profile': user.profile
    }
    return render(request, 'profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        # Отримуємо поточного користувача
        user = request.user
        profile = user.profile

        # Оновлення повного імені
        if 'full_name' in request.POST:
            full_name = request.POST.get('full_name', '').strip()

            # Перевірка наявності пробілу для розділення на ім'я та прізвище
            if ' ' in full_name:
                first_name, last_name = full_name.split(' ', 1)
            else:
                first_name, last_name = full_name, ''
            
            # Оновлюємо ім'я та прізвище користувача
            user.first_name = first_name
            user.last_name = last_name
            user.save()  # Зберігаємо зміни користувача

            # Оновлюємо поле `full_name` в профілі
            profile.full_name = full_name
            profile.save()  # Зберігаємо зміни профілю

        # Оновлення інших даних профілю
        if 'gender' in request.POST:
            profile.gender = request.POST.get('gender', 'not_selected')

        if 'language' in request.POST:
            profile.language = request.POST.get('language', 'uk')

        # Зберігаємо зміни профілю
        profile.save()

        # Повертаємо повідомлення про успішне оновлення
        return JsonResponse({'status': 'success', 'message': 'Дані успішно збережено!'})

    # Якщо запит не POST, перенаправляємо на сторінку профілю
    return redirect('profile')

@csrf_exempt
def save_card(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Створення нової картки
            card = UserCard(
                user=request.user,
                card_number=data.get('cardNumber'),
                card_holder=data.get('cardHolder'),
                expiry_date=data.get('cardExpiry'),
                cvv=data.get('cardCvv'),
                card_type=data.get('cardType')
            )
            card.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Картку збережено успішно',
                'card_id': card.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Метод не підтримується'
    }, status=405)

def get_user_cards(request):
    if request.user.is_authenticated:
        cards = request.user.cards.all()
        cards_data = []
        
        for card in cards:
            cards_data.append({
                'id': card.id,
                'card_number': card.card_number,
                'card_holder': card.card_holder,
                'expiry_date': card.expiry_date,
                'card_type': card.card_type
            })
        
        return JsonResponse({
            'status': 'success',
            'cards': cards_data
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Необхідно авторизуватися'
    }, status=401)


@login_required
@require_POST
def upload_avatar(request):
    if 'avatar' in request.FILES:
        avatar = request.FILES['avatar']
        
        # Перевірка розміру (5MB)
        if avatar.size > 5 * 1024 * 1024:
            return JsonResponse({'status': 'error', 'message': 'Розмір файлу перевищує 5MB'})
        
        # Перевірка типу файлу
        valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar.content_type not in valid_types:
            return JsonResponse({'status': 'error', 'message': 'Недопустимий формат файлу'})
        
        # Збереження аватарки в профілі користувача
        profile = request.user.profile
        profile.avatar = avatar
        profile.save()
        
        return JsonResponse({'status': 'success', 'message': 'Аватарка успішно оновлена'})
    
    return JsonResponse({'status': 'error', 'message': 'Файл не знайдено'})