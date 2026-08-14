# Testing Guide for Agentic SQL Data Analyst

## Pre-Testing Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with valid credentials
- [ ] MySQL server running and database created
- [ ] Groq API key valid

## Database Setup

### Create MySQL Database

```sql
CREATE DATABASE IF NOT EXISTS agentic_analyst CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agentic_analyst;
```

## Test Data Files

### 1. Sample Sales Data (sales.csv)

```csv
date,product_name,quantity,unit_price,customer_id,region
2024-01-01,Widget A,10,29.99,1,North
2024-01-02,Widget B,5,49.99,2,South
2024-01-03,Widget A,3,29.99,1,North
2024-01-04,Widget C,8,19.99,3,East
2024-01-05,Widget B,2,49.99,2,South
2024-01-06,Widget A,15,29.99,4,West
2024-01-07,Widget D,7,99.99,5,North
2024-01-08,Widget C,12,19.99,1,North
2024-01-09,Widget B,4,49.99,3,East
2024-01-10,Widget A,6,29.99,2,South
2024-01-11,Widget D,3,99.99,4,West
2024-01-12,Widget C,9,19.99,5,North
```

### 2. Sample Customer Data (customers.csv)

```csv
customer_id,customer_name,email,signup_date,total_purchases
1,John Smith,john@example.com,2023-06-15,5
2,Jane Doe,jane@example.com,2023-07-20,4
3,Bob Johnson,bob@example.com,2023-08-10,3
4,Alice Williams,alice@example.com,2023-09-05,2
5,Charlie Brown,charlie@example.com,2023-10-12,6
```

### 3. Sample Inventory Data (inventory.csv)

```csv
product_id,product_name,category,stock_quantity,reorder_level,warehouse
1,Widget A,General,150,50,Main
2,Widget B,Premium,25,20,Main
3,Widget C,Basic,300,75,Secondary
4,Widget D,Luxury,10,5,Main
```

## Test Scenarios

### Scenario 1: File Upload

**Steps:**
1. Start application: `chainlit run app.py -w`
2. Click attachment button
3. Upload `sales.csv`
4. Verify table created successfully

**Expected:**
- ✅ Message: "File imported successfully!"
- ✅ Table name shown (e.g., `sales`)
- ✅ Row count displayed (12 rows)
- ✅ Column types shown

---

### Scenario 2: Simple Query

**Query:** "What are the total sales by product?"

**Expected Flow:**
1. ✅ Retrieving Schema
2. ✅ Generating SQL (should use GROUP BY)
3. ✅ Executing SQL
4. ✅ Generating Summary
5. ✅ Results displayed as table

**Expected SQL:**
```sql
SELECT `product_name`, SUM(`quantity` * `unit_price`) as total_sales
FROM `sales`
GROUP BY `product_name`
ORDER BY total_sales DESC
```

---

### Scenario 3: Filtering Query

**Query:** "Show me all sales from the North region"

**Expected SQL:**
```sql
SELECT * FROM `sales` WHERE `region` = 'North'
```

**Expected Results:**
- Rows with region = 'North'
- Formatted as interactive table

---

### Scenario 4: Date-based Query

**Query:** "What are the total sales by date?"

**Expected SQL:**
```sql
SELECT `date`, SUM(`quantity` * `unit_price`) as daily_total
FROM `sales`
GROUP BY `date`
ORDER BY `date` DESC
```

---

### Scenario 5: Join Query (After loading multiple tables)

1. Upload `sales.csv`
2. Upload `customers.csv`

**Query:** "Show customers with their total orders value"

**Expected SQL:**
```sql
SELECT c.`customer_name`, COUNT(s.`customer_id`) as order_count, SUM(s.`quantity` * s.`unit_price`) as total_value
FROM `customers` c
LEFT JOIN `sales` s ON c.`customer_id` = s.`customer_id`
GROUP BY c.`customer_id`, c.`customer_name`
ORDER BY total_value DESC
```

---

### Scenario 6: Error Correction

**Query (intentionally vague):** "How much did customer 5 spend?"

**Expected Behavior:**
1. ✅ Schema Inspector runs
2. ✅ SQL Generator creates query
3. ✅ Executor finds error (e.g., ambiguous join)
4. ✅ Self-Corrector fixes it
5. ✅ Second execution succeeds

