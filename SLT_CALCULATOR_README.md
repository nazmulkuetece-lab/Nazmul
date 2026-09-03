# SLT Calculator - Tender Evaluation Software

## Overview
The **SLT (Significant Level Threshold) Calculator** is a statistical tool used for fair and transparent supplier selection in procurement/tender evaluation processes. It calculates the lowest significant value to determine the best supplier bid.

## Key Inputs

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Estimated Cost** | Budget/Estimated cost for the procurement | BDT 1,100,000 |
| **Organizations** | List of supplier names/organizations | MM BUSINESS SOLUTION |
| **Quotation BDT** | Bid amount in Bengali Taka (or local currency) | BDT 982,700 |
| **xNPPI Factor** | NPPI (Non-Preferential Price Index) adjustment factor | 0.955 |

## Calculation Formula

### 1. **Mean (Average Quotation)**
```
Mean = (Sum of all quotations) / Number of suppliers
```

### 2. **Standard Deviation**
```
SD = √[ Σ(quotation - mean)² / n ]
```

### 3. **xNPPI (Indexed Average)**
```
xNPPI = Mean / NPPI Factor
```

### 4. **SLT (Significant Level Threshold)**
```
SLT = Mean - Standard Deviation
```

### 5. **SLT Score for Each Supplier**
```
SLT Score = Supplier Quotation - SLT Threshold
```

## Selection Criteria

- **Valid Bids**: Suppliers with SLT Score ≥ 0 (above or equal to threshold)
- **Winner**: Supplier with the **lowest SLT score** that meets the threshold
- **Fallback**: If no supplier meets threshold, select the lowest quotation

## Example Calculation

### Data from Excel File:

| Rank | Organization | Quotation (BDT) | SLT Score | Valid |
|------|--------------|-----------------|-----------|-------|
| 1 | MM BUSINESS SOLUTION | 982,700.00 | -674.12 | ✗ |
| 2 | TRADE ARK COMPUTER | 995,990.04 | 12,615.92 | ✓ |
| 3 | F.D INTERNATIONAL | 1,023,000.00 | 39,625.88 | ✓ |
| 4 | Optimal Technology (Pvt.) Ltd. | 1,078,055.56 | 94,681.44 | ✓ |

### Statistical Analysis:
- **Mean**: BDT 1,019,936.40
- **Standard Deviation**: BDT 36,562.28
- **NPPI Factor**: 0.955
- **xNPPI**: BDT 1,067,996.25
- **SLT Threshold**: BDT 983,374.12

### Winner:
- **Organization**: TRADE ARK COMPUTER
- **Quotation**: BDT 995,990.04
- **SLT Score**: 12,615.92 ✓

---

## Usage

### Python Implementation

```python
from slt_calculator import SLTCalculator

# Create calculator
calculator = SLTCalculator(nppi_factor=0.955)

# Add suppliers
calculator.add_supplier("MM BUSINESS SOLUTION", 982700)
calculator.add_supplier("TRADE ARK COMPUTER", 995990.04)
calculator.add_supplier("F.D INTERNATIONAL", 1023000)
calculator.add_supplier("Optimal Technology (Pvt.) Ltd.", 1078055.561)

# Get winner
winner, quotation, details = calculator.get_winner()
print(f"Winner: {winner} - BDT {quotation:,.2f}")

# Print full report
calculator.print_report()
```

### JavaScript/Node.js Implementation

```javascript
const SLTCalculator = require('./slt_calculator.js');

// Create calculator
const calculator = new SLTCalculator(0.955);

// Add suppliers
calculator.addSupplier("MM BUSINESS SOLUTION", 982700);
calculator.addSupplier("TRADE ARK COMPUTER", 995990.04);
calculator.addSupplier("F.D INTERNATIONAL", 1023000);
calculator.addSupplier("Optimal Technology (Pvt.) Ltd.", 1078055.561);

// Get winner
const winner = calculator.getWinner();
console.log(`Winner: ${winner.organization} - BDT ${winner.quotationBdt}`);

// Print full report
calculator.printReport();

// Export as JSON
console.log(JSON.stringify(calculator.exportJSON(), null, 2));
```

### PowerShell Implementation

```powershell
$suppliers = @(
    @{ organization = "MM BUSINESS SOLUTION"; quotation_bdt = 982700 },
    @{ organization = "TRADE ARK COMPUTER"; quotation_bdt = 995990.04 },
    @{ organization = "F.D INTERNATIONAL"; quotation_bdt = 1023000 }
)

Calculate-SLT -Suppliers $suppliers -NPPIFactor 0.955
```

---

## Output

The calculator provides:

1. **Statistical Summary**
   - Number of suppliers
   - Mean quotation
   - Standard deviation
   - xNPPI factor
   - SLT threshold

2. **Individual Supplier Scores**
   - Organization name
   - Quotation amount
   - SLT score
   - Validity status (meets threshold or not)

3. **Winner Selection**
   - Winning organization
   - Selected quotation
   - SLT score
   - Ranking/justification

4. **JSON Export**
   - Structured data for integration with databases/APIs
   - Complete audit trail

---

## Why SLT Matters

✓ **Fair Selection**: Removes bias and ensures transparent evaluation  
✓ **Statistical Basis**: Uses proven statistical methods  
✓ **Quality Assurance**: Rejects outliers (too low or too high)  
✓ **Value for Money**: Balances cost with reasonable pricing  
✓ **Audit Trail**: Complete documentation for compliance  

---

## Files Included

- **slt_calculator.py** - Python implementation
- **slt_calculator.js** - JavaScript/Node.js implementation
- **SLT_CALCULATOR_README.md** - This documentation file

---

## Support

For questions or customization:
- Adjust NPPI Factor based on market conditions
- Modify SLT formula if needed (e.g., Mean - 1.5×SD)
- Export JSON for integration with procurement systems
- Integrate with Excel/Google Sheets via APIs

---

**Created**: 2026-09-01  
**Version**: 1.0  
**License**: Open Source
