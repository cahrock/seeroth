# seeroth-web — Angular 18 Frontend

## Folder Structure
```
src/
  app/
    core/                     # Singleton services, loaded once at app start
      auth/                   # AuthService, TokenService
      guards/                 # AuthGuard, HalalGuard
      interceptors/           # AuthInterceptor, ErrorInterceptor
      services/               # ApiService, WebSocketService
      models/                 # TypeScript interfaces (global)
    shared/                   # Reusable presentational components
      components/             # HalalBadge, SignalChip, ZakatCard, PriceTag
      directives/             # HalalOnly, RoleAccess
      pipes/                  # CurrencyHalal, ZakatFormat, HijriDate
      utils/                  # numberFormat, dateUtil
    features/                 # Feature modules — lazy loaded
      dashboard/              # Main portfolio overview
      screening/              # L1 Halal Gate + L3 Stock Screening
      portfolio/              # L5 Portfolio Risk + Holdings
      zakat/                  # L6 Zakat & Purification Calculator
      advisory/               # L12 AI Chat Interface (Claude streaming)
      simulation/             # Paper trading — simulation mode
      settings/               # User profile, mazhab, risk tolerance
    layout/
      navbar/
      sidebar/
      footer/
  assets/
    icons/
    images/
    i18n/                     # en.json | id.json | ar.json
  environments/
    environment.ts            # Development
    environment.prod.ts       # Production
```

## Package Naming
`@seeroth/<feature>` when extracted to shared libraries.

## Key Commands
```bash
ng serve                          # Dev server: http://localhost:4200
ng build --configuration production
ng test --watch=false
ng lint
```
