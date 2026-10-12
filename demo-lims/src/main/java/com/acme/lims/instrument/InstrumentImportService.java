package com.acme.lims.instrument;

import com.acme.lims.result.ResultService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.io.File;
import java.util.logging.Logger;

@Service
public class InstrumentImportService {
    private static final Logger logger = Logger.getLogger(InstrumentImportService.class.getName());

    @Autowired
    private ResultService resultService;

    public void processInstrumentDirectory() {
        // Planted Smell 2: Local Windows File Share dependency (Cloud Blocker - 12 Factor III/VI)
        File directory = new File("C:\\instrument\\import");
        if (directory.exists() && directory.isDirectory()) {
            File[] files = directory.listFiles();
            if (files != null) {
                for (File f : files) {
                    logger.info("Processing instrument raw output file from local path: " + f.getAbsolutePath());
                    // Parses peak areas and passes to resultService.enterResult(...)
                }
            }
        }
    }
}
