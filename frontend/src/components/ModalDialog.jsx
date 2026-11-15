// ===== AI GENERATED: ModalDialog =====
// Purpose: An accessible modal (native dialog) that slides up on phones and centres on desktop
// Inputs: title, open flag, close handler and content (props only)
// Returns: dialog markup; content is only mounted while open so forms reset
// Flow:
// 1. showModal / close follow the isOpen prop
// 2. Escape, the backdrop and the close button all call onClose

import { useEffect, useRef } from 'react'
import { Icon } from './Icon'

/**
 * @function ModalDialog
 * @description Pure UI modal.
 * @param {{title: string, isOpen: boolean, onClose: function(): void, wide?: boolean, children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function ModalDialog({ title, isOpen, onClose, wide = false, children }) {
  const dialogReference = useRef(null)

  useEffect(() => {
    const dialogElement = dialogReference.current
    if (!dialogElement) return
    if (isOpen && !dialogElement.open) dialogElement.showModal()
    if (!isOpen && dialogElement.open) dialogElement.close()
  }, [isOpen])

  return (
    <dialog ref={dialogReference} className="modal modal-bottom sm:modal-middle" onClose={onClose}>
      <div className={`modal-box ${wide ? 'sm:max-w-2xl' : ''}`}>
        <form method="dialog">
          <button type="submit" className="btn btn-sm btn-circle btn-ghost absolute right-3 top-3" aria-label="Close">
            <Icon name="x" className="h-4 w-4" />
          </button>
        </form>
        <h3 className="pr-8 text-lg font-bold">{title}</h3>
        <div className="mt-4">{isOpen ? children : null}</div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button type="submit" aria-label="Close dialog">
          close
        </button>
      </form>
    </dialog>
  )
}
