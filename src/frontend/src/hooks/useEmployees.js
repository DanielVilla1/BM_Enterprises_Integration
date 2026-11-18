// ===== AI GENERATED: useEmployees =====
// Purpose: Employees for the People screen with all owner/HR actions
// Inputs: none
// Returns: store state plus create, update, activate, roles, link and license actions
// Flow:
// 1. Load employees on mount; every mutation reloads the list
// 2. License reads return a result object so a dialog can show "none on record"

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useCallback, useEffect } from 'react'
import {
  assignEmployeeRoles,
  createEmployee,
  fetchDriverLicense,
  linkEmployeeIdentity,
  listEmployees,
  saveDriverLicense,
  setEmployeeActive,
  updateEmployee,
} from '../services/employeeService'
import { loadIntoStore } from '../shared/services/collectionLoader'
import { useEmployeeStore } from '../store/employeeStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useEmployees
 * @description Employees list and actions.
 * @returns {Object}
 */
export function useEmployees() {
  const loadState = useEmployeeStore((state) => state.loadState)
  const items = useEmployeeStore((state) => state.items)
  const failure = useEmployeeStore((state) => state.failure)
  const reloadEmployees = useCallback(() => loadIntoStore(useEmployeeStore, listEmployees), [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadEmployees)

  const loadLicense = useCallback(async (employeeIdentifier) => {
    try {
      return { license: await fetchDriverLicense(employeeIdentifier), failure: null }
    } catch (requestFailure) {
      return { license: null, failure: requestFailure }
    }
  }, [])

  useEffect(() => {
    reloadEmployees()
  }, [reloadEmployees])

  return {
    loadState,
    employees: items,
    failure,
    actionFailure,
    isBusy,
    submitCreate: (employeePayload) => runAction(() => createEmployee(employeePayload)),
    submitUpdate: (employeeIdentifier, changes) =>
      runAction(() => updateEmployee(employeeIdentifier, changes)),
    submitActive: (employeeIdentifier, shouldBeActive) =>
      runAction(() => setEmployeeActive(employeeIdentifier, shouldBeActive)),
    submitRoles: (employeeIdentifier, roleCodes, exceptionReason) =>
      runAction(() => assignEmployeeRoles(employeeIdentifier, roleCodes, exceptionReason)),
    submitIdentity: (employeeIdentifier, clerkUserIdentifier) =>
      runAction(() => linkEmployeeIdentity(employeeIdentifier, clerkUserIdentifier)),
    submitLicense: (employeeIdentifier, licensePayload) =>
      runAction(() => saveDriverLicense(employeeIdentifier, licensePayload)),
    loadLicense,
  }
}
