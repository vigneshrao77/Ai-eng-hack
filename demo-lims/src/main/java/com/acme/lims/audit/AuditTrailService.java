package com.acme.lims.audit;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.Date;
import java.util.logging.Logger;

@Service
@Transactional
public class AuditTrailService {
    private static final Logger logger = Logger.getLogger(AuditTrailService.class.getName());

    // GxP AUDIT_TRAIL tag
    public void logAuditEvent(String entityName, String entityId, String action, String changedBy, String oldValue, String newValue) {
        // Planted Smell 1: AUDIT_TRAIL table missing 'reason' column (Compliance Gap for 21 CFR Part 11.10(e))
        // INSERT INTO AUDIT_TRAIL (id, entity, entity_id, action, changed_by, old_val, new_val, timestamp)
        // Notice: NO 'reason' column in table schema or method signature!
        Date eventTime = new Date();
        logger.info("[AUDIT] " + action + " on " + entityName + ":" + entityId + " by " + changedBy + " at " + eventTime);
    }
}
