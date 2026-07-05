-- Create Database
CREATE DATABASE Coffee_shop_sales_db;

-- Select Data from coffee_shop_sales 
SELECT * FROM coffee_shop_sales;

DESCRIBE coffee_shop_sales;

SET SQL_SAFE_UPDATES = 0;-- turn OFF Safe Update Mode

-- Convert Date(transaction_date) column to proper date format
UPDATE coffee_shop_sales
SET transaction_date = STR_TO_DATE(transaction_date, '%d-%m-%Y'); -- set date format

SET SQL_SAFE_UPDATES = 1; -- turn ON Safe Update Mode

-- Alter Date(transaction_date)Column to DATE Datatype
ALTER TABLE coffee_shop_sales
MODIFY COLUMN transaction_date DATE; -- change datatype

DESCRIBE coffee_shop_sales;

SET SQL_SAFE_UPDATES = 0;-- turn OFF Safe Update Mode

-- Convert Time(transaction_time) Column to proper time format
UPDATE coffee_shop_sales
SET transaction_time = STR_TO_DATE(transaction_time, '%H:%i:%s');-- set time format

-- Alter Time(transaction_time) Column to TIME Datatype
ALTER TABLE coffee_shop_sales
MODIFY COLUMN transaction_time TIME;-- change datatype 

SET SQL_SAFE_UPDATES = 1; -- turn ON Safe Update Mode

DESCRIBE coffee_shop_sales;

-- Change Column Name 'ï»¿transaction_id' to 'transaction_id'
ALTER TABLE coffee_shop_sales 
CHANGE COLUMN ï»¿transaction_id transaction_id INT; -- change field name

-- Datatypes of different columns
DESCRIBE coffee_shop_sales;

-- Total Sales Analysis
SELECT CONCAT((ROUND(SUM(unit_price * transaction_qty)))/1000,"K") AS Total_Sales
FROM coffee_shop_sales
WHERE 
MONTH(transaction_date) = 5; -- May Month

-- Total Sales - Month on Month difference and Month On Month Growth
SELECT 
	MONTH(transaction_date) AS month, -- Number of month
    ROUND(SUM(unit_price * transaction_qty)) AS total_sales, -- total sales
    (SUM(unit_price * transaction_qty) - LAG(SUM(unit_price * transaction_qty),1) -- difference of sales
    -- (SUM(unit_price * transaction_qty) >> gives value for current month
    -- LAG(SUM(unit_price * transaction_qty),1) >> gives value for previous month
    -- LAG is window function 
    -- 1 is for go one month back
    OVER (ORDER BY MONTH(transaction_date))) / LAG(SUM(unit_price * transaction_qty),1) -- Division by previous month sales
    OVER (ORDER BY MONTH(transaction_date)) * 100 AS mom_increase_percentage -- Percentage
FROM
	coffee_shop_sales
WHERE
	MONTH(transaction_date) IN (4,5) -- for month of April(previous month) and May(current month)
GROUP BY
	MONTH(transaction_date)
ORDER BY
	MONTH(transaction_date)
;

-- 2.Total Order Analysis
SELECT * FROM coffee_shop_sales;

SELECT COUNT(transaction_id) AS Total_Orders
FROM coffee_shop_sales
WHERE
MONTH(transaction_date) = 3; -- March Month

-- Total Orders - Month On Month Diffrence and Month On Month Growth

SELECT 
    MONTH(transaction_date) AS month, -- number of month
    ROUND(COUNT(transaction_id)) AS total_orders, -- total orders
    (COUNT(transaction_id) - LAG(COUNT(transaction_id), 1) 
    OVER (ORDER BY MONTH(transaction_date))) / LAG(COUNT(transaction_id), 1) 
    OVER (ORDER BY MONTH(transaction_date)) * 100 AS mom_increase_percentage
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5) -- for April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- Total Quantity Sold Analysis

SELECT SUM(transaction_qty) AS Total_Quantity_Sold
FROM coffee_shop_sales 
WHERE MONTH(transaction_date) = 5; -- for month of (CM-May)

-- Total Quantity Sold - Month On Month Difference and Month On  Month Growth
SELECT 
    MONTH(transaction_date) AS month,
    ROUND(SUM(transaction_qty)) AS total_quantity_sold,
    (SUM(transaction_qty) - LAG(SUM(transaction_qty), 1) 
    OVER (ORDER BY MONTH(transaction_date))) / LAG(SUM(transaction_qty), 1) 
    OVER (ORDER BY MONTH(transaction_date)) * 100 AS mom_increase_percentage
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) IN (4, 5)   -- for April and May
GROUP BY 
    MONTH(transaction_date)
ORDER BY 
    MONTH(transaction_date);

-- Daily Sales, Quantity and Total Orders
SELECT
    CONCAT(ROUND(SUM(unit_price * transaction_qty)/1000,1),'K') AS total_sales,
    CONCAT(ROUND(SUM(transaction_qty)/1000,1),'K') AS total_quantity_sold,
    CONCAT(ROUND(COUNT(transaction_id)/1000,1),'K') AS total_orders
FROM 
    coffee_shop_sales
WHERE 
    transaction_date = '2023-05-18'; -- For 18 May 2023
    
-- Sales Trend Over Period
SELECT 
	CONCAT(ROUND(AVG(total_sales)/1000,1),'K') AS Avg_sales
