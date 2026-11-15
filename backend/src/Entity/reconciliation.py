# ===== AI GENERATED: reconciliation_report =====
# Purpose: Result value of one Clerk reconciliation run
# Inputs: counts computed by the service
# Returns: frozen ReconciliationReport
# Flow:
# 1. Carry deactivated, linked and orphan counts to the caller

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationReport:
    deactivated_count: int
    linked_count: int
    clerk_users_without_employee: int
