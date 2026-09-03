"""
SLT (Significant Level Threshold) Calculator for Tender Evaluation
CORRECTED VERSION - Uses proper Weighted Average calculation

The Excel implementation uses a specific Weighted Average (x-bar) value
that may differ from the simple mean. This value is used as the reference
for calculating standard deviation and SLT threshold.

Formula (as per Excel):
1. Weighted Average (x-bar) - typically calculated as mean or special formula
2. Deviations: deviation = x-bar - quotation
3. Standard Deviation: SD = sqrt(average of deviations²)
4. SLT = x-bar - SD
5. SLT Score = quotation - SLT
6. Winner = lowest valid SLT score (>= 0)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Supplier:
    """Supplier bid information"""
    organization: str
    quotation_bdt: float


class SLTCalculator:
    """Calculate SLT using weighted average as reference (Excel implementation)"""
    
    def __init__(self, weighted_avg: Optional[float] = None, nppi_factor: float = 0.955):
        """
        Initialize SLT calculator
        
        Args:
            weighted_avg: Reference weighted average (x-bar). If None, uses simple mean
            nppi_factor: NPPI Index factor (typically 0.955)
        """
        self.custom_weighted_avg = weighted_avg
        self.nppi_factor = nppi_factor
        self.suppliers: List[Supplier] = []
        self.quotations: List[float] = []
        
    def add_supplier(self, organization: str, quotation_bdt: float) -> None:
        """Add a supplier bid"""
        supplier = Supplier(organization, quotation_bdt)
        self.suppliers.append(supplier)
        self.quotations.append(quotation_bdt)
    
    def calculate_weighted_average(self) -> float:
        """Calculate weighted average (x-bar)"""
        if self.custom_weighted_avg is not None:
            return self.custom_weighted_avg
        if len(self.quotations) == 0:
            return 0
        return sum(self.quotations) / len(self.quotations)
    
    def calculate_standard_deviation(self, weighted_avg: float) -> float:
        """Calculate SD from deviations of quotations from weighted average"""
        if len(self.quotations) < 1:
            return 0
        
        squared_devs = [(weighted_avg - q) ** 2 for q in self.quotations]
        avg_squared = sum(squared_devs) / len(squared_devs)
        return avg_squared ** 0.5
        
    def calculate_statistics(self) -> Dict:
        """Calculate all metrics"""
        if len(self.quotations) < 1:
            raise ValueError("No suppliers added")
        
        weighted_avg = self.calculate_weighted_average()
        std_dev = self.calculate_standard_deviation(weighted_avg)
        xnppi = weighted_avg / self.nppi_factor
        slt = weighted_avg - std_dev
        
        return {
            'weighted_average': weighted_avg,
            'std_dev': std_dev,
            'xnppi': xnppi,
            'slt': slt,
            'min_quotation': min(self.quotations),
            'max_quotation': max(self.quotations)
        }
    
    def calculate_slt_scores(self) -> List[Dict]:
        """Calculate SLT scores for each supplier"""
        stats = self.calculate_statistics()
        slt = stats['slt']
        
        scores = []
        for supplier in self.suppliers:
            slt_score = supplier.quotation_bdt - slt
            scores.append({
                'organization': supplier.organization,
                'quotation_bdt': supplier.quotation_bdt,
                'slt_score': slt_score,
                'within_range': slt_score >= 0
            })
        
        return sorted(scores, key=lambda x: x['slt_score'])
    
    def get_winner(self) -> tuple:
        """Determine winner (lowest valid SLT score)"""
        scores = self.calculate_slt_scores()
        stats = self.calculate_statistics()
        
        winner = next((s for s in scores if s['within_range']), scores[0])
        
        return (
            winner['organization'],
            winner['quotation_bdt'],
            {
                'slt': stats['slt'],
                'weighted_average': stats['weighted_average'],
                'std_dev': stats['std_dev'],
                'xnppi': stats['xnppi'],
                'slt_score': winner['slt_score'],
                'all_scores': scores
            }
        )
    
    def print_report(self) -> None:
        """Print detailed report"""
        stats = self.calculate_statistics()
        winner, quotation, details = self.get_winner()
        
        print("=" * 70)
        print("SLT CALCULATOR - TENDER EVALUATION (Excel Formula)")
        print("=" * 70)
        print()
        
        print("STATISTICAL ANALYSIS:")
        print("-" * 70)
        print(f"Number of Suppliers:        {len(self.suppliers)}")
        print(f"Weighted Average (x-bar):   BDT {stats['weighted_average']:,.2f}")
        print(f"Standard Deviation:         BDT {stats['std_dev']:,.2f}")
        print(f"NPPI Factor:                {self.nppi_factor}")
        print(f"xNPPI (Indexed Avg):        BDT {stats['xnppi']:,.2f}")
        print(f"SLT Threshold:              BDT {stats['slt']:,.2f}")
        print()
        
        print("SUPPLIER EVALUATION:")
        print("-" * 70)
        print(f"{'Rank':<6} {'Organization':<35} {'Quotation':<18} {'SLT Score':<15}")
        print("-" * 70)
        
        for i, score in enumerate(details['all_scores'], 1):
            status = "✓" if score['within_range'] else "✗"
            print(f"{i:<6} {score['organization']:<35} BDT {score['quotation_bdt']:>14,.2f} "
                  f"{score['slt_score']:>12,.2f} {status}")
        
        print()
        print("=" * 70)
        print("WINNER:")
        print("=" * 70)
        print(f"Organization:               {winner}")
        print(f"Quotation (BDT):            BDT {quotation:,.2f}")
        print(f"SLT Score:                  {details['slt_score']:,.2f}")
        print("=" * 70)


def main():
    """Example with Excel data"""
    
    # Suppliers from Excel
    suppliers_data = [
        ("MM BUSINESS SOLUTION", 982700),
        ("TRADE ARK COMPUTER", 995990.04),
        ("F.D INTERNATIONAL", 1023000),
        ("Optimal Technology (Pvt.) Ltd.", 1078055.561)
    ]
    
    # NOTE: The weighted average value (1045118.200125) comes from Excel's
    # specific calculation. You may need to adjust this based on your Excel formula.
    # It could be: simple mean, weighted mean, or result of a complex formula.
    
    print("Example 1: Using Simple Mean as Weighted Average")
    print("=" * 70)
    calc1 = SLTCalculator(nppi_factor=0.955)
    for org, quotation in suppliers_data:
        calc1.add_supplier(org, quotation)
    calc1.print_report()
    
    print("\n\n")
    print("Example 2: Using Excel's Weighted Average (1045118.200125)")
    print("=" * 70)
    calc2 = SLTCalculator(weighted_avg=1045118.200125, nppi_factor=0.955)
    for org, quotation in suppliers_data:
        calc2.add_supplier(org, quotation)
    calc2.print_report()


if __name__ == "__main__":
    main()
