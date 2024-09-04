from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Emp
from .forms import SignupForm, LoginForm
import re

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            auth_login(request, user)  # Log the user in
            messages.success(request, "Signup successful!")
            return redirect('login')  # Redirect to the login page or any other page
        else:
            print(form.errors)  # Debug: Print any errors that caused form invalidation
            messages.error(request, "Signup failed. Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Login successful!")
                return redirect('emp_home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            print(form.errors)  # Debugging: Print form errors if the form is not valid
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, "Logout successful.")  # Add a success message
    return redirect('login')  # Redirect to the login page after logout

@login_required(login_url='/emp/login/')
def emp_home(request):
    emps = Emp.objects.filter(user=request.user)
    return render(request, "emp/home.html", {'emps': emps})



@login_required(login_url='/emp/login/')
def add_emp(request):
    if request.method == "POST":
        emp_name = request.POST.get("emp_name")
        emp_id = request.POST.get("emp_id")
        emp_phone = request.POST.get("emp_phone")
        emp_address = request.POST.get("emp_address")
        emp_working = request.POST.get("emp_working")
        emp_department = request.POST.get("emp_department")

        # Validate fields
        if not all([emp_name, emp_id, emp_phone, emp_address, emp_department]):
            messages.error(request, "All fields are required.")
            return render(request, "emp/add_emp.html")

        if not emp_id.isdigit():
            messages.error(request, "Employee ID must be a number.")
            return render(request, "emp/add_emp.html")
        
        if not emp_phone.isdigit():
            messages.error(request, "Phone number must be a number.")
            return render(request, "emp/add_emp.html")
        
        # Check for duplicate emp_id and phone for the current user
        if Emp.objects.filter(emp_id=emp_id, user=request.user).exists():
            messages.error(request, "Employee ID already exists.")
            return render(request, "emp/add_emp.html")
        
        if Emp.objects.filter(phone=emp_phone, user=request.user).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, "emp/add_emp.html")
        
        e = Emp(
            name=emp_name,
            emp_id=emp_id,
            phone=emp_phone,
            address=emp_address,
            department=emp_department,
            working=bool(emp_working),
            user=request.user  # Assign the current user
        )
        try:
            e.save()
            messages.success(request, "Employee added successfully.")
            return redirect("emp_home")
        except IntegrityError:
            messages.error(request, "Unable to save employee.")
        
    return render(request, "emp/add_emp.html")


@login_required(login_url='/emp/login/')
def delete_emp(request, emp_id):
    emp = get_object_or_404(Emp, pk=emp_id, user=request.user)
    emp.delete()
    messages.success(request, "Employee deleted successfully.")
    return redirect("emp_home")
    
@login_required(login_url='/emp/login/')
def update_emp(request, emp_id):
    emp = get_object_or_404(Emp, pk=emp_id, user=request.user)
    return render(request, "emp/update_emp.html", {'emp': emp})

@login_required(login_url='/emp/login/')
def do_update_emp(request, emp_id):
    if request.method == "POST":
        emp_name = request.POST.get("emp_name")
        emp_id_temp = request.POST.get("emp_id")
        emp_phone = request.POST.get("emp_phone")
        emp_address = request.POST.get("emp_address")
        emp_working = request.POST.get("emp_working")
        emp_department = request.POST.get("emp_department")

        # Validate fields
        if not all([emp_name, emp_id_temp, emp_phone, emp_address, emp_department]):
            messages.error(request, "All fields are required.")
            return render(request, "emp/update_emp.html", {'emp': Emp.objects.get(pk=emp_id, user=request.user)})

        if not emp_id_temp.isdigit():
            messages.error(request, "Employee ID must be a number.")
            return render(request, "emp/update_emp.html", {'emp': Emp.objects.get(pk=emp_id, user=request.user)})
        
        if not emp_phone.isdigit():
            messages.error(request, "Phone number must be a number.")
            return render(request, "emp/update_emp.html", {'emp': Emp.objects.get(pk=emp_id, user=request.user)})

        try:
            e = Emp.objects.get(pk=emp_id, user=request.user)

            # Check for duplicate emp_id and phone number excluding the current record
            if Emp.objects.exclude(pk=emp_id).filter(emp_id=emp_id_temp, user=request.user).exists():
                messages.error(request, "Employee ID already exists.")
                return render(request, "emp/update_emp.html", {'emp': e})
            
            if Emp.objects.exclude(pk=emp_id).filter(phone=emp_phone, user=request.user).exists():
                messages.error(request, "Phone number already exists.")
                return render(request, "emp/update_emp.html", {'emp': e})

            # Update employee details
            e.name = emp_name
            e.emp_id = emp_id_temp
            e.phone = emp_phone
            e.address = emp_address
            e.department = emp_department
            e.working = bool(emp_working)
            e.save()
            
            messages.success(request, "Employee updated successfully.")
        except Emp.DoesNotExist:
            messages.error(request, "Employee not found.")
        except IntegrityError:
            messages.error(request, "Unable to update employee.")

    return redirect("emp_home")