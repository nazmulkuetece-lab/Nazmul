"""
SLT (Significant Level Threshold) Calculator for Tender Evaluation
Determines the winning supplier bid using statistical analysis

CORRECT FORMULA (as per Excel implementation):
1. Calculate Weighted Average (x-bar) from all quotations
2. Calculate deviations from weighted average: deviation = x-bar - quotation
3. Calculate standard deviation: SD = sqrt(average of deviations^2)
4. SLT = x-bar - Standard Deviation
5. SLT Score for each supplier = quotation - SLT
6. Winner = supplier with lowest valid SLT score (>= 0)
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Supplier:
    """Supplier bid information"""
    organization: str
    quotation_bdt: float
    
    
class SLTCalculator:
    """Calculate SLT and identify the lowest significant value winner"""
    
    def __init__(self, nppi_factor: float = 0.955):
        """
        Initialize SLT calculator
        
        Args:
            nppi_factor: NPPI Index factor (typically 0.955)
        """
        self.nppi_factor = nppi_factor
        self.suppliers: List[Supplier] = []
        self.quotations: List[float] = []
        
    def add_supplier(self, organization: str, quotation_bdt: float) -> None:
        """Add a supplier bid to the calculation"""
        supplier = Supplier(organization, quotation_bdt)
        self.suppliers.append(supplier)
        self.quotations.append(quotation_bdt)
    
    def calculate_weighted_average(self) -> float:
        """
        Calculate weighted average (x-bar) of quotations.
        This is the reference mean for SLT calculation.
        
        Formula: x-bar = sum(quotations) / count
        """
        if len(self.quotations) == 0:
            return 0
        return sum(self.quotations) / len(self.quotations)
    
    def calculate_standard_deviation_from_weighted_avg(self, weighted_avg: float) -> float:
        """
        Calculate standard deviation using weighted average as reference.
        
        Formula: SD = sqrt(average of (x-bar - quotation)^2)
        """
        if len(self.quotations) < 1:
            return 0
        
        # Step 1: Calculate deviations from weighted average
        deviations = [weighted_avg - q for q in self.quotations]
        
        # Step 2: Square the deviations
        squared_deviations = [d ** 2 for d in deviations]
        
        # Step 3: Calculate average of squared deviations
        average_squared_deviation = sum(squared_deviations) / len(squared_deviations)
        
        # Step 4: Take square root to get standard deviation
        return average_squared_deviation ** 0.5
        
    def calculate_statistics(self) -> Dict:
        """Calculate all statistical metrics"""
        if len(self.quotations) < 1:
            raise ValueError("No suppliers added")
        
        # Calculate weighted average (x-bar)
        weighted_avg = self.calculate_weighted_average()
        
        # Calculate standard deviation from weighted average
        std_dev = self.calculate_standard_deviation_from_weighted_avg(weighted_avg)
        
        # Calculate xNPPI (indexed average)
        xnppi = weighted_avg / self.nppi_factor
        
        # Calculate SLT = x-bar - Standard Deviation
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
        """Calculate individual SLT scores for each supplier"""
        stats = self.calculate_statistics()
        slt = stats['slt']
        
        scores = []
        for supplier in self.suppliers:
            # Calculate SLT score (quotation - SLT threshold)
            slt_score = supplier.quotation_bdt - slt
            
            scores.append({
                'organization': supplier.organization,
                'quotation_bdt': supplier.quotation_bdt,
                'slt_score': slt_score,
                'within_range': slt_score >= 0
            })
        
        # Sort by SLT score (lowest is best)
        return sorted(scores, key=lambda x: x['slt_score'])
    
    def get_winner(self) -> tuple:
        """
        Determine the winner based on lowest significant SLT value
        
        Returns:
            Tuple of (winning_organization, quotation_bdt, statistics)
        """
        scores = self.calculate_slt_scores()
        stats = self.calculate_statistics()
        
        # Find supplier with lowest valid SLT score (>= 0)
        winner = None
        for score in scores:
            if score['within_range']:
                winner = score
                break
        
        # If no supplier meets criteria, select lowest quotation
        if winner is None:
            winner = scores[0]
        
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
        """Print detailed SLT analysis report"""
        stats = self.calculate_statistics()
        winner, quotation, details = self.get_winner()
        
        print("=" * 70)
        print("SLT (SIGNIFICANT LEVEL THRESHOLD) CALCULATOR - TENDER EVALUATION")
        print("=" * 70)
        print()
        
        print("STATISTICAL ANALYSIS:")
        print("-" * 70)
        print(f"Number of Suppliers:        {len(self.suppliers)}")
        print(f"Weighted Average (x-bar):   BDT {stats['weighted_average']:,.2f}")
        print(f"Standard Deviation:         BDT {stats['std_dev']:,.2f}")
        print(f"NPPI Factor:                {self.nppi_factor}")
        print(f"xNPPI (Indexed Average):    BDT {stats['xnppi']:,.2f}")
        print(f"SLT Threshold:              BDT {stats['slt']:,.2f}")
        print(f"Quotation Range:            BDT {stats['min_quotation']:,.2f} - {stats['max_quotation']:,.2f}")
        print()
        
        print("SUPPLIER EVALUATION SCORES:")
        print("-" * 70)
        print(f"{'Rank':<6} {'Organization':<35} {'Quotation (BDT)':<18} {'SLT Score':<12} {'Valid':<8}")
        print("-" * 70)
        
        for i, score in enumerate(details['all_scores'], 1):
            status = "✓" if score['within_range'] else "✗"
            print(f"{i:<6} {score['organization']:<35} {score['quotation_bdt']:>15,.2f} "
                  f"{score['slt_score']:>12,.2f} {status:<8}")
        
        print()
        print("=" * 70)
        print("WINNER SELECTION:")
        print("=" * 70)
        print(f"Selected Organization:      {winner}")
        print(f"Quotation Value (BDT):      BDT {quotation:,.2f}")
        print(f"SLT Score:                  {details['slt_score']:,.2f}")
        print("=" * 70)
        print()


def main():
    """Example usage of SLT Calculator"""
    
    # Example data from the Excel file
    estimated_cost = 1100000
    nppi_factor = 0.955
    
    # Create calculator
    calculator = SLTCalculator(nppi_factor)
    
    # Add supplier bids
    suppliers_data = [
        ("MM BUSINESS SOLUTION", 982700),
        ("TRADE ARK COMPUTER", 995990.04),
        ("F.D INTERNATIONAL", 1023000),
        ("Optimal Technology (Pvt.) Ltd.", 1078055.561)
    ]
    
    print(f"Estimated Cost: BDT {estimated_cost:,.2f}")
    print(f"NPPI Factor: {nppi_factor}\n")
    
    for org, quotation in suppliers_data:
        calculator.add_supplier(org, quotation)
    
    # Print detailed report
    calculator.print_report()
    
    # Get winner
    winner, quotation, details = calculator.get_winner()
    print(f"\nWINNER: {winner} with quotation BDT {quotation:,.2f}")


if __name__ == "__main__":
    main()
