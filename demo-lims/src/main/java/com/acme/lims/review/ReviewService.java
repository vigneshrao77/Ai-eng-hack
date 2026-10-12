package com.acme.lims.review;

import com.acme.lims.audit.AuditTrailService;
import com.acme.lims.result.ResultService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.logging.Logger;

@Service
@Transactional
public class ReviewService {
    private static final Logger logger = Logger.getLogger(ReviewService.class.getName());

    @Autowired
    private ResultService resultService;

    @Autowired
    private AuditTrailService auditTrailService;

    // GxP E_SIGNATURE tag - requires re-authentication & electronic signature meaning
    public boolean reviewAndSignResult(String resultId, String reviewerUser, String password, String signatureMeaning) {
        logger.info("Executing Electronic Signature verification for result: " + resultId + " by " + reviewerUser);
        
        // Simulating credential check: PasswordEncoder.matches / AuthenticationManager
        boolean passwordValid = (password != null && !password.isEmpty());
        if (!passwordValid) {
            throw new SecurityException("Electronic signature verification failed: invalid credentials");
        }

        // Audit the signature event
        auditTrailService.logAuditEvent("RESULT", resultId, "E_SIGN_REVIEW", reviewerUser, "PENDING", "APPROVED");
        return true;
    }
}
