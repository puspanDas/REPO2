def bmi_calculator(weight,height):
    bmi = weight/(height**2)
    return round(bmi,2)

##user input and case 
height = float(input("enter your value:"))
weight = float(input("enter your value:"))

#calculate bmi
bmi_value =bmi_calculator(weight,height)

if bmi_value <= 18.5:
    category = "underweight"
elif bmi_value <= 24.9:
    category = "normal weight"
elif bmi_value <= 29.9:
    category = "overweight"
else:
    category = "obese"


print(f"Your BMI is: {bmi_value}")
print(f"You are {category}.")