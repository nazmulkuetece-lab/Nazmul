"""
SLT (Significant Level Threshold) Calculator for Tender Evaluation
Determines the winning supplier bid using statistical analysis
"""

import statistics
from typing import List, Dict, Tuple
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
        
    def calculate_statistics(self) -> Dict:
        """Calculate statistical metrics"""
        if len(self.quotations) < 1:
            raise ValueError("No suppliers added")
        
        mean = statistics.mean(self.quotations)
        
        if len(self.quotations) > 1:
            std_dev = statistics.stdev(self.quotations)
        else:
            std_dev = 0
        
        # Calculate xNPPI (indexed average)
        xnppi = mean / self.nppi_factor
        
        # Calculate SLT (Significant Level Threshold)
        slt = mean - std_dev
        
        return {
            'mean': mean,
            'std_dev': std_dev,
            'xnppi': xnppi,
            'slt': slt,
            'min_quotation': min(self.quotations),
            'max_quotation': max(self.quotations)
        }
    
    def calculate_slt_scores(self) -> List[Dict]:
        """Calculate individual SLT scores for each supplier"""
        stats = self.calculate_statistics()
        mean = stats['mean']
        std_dev = stats['std_dev']
        
        scores = []
        for supplier in self.suppliers:
            # Calculate deviation from mean
            deviation = supplier.quotation_bdt - mean
            
            # Calculate SLT score (distance from SLT threshold)
            slt_score = supplier.quotation_bdt - (mean - std_dev)
            
            scores.append({
                'organization': supplier.organization,
                'quotation_bdt': supplier.quotation_bdt,
                'deviation_from_mean': deviation,
                'slt_score': slt_score,
                'within_range': slt_score >= 0
            })
        
        # Sort by SLT score (lowest is best)
        scores.sort(key=lambda x: x['slt_score'])
        
        return scores
    
    def get_winner(self) -> Tuple[str, float, Dict]:
        """
        Determine the winner based on lowest significant SLT value
        
        Returns:
            Tuple of (winning_organization, quotation_bdt, statistics)
        """
        scores = self.calculate_slt_scores()
        stats = self.calculate_statistics()
        
        # Find supplier with lowest valid SLT score (within acceptable range)
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
                'mean': stats['mean'],
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
        print("SLT (Significant Level Threshold) CALCULATOR - TENDER EVALUATION")
        print("=" * 70)
        print()
        
        print("STATISTICAL ANALYSIS:")
        print("-" * 70)
        print(f"Number of Suppliers:        {len(self.suppliers)}")
        print(f"Average Quotation (Mean):   BDT {stats['mean']:,.2f}")
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
