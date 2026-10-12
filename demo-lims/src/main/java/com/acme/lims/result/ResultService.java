package com.acme.lims.result;

import com.acme.lims.sample.SampleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.UUID;
import java.util.logging.Logger;

@Service
@Transactional
public class ResultService {
    private static final Logger logger = Logger.getLogger(ResultService.class.getName());

    @Autowired
    private SampleService sampleService;

    // GxP DATA_INTEGRITY write path to RESULT table
    public String enterResult(String sampleId, String testParam, double value, String analystId) {
        logger.info("Entering test result for sample " + sampleId + ", param=" + testParam + ", value=" + value);
        
        // Planted Smell 6: Direct write to shared RESULT table (also read directly by reporting service)
        // INSERT INTO RESULT (id, sample_id, parameter, numerical_value, analyst, status)
        String resultId = "RES-" + UUID.randomUUID().toString().substring(0, 8);
        return resultId;
    }

    public boolean isOutOfSpecification(double value, double minLimit, double maxLimit) {
        return value < minLimit || value > maxLimit;
    }
}
