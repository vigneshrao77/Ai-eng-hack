package com.acme.lims.reporting;

import org.springframework.stereotype.Service;
import java.util.logging.Logger;

@Service
public class ReportService {
    private static final Logger logger = Logger.getLogger(ReportService.class.getName());

    // GxP REPORTING_ONLY tag - Read-only analytics, LOW regulatory tier
    // Quick-win candidate for early cloud migration
    public byte[] generateCertificateOfAnalysis(String batchNumber) {
        logger.info("Generating CoA report for batch: " + batchNumber);
        
        // Planted Smell 6: Directly reads from shared RESULT table without bounded context
        // SELECT * FROM RESULT WHERE batch_id = ...
        return new byte[]{0x25, 0x50, 0x44, 0x46}; // PDF mock header
    }

    public void cacheReportData(String reportId, String data) {
        // Writes to non-regulated table: INSERT INTO REPORT_CACHE
        logger.info("Caching non-regulated analytics report data: " + reportId);
    }
}
