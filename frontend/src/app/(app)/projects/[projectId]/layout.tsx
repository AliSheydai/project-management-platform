import { ProjectLayoutShell } from "@/components/projects/project-layout-shell";

export default async function ProjectLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return (
    <ProjectLayoutShell projectId={projectId}>{children}</ProjectLayoutShell>
  );
}
