// ===== AI GENERATED: DocumentLinks =====
// Purpose: Buttons that open a trip's stored OR documents
// Inputs: documents, disabled flag, onOpen callback (props only)
// Returns: list markup or nothing
// Flow:
// 1. One small button per stored document
// 2. The parent fetches a short-lived signed URL when a button is pressed

import { describeDocumentKind } from '../shared/utils/dispatch'
import { Icon } from './Icon'

/**
 * @function DocumentLinks
 * @description Pure UI for opening stored documents.
 * @param {{documents: Array<Object>, disabled: boolean, onOpen: function(string): void}} componentProps
 * @returns {import('react').ReactElement|null}
 */
export function DocumentLinks({ documents, disabled, onOpen }) {
  if (!documents.length) return null
  return (
    <ul className="flex flex-wrap gap-2">
      {documents.map((documentRecord) => (
        <li key={documentRecord.document_id}>
          <button
            type="button"
            disabled={disabled}
            onClick={() => onOpen(documentRecord.document_id)}
            className="btn btn-outline btn-xs"
          >
            <Icon name="document" className="h-3.5 w-3.5" /> View {describeDocumentKind(documentRecord.kind)}
          </button>
        </li>
      ))}
    </ul>
  )
}
