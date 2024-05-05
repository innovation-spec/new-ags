import { Link } from 'react-router-dom'
import { CheckCircle2, FileSpreadsheet, FlaskConical } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { coveragePhases, workbookControls } from '../data/coverage'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export function CoveragePage() {
  return <>
    <PageHeader eyebrow="2024 engineering workbook" title="R&D implementation coverage" description="A transparent mapping from the nine reconstructed workstreams to the working local demo and its evidence-oriented controls." />
    <Card className="mb-5"><CardContent className="workbook-banner p-5"><FileSpreadsheet /><div><strong>Workbook control totals</strong><p>These are workbook-derived evidence metadata, not live runtime measurements.</p></div><div className="workbook-numbers"><span><strong>{workbookControls.tickets}</strong> tickets</span><span><strong>{workbookControls.hours.toLocaleString(undefined, { maximumFractionDigits: 2 })}</strong> reconstructed hours</span><span><strong>{workbookControls.employeeTickets}</strong> employee tickets</span><span><strong>{workbookControls.contractorTickets}</strong> contractor tickets</span></div></CardContent></Card>
