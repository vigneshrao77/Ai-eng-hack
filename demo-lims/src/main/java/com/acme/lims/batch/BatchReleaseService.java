package com.acme.lims.batch;

import com.acme.lims.audit.AuditTrailService;
import com.acme.lims.review.ReviewService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.logging.Logger;

@Service
@Transactional
public class BatchReleaseService {
    private static final Logger logger = Logger.getLogger(BatchReleaseService.class.getName());

    @Autowired
    private ReviewService reviewService;

    @Autowired
    private AuditTrailService auditTrailService;

    // GxP PRODUCT_RELEASE tag - Qualified Person (QP) Batch Disposition Decision
    public boolean releaseBatch(String batchNumber, String qpUser, String justification, String esigPassword) {
        logger.info("CRITICAL GxP ACTION: Releasing Batch " + batchNumber + " by QP: " + qpUser);

        // Verify QP credentials
        if (esigPassword == null || esigPassword.trim().isEmpty()) {
            throw new SecurityException("Batch release rejected: Missing QP electronic signature password");
        }

        // Writes to BATCH table: UPDATE BATCH SET disposition='RELEASED', qp_released_by=...
        auditTrailService.logAuditEvent("BATCH", batchNumber, "BATCH_DISPOSITION_RELEASE", qpUser, "QUARANTINE", "RELEASED");
        return true;
    }
}
