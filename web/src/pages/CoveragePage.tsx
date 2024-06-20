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
    <div className="coverage-list">{coveragePhases.map(phase => <Card key={phase.id} className="overflow-hidden"><CardContent className="grid grid-cols-[74px_1fr] p-0 max-sm:grid-cols-1"><div className="coverage-id">{phase.id}</div><div className="coverage-body"><div className="coverage-title"><div><h2>{phase.title}</h2><p>{phase.objective}</p></div><Badge variant="success" className="gap-1.5"><CheckCircle2 className="size-4" />Implemented in demo</Badge></div><div className="coverage-implementation"><strong>Implementation</strong><p>{phase.implementation}</p></div><div className="evidence-chips">{phase.evidence.map(item => <Badge variant="secondary" key={item}>{item}</Badge>)}</div><div className="coverage-footer"><span>{phase.tickets} tickets · {phase.hours.toLocaleString()} hours</span><Button asChild variant="link" size="sm"><Link to={phase.route}>Open feature →</Link></Button></div></div></CardContent></Card>)}</div>
    <Alert><FlaskConical className="size-4" /><AlertTitle>Important evidence note</AlertTitle><AlertDescription>The workbook itself states that ticket wording/module paths are reconstructed and should be validated against contemporaneous source control/Jira/ADO records. This page therefore shows demo alignment, not a claim that the new demo source is the original 2024 source artifact.</AlertDescription></Alert>
  </>
}
