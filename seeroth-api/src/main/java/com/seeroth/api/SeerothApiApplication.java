package com.seeroth.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class SeerothApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(SeerothApiApplication.class, args);
    }
}
