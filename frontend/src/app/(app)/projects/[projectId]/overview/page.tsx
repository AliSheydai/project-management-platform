import { ProjectOverviewView } from "@/components/projects/project-overview-view";

export default async function ProjectOverviewPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return <ProjectOverviewView projectId={projectId} />;
}