FROM 
	(
    SELECT SUM(transaction_qty * unit_price) AS total_Sales
	FROM coffee_shop_sales
	WHERE MONTH(transaction_date) = 5
    GROUP BY transaction_date
    ) AS Internal_query;

-- Daily Sales for Month Selected
SELECT 
	DAY(transaction_date) AS day_of_month,
	ROUND(SUM(unit_price * transaction_qty),1) AS total_sales
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) = 5  -- Filter for May
GROUP BY 
    DAY(transaction_date)
ORDER BY 
    DAY(transaction_date);

-- Comparing Daily Sales with average sales - If greater than "Above Average" and Lesser than "Below Average"
SELECT 
    day_of_month,
    CASE 
        WHEN total_sales > avg_sales THEN 'Above Average'
        WHEN total_sales < avg_sales THEN 'Below Average'
        ELSE 'Average'
    END AS sales_status,
    total_sales
FROM (
    SELECT 
        DAY(transaction_date) AS day_of_month,
        SUM(unit_price * transaction_qty) AS total_sales,
        AVG(SUM(unit_price * transaction_qty)) OVER () AS avg_sales
    FROM 
        coffee_shop_sales
    WHERE 
        MONTH(transaction_date) = 5  -- Filter for May
    GROUP BY 
        DAY(transaction_date)
) AS sales_data
ORDER BY 
    day_of_month;


-- Sales By Weekday/Weekend
SELECT 
	CASE WHEN DAYOFWEEK(transaction_date) IN (1,7) THEN 'Weekends'
    ELSE 'Weekdays'
    END AS dat_type,
    CONCAT(ROUND(SUM(unit_price * transaction_qty)/1000,1),'K') AS Total_sales
FROM 
	coffee_shop_sales
WHERE MONTH(transaction_date) = 5 -- May Month
GROUP BY 
	CASE WHEN DAYOFWEEK(transaction_date) IN (1,7) THEN 'Weekends'
    ELSE 'Weekdays'
    END;
    
-- Sales By Store Location
SELECT 
	store_location,
    CONCAT(ROUND(SUM(unit_price * transaction_qty)/1000,2),'K') AS Total_sales
FROM coffee_shop_sales
WHERE MONTH(transaction_date) = 6 -- June
GROUP BY store_location
ORDER BY SUM(unit_price * transaction_qty) DESC;

-- Sales By Product Category
SELECT 
	product_category,
	ROUND(SUM(unit_price * transaction_qty),1) as Total_Sales
FROM coffee_shop_sales
WHERE
	MONTH(transaction_date) = 5 
GROUP BY product_category
ORDER BY SUM(unit_price * transaction_qty) DESC;

-- Sales By Product(Top 10)
SELECT 
	product_type,
	ROUND(SUM(unit_price * transaction_qty),1) as Total_Sales
FROM coffee_shop_sales
WHERE
	MONTH(transaction_date) = 5 
GROUP BY product_type
ORDER BY SUM(unit_price * transaction_qty) DESC
LIMIT 10;

-- Sales By Day/Hour
SELECT 
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales,
    SUM(transaction_qty) AS Total_Quantity,
    COUNT(*) AS Total_Orders
FROM 
    coffee_shop_sales
WHERE 
    DAYOFWEEK(transaction_date) = 3 -- Filter for Tuesday (1 is Sunday, 2 is Monday, ..., 7 is Saturday)
    AND HOUR(transaction_time) = 8 -- Filter for hour number 8
    AND MONTH(transaction_date) = 5; -- Filter for May (month number 5)

-- To get Sales from Monday to Sunday for month of May
SELECT 
    CASE 
        WHEN DAYOFWEEK(transaction_date) = 2 THEN 'Monday'
        WHEN DAYOFWEEK(transaction_date) = 3 THEN 'Tuesday'
        WHEN DAYOFWEEK(transaction_date) = 4 THEN 'Wednesday'
        WHEN DAYOFWEEK(transaction_date) = 5 THEN 'Thursday'
        WHEN DAYOFWEEK(transaction_date) = 6 THEN 'Friday'
        WHEN DAYOFWEEK(transaction_date) = 7 THEN 'Saturday'
        ELSE 'Sunday'
    END AS Day_of_Week,
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) = 5 -- Filter for May (month number 5)
GROUP BY 
    CASE 
        WHEN DAYOFWEEK(transaction_date) = 2 THEN 'Monday'
        WHEN DAYOFWEEK(transaction_date) = 3 THEN 'Tuesday'
        WHEN DAYOFWEEK(transaction_date) = 4 THEN 'Wednesday'
        WHEN DAYOFWEEK(transaction_date) = 5 THEN 'Thursday'
        WHEN DAYOFWEEK(transaction_date) = 6 THEN 'Friday'
        WHEN DAYOFWEEK(transaction_date) = 7 THEN 'Saturday'
        ELSE 'Sunday'
    END;

-- To get sales for all hours for month of May
SELECT 
    HOUR(transaction_time) AS Hour_of_Day,
    ROUND(SUM(unit_price * transaction_qty)) AS Total_Sales
FROM 
    coffee_shop_sales
WHERE 
    MONTH(transaction_date) = 5 -- Filter for May (month number 5)
GROUP BY 
    HOUR(transaction_time)
ORDER BY 
    HOUR(transaction_time);
