from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from pymongo import MongoClient
from django.contrib import messages

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["loan_eligibility"]
applicants_collection = db["applicants"]

def intro(request):
    return render(request, 'index.html')
@csrf_protect
def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Look up user by email and password
        user = applicants_collection.find_one({"email": email, "password": password})

        if user:
            # Redirect to registration or any authenticated page
            return redirect('bank')
        else:
            # Invalid login, show error
            return render(request, 'login.html', {"error": "Invalid email or password"})

    return render(request, 'login.html')

@csrf_protect
def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        state = request.POST.get('state')
        annual_income = request.POST.get('annual_income')
        monthly_income = request.POST.get('monthly_income')
        dob = request.POST.get('dob')
        age = request.POST.get('age')
        loan_reason = request.POST.get('loan_reason')
        loan_amount = request.POST.get('loan_amount')
        employment = request.POST.get('employment')
        work_type = request.POST.get('work_type')
        marital_status = request.POST.get('marital_status')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        if password != repassword:
            messages.error(request, "Passwords do not match!")
            return render(request, 'register.html')

        # Save to MongoDB
        applicants_collection.insert_one({
            "fullname": fullname,
            "phone": phone,
            "email": email,
            "state": state,
            "annual_income": annual_income,
            "monthly_income": monthly_income,
            "dob": dob,
            "age": age,
            "loan_reason": loan_reason,
            "loan_amount": loan_amount,
            "employment": employment,
            "work_type": work_type,
            "marital_status": marital_status,
            "password": password
        })

        return redirect('bank')  # Go to bank details after registration

    return render(request, 'register.html')


def predict(request):
    latest_applicant = db.applicants.find().sort([('_id', -1)]).limit(1)[0]
    latest_bank = db.banks.find().sort([('_id', -1)]).limit(1)[0]

    eligible = latest_bank['credit_score'] > 600 and latest_applicant['income'] > latest_applicant['loan_amount'] * 0.2
    return render(request, 'predict.html', {
        "eligible": eligible,
        "credit_score": latest_bank['credit_score']
    })

def about(request):
    return render(request, 'about.html')


def bank(request):
    if request.method == "POST":
        bank_name = request.POST.get('bank_name')
        ifsc = request.POST.get('ifsc')
        account_number = request.POST.get('account_number')
        credit_card = request.POST.get('credit_card')
        existing_loans = request.POST.get('existing_loans')
        repayment_history = request.POST.get('repayment_history')

        # Handle empty fields
        if not all([bank_name, ifsc, account_number, credit_card, existing_loans, repayment_history]):
            return render(request, 'bank.html', {'error': 'Please fill all fields properly.'})

        # Calculate credit score based on simple logic
        score = 600  # base score

        if credit_card == 'yes':
            score += 100
        score -= int(existing_loans) * 20

        if repayment_history == 'good':
            score += 100
        elif repayment_history == 'average':
            score += 50
        else:
            score -= 50

        score = max(300, min(900, score))  # Clamp score between 300 and 900

        return render(request, 'bank.html', {'score': score})

    return render(request, 'bank.html')