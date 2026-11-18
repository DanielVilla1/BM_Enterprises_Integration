// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: OrUploadForm =====
// Purpose: Pick a JPEG/PNG photo of the signed OR (or the stamped copy) and upload it
// Inputs: label, disabled flag, onUpload callback (props only)
// Returns: small form markup
// Flow:
// 1. File input limited to JPEG and PNG; opens the camera on phones
// 2. Oversized or missing files are caught before sending; the backend still enforces the rule
// 3. The parent performs the upload

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { isUploadTooLarge } from '../../shared/utils/forms'
import { Icon } from '../../shared/components/Icon'

/**
 * @function OrUploadForm
 * @description Pure UI for a single image upload.
 * @param {{label: string, disabled: boolean, onUpload: function(File): Promise<boolean>}} componentProps
 * @returns {import('react').ReactElement}
 */
export function OrUploadForm({ label, disabled, onUpload }) {
  const [localProblem, setLocalProblem] = useState('')
  return (
    <form
      className="space-y-2"
      onSubmit={async (event) => {
        event.preventDefault()
        const formElement = event.currentTarget
        const chosenFile = new FormData(formElement).get('file')
        if (!chosenFile || !chosenFile.size) {
          setLocalProblem('Choose a photo first.')
          return
        }
        if (isUploadTooLarge(chosenFile)) {
          setLocalProblem('That file is larger than 5 MB.')
          return
        }
        setLocalProblem('')
        if (await onUpload(chosenFile)) formElement.reset()
      }}
    >
      <fieldset className="fieldset">
        <legend className="fieldset-legend">{label}</legend>
        <input
          name="file"
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          className="file-input file-input-sm w-full"
        />
        <p className="label text-xs">
          JPEG or PNG, up to 5 MB. Location data is removed automatically.
        </p>
      </fieldset>
      {localProblem ? (
        <p role="alert" className="text-sm text-error">
          {localProblem}
        </p>
      ) : null}
      <button type="submit" disabled={disabled} className="btn btn-primary btn-sm">
        <Icon name="upload" className="h-4 w-4" /> Upload
      </button>
    </form>
  )
}
