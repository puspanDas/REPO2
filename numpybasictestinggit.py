import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Sample configuration
cities = ['CityA', 'CityB', 'CityC']
weeks = 4

# Generate random weekly sales data (in thousands) for restaurant and bar
# Shape: (cities, weeks, type) where type 0=restaurant, 1=bar
sales_data = np.random.randint(50, 150, size=(len(cities), weeks, 2))

# Analyze: total weekly sales per city (restaurant + bar)
total_weekly_sales = sales_data.sum(axis=2)  # shape: (cities, weeks)

# Average weekly sales per type for each city
avg_weekly_sales = sales_data.mean(axis=1)  # shape: (cities, type)

# Overall average sales per type (across all cities and weeks)
overall_avg_sales = sales_data.mean(axis=(0, 1))

# Output results
print('Weekly Restaurant+Bar Sales per City (in thousands):\\n', total_weekly_sales)
print('Average Weekly Sales [Restaurant, Bar] per City (in thousands):\\n', avg_weekly_sales)
print('Overall Average Sales [Restaurant, Bar] (in thousands):\\n', overall_avg_sales)
