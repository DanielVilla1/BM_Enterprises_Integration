// ===== AI GENERATED: OrUploadForm =====
// Purpose: Pick a JPEG/PNG photo of the signed OR (or the stamped copy) and upload it
// Inputs: label, disabled flag, onUpload callback (props only)
// Returns: small form markup
// Flow:
// 1. File input limited to JPEG and PNG; size hint shown
// 2. Oversized files are caught before sending; the backend still enforces the rule
// 3. The parent performs the upload

import { useState } from 'react'
import { isUploadTooLarge } from '../shared/utils/forms'

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
      className="space-y-1"
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
      <label className="block text-sm font-medium">
        {label}
        <input
          name="file"
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          className="mt-1 block text-sm"
        />
      </label>
      <p className="text-xs text-gray-600">JPEG or PNG, up to 5 MB.</p>
      {localProblem ? (
        <p role="alert" className="text-sm text-red-700">
          {localProblem}
        </p>
      ) : null}
      <button type="submit" disabled={disabled} className="rounded bg-gray-900 px-3 py-1 text-sm text-white">
        Upload
      </button>
    </form>
  )
}
