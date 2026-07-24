# Drishti — Catalyst Data Store Schema
Derived from: `Police_FIR_ER_Diagram.pdf` (Karnataka Police, official)
Target: Zoho Catalyst Data Store (Cloud Scale)

## Catalyst Data Store type reference (confirmed from Catalyst docs)
- `VARCHAR` — up to 255 chars — use for codes, names, short strings
- `TEXT` — up to 10,000 chars — use for free text (BriefFacts, notes)
- `INT` — 4-byte integer, up to 10 digits — use for IDs, ages, counts
- `DATE` — `YYYY-MM-DD`
- `DATETIME` — `YYYY-MM-DD HH:MM:SS`
- `DOUBLE` — use for latitude/longitude
- `BOOLEAN` — use for Active/flag columns (0/1)

Note: Catalyst Data Store does not enforce relational FK constraints server-side the way SQL does — FKs below are stored as plain `INT` columns and enforced at the app layer (FastAPI). Optionally use Catalyst's **Lookup** column type for console-side convenience on high-traffic joins (e.g. CaseMaster → Unit), but plain INT is simpler and faster to build under time pressure — recommend plain INT for all FKs in this build.

Enable the **PII/ePHI validator** (Catalyst column setting) on: `ComplainantName`, `VictimName`, `AccusedName`, `Employee.KGID`, `Employee.FirstName`, `Employee.EmployeeDOB`. Flagged, not optional — this is real name/ID data even in a demo.

---

## Build order (do NOT build all 26 tables before touching the frontend)

**Batch A — lookup/reference tables (fast, zero dependencies, do first, ~30 min total):**
State, District, UnitType, Rank, Designation, CaseCategory, GravityOffence, CrimeHead, CrimeSubHead, CaseStatusMaster, CasteMaster, ReligionMaster, OccupationMaster, Act, Section

**Batch B — org/people tables (depend on Batch A):**
Unit, Employee, Court

**Batch C — core case tables (depend on Batch A+B, this is where the actual product lives):**
CaseMaster, ComplainantDetails, Victim, Accused, ActSectionAssociation, CrimeHeadActSection

**Batch D — case lifecycle tables (depend on Batch C):**
ArrestSurrender, ChargesheetDetails

**Batch E — Drishti analytics extension (new, not in original ERD, needed for the differentiators — build after synthetic data is loaded into Batch C/D):**
HotspotCluster, AnomalyFlag, StationResolutionMetric, RiskScore

Demo-critical path is **A → B → C → E**. Batch D (arrest/chargesheet) matters for the resolution loop but can be thinner — populate `CaseStatusMaster` + `ChargesheetDetails.cstype` even if `ArrestSurrender` stays minimal.

---

## Batch A — Lookup Tables

### State
| Column | Type | Key |
|---|---|---|
| StateID | INT | PK |
| StateName | VARCHAR | |
| NationalityID | INT | |
| Active | BOOLEAN | |

### District
| Column | Type | Key |
|---|---|---|
| DistrictID | INT | PK |
| DistrictName | VARCHAR | |
| StateID | INT | FK → State |
| Active | BOOLEAN | |

### UnitType
| Column | Type | Key |
|---|---|---|
| UnitTypeID | INT | PK |
| UnitTypeName | VARCHAR | |
| CityDistState | VARCHAR | |
| Hierarchy | INT | |
| Active | BOOLEAN | |

### Rank
| Column | Type | Key |
|---|---|---|
| RankID | INT | PK |
| RankName | VARCHAR | |
| Hierarchy | INT | |
| Active | BOOLEAN | |

### Designation
| Column | Type | Key |
|---|---|---|
| DesignationID | INT | PK |
| DesignationName | VARCHAR | |
| Active | BOOLEAN | |
| SortOrder | INT | |

### CaseCategory
| Column | Type | Key |
|---|---|---|
| CaseCategoryID | INT | PK |
| LookupValue | VARCHAR | (FIR, UDR, PAR, Zero FIR) |

### GravityOffence
| Column | Type | Key |
|---|---|---|
| GravityOffenceID | INT | PK |
| LookupValue | VARCHAR | (Heinous, Non-Heinous) |

### CrimeHead
| Column | Type | Key |
|---|---|---|
| CrimeHeadID | INT | PK |
| CrimeGroupName | VARCHAR | |
| Active | BOOLEAN | |

### CrimeSubHead
| Column | Type | Key |
|---|---|---|
| CrimeSubHeadID | INT | PK |
| CrimeHeadID | INT | FK → CrimeHead |
| CrimeHeadName | VARCHAR | (e.g. Murder, Robbery — misnamed in source doc, is really the sub-head name) |
| SeqID | INT | |

### CaseStatusMaster
| Column | Type | Key |
|---|---|---|
| CaseStatusID | INT | PK |
| CaseStatusName | VARCHAR | (Under Investigation, Charge Sheeted, Closed) |

