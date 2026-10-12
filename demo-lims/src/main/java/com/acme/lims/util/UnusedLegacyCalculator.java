package com.acme.lims.util;

// Planted Smell 5: Dead code (0 inbound calls, 0 runtime trace hits, 0 endpoints)
// Candidate for 7R "Retire" strategy
public class UnusedLegacyCalculator {
    public static double computeDeprecatedFormula(double a, double b) {
        return (a * 1.414) + (b * 0.707);
    }

    public static String getLegacyDateFormat(long timestamp) {
        return "OBSOLETE_" + timestamp;
    }
}
