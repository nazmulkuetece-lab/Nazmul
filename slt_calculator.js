/**
 * SLT (Significant Level Threshold) Calculator for Tender Evaluation
 * Determines the winning supplier bid using statistical analysis
 * 
 * Input Parameters:
 * - estimatedCost: Budget/Estimated cost
 * - organizations: Array of supplier objects
 * - quotationBDT: Quotation amount in Bengali Taka
 * - xNPPIFactor: NPPI Index factor (typically 0.955)
 */

class SLTCalculator {
    constructor(nppiFactorParam = 0.955) {
        this.nppiFactorParam = nppiFactorParam;
        this.suppliers = [];
    }

    /**
     * Add a supplier bid to the calculation
     */
    addSupplier(organization, quotationBdt) {
        this.suppliers.push({
            organization,
            quotationBdt
        });
    }

    /**
     * Calculate mean (average) of quotations
     */
    calculateMean() {
        const sum = this.suppliers.reduce((acc, s) => acc + s.quotationBdt, 0);
        return sum / this.suppliers.length;
    }

    /**
     * Calculate standard deviation
     */
    calculateStdDev() {
        const mean = this.calculateMean();
        const squaredDiffs = this.suppliers.map(s => 
            Math.pow(s.quotationBdt - mean, 2)
        );
        const variance = squaredDiffs.reduce((a, b) => a + b, 0) / this.suppliers.length;
        return Math.sqrt(variance);
    }

    /**
     * Calculate all statistics
     */
    calculateStatistics() {
        const mean = this.calculateMean();
        const stdDev = this.calculateStdDev();
        const xNPPI = mean / this.nppiFactorParam;
        const slt = mean - stdDev;

        return {
            mean,
            stdDev,
            xNPPI,
            slt,
            minQuotation: Math.min(...this.suppliers.map(s => s.quotationBdt)),
            maxQuotation: Math.max(...this.suppliers.map(s => s.quotationBdt))
        };
    }

    /**
     * Calculate SLT scores for each supplier
     */
    calculateSLTScores() {
        const stats = this.calculateStatistics();
        const { mean, stdDev } = stats;

        const scores = this.suppliers.map(supplier => ({
            organization: supplier.organization,
            quotationBdt: supplier.quotationBdt,
            deviationFromMean: supplier.quotationBdt - mean,
            sltScore: supplier.quotationBdt - (mean - stdDev),
            withinRange: (supplier.quotationBdt - (mean - stdDev)) >= 0
        }));

        // Sort by SLT score (lowest is best)
        return scores.sort((a, b) => a.sltScore - b.sltScore);
    }

    /**
     * Determine the winner based on lowest significant SLT value
     */
    getWinner() {
        const scores = this.calculateSLTScores();
        const stats = this.calculateStatistics();

        // Find supplier with lowest valid SLT score
        let winner = scores.find(score => score.withinRange);
        
        // If no supplier meets criteria, select lowest quotation
        if (!winner) {
            winner = scores[0];
        }

        return {
            organization: winner.organization,
            quotationBdt: winner.quotationBdt,
            sltScore: winner.sltScore,
            details: {
                slt: stats.slt,
                mean: stats.mean,
                stdDev: stats.stdDev,
                xNPPI: stats.xNPPI,
                allScores: scores
            }
        };
    }

