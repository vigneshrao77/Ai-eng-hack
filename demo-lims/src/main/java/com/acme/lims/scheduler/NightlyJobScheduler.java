package com.acme.lims.scheduler;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import java.util.logging.Logger;

@Component
public class NightlyJobScheduler {
    private static final Logger logger = Logger.getLogger(NightlyJobScheduler.class.getName());

    // Cloud Blocker: Monolithic in-process scheduled job
    // Target cloud pattern: EventBridge / CloudWatch Events / Kubernetes CronJob
    @Scheduled(cron = "0 0 2 * * ?")
    public void runNightlyStabilityCheck() {
        logger.info("Executing scheduled batch job: Nightly Stability Sample Pull");
    }
}