### CasteMaster
| Column | Type | Key |
|---|---|---|
| caste_master_id | INT | PK |
| caste_master_name | VARCHAR | |

### ReligionMaster
| Column | Type | Key |
|---|---|---|
| ReligionID | INT | PK |
| ReligionName | VARCHAR | |

### OccupationMaster
| Column | Type | Key |
|---|---|---|
| OccupationID | INT | PK |
| OccupationName | VARCHAR | |

### Act
| Column | Type | Key |
|---|---|---|
| ActCode | VARCHAR | PK |
| ActDescription | VARCHAR | |
| ShortName | VARCHAR | |
| Active | BOOLEAN | |

### Section
| Column | Type | Key |
|---|---|---|
| ActCode | VARCHAR | FK → Act |
| SectionCode | VARCHAR | PK (composite w/ ActCode in practice) |
| SectionDescription | VARCHAR | |
| Active | BOOLEAN | |

---

## Batch B — Org/People Tables

### Unit (police stations)
| Column | Type | Key |
|---|---|---|
| UnitID | INT | PK |
| UnitName | VARCHAR | |
| TypeID | INT | FK → UnitType |
| ParentUnit | INT | self-ref → UnitID |
| NationalityID | INT | |
| StateID | INT | FK → State |
| DistrictID | INT | FK → District |
| Active | BOOLEAN | |

### Employee
| Column | Type | Key |
|---|---|---|
| EmployeeID | INT | PK |
| DistrictID | INT | FK → District |
| UnitID | INT | FK → Unit |
| RankID | INT | FK → Rank |
| DesignationID | INT | FK → Designation |
| KGID | VARCHAR | PII |
| FirstName | VARCHAR | PII |
| EmployeeDOB | DATE | PII |
| GenderID | INT | |
| BloodGroupID | INT | |
| PhysicallyChallenged | BOOLEAN | |
| AppointmentDate | DATE | |

### Court
| Column | Type | Key |
|---|---|---|
| CourtID | INT | PK |
| CourtName | VARCHAR | |
| DistrictID | INT | FK → District |
| StateID | INT | FK → State |
| Active | BOOLEAN | |

---

## Batch C — Core Case Tables

### CaseMaster (the central table — everything hangs off this)
| Column | Type | Key |
|---|---|---|
| CaseMasterID | INT | PK |
| CrimeNo | VARCHAR | |
| CaseNo | VARCHAR | |
| CrimeRegisteredDate | DATE | |
| PolicePersonID | INT | FK → Employee |
| PoliceStationID | INT | FK → Unit |
| CaseCategoryID | INT | FK → CaseCategory |
| GravityOffenceID | INT | FK → GravityOffence |
| CrimeMajorHeadID | INT | FK → CrimeHead |
| CrimeMinorHeadID | INT | FK → CrimeSubHead |
| CaseStatusID | INT | FK → CaseStatusMaster |
| CourtID | INT | FK → Court |
| IncidentFromDate | DATETIME | |
| IncidentToDate | DATETIME | |
| InfoReceivedPSDate | DATETIME | |
| latitude | DOUBLE | |
| longitude | DOUBLE | |
| BriefFacts | TEXT | |

### ComplainantDetails
| Column | Type | Key |
|---|---|---|
| ComplainantID | INT | PK |
| CaseMasterID | INT | FK → CaseMaster |
| ComplainantName | VARCHAR | PII |
| AgeYear | INT | |
| OccupationID | INT | FK → OccupationMaster |
| ReligionID | INT | FK → ReligionMaster |
| CasteID | INT | FK → CasteMaster |
| GenderID | INT | |

### Victim
| Column | Type | Key |
|---|---|---|
| VictimMasterID | INT | PK |
| CaseMasterID | INT | FK → CaseMaster |
| VictimName | VARCHAR | PII |
| AgeYear | INT | |
| GenderID | INT | |
| VictimPolice | BOOLEAN | |

### Accused
| Column | Type | Key |
|---|---|---|
| AccusedMasterID | INT | PK |
| CaseMasterID | INT | FK → CaseMaster |
| AccusedName | VARCHAR | PII |
| AgeYear | INT | |
| GenderID | INT | |
| PersonID | VARCHAR | (A1, A2, A3…) |

### ActSectionAssociation
| Column | Type | Key |
|---|---|---|
| CaseMasterID | INT | FK → CaseMaster |
| ActID | INT | FK → Act |
| SectionID | INT | FK → Section |
| ActOrderID | INT | |
| SectionOrderID | INT | |

### CrimeHeadActSection
| Column | Type | Key |
|---|---|---|
| CrimeHeadID | INT | FK → CrimeHead |
| ActCode | VARCHAR | FK → Act |
| SectionCode | VARCHAR | FK → Section |

---

## Batch D — Case Lifecycle Tables

