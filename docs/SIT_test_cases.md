# SIT (System Integration Testing) Test Cases

SIT checks that the modules work together end to end: URLs, views, forms,
business logic (services) and the database. Unit tests check each piece alone.

Automated in `tests/test_sit_flow.py`.

| ID | Module | Scenario | Steps | Expected result | Status |
|----|--------|----------|-------|-----------------|--------|
| SIT-01 | Projects | Create client project | Fill name, client, methodology = Agile, submit | Project saved, user redirected to project page | Pass |
| SIT-02 | Sprints / Milestones | Add sprint to Agile project | Add "Sprint 1" with dates | Saved with kind = Sprint (Milestone for Waterfall) | Pass |
| SIT-03 | Requirements | Capture requirement | Add REQ-001, plan it into Sprint 1 | Requirement listed under project and sprint | Pass |
| SIT-04 | Design documents | Generate design doc | Click "Generate design document" | v1 created in Draft, contains REQ-001 and the sprint plan | Pass |
| SIT-05 | Client review | Change request then approval | Client requests changes on v1, team regenerates v2, client approves v2 | v1 = Changes requested, v2 = Approved, v1 still kept | Pass |
| SIT-06 | Sprints / Milestones | Invalid dates | End date before start date | Form error shown, nothing saved | Pass |
| SIT-07 | Requirements | Duplicate code | Add REQ-001 twice in one project | Form error "already exists", nothing saved | Pass |
| SIT-08 | Client review | Review old version | Try to sign off v1 after v2 exists | Rejected: only latest version can be signed off | Pass (unit test) |
