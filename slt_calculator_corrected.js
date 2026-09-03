/**
 * SLT (Significant Level Threshold) Calculator for Tender Evaluation
 * Determines the winning supplier bid using statistical analysis
 * 
 * CORRECT FORMULA (as per Excel implementation):
 * 1. Calculate Weighted Average (x-bar) from all quotations
 * 2. Calculate deviations from weighted average: deviation = x-bar - quotation
 * 3. Calculate standard deviation: SD = sqrt(average of deviations^2)
 * 4. SLT = x-bar - Standard Deviation
 * 5. SLT Score for each supplier = quotation - SLT
 * 6. Winner = supplier with lowest valid SLT score (>= 0)
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
     * Calculate weighted average (x-bar) of quotations.
     * This is the reference mean for SLT calculation.
     */
    calculateWeightedAverage() {
        if (this.suppliers.length === 0) return 0;
        const sum = this.suppliers.reduce((acc, s) => acc + s.quotationBdt, 0);
        return sum / this.suppliers.length;
    }

    /**
     * Calculate standard deviation using weighted average as reference.
     * Formula: SD = sqrt(average of (x-bar - quotation)^2)
     */
    calculateStdDevFromWeightedAvg(weightedAvg) {
        if (this.suppliers.length < 1) return 0;

        // Step 1: Calculate deviations from weighted average
        const deviations = this.suppliers.map(s => weightedAvg - s.quotationBdt);

        // Step 2: Square the deviations
        const squaredDeviations = deviations.map(d => Math.pow(d, 2));

        // Step 3: Calculate average of squared deviations
        const avgSquaredDev = squaredDeviations.reduce((a, b) => a + b, 0) / this.suppliers.length;

        // Step 4: Take square root to get standard deviation
        return Math.sqrt(avgSquaredDev);
    }

    /**
     * Calculate all statistics
     */
    calculateStatistics() {
        if (this.suppliers.length < 1) {
            throw new Error("No suppliers added");
        }

        // Calculate weighted average (x-bar)
        const weightedAvg = this.calculateWeightedAverage();

        // Calculate standard deviation from weighted average
        const stdDev = this.calculateStdDevFromWeightedAvg(weightedAvg);

        // Calculate xNPPI (indexed average)
        const xNPPI = weightedAvg / this.nppiFactorParam;

        // Calculate SLT = x-bar - Standard Deviation
        const slt = weightedAvg - stdDev;

        return {
            weightedAvg,
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
        const { slt } = stats;

        const scores = this.suppliers.map(supplier => ({
            organization: supplier.organization,
            quotationBdt: supplier.quotationBdt,
            sltScore: supplier.quotationBdt - slt,
            withinRange: (supplier.quotationBdt - slt) >= 0
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
                weightedAvg: stats.weightedAvg,
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
        console.log(`Weighted Average (x-bar):   BDT ${this.formatNumber(stats.weightedAvg)}`);
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
            nppiFactorParam: this.nppiFactorParam,
            statistics: {
                numberSuppliers: this.suppliers.length,
                weightedAverage: stats.weightedAvg,
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
