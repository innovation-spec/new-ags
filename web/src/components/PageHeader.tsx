import type { ReactNode } from 'react'
export function PageHeader({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description: string; actions?: ReactNode }) {
  return <div className="page-header">
    <div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h1 className="text-3xl font-semibold tracking-tight md:text-4xl">{title}</h1><p>{description}</p></div>
