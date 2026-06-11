# seeroth-api — Spring Boot 3.5 Backend

## Package Structure
```
com.seeroth.api/
  config/             # SecurityConfig, RedisConfig, CorsConfig, SwaggerConfig
  controller/
    v1/               # Versioned REST controllers
      AuthController
      PortfolioController
      ScreeningController
      ZakatController
      DecisionController
  service/            # Business logic layer
      AuthService
      PortfolioService
      HalalScreeningService
      ZakatService
      DecisionEngineService
  repository/         # Spring Data JPA repositories
  model/
    entity/           # JPA entities: User, Portfolio, Transaction, HalalCache
    enums/            # HalalStatus, Mazhab, TradeAction, HorizonProfile
  dto/                # Request and Response DTOs
  exception/          # GlobalExceptionHandler, SeerothException
  security/           # JwtUtil, JwtAuthFilter, UserDetailsServiceImpl
  util/               # DateUtil, MathUtil, PurificationCalculator
```

## Package Naming
`com.seeroth.api.<package>.<ClassName>`

## Key Commands
```bash
./mvnw spring-boot:run          # Dev server: http://localhost:8080
./mvnw test                     # Unit tests
./mvnw verify                   # Full test suite + integration
./mvnw package -DskipTests      # Build JAR for deploy
```

## Key Dependencies
- Spring Boot 3.5 (Web, Data JPA, Security, Validation, Cache)
- PostgreSQL 16 + TimescaleDB
- Redis (Spring Data Redis)
- JWT via jjwt 0.12
- Lombok + MapStruct
- Flyway (DB migrations)
- Springdoc OpenAPI 3 (Swagger UI)
