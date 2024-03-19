import * as React from 'react'
import { cn } from '@/lib/utils'

export const Table = React.forwardRef<HTMLTableElement, React.HTMLAttributes<HTMLTableElement>>(({ className, ...props }, ref) => <div className="relative w-full overflow-auto"><table ref={ref} className={cn('w-full caption-bottom text-sm', className)} {...props} /></div>)
Table.displayName = 'Table'
export const TableHeader = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(({ className, ...props }, ref) => <thead ref={ref} className={cn('[&_tr]:border-b', className)} {...props} />)
TableHeader.displayName = 'TableHeader'
export const TableBody = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(({ className, ...props }, ref) => <tbody ref={ref} className={cn('[&_tr:last-child]:border-0', className)} {...props} />)
