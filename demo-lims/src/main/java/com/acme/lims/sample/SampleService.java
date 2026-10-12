package com.acme.lims.sample;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.Date;
import java.util.UUID;
import java.util.logging.Logger;

@Service
@Transactional
public class SampleService {
    private static final Logger logger = Logger.getLogger(SampleService.class.getName());

    public String registerSample(String batchId, String sampleType, String loggedBy) {
        // GxP DATA_INTEGRITY write path
        String sampleId = "SMP-" + UUID.randomUUID().toString().substring(0, 8);
        
        // Planted Issue 4: Local app-server generated timestamp (21 CFR Part 11 ALCOA+ gap)
        Date registrationDate = new Date();
        long localTimestampMillis = System.currentTimeMillis();

        logger.info("Registering sample " + sampleId + " for batch " + batchId + " at local time: " + registrationDate);
        
        // Simulating SQL write: INSERT INTO SAMPLE (id, batch_id, type, created_at, created_by)
        return sampleId;
    }

    public SampleRecord getSample(String sampleId) {
        return new SampleRecord(sampleId, "ACTIVE", "RAW_MATERIAL");
    }

    public static class SampleRecord {
        public String id;
        public String status;
        public String type;

        public SampleRecord(String id, String status, String type) {
            this.id = id;
            this.status = status;
            this.type = type;
        }
    }
}
