// ===== AI GENERATED: mockup_sample_data =====
// Purpose: Invented sample data for the design-preview screens (expenses, payroll, advances, billing, reports)
// Inputs: none
// Returns: arrays and objects used only by Preview* components
// Flow:
// 1. Nothing here is real and nothing is sent to the backend
// 2. Amounts follow the specification's worked example (charge 20,000, expenses 5,500)

export const SAMPLE_EXPENSES = [
  { id: 'x1', trip: 'Plant → Subic · Nov 12', category: 'Fuel', amount: 4200, state: 'FINALIZED', enteredBy: 'Dee Dispatcher' },
  { id: 'x2', trip: 'Plant → Subic · Nov 12', category: 'Toll', amount: 1300, state: 'FINALIZED', enteredBy: 'Dee Dispatcher' },
  { id: 'x3', trip: 'Mill → Mandaue · Nov 13', category: 'Fuel', amount: 3100, state: 'AWAITING_REVIEW', enteredBy: 'Juan Santos' },
  { id: 'x4', trip: 'Mill → Mandaue · Nov 13', category: 'Toll', amount: 600, state: 'AWAITING_REVIEW', enteredBy: 'Juan Santos' },
  { id: 'x5', trip: 'Plant → Manila · Nov 14', category: 'Fuel', amount: 2800, state: 'ENTERING', enteredBy: 'Dee Dispatcher' },
  { id: 'x6', trip: 'Plant → Batangas · Nov 14', category: 'No expenses', amount: 0, state: 'ZERO_CONFIRMED', enteredBy: 'Dee Dispatcher' },
]

export const SAMPLE_PAYROLL_PERIOD = { label: 'Nov 1 – 15, 2026', status: 'PENDING_CALCULATION' }

export const SAMPLE_CALCULATION = {
  charge: 20000,
  expenses: 5500,
  base: 14500,
  oneHelper: [
    { role: 'Driver', percent: 8, amount: 1160 },
    { role: 'Helper', percent: 4, amount: 580 },
  ],
  twoHelpers: [
    { role: 'Driver', percent: 6, amount: 870 },
    { role: 'Helper 1', percent: 3, amount: 435 },
    { role: 'Helper 2', percent: 3, amount: 435 },
  ],
}

export const SAMPLE_EARNINGS = [
  { id: 'e1', employee: 'Juan Santos', role: 'Driver', trip: 'Plant → Subic', percent: 8, base: 14500, amount: 1160 },
  { id: 'e2', employee: 'Mario Cruz', role: 'Helper', trip: 'Plant → Subic', percent: 4, base: 14500, amount: 580 },
  { id: 'e3', employee: 'Pedro Lim', role: 'Driver', trip: 'Mill → Mandaue', percent: 6, base: 14500, amount: 870 },
  { id: 'e4', employee: 'Ramon Diaz', role: 'Helper', trip: 'Mill → Mandaue', percent: 3, base: 14500, amount: 435 },
  { id: 'e5', employee: 'Luis Tan', role: 'Helper', trip: 'Mill → Mandaue', percent: 3, base: 14500, amount: 435 },
]

export const SAMPLE_STATEMENT = {
  employee: 'Juan Santos',
  period: 'Nov 1 – 15, 2026',
  trips: [
    { id: 's1', trip: 'Plant → Subic · Nov 12', percent: 8, amount: 1160 },
    { id: 's2', trip: 'Mill → Mandaue · Nov 13', percent: 8, amount: 1160 },
    { id: 's3', trip: 'Plant → Manila · Nov 14', percent: 8, amount: 1160 },
    { id: 's4', trip: 'Plant → Batangas · Nov 14', percent: 8, amount: 2520 },
  ],
  gross: 6000,
  deduction: 300,
  deductionNote: 'Damaged straps',
  repayment: 1000,
  net: 4700,
  remainingAdvance: 2000,
}

export const SAMPLE_ADVANCES = [
  { id: 'a1', employee: 'Juan Santos', amount: 3000, status: 'REPAYING', balance: 2000, note: '₱1,000 per payroll' },
  { id: 'a2', employee: 'Mario Cruz', amount: 2000, status: 'APPROVED', balance: 0, note: 'Waiting to be released' },
  { id: 'a3', employee: 'Pedro Lim', amount: 1500, status: 'REQUESTED', balance: 0, note: 'Waiting for Owner approval' },
  { id: 'a4', employee: 'Ramon Diaz', amount: 1000, status: 'SETTLED', balance: 0, note: 'Fully repaid' },
]

export const SAMPLE_UNBILLED_TRIPS = [
  { id: 'u1', trip: 'Plant → Subic', date: 'Nov 12', charge: 20000, carried: false },
  { id: 'u2', trip: 'Mill → Mandaue', date: 'Nov 13', charge: 18500, carried: false },
  { id: 'u3', trip: 'Plant → Manila', date: 'Oct 29', charge: 15200, carried: true },
]

export const SAMPLE_BATCHES = [
  { id: 'B-2026-11-A', trips: 6, total: 112400, status: 'DRAFT', paid: 0 },
  { id: 'B-2026-10-B', trips: 9, total: 168000, status: 'PARTIALLY_PAID', paid: 100000 },
  { id: 'B-2026-10-A', trips: 8, total: 140250, status: 'PAID', paid: 140250 },
  { id: 'B-2026-09-C', trips: 2, total: 31000, status: 'VOID', paid: 0 },
]

export const SAMPLE_REPORTS = {
  kpis: [
    { label: 'Deliveries this month', value: '42', hint: '+6 vs last month', tone: 'primary', icon: 'truck' },
    { label: 'Tons hauled', value: '1,036 t', hint: 'Across 7 trucks', tone: 'info', icon: 'chart' },
    { label: 'Awaiting OR receipt', value: '5', hint: 'Oldest: 3 days', tone: 'warning', icon: 'document' },
    { label: 'No stamped copy', value: '3', hint: 'For owner spot-check', tone: 'error', icon: 'alert' },
  ],
  weekly: [
    { label: 'Wk 1', value: 8 },
    { label: 'Wk 2', value: 11 },
    { label: 'Wk 3', value: 9 },
    { label: 'Wk 4', value: 14 },
  ],
  utilization: [
    { plate: 'ABC 1234', percent: 86 },
    { plate: 'DEF 5678', percent: 72 },
    { plate: 'GHI 9012', percent: 64 },
    { plate: 'JKL 3456', percent: 35 },
  ],
  withoutStampedCopy: [
    { id: 'r1', trip: 'Plant → Subic · Nov 9', driver: 'Juan Santos' },
    { id: 'r2', trip: 'Mill → Mandaue · Nov 10', driver: 'Pedro Lim' },
    { id: 'r3', trip: 'Plant → Manila · Nov 11', driver: 'Juan Santos' },
  ],
}