    /**
     * Print detailed SLT analysis report
     */
    printReport() {
        const stats = this.calculateStatistics();
        const winner = this.getWinner();

        console.log("=".repeat(70));
        console.log("SLT (SIGNIFICANT LEVEL THRESHOLD) CALCULATOR - TENDER EVALUATION");
        console.log("=".repeat(70));
        console.log("");

        console.log("STATISTICAL ANALYSIS:");
        console.log("-".repeat(70));
        console.log(`Number of Suppliers:        ${this.suppliers.length}`);
        console.log(`Average Quotation (Mean):   BDT ${this.formatNumber(stats.mean)}`);
        console.log(`Standard Deviation:         BDT ${this.formatNumber(stats.stdDev)}`);
        console.log(`NPPI Factor:                ${this.nppiFactorParam}`);
        console.log(`xNPPI (Indexed Average):    BDT ${this.formatNumber(stats.xNPPI)}`);
        console.log(`SLT Threshold:              BDT ${this.formatNumber(stats.slt)}`);
        console.log(`Quotation Range:            BDT ${this.formatNumber(stats.minQuotation)} - ${this.formatNumber(stats.maxQuotation)}`);
        console.log("");

        console.log("SUPPLIER EVALUATION SCORES:");
        console.log("-".repeat(70));
        console.log(`${"Rank":<6} ${"Organization":<35} ${"Quotation (BDT)":<18} ${"SLT Score":<12} ${"Valid":<8}`);
        console.log("-".repeat(70));

        winner.details.allScores.forEach((score, index) => {
            const status = score.withinRange ? "✓" : "✗";
            const org = score.organization.substring(0, 33).padEnd(35);
            const quotation = this.formatNumber(score.quotationBdt).padStart(17);
            const sltScore = this.formatNumber(score.sltScore).padStart(12);
            console.log(`${(index + 1)}${" ".repeat(5)}${org}${quotation} ${sltScore} ${status}`);
        });

        console.log("");
        console.log("=".repeat(70));
        console.log("WINNER SELECTION:");
        console.log("=".repeat(70));
        console.log(`Selected Organization:      ${winner.organization}`);
        console.log(`Quotation Value (BDT):      BDT ${this.formatNumber(winner.quotationBdt)}`);
        console.log(`SLT Score:                  ${this.formatNumber(winner.sltScore)}`);
        console.log("=".repeat(70));
        console.log("");

        return winner;
    }

    /**
     * Format number with thousand separators
     */
    formatNumber(num) {
        return num.toLocaleString('en-BD', { 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 2 
        });
    }

    /**
     * Export results as JSON
     */
    exportJSON() {
        const winner = this.getWinner();
        const stats = this.calculateStatistics();

        return {
            estimatedCost: this.suppliers[0]?.quotationBdt || null,
            nppiFactorParam: this.nppiFactorParam,
            statistics: {
                numberSuppliers: this.suppliers.length,
                meanQuotation: stats.mean,
                standardDeviation: stats.stdDev,
                xNPPI: stats.xNPPI,
                sltThreshold: stats.slt,
                minQuotation: stats.minQuotation,
                maxQuotation: stats.maxQuotation
            },
            allSuppliers: winner.details.allScores,
            winnerSelection: {
                organization: winner.organization,
                quotationBdt: winner.quotationBdt,
                sltScore: winner.sltScore
            }
        };
    }
}

// Example usage with data from Excel file
function main() {
    const estimatedCost = 1100000;
    const nppiFactorValue = 0.955;

    const calculator = new SLTCalculator(nppiFactorValue);

    // Add supplier data from Excel
    const suppliersData = [
        { organization: "MM BUSINESS SOLUTION", quotationBdt: 982700 },
        { organization: "TRADE ARK COMPUTER", quotationBdt: 995990.04 },
        { organization: "F.D INTERNATIONAL", quotationBdt: 1023000 },
        { organization: "Optimal Technology (Pvt.) Ltd.", quotationBdt: 1078055.561 }
    ];

    console.log(`Estimated Cost: BDT ${estimatedCost.toLocaleString('en-BD')}`);
    console.log(`NPPI Factor: ${nppiFactorValue}\n`);

    suppliersData.forEach(supplier => {
        calculator.addSupplier(supplier.organization, supplier.quotationBdt);
    });

    // Print detailed report
    const winner = calculator.printReport();

    // Export as JSON (useful for API/database storage)
    console.log("JSON Export:");
    console.log(JSON.stringify(calculator.exportJSON(), null, 2));
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SLTCalculator;
}

// Run if executed directly
if (typeof require !== 'undefined' && require.main === module) {
    main();
}