**Trace Should Show:**
- Attempt 1 SQL
- Error message
- Attempt 2 SQL (corrected)
- Final results

---

### Scenario 7: Data Type Inference

1. Create `mixed_types.csv`:
```csv
id,name,age,salary,hire_date,active
1,Alice,28,75000.50,2022-01-15,true
2,Bob,34,85000.00,2020-06-01,true
3,Charlie,29,72000.75,2021-03-20,false
```

2. Upload file

**Expected:**
- ✅ ID → Integer
- ✅ Name → VARCHAR
- ✅ Age → Integer
- ✅ Salary → Float
- ✅ Hire_date → DateTime
- ✅ Active → Boolean

---

### Scenario 8: Security Test

**Query (should be blocked):** "Delete all sales where product = 'Widget A'"

**Expected:**
- ❌ Error message: "Only SELECT queries are allowed"
- ❌ Query NOT executed

---

### Scenario 9: Large Dataset

1. Create `large_sales.csv` with 10,000 rows
2. Upload file
3. Query: "What is the average order value?"

**Expected:**
- ✅ File imports successfully (may take 5-10 seconds)
- ✅ Query executes efficiently
- ✅ Results returned within reasonable time

---

### Scenario 10: Special Characters in Names

1. Create `special_chars.csv`:
```csv
Order_ID,Customer Name,Product (Type),Amount ($),Date/Time
1,John Doe,Widget (Type A),100,2024-01-01 10:30
2,Jane Smith,Gadget (Type B),150,2024-01-02 14:15
```

2. Upload file

**Expected:**
- ✅ Column names sanitized to: `order_id`, `customer_name`, `product_type`, `amount`, `datetime`
- ✅ No special characters in table/column names
- ✅ Data preserved correctly

---

## Debugging Checklist

### If file upload fails:
- [ ] File is CSV or XLSX
- [ ] File is not corrupted
- [ ] Disk space available for temp files
- [ ] Correct file format detected

### If query execution fails:
- [ ] Check MySQL connection in `.env`
- [ ] Verify table exists (upload file first)
- [ ] Check logs for SQL error details
- [ ] Try simpler query first

### If LLM calls fail:
- [ ] GROQ_API_KEY is valid
- [ ] Internet connection working
- [ ] API rate limits not exceeded
- [ ] Check Groq dashboard for errors

### If UI not displaying:
- [ ] Chainlit installed correctly
- [ ] Port 8000 not in use
- [ ] Try: `netstat -an | grep 8000` (Windows) or `lsof -i :8000` (Unix)
- [ ] Kill process on port: `netstat -ano | findstr :8000` → `taskkill /PID <PID>`

---

## Performance Benchmarks

| Test | Expected Time | Limit |
|------|----------------|-------|
| File upload (1000 rows) | 2-5 seconds | < 10s |
| Simple query (SELECT *) | 1-3 seconds | < 5s |
| Aggregate query | 2-4 seconds | < 10s |
| Join query | 3-6 seconds | < 15s |
| Error correction | 4-8 seconds | < 20s |
| Large dataset (10K rows) | 5-15 seconds | < 30s |

---

## Sample Query Library

### Analytics Queries

```
"How many total orders were placed?"
"What's the average order value?"
"Which customer spent the most?"
"What's the most popular product?"
"Show me sales trend by month"
"Which region has highest sales?"
"What's the distribution of order values?"
```

### Data Quality Queries

```
"Show products with low stock"
"List customers who haven't purchased in 30 days"
"Which products have never been ordered?"
"Show duplicate customer records"
"Find orders with unusual amounts"
```

### Business Intelligence

```
"What are top 5 products by revenue?"
"Show customer lifetime value ranking"
"Which customers are at churn risk?"
"What's the repeat purchase rate?"
"Compare sales performance by region"
```

---

## Success Criteria

✅ All 10 scenarios pass  
✅ No crashes or unhandled errors  
✅ Response times within benchmarks  
✅ Data accuracy verified  
✅ Security constraints enforced  
✅ UI displays results clearly  
✅ Logs show proper execution trace  

---

## Reporting Issues

When reporting a bug, include:
1. **Query used**
2. **Error message** (full stack trace from logs)
3. **Steps to reproduce**
4. **Expected vs actual behavior**
5. **Environment** (OS, Python version, MySQL version)
6. **Log file** (from terminal or `.chainlit/` directory)

---

**Happy Testing! 🚀**
