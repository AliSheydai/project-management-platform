import { ActivityView } from "@/components/activity/activity-view";

export default async function ProjectActivityPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return <ActivityView projectId={projectId} />;
}