### ArrestSurrender
| Column | Type | Key |
|---|---|---|
| ArrestSurrenderID | INT | PK |
| CaseMasterID | INT | FK → CaseMaster |
| ArrestSurrenderTypeID | INT | |
| ArrestSurrenderDate | DATE | |
| ArrestSurrenderStateId | INT | FK → State |
| ArrestSurrenderDistrictId | INT | FK → District |
| PoliceStationID | INT | FK → Unit |
| IOID | INT | FK → Employee |
| CourtID | INT | FK → Court |
| AccusedMasterID | INT | FK → Accused |
| IsAccused | BOOLEAN | |
| IsComplainantAccused | BOOLEAN | |

### ChargesheetDetails
| Column | Type | Key |
|---|---|---|
| CSID | INT | PK |
| CaseMasterID | INT | FK → CaseMaster |
| csdate | DATETIME | |
| cstype | VARCHAR | (A=Chargesheet, B=False Case, C=Undetected) |
| PolicePersonID | INT | FK → Employee |

---

## Batch E — Drishti Analytics Extension (NOT in the original ERD — new, built by us)

These are precomputed outputs, not live-query tables. Populate via batch script after Batch C/D data exists. Store in Data Store (small, queryable) or Stratus (large JSON blobs) — recommend Data Store for these four since they're small and the frontend needs to filter/query them, not just fetch a blob.

### HotspotCluster
| Column | Type | Key |
|---|---|---|
| ClusterID | INT | PK |
| DistrictID | INT | FK → District |
| UnitID | INT | FK → Unit (nullable — cluster may span stations) |
| CrimeMajorHeadID | INT | FK → CrimeHead |
| CentroidLat | DOUBLE | |
| CentroidLng | DOUBLE | |
| IncidentCount | INT | |
| TimeWindowStart | DATE | |
| TimeWindowEnd | DATE | |
| ComputedAt | DATETIME | |

### AnomalyFlag
| Column | Type | Key |
|---|---|---|
| AnomalyID | INT | PK |
| DistrictID | INT | FK → District |
| UnitID | INT | FK → Unit |
| CrimeMajorHeadID | INT | FK → CrimeHead |
| ObservedCount | INT | |
| ExpectedCount | DOUBLE | (historical baseline) |
| AnomalyScore | DOUBLE | |
| FlagReason | VARCHAR | |
| WindowStart | DATE | |
| WindowEnd | DATE | |

### StationResolutionMetric (the accountability differentiator)
| Column | Type | Key |
|---|---|---|
| MetricID | INT | PK |
| UnitID | INT | FK → Unit |
| PeriodStart | DATE | |
| PeriodEnd | DATE | |
| TotalCases | INT | |
| Chargesheeted | INT | (cstype = A) |
| FalseCases | INT | (cstype = B) |
| Undetected | INT | (cstype = C) |
| AvgDaysToResolution | DOUBLE | |
| ResolutionRatePct | DOUBLE | |

### RiskScore (predictive — feeds from Zia AutoML / QuickML output)
| Column | Type | Key |
|---|---|---|
| RiskScoreID | INT | PK |
| DistrictID | INT | FK → District |
| UnitID | INT | FK → Unit |
| CrimeMajorHeadID | INT | FK → CrimeHead |
| RiskLevel | VARCHAR | (Low/Medium/High) |
| RiskValue | DOUBLE | |
| ModelVersion | VARCHAR | |
| ComputedAt | DATETIME | |

---

## Link-analysis graph — no new table needed

Network/link analysis (Accused ↔ Victim ↔ Location ↔ repeat CaseMasterID) can be computed **on demand from Batch C tables** via a join query, not a precomputed table:
- Repeat offender = same `AccusedName` (or a matched `PersonID` pattern) appearing across multiple `CaseMasterID`s
- Shared location = multiple `CaseMasterID`s with close `lat/lng` and overlapping `Accused`
- Node types: Accused, Victim, Unit (location)
- Edge = shared CaseMasterID

For the demo, precompute this into a Stratus JSON blob per district (not a Data Store table) since graph shape is irregular and doesn't need SQL filtering — just fetched whole by the frontend graph component.

---

## What I did NOT include (deliberately, for time)

Skipped populating in the demo (schema-complete on paper if a judge asks, but not built): `Rank`/`Designation` depth beyond 2-3 sample values, `Court` beyond a handful of rows, `BloodGroupID`/`PhysicallyChallenged` on Employee. These exist in the schema for completeness but don't need real data — nobody will query them in your demo flow.

## Optics note (not a schema issue, a UI one)

`CasteMaster`/`ReligionMaster` are in the official schema and legitimately used for socio-economic correlation per the brief — keep them in the schema and in your backend. But think twice before putting a live "crime by caste/religion" chart on a public-facing demo screen; it's the kind of thing that reads badly out of context even when the underlying analytics use is legitimate. Safer: aggregate this into your broader "socio-economic correlation" overlay (occupation, urbanization) without a standalone caste/religion breakdown chart in the UI.
