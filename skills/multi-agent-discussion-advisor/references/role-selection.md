# Role Selection: Minimal Sufficient Set

## 1. Role Taxonomy (Reference)
- Product: user value, scope boundary, acceptance definition.
- Architect: system constraints, dependency shape, integration risk.
- Algorithm/ML: model capability, data feasibility, quality/runtime trade-offs.
- Backend: service contract, storage, reliability, operability.
- Frontend: interaction feasibility, rendering/performance, UX constraints.
- Domain Expert: regulation, business rules, industry-specific constraints.

## 2. Selection Rules
- Rule 1: Every selected role must map to at least one unresolved uncertainty.
- Rule 2: Remove roles that do not change decision quality.
- Rule 3: Prefer 2-3 roles first, then expand only if risks remain.
- Rule 4: Separate must-have roles from optional reviewers.

## 3. Quick Decision Matrix
- Requirement ambiguity high -> include Product plus one technical validator.
- Feasibility dispute -> include proposing role plus strongest feasibility owner.
- Cross-layer impact -> include Architect plus impacted implementation roles.
- Domain/regulatory risk -> include Domain Expert early.

## 4. Anti-patterns
- Role inflation for appearance rather than decision quality.
- Using predefined role bundles without checking current uncertainty map.
